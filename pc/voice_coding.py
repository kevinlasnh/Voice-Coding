"""
Voicing - PC Application
语音编程 - 电脑端应用

A system tray application that receives text from phone and types it at cursor position.
系统托盘应用，接收手机发送的文本并在光标处输入。
"""

import asyncio
import ipaddress
import json
import logging
import os
import re
import socket
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional

# PyQt5 for modern tray menu
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMessageBox,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QMenu,
)
from PyQt5.QtCore import (
    QObject,
    Qt,
    QTimer,
    pyqtSignal,
    pyqtProperty,
    QPoint,
    QPointF,
    QRect,
    QEasingCurve,
    QPropertyAnimation,
    QParallelAnimationGroup,
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QCursor, QFont, QPen

# Third-party imports
import qrcode
import websockets
from websockets.server import serve
from PIL import Image, ImageDraw

try:
    import psutil
except Exception:
    psutil = None

from device_identity import get_or_create_device_identity
from platform_autostart import is_startup_enabled, set_startup_enabled
from platform_instance import check_single_instance, show_already_running_message
from platform_keyboard import (
    PasteMode,
    get_paste_mode,
    get_paste_mode_label,
    press_enter,
    set_paste_mode,
    start_wayland_focus_prewarm,
    type_text_at_cursor,
)
from platform_utils import (
    WINDOWS_HOTSPOT_PREFIXES,
    ensure_runtime_supported,
    get_default_server_ip,
    get_known_hotspot_prefixes,
    get_log_dir,
    get_native_font_family,
    get_platform,
    get_preferred_hotspot_prefixes,
    open_file_in_default_app,
    open_file_in_text_editor,
)
from voicing_protocol import (
    QR_SCAN_PING_SOURCE,
    TYPE_PING,
    TYPE_TEXT,
    WEBSOCKET_PORT,
    TEXT_SEND_MODE_COMMIT,
    TEXT_SEND_MODE_SUBMIT,
    build_ack_message,
    build_connected_message,
    build_qr_payload,
    build_pong_message,
    build_sync_disabled_message,
    build_sync_state_message,
)

# ============================================================
# Configuration / 配置
# ============================================================
APP_NAME = "Voicing"
APP_VERSION = "2.9.10"
WS_PORT = WEBSOCKET_PORT      # WebSocket port
AUTO_ENTER_SETTLE_DELAY_SEC = 0.35
NATIVE_FONT_FAMILY = get_native_font_family()
NETWORK_INTERFACE_REFRESH_SEC = 1


# ============================================================
# Global State / 全局状态
# ============================================================
class UiSignals(QObject):
    qr_scan_succeeded = pyqtSignal(str)


class AppState:
    """Application state management / 应用状态管理"""
    def __init__(self):
        self.sync_enabled = True
        self.running = True
        self.server = None
        self.tray_icon = None
        self.ws_port = WS_PORT
        self.connected_clients = set()
        self.blink_state = False  # For icon blinking / 图标闪烁状态
        self.blink_timer: Optional[threading.Timer] = None
        self.log_file = None  # 日志文件路径
        self.lock = threading.Lock()  # 保护共享状态
        self.shutdown_event = threading.Event()  # 用于优雅退出
        self.qr_dialog = None  # QR 码弹窗（懒加载）
        self.ui_signals = None  # Qt UI 线程信号桥
        self.bound_ws_host = None  # 当前 WebSocket 实际绑定地址
        self.bound_ws_hosts = []  # 当前 WebSocket 实际绑定成功的地址列表
        self.server_loop = None  # WebSocket server 所属 asyncio event loop

state = AppState()


def notify_qr_scan_succeeded(reason="unknown"):
    logging.info(f"QR 扫码连通成功信号: {reason}")
    signals = state.ui_signals
    if signals is not None:
        signals.qr_scan_succeeded.emit(reason)
    else:
        logging.warning("QR 扫码连通成功信号未送达：UI signal bridge 尚未初始化")


def show_qr_scan_success(reason="unknown"):
    logging.info(f"准备播放 QR 成功态动画: {reason}")
    if state.qr_dialog is not None:
        state.qr_dialog.show_scan_success()


# ============================================================
# Logging Setup / 日志配置
# ============================================================
def setup_logging():
    """设置日志系统"""
    # 日志文件保存在用户数据目录
    log_dir = get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 使用日期作为文件名
    from datetime import datetime
    log_file = log_dir / f"voice_coding_{datetime.now().strftime('%Y%m%d')}.log"
    state.log_file = log_file
    
    # 配置 logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # 同时输出到控制台
        ]
    )
    logging.info(f"=== Voicing 启动 ===")
    logging.info(f"日志文件: {log_file}")


# ============================================================
# Network Configuration / 网络配置
# ============================================================
# Platform discovery default IP / 平台默认发现 IP
DEFAULT_SERVER_IP = get_default_server_ip()
class NetworkInterfaceCandidate(NamedTuple):
    ip: str
    prefix_length: int
    name: str
    interface_type: str


def get_hotspot_ip() -> str:
    """
    Get the actual hotspot IP address / 获取热点的实际 IP 地址
    
    Windows Mobile Hotspot typically uses 192.168.137.1, but this function
    will try to detect the actual IP by looking for the hotspot adapter.
    """
    try:
        all_local_ips = get_all_local_ips()
        for prefixes in (get_preferred_hotspot_prefixes(), get_known_hotspot_prefixes()):
            for adapter_ip in all_local_ips:
                if any(adapter_ip.startswith(prefix) for prefix in prefixes):
                    return adapter_ip

        if all_local_ips:
            return all_local_ips[0]

        return DEFAULT_SERVER_IP

    except Exception as e:
        logging.warning(f"Error detecting hotspot IP: {e}")
        return DEFAULT_SERVER_IP


def get_all_local_ips() -> list:
    """Get all local IP addresses / 获取所有本地 IP 地址"""
    discovered_ips = [ip for ip, _ in get_all_local_interfaces()]
    if discovered_ips:
        return discovered_ips

    fallback_ips = []
    seen = set()

    def add_fallback_ip(ip: str) -> None:
        if _is_discoverable_private_ip(ip, require_private=True) and ip not in seen:
            seen.add(ip)
            fallback_ips.append(ip)

    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            add_fallback_ip(info[4][0])
    except Exception:
        pass

    return _sort_ip_addresses(fallback_ips)


def get_all_network_candidates() -> list[NetworkInterfaceCandidate]:
    """Return physical-ish private IPv4 interfaces sorted by connection priority."""
    platform_name = get_platform()
    candidates = get_psutil_network_candidates(platform_name)
    if candidates:
        return candidates
    return get_command_network_candidates(platform_name)


def get_psutil_network_candidates(
    platform_name: str,
) -> list[NetworkInterfaceCandidate]:
    """Fast in-process interface discovery used for runtime QR/WS refresh."""
    if psutil is None:
        return []

    try:
        adapters = psutil.net_if_addrs()
    except Exception as exc:
        logging.debug(f"psutil 网络接口探测失败: {exc}")
        return []

    interfaces: list[NetworkInterfaceCandidate] = []
    seen: set[tuple[str, int]] = set()
    for interface_name, addresses in adapters.items():
        for address in addresses:
            if address.family != socket.AF_INET:
                continue
            prefix_length = _prefix_length_from_netmask(address.netmask)
            candidate = _build_network_interface_candidate(
                platform_name,
                address.address,
                prefix_length,
                interface_name,
            )
            if candidate is None:
                continue
            key = (candidate.ip, candidate.prefix_length)
            if key in seen:
                continue
            seen.add(key)
            interfaces.append(candidate)

    return _sort_interface_candidates(interfaces, platform_name)


def get_command_network_candidates(
    platform_name: str | None = None,
) -> list[NetworkInterfaceCandidate]:
    """Slower command-based fallback for platforms without psutil."""
    platform_name = platform_name or get_platform()
    interface_discovery_commands = {
        "windows": [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-NetIPAddress -AddressFamily IPv4 | "
                "Select-Object IPAddress, PrefixLength, InterfaceAlias, AddressState, SkipAsSource | "
                "ConvertTo-Json -Compress"
            ),
        ],
        "darwin": ["ifconfig"],
        "linux": ["ip", "-j", "-4", "addr", "show", "up", "scope", "global"],
    }
    command = interface_discovery_commands.get(platform_name)
    if not command:
        return []

    creationflags = 0
    if platform_name == "windows":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            creationflags=creationflags,
            check=False,
        )
    except Exception as exc:
        logging.debug(f"网络接口探测命令执行失败: {exc}")
        return []

    if result.returncode != 0 and not result.stdout.strip():
        logging.debug(f"网络接口探测命令返回非零退出码: {result.returncode}")
        return []

    return extract_command_interface_candidates(platform_name, result.stdout)


def extract_command_ips(platform_name: str, command_output: str) -> list[str]:
    if platform_name == "windows":
        return [
            line.strip()
            for line in command_output.splitlines()
            if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", line.strip())
        ]

    if platform_name == "darwin":
        return [
            match.group(1)
            for match in re.finditer(r"\binet\s+(\d{1,3}(?:\.\d{1,3}){3})\b", command_output)
        ]

    if platform_name == "linux":
        return [
            match.group(1)
            for match in re.finditer(r"\binet\s+(\d{1,3}(?:\.\d{1,3}){3})/\d+\b", command_output)
        ]

    return []


def get_all_local_interfaces() -> list[tuple[str, int]]:
    """Return broadcast-capable private IPv4 interfaces as (ip, prefix_length)."""
    return [
        (candidate.ip, candidate.prefix_length)
        for candidate in get_all_network_candidates()
    ]


def extract_command_interfaces(platform_name: str, command_output: str) -> list[tuple[str, int]]:
    return [
        (candidate.ip, candidate.prefix_length)
        for candidate in extract_command_interface_candidates(platform_name, command_output)
    ]


def _prefix_length_from_netmask(netmask: str | None) -> Optional[int]:
    if not netmask:
        return None
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}").prefixlen
    except ValueError:
        return None


def _build_network_interface_candidate(
    platform_name: str,
    ip: str,
    prefix_length: Optional[int],
    name: str = "",
) -> Optional[NetworkInterfaceCandidate]:
    try:
        normalized_prefix = int(prefix_length)
    except (TypeError, ValueError):
        return None
    if not _is_discoverable_private_ip(ip, normalized_prefix):
        return None
    normalized_name = str(name or "").strip()
    if _is_vpn_or_virtual_interface(platform_name, normalized_name):
        return None
    return NetworkInterfaceCandidate(
        ip=ip,
        prefix_length=normalized_prefix,
        name=normalized_name,
        interface_type=_classify_interface_type(platform_name, normalized_name),
    )


def extract_command_interface_candidates(
    platform_name: str,
    command_output: str,
) -> list[NetworkInterfaceCandidate]:
    command_output = command_output.strip()
    if not command_output:
        return []

    interfaces: list[NetworkInterfaceCandidate] = []
    seen: set[tuple[str, int]] = set()

    def add_interface(ip: str, prefix_length: int, name: str = "") -> None:
        interface = _build_network_interface_candidate(
            platform_name,
            ip,
            prefix_length,
            name,
        )
        if interface is None:
            return
        candidate = (interface.ip, interface.prefix_length)
        if candidate in seen:
            return
        seen.add(candidate)
        interfaces.append(interface)

    if platform_name == "windows":
        try:
            records = json.loads(command_output)
            if isinstance(records, dict):
                records = [records]
            if isinstance(records, list):
                for record in records:
                    if not isinstance(record, dict):
                        continue
                    address_state = record.get("AddressState")
                    if address_state not in (None, "Preferred", 4):
                        continue
                    if record.get("SkipAsSource") is True:
                        continue
                    add_interface(
                        record.get("IPAddress", ""),
                        record.get("PrefixLength"),
                        record.get("InterfaceAlias", ""),
                    )
                return _sort_interface_candidates(interfaces, platform_name)
        except json.JSONDecodeError:
            pass

        for ip, prefix_length in re.findall(
            r"(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,2})",
            command_output,
        ):
            add_interface(ip, int(prefix_length))
        return _sort_interface_candidates(interfaces, platform_name)

    if platform_name == "linux":
        try:
            records = json.loads(command_output)
            if not isinstance(records, list):
                return []
            for record in records:
                if not isinstance(record, dict):
                    continue
                interface_name = str(record.get("ifname", ""))
                for addr_info in record.get("addr_info", []):
                    if not isinstance(addr_info, dict):
                        continue
                    if addr_info.get("family") != "inet":
                        continue
                    if addr_info.get("scope") != "global":
                        continue
                    if "broadcast" not in addr_info:
                        continue
                    add_interface(
                        addr_info.get("local", ""),
                        addr_info.get("prefixlen"),
                        interface_name,
                    )
        except json.JSONDecodeError:
            pass
        return _sort_interface_candidates(interfaces, platform_name)

    if platform_name == "darwin":
        supports_broadcast = False
        interface_name = ""
        for raw_line in command_output.splitlines():
            line = raw_line.rstrip()
            header_match = re.match(r"^([^\s:]+):\s+flags=\d+<([^>]*)>", line)
            if header_match:
                interface_name = header_match.group(1)
                flags = {flag.strip().upper() for flag in header_match.group(2).split(",")}
                supports_broadcast = (
                    "UP" in flags
                    and "BROADCAST" in flags
                    and "POINTOPOINT" not in flags
                    and not _is_vpn_or_virtual_interface(platform_name, interface_name)
                )
                continue

            if not supports_broadcast:
                continue

            match = re.search(
                r"\binet\s+(\d{1,3}(?:\.\d{1,3}){3})\s+netmask\s+(0x[0-9a-fA-F]+)\b",
                line,
            )
            if not match:
                continue
            prefix_length = bin(int(match.group(2), 16)).count("1")
            add_interface(match.group(1), prefix_length, interface_name)
        return _sort_interface_candidates(interfaces, platform_name)

    return []


def calculate_broadcast_addresses(
    interfaces: list[tuple[str, int]],
) -> list[tuple[str, str]]:
    """Convert interface prefixes to directed broadcast targets."""
    result = []
    seen = set()
    for ip, prefix_length in interfaces:
        try:
            network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
        except ValueError:
            continue
        candidate = (ip, str(network.broadcast_address))
        if candidate in seen:
            continue
        seen.add(candidate)
        result.append(candidate)
    return result


def _is_discoverable_private_ip(
    ip: str,
    prefix_length: Optional[int] = None,
    *,
    require_private: bool = True,
) -> bool:
    try:
        address = ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError:
        return False

    if (
        address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_unspecified
    ):
        return False

    if require_private and not address.is_private:
        return False

    if prefix_length is None:
        return True

    return 1 <= prefix_length <= 30


def _is_vpn_or_virtual_interface(platform_name: str, interface_name: str) -> bool:
    normalized = interface_name.lower()
    if not normalized:
        return False

    windows_markers = (
        "tap",
        "wintun",
        "wireguard",
        "pangp",
        "cisco anyconnect",
        "openvpn",
        "hyper-v",
        "vethernet",
        "tailscale",
        "zerotier",
    )
    if platform_name == "windows":
        return any(marker in normalized for marker in windows_markers)

    unix_vpn_prefixes = ("tun", "tap", "utun", "wg", "ppp", "tailscale", "zt")
    if platform_name in {"linux", "darwin"}:
        return normalized.startswith(unix_vpn_prefixes)

    return False


def _classify_interface_type(platform_name: str, interface_name: str) -> str:
    normalized = interface_name.lower()
    if platform_name == "windows":
        if "ethernet" in normalized or "以太网" in interface_name:
            return "ethernet"
        if (
            "wi-fi" in normalized
            or "wifi" in normalized
            or "wlan" in normalized
            or "wireless" in normalized
            or "local area connection" in normalized
        ):
            return "wifi"
        return "unknown"

    if platform_name == "linux":
        if re.match(r"^(eth|en[opsx])", normalized):
            return "ethernet"
        if re.match(r"^(wlan|wlp|wlx)", normalized):
            return "wifi"
        return "unknown"

    if platform_name == "darwin":
        if re.match(r"^en\d+$", normalized):
            return "unknown"
        return "unknown"

    return "unknown"


def _sort_ip_addresses(ips: list[str]) -> list[str]:
    return sorted(ips, key=_ip_sort_key)


def _sort_interfaces(interfaces: list[tuple[str, int]]) -> list[tuple[str, int]]:
    return sorted(interfaces, key=lambda item: (_ip_sort_key(item[0]), item[1]))


def _sort_interface_candidates(
    interfaces: list[NetworkInterfaceCandidate],
    platform_name: str,
) -> list[NetworkInterfaceCandidate]:
    priority = {
        "ethernet": 0,
        "wifi": 1,
        "unknown": 2,
    }
    return sorted(
        interfaces,
        key=lambda item: (
            _windows_hotspot_rank(platform_name, item.ip),
            priority.get(item.interface_type, 3),
            _ip_sort_key(item.ip),
            item.prefix_length,
            item.name.lower(),
        ),
    )


def _windows_hotspot_rank(platform_name: str, ip: str) -> int:
    if platform_name == "windows" and any(
        ip.startswith(prefix) for prefix in WINDOWS_HOTSPOT_PREFIXES
    ):
        return 0
    return 1


def _ip_sort_key(ip: str) -> tuple[int, str]:
    if any(ip.startswith(prefix) for prefix in get_preferred_hotspot_prefixes()):
        return (0, ip)
    if any(ip.startswith(prefix) for prefix in get_known_hotspot_prefixes()):
        return (1, ip)
    return (2, ip)


def refresh_server_interfaces(*, log_changes: bool = True) -> list[tuple[str, str]]:
    """Refresh the QR/WS interface snapshot from the current OS network state."""
    global SERVER_INTERFACES, SERVER_INTERFACES_INITIALIZED

    discovered_interfaces = get_all_network_candidates()
    latest_interfaces = calculate_broadcast_addresses(
        [(candidate.ip, candidate.prefix_length) for candidate in discovered_interfaces]
    )

    with SERVER_INTERFACES_LOCK:
        was_initialized = SERVER_INTERFACES_INITIALIZED
        previous_interfaces = list(SERVER_INTERFACES)
        changed = latest_interfaces != SERVER_INTERFACES
        if changed:
            SERVER_INTERFACES = latest_interfaces
        SERVER_INTERFACES_INITIALIZED = True
        snapshot = list(SERVER_INTERFACES)

    if log_changes and (changed or not was_initialized):
        logging.info(
            "QR/WS 网络接口刷新: "
            f"{_format_server_interface_ips(previous_interfaces)} -> "
            f"{_format_server_interface_ips(snapshot)}"
        )
        log_detected_network_interfaces(discovered_interfaces)

    return snapshot


def get_server_interfaces(*, refresh: bool = False) -> list[tuple[str, str]]:
    if refresh:
        return refresh_server_interfaces()
    with SERVER_INTERFACES_LOCK:
        return list(SERVER_INTERFACES)


def _format_server_interface_ips(interfaces: list[tuple[str, str]]) -> str:
    return ", ".join(ip for ip, _broadcast in interfaces) or "none"


def get_primary_server_ip(*, refresh: bool = False) -> str:
    server_interfaces = get_server_interfaces(refresh=refresh)
    if server_interfaces:
        return server_interfaces[0][0]
    return get_hotspot_ip()


def get_advertised_server_ips(*, refresh: bool = False) -> list[str]:
    ips: list[str] = []
    for ip, _broadcast in get_server_interfaces(refresh=refresh):
        if ip not in ips:
            ips.append(ip)
    if not ips:
        fallback_ip = get_hotspot_ip()
        if fallback_ip:
            ips.append(fallback_ip)
    return ips


def get_bound_server_ips() -> list[str]:
    with state.lock:
        return list(state.bound_ws_hosts)


def set_bound_server_ips(hosts: list[str]) -> None:
    normalized_hosts = list(dict.fromkeys(hosts))
    with state.lock:
        state.bound_ws_hosts = normalized_hosts
        state.bound_ws_host = ",".join(normalized_hosts) if normalized_hosts else None


def get_qr_advertised_server_ips(*, refresh: bool = False) -> list[str]:
    bound_ips = get_bound_server_ips()
    if bound_ips:
        return bound_ips
    return get_advertised_server_ips(refresh=refresh)


def log_detected_network_interfaces(interfaces: list[NetworkInterfaceCandidate]) -> None:
    if not interfaces:
        logging.warning("未检测到可用于 QR 连接的私有 IPv4 接口。")
        logging.info(f"回退 QR IP: {get_hotspot_ip()}")
        return

    logging.info(f"检测到 {len(interfaces)} 个 QR 连接候选网络接口:")
    for candidate in interfaces:
        label = candidate.interface_type
        if any(candidate.ip.startswith(prefix) for prefix in get_known_hotspot_prefixes()):
            label = f"{label}/hotspot"
        logging.info(f"  - {candidate.ip}/{candidate.prefix_length} ({label}; {candidate.name or 'unknown'})")


# Will be set at runtime / 运行时设置
SERVER_INTERFACES: list[tuple[str, str]] = []
SERVER_INTERFACES_LOCK = threading.Lock()
SERVER_INTERFACES_INITIALIZED = False


# ============================================================
# Text Input / 文本输入
# ============================================================
def type_text(text: str, auto_enter: bool = False) -> bool:
    """
    Type text at current cursor position.
    在当前光标位置输入文本。

    Uses clipboard paste for cross-platform Unicode input.

    Args:
        text: Text to type
        auto_enter: If True, press Enter after typing
    """
    if not text or not state.sync_enabled:
        return False

    try:
        type_text_at_cursor(
            text,
            auto_enter=auto_enter,
            enter_delay_sec=AUTO_ENTER_SETTLE_DELAY_SEC,
        )
        return True

    except Exception as e:
        logging.error(f"Error typing text: {e}")
        return False


def press_enter_after_settle(delay_sec: float = AUTO_ENTER_SETTLE_DELAY_SEC) -> bool:
    """Press Enter after giving the target app time to consume a paste event."""
    try:
        threading.Event().wait(delay_sec)
        press_enter()
        return True
    except Exception as e:
        logging.error(f"Error pressing Enter: {e}")
        return False


# ============================================================
# Reserved for future features / 保留给未来功能
# ============================================================


# ============================================================
# WebSocket Server / WebSocket 服务器
# ============================================================
async def handle_client(websocket):
    """Handle incoming WebSocket connections / 处理传入的WebSocket连接"""
    client_addr = websocket.remote_address
    with state.lock:
        state.connected_clients.add(websocket)
    print(f"Client connected: {client_addr}")

    try:
        # Get computer name for identification
        device_identity = get_or_create_device_identity()

        # Send welcome message with current sync state and computer name
        await websocket.send(json.dumps(build_connected_message(
            sync_enabled=state.sync_enabled,
            computer_name=device_identity.name,
            device_id=device_identity.device_id,
            os_name=device_identity.os,
        )))

        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type", "")

                if msg_type == TYPE_TEXT:
                    # Check if sync is enabled
                    if not state.sync_enabled:
                        await websocket.send(json.dumps(build_sync_disabled_message()))
                        continue

                    text = data.get("content", "")
                    send_mode = data.get("send_mode", TEXT_SEND_MODE_SUBMIT)
                    auto_enter = data.get("auto_enter", False) and send_mode == TEXT_SEND_MODE_SUBMIT
                    if send_mode == TEXT_SEND_MODE_COMMIT:
                        entered = False
                        if data.get("auto_enter", False):
                            entered = await asyncio.to_thread(press_enter_after_settle)
                        await websocket.send(json.dumps(build_ack_message(
                            clear_input=entered,
                        )))
                    elif text:
                        # Type the received text (run in thread to avoid blocking event loop)
                        typed = await asyncio.to_thread(type_text, text, auto_enter)
                        # Send acknowledgment
                        await websocket.send(json.dumps(build_ack_message(
                            clear_input=typed and send_mode == TEXT_SEND_MODE_SUBMIT,
                        )))

                elif msg_type == TYPE_PING:
                    if data.get("source") == QR_SCAN_PING_SOURCE:
                        notify_qr_scan_succeeded("qr_scan_probe")
                    # Respond with pong and current sync state
                    await websocket.send(json.dumps(build_pong_message(
                        sync_enabled=state.sync_enabled,
                    )))

            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                if message.strip() and state.sync_enabled:
                    await asyncio.to_thread(type_text, message)
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        with state.lock:
            state.connected_clients.discard(websocket)
        print(f"Client disconnected: {client_addr}")


async def broadcast_sync_state():
    """Broadcast sync state to all connected clients / 广播同步状态给所有客户端"""
    if not state.connected_clients:
        return
    
    message = json.dumps(build_sync_state_message(sync_enabled=state.sync_enabled))
    
    for client in state.connected_clients.copy():  # copy() 避免迭代时修改
        try:
            await client.send(message)
        except Exception:
            pass


def schedule_sync_state_broadcast():
    """Schedule sync state broadcast on the WebSocket server loop."""
    loop = state.server_loop
    if loop is None or loop.is_closed():
        logging.warning("同步状态广播跳过：WebSocket event loop 尚未可用")
        return

    future = asyncio.run_coroutine_threadsafe(broadcast_sync_state(), loop)

    def log_broadcast_error(completed_future):
        try:
            completed_future.result()
        except Exception as exc:
            logging.warning(f"同步状态广播失败: {exc}")

    future.add_done_callback(log_broadcast_error)


async def start_server():
    """Start the WebSocket server / 启动WebSocket服务器"""
    state.server_loop = asyncio.get_running_loop()
    while state.running:
        bind_hosts = get_advertised_server_ips(refresh=True)
        servers = []
        bound_hosts = []
        try:
            for bind_host in bind_hosts:
                try:
                    server = await serve(handle_client, bind_host, state.ws_port)
                except OSError as e:
                    logging.error(f"WebSocket 绑定 {bind_host}:{state.ws_port} 失败: {e}")
                    continue
                servers.append(server)
                bound_hosts.append(bind_host)
                print(f"WebSocket server started at ws://{bind_host}:{state.ws_port}")

            if not servers:
                set_bound_server_ips([])
                logging.error(
                    "没有可监听的物理网络接口，WebSocket server 暂停重试。"
                )
                await asyncio.sleep(2)
                continue

            set_bound_server_ips(bound_hosts)
            logging.info(
                "WebSocket server listening on physical interfaces: "
                f"{', '.join(f'{host}:{state.ws_port}' for host in bound_hosts)}"
            )
            while state.running:
                await asyncio.sleep(NETWORK_INTERFACE_REFRESH_SEC)
                latest_hosts = get_advertised_server_ips(refresh=True)
                if set(latest_hosts) != set(bound_hosts):
                    old_hosts = ", ".join(bound_hosts) or "none"
                    new_hosts = ", ".join(latest_hosts) or "none"
                    logging.info(f"WebSocket 监听接口变化: {old_hosts} -> {new_hosts}")
                    break
        except Exception as e:
            print(f"Server error: {e}")
            logging.error(f"WebSocket server error: {e}")
            await asyncio.sleep(2)
        finally:
            for server in servers:
                server.close()
            if servers:
                logging.info(
                    "WebSocket server closing listeners: "
                    f"{', '.join(f'{host}:{state.ws_port}' for host in bound_hosts)}"
                )
                await asyncio.gather(
                    *(server.wait_closed() for server in servers),
                    return_exceptions=True,
                )
            set_bound_server_ips([])


def run_server():
    """Run the server in a separate thread / 在单独线程中运行服务器"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())


# ============================================================
# PyQt5 Modern Tray Menu / PyQt5 现代托盘菜单
# ============================================================

class MenuItemWidget(QWidget):
    """单个菜单项 - Windows 11 Fluent Design 风格"""

    clicked = pyqtSignal()

    def __init__(self, icon_text, text, has_toggle=False, is_checked=False, parent=None):
        super().__init__(parent)
        self.has_toggle = has_toggle
        self.is_checked = is_checked
        self._hovered = False
        self._pressed = False
        self.setFixedHeight(36)  # Windows 11 标准高度
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

        self.setup_ui(icon_text, text, has_toggle, is_checked)

    def setup_ui(self, icon_text, text, has_toggle, is_checked):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)  # 更宽的水平内边距
        layout.setSpacing(10)

        # 图标 - 使用白色
        self.icon_label = QLabel(icon_text)
        self.icon_label.setFixedWidth(20)
        self.icon_label.setStyleSheet("font-size: 14px; background: transparent; color: #FFFFFF;")
        self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 文字 - 使用 Segoe UI 字体（Windows 11 默认字体）
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: %s;
                font-size: 13px;
                font-weight: 400;
                background: transparent;
            }
        """ % NATIVE_FONT_FAMILY)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        # 开关项 - 显示简洁的状态
        if has_toggle:
            self.status_label = QLabel()
            self.status_label.setFixedWidth(24)
            self.status_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.update_toggle_status(is_checked)
            layout.addWidget(self.status_label)

    def paintEvent(self, event):
        """自定义绘制背景 - Windows 11 风格"""
        from PyQt5.QtGui import QPainter, QColor
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制圆角矩形背景
        rect = self.rect().adjusted(4, 2, -4, -2)  # 内缩，留出边距

        if self._pressed:
            # 按下状态 - 更亮的背景
            painter.setBrush(QColor(255, 255, 255, 25))  # 白色 10% 透明度
        elif self._hovered:
            # 悬停状态
            painter.setBrush(QColor(255, 255, 255, 15))  # 白色 6% 透明度
        else:
            painter.setBrush(Qt.transparent)

        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 4, 4)  # 4px 圆角

    def enterEvent(self, event):
        """鼠标进入 - 显示高亮"""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开 - 恢复正常"""
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def update_toggle_status(self, checked):
        """更新开关状态 - 使用现代化的开关指示器"""
        self.is_checked = checked
        if checked:
            self.status_label.setText("✓")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #60CDFF;
                    font-family: %s;
                    font-size: 14px;
                    font-weight: bold;
                    background: transparent;
                }
            """ % NATIVE_FONT_FAMILY)
        else:
            self.status_label.setText("")
            self.status_label.setStyleSheet("background: transparent;")

    def mousePressEvent(self, event):
        """鼠标按下 - 显示按压反馈"""
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放 - 恢复状态并触发点击"""
        self._pressed = False
        self.update()
        if self.rect().contains(event.pos()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class ModernMenuWidget(QWidget):
    """Windows 11 Fluent Design 风格的自定义菜单窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 动画相关
        self.animation_step = 0
        self.animation_max_steps = 10  # 约 160ms - 更快更流畅
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self._animation_group = None

        self.setup_ui()

    def setup_ui(self):
        """设置 UI - Windows 11 Fluent Design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # 阴影边距
        layout.setSpacing(0)

        # 主容器 - 使用深色半透明背景
        self.container = QWidget()
        self.container.setObjectName("menuContainer")
        self.container.setStyleSheet("""
            #menuContainer {
                background-color: rgba(32, 32, 32, 245);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(4, 6, 4, 6)  # 内边距
        container_layout.setSpacing(4)  # 项间距（4px 网格）

        # 显示 QR 码（最顶部）
        self.qr_btn = MenuItemWidget("📱", "显示 QR 码")
        self.qr_btn.clicked.connect(self.show_qr_dialog)
        container_layout.addWidget(self.qr_btn)

        # 同步输入
        self.sync_btn = MenuItemWidget("📡", "同步输入", has_toggle=True, is_checked=True)
        self.sync_btn.clicked.connect(self.toggle_sync)
        container_layout.addWidget(self.sync_btn)

        self.paste_mode_btn = MenuItemWidget("⌨", get_paste_mode_label())
        self.paste_mode_btn.clicked.connect(self.cycle_paste_mode)
        container_layout.addWidget(self.paste_mode_btn)

        # 开机自启
        self.startup_btn = MenuItemWidget("🚀", "开机自启", has_toggle=True, is_checked=False)
        self.startup_btn.clicked.connect(self.toggle_startup)
        container_layout.addWidget(self.startup_btn)

        # 打开日志
        log_btn = MenuItemWidget("📋", "打开日志")
        log_btn.clicked.connect(self.open_log)
        container_layout.addWidget(log_btn)

        # 退出应用
        quit_btn = MenuItemWidget("🚪", "退出应用")
        quit_btn.clicked.connect(self.quit_app)
        container_layout.addWidget(quit_btn)

        layout.addWidget(self.container)

        # 设置阴影
        self.set_shadow_effect()

        # 更新初始状态
        QTimer.singleShot(0, self.update_state)

    def set_shadow_effect(self):
        """设置阴影效果 - Windows 11 风格的柔和阴影"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

    def show_at_position(self, tray_pos):
        """在指定位置显示菜单，视觉左下角对齐鼠标点击位置"""
        self.adjustSize()
        # adjustSize() 对顶层 Popup 窗口给出的宽度偏大（实测比 sizeHint 多约 36px），
        # 导致菜单右边留白、宽度与文字不匹配。强制收紧到内容 sizeHint，使宽度随最长文字自适应。
        self.setFixedWidth(self.sizeHint().width())
        menu_width = self.width()
        menu_height = self.height()
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry() if screen else None

        shadow = self.layout().contentsMargins()
        x = tray_pos.x() - shadow.left()
        if get_platform() == "windows":
            target_y = tray_pos.y() - menu_height + shadow.bottom()
            animation_start_y = target_y + 16
        else:
            target_y = tray_pos.y() - shadow.top()
            animation_start_y = target_y - 16

        if available_geometry:
            screen_geometry = screen.geometry() if screen else available_geometry
            min_x = screen_geometry.left() + 8
            max_x = screen_geometry.right() - menu_width - 8
            x = max(min_x, min(x, max_x))
            if get_platform() == "windows":
                min_y = screen_geometry.top() + 8
                max_y = screen_geometry.bottom() - menu_height - 8
            else:
                min_y = available_geometry.top() + 8
                max_y = available_geometry.bottom() - menu_height - 8
            target_y = max(min_y, min(target_y, max_y))
            animation_start_y = max(min_y, min(animation_start_y, max_y))

        self.target_y = target_y
        self.animation_start_y = animation_start_y
        self.move(x, target_y)

        self.animation_step = 0
        self.move(x, animation_start_y)
        self.setWindowOpacity(0.0)
        self.show()
        self._start_open_animation(x, animation_start_y, target_y)

    def _stop_animation_group(self):
        if self._animation_group is not None:
            self._animation_group.stop()
            self._animation_group.deleteLater()
            self._animation_group = None

    def _start_open_animation(self, x, animation_start_y, target_y):
        """使用 Qt 原生属性动画，避免 Python QTimer 每帧驱动窗口移动。"""
        self.animation_timer.stop()
        self._stop_animation_group()

        pos_anim = QPropertyAnimation(self, b"pos", self)
        pos_anim.setDuration(160)
        pos_anim.setStartValue(QPoint(x, animation_start_y))
        pos_anim.setEndValue(QPoint(x, target_y))
        pos_anim.setEasingCurve(QEasingCurve.OutQuad)

        opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        opacity_anim.setDuration(120)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.OutQuad)

        group = QParallelAnimationGroup(self)
        group.addAnimation(pos_anim)
        group.addAnimation(opacity_anim)
        group.finished.connect(lambda: self._finish_open_animation(target_y))
        self._animation_group = group
        group.start()

    def _finish_open_animation(self, target_y):
        self.move(self.pos().x(), target_y)
        self.setWindowOpacity(1.0)
        self._stop_animation_group()

    def update_animation(self):
        """更新滑入动画"""
        self.animation_step += 1

        if self.animation_step >= self.animation_max_steps:
            # 动画结束
            self.animation_timer.stop()
            self.move(self.pos().x(), self.target_y)
            self.setWindowOpacity(1.0)
        else:
            # 缓动
            progress = self.animation_step / self.animation_max_steps
            eased = 1 - pow(1 - progress, 2)  # easeOutQuad

            current_y = self.animation_start_y + (self.target_y - self.animation_start_y) * eased
            self.move(self.pos().x(), int(current_y))

            # 淡入
            self.setWindowOpacity(min(1.0, eased * 1.5))

    def update_state(self):
        """更新菜单状态"""
        self.sync_btn.update_toggle_status(state.sync_enabled)
        self.startup_btn.update_toggle_status(is_startup_enabled())
        self.paste_mode_btn.text_label.setText(get_paste_mode_label())

    def toggle_sync(self):
        """切换同步状态"""
        new_state = not self.sync_btn.is_checked
        state.sync_enabled = new_state
        self.sync_btn.update_toggle_status(new_state)
        # 更新托盘图标
        if state.tray_icon:
            update_tray_icon_pyqt(state.tray_icon)
        self.close_with_animation()
        schedule_sync_state_broadcast()

    def cycle_paste_mode(self):
        modes = (
            PasteMode.AUTO,
            PasteMode.NORMAL,
            PasteMode.TERMINAL,
            PasteMode.COMPAT,
        )
        current_index = modes.index(get_paste_mode())
        next_mode = modes[(current_index + 1) % len(modes)]
        set_paste_mode(next_mode)
        self.paste_mode_btn.text_label.setText(get_paste_mode_label(next_mode))
        self.close_with_animation()

    def toggle_startup(self):
        """切换开机自启"""
        new_state = not self.startup_btn.is_checked
        set_startup_enabled(new_state)
        self.startup_btn.update_toggle_status(new_state)
        self.close_with_animation()

    def open_log(self):
        """打开日志文件"""
        self.close_with_animation()
        if state.log_file and state.log_file.exists():
            open_file_in_text_editor(state.log_file)
        else:
            log_dir = get_log_dir()
            log_dir.mkdir(parents=True, exist_ok=True)
            open_file_in_default_app(log_dir)

    def show_qr_dialog(self):
        """显示 QR 码弹窗"""
        anchor = QCursor.pos()
        self.close_with_animation()
        if not hasattr(state, 'qr_dialog') or state.qr_dialog is None:
            state.qr_dialog = QRCodeDialog()
        state.qr_dialog.show_from(anchor)

    def quit_app(self):
        """退出应用"""
        state.running = False
        state.shutdown_event.set()
        QApplication.quit()

    def close_with_animation(self):
        """关闭动画"""
        self.animation_timer.stop()
        self._stop_animation_group()
        self.close()

    def keyPressEvent(self, event):
        """键盘事件 - Escape 关闭菜单"""
        if event.key() == Qt.Key_Escape:
            self.close_with_animation()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Popup 模式下，点击菜单外部的事件会发到这里。
        若点击落在托盘图标矩形内 → 关闭自身并在新位置立刻重开（修复"连续右键第二次不弹"）。
        """
        # Qt.Popup 行为：点击外部时坐标是相对于 Popup 窗口的，转全局坐标再判断
        global_pos = event.globalPos() if hasattr(event, 'globalPos') else self.mapToGlobal(event.pos())
        if event.button() == Qt.RightButton and state.tray_icon is not None:
            tray_rect = state.tray_icon.geometry()
            if tray_rect.isValid() and tray_rect.contains(global_pos):
                # 关掉自己，延迟一下在新位置重开
                self.close_with_animation()
                QTimer.singleShot(0, lambda: state.tray_icon.show_custom_menu())
                event.accept()
                return
        super().mousePressEvent(event)


class QRSuccessOverlay(QWidget):
    """QR 白底范围上的成功态遮罩与对勾动画。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._shade_progress = 0.0
        self._check_progress = 0.0
        self._animation_group = None
        self.hide()

    def get_shade_progress(self):
        return self._shade_progress

    def set_shade_progress(self, value):
        self._shade_progress = max(0.0, min(1.0, float(value)))
        self.update()

    shadeProgress = pyqtProperty(
        float,
        fget=get_shade_progress,
        fset=set_shade_progress,
    )

    def get_check_progress(self):
        return self._check_progress

    def set_check_progress(self, value):
        self._check_progress = float(value)
        self.update()

    checkProgress = pyqtProperty(
        float,
        fget=get_check_progress,
        fset=set_check_progress,
    )

    def reset(self):
        self._stop_animation()
        self._shade_progress = 0.0
        self._check_progress = 0.0
        self.hide()
        self.update()

    def play(self):
        self._stop_animation()
        self._shade_progress = 0.0
        self._check_progress = 0.0
        self.show()
        self.raise_()

        shade_anim = QPropertyAnimation(self, b"shadeProgress", self)
        shade_anim.setDuration(180)
        shade_anim.setStartValue(0.0)
        shade_anim.setEndValue(1.0)
        shade_anim.setEasingCurve(QEasingCurve.OutCubic)

        check_anim = QPropertyAnimation(self, b"checkProgress", self)
        check_anim.setDuration(520)
        check_anim.setStartValue(0.0)
        check_anim.setEndValue(1.0)
        check_anim.setEasingCurve(QEasingCurve.OutBack)

        group = QParallelAnimationGroup(self)
        group.addAnimation(shade_anim)
        group.addAnimation(check_anim)
        self._animation_group = group
        group.start()

    def _stop_animation(self):
        if self._animation_group is not None:
            self._animation_group.stop()
            self._animation_group.deleteLater()
            self._animation_group = None

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(-1, -1, 1, 1)
        shade_alpha = int(176 * self._shade_progress)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, shade_alpha))
        painter.drawRoundedRect(rect, 6, 6)

        raw_progress = self._check_progress
        progress = max(0.0, min(1.0, raw_progress))
        if progress <= 0:
            return

        center = QPointF(self.width() / 2, self.height() / 2)
        scale = 0.72 + 0.28 * progress + max(0.0, raw_progress - 1.0) * 0.34
        painter.save()
        painter.translate(center)
        painter.scale(scale, scale)

        ring_progress = min(1.0, progress / 0.82)
        ring_alpha = int(125 * (1.0 - ring_progress) * progress)
        if ring_alpha > 0:
            ring_pen = QPen(QColor(54, 222, 116, ring_alpha), 3)
            ring_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(ring_pen)
            painter.setBrush(Qt.NoBrush)
            ring_radius = 25 + 32 * ring_progress
            painter.drawEllipse(QPointF(0, 0), ring_radius, ring_radius)

        check_alpha = int(255 * min(1.0, progress * 1.4))
        check_pen = QPen(QColor(54, 222, 116, check_alpha), 10)
        check_pen.setCapStyle(Qt.RoundCap)
        check_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(check_pen)
        painter.setBrush(Qt.NoBrush)

        a = QPointF(-34, -2)
        b = QPointF(-11, 22)
        c = QPointF(36, -25)
        if progress < 0.46:
            t = progress / 0.46
            end = QPointF(a.x() + (b.x() - a.x()) * t, a.y() + (b.y() - a.y()) * t)
            painter.drawLine(a, end)
        else:
            painter.drawLine(a, b)
            t = (progress - 0.46) / 0.54
            end = QPointF(b.x() + (c.x() - b.x()) * t, b.y() + (c.y() - b.y()) * t)
            painter.drawLine(b, end)

        painter.restore()


class QRCodeDialog(QWidget):
    """QR 码弹窗 - 与托盘菜单同色同风格，直接在屏幕中心显示。"""

    DIALOG_WIDTH = 282
    DIALOG_HEIGHT = 308
    QR_SIZE = 230

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Tool
            | Qt.WindowStaysOnTopHint
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._ignore_focus_loss = False
        self._anim_end_rect = None

        # Keep QR payload aligned with runtime IP changes.
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_qr)

        self._cached_qr_payload = None
        self._cached_qr_pixmap = None
        self._scan_success_shown = False
        self._closing_after_success = False
        self._success_generation = 0

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # 阴影边距
        layout.setSpacing(0)

        self.container = QWidget()
        self.container.setObjectName("qrContainer")
        self.container.setStyleSheet("""
            QWidget#qrContainer {
                background-color: rgba(32, 32, 32, 245);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
        """)
        cl = QVBoxLayout(self.container)
        # 左右下三边 10px，上方 padding 6（header 18 + spacing 6 额外占用）
        cl.setContentsMargins(10, 6, 10, 10)
        cl.setSpacing(6)

        # 顶栏：标题 + 关闭按钮（高度 24，容纳 14px 字号）
        header = QWidget()
        header.setFixedHeight(24)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        title = QLabel("用 Voicing 手机端扫描")
        title_font = QFont(get_native_font_family())
        title_font.setPixelSize(14)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF; background: transparent;")
        # 水平 + 垂直 全部居中，避免 QLabel 默认上对齐造成文字偏上
        title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        header_layout.addSpacing(24)
        header_layout.addStretch(1)
        header_layout.addWidget(title, 0, Qt.AlignVCenter)
        header_layout.addStretch(1)

        self.close_btn = QLabel("✕")
        close_font = QFont(get_native_font_family())
        close_font.setPixelSize(15)
        close_font.setWeight(QFont.Black)
        self.close_btn.setFont(close_font)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setAlignment(Qt.AlignCenter)
        self.close_btn.setStyleSheet("""
            QLabel {
                color: #A0A0A0;
                background: transparent;
                border-radius: 12px;
            }
            QLabel:hover {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 25);
            }
        """)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        # 用事件过滤器处理点击（QLabel 没有 clicked 信号）
        self.close_btn.mousePressEvent = lambda e: self.close_with_animation()
        header_layout.addWidget(self.close_btn, 0, Qt.AlignVCenter)

        cl.addWidget(header)

        # QR 图像
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(self.QR_SIZE + 16, self.QR_SIZE + 16)
        self.qr_label.setStyleSheet(
            "background-color: #FFFFFF;"
            "border-radius: 6px;"
            "padding: 8px;"
        )
        self.success_overlay = QRSuccessOverlay(self.qr_label)
        self.success_overlay.setGeometry(self.qr_label.rect())
        cl.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        layout.addWidget(self.container)

        # 精确尺寸：窗口始终保持最终尺寸，避免 Wayland 上 resize/remap 闪烁。
        self.setFixedSize(self.DIALOG_WIDTH, self.DIALOG_HEIGHT)

    def _generate_qr_pixmap(self, payload: str) -> QPixmap:
        """生成 QR pixmap（黑底白点，反相成符合暗色 UI）"""
        import io
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        # 缩放到目标尺寸
        img = img.resize((self.QR_SIZE, self.QR_SIZE), Image.NEAREST)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pix = QPixmap()
        pix.loadFromData(buf.getvalue())
        return pix

    def _refresh_qr(self):
        """Refresh QR payload from the current interface snapshot."""
        self._populate_content()

    def _build_qr_payload(self):
        device_identity = get_or_create_device_identity()
        advertised_ips = get_qr_advertised_server_ips(refresh=True)
        primary_ip = advertised_ips[0] if advertised_ips else get_primary_server_ip(refresh=True)
        payload = build_qr_payload(
            device_id=device_identity.device_id,
            ip=primary_ip,
            port=state.ws_port,
            name=device_identity.name,
            os_name=device_identity.os,
            ips=advertised_ips,
        )
        return json.dumps(payload, separators=(",", ":"))

    def _populate_content(self):
        """填充 QR"""
        payload = self._build_qr_payload()
        if self._cached_qr_payload != payload or self._cached_qr_pixmap is None:
            self._cached_qr_payload = payload
            self._cached_qr_pixmap = self._generate_qr_pixmap(payload)
        pix = self._cached_qr_pixmap
        self.qr_label.setPixmap(pix)

    def show_from(self, anchor_global_pos):
        """在屏幕中心显示 QR 弹窗，不做跨窗口飞入动画。"""
        self._populate_content()
        self.success_overlay.reset()
        self._scan_success_shown = False
        self._closing_after_success = False
        self._success_generation += 1
        generation = self._success_generation

        end_rect = self._build_end_rect(anchor_global_pos)

        self._anim_end_rect = end_rect
        self._refresh_timer.stop()
        # 短暂忽略 focus-out，避免 Wayland show/activate 过程中的焦点事件把弹窗立即关闭。
        self._ignore_focus_loss = True
        self.setUpdatesEnabled(False)
        self.setGeometry(end_rect)
        self.setWindowOpacity(1.0)
        self.container.show()
        self.setUpdatesEnabled(True)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)
        self.repaint()
        QTimer.singleShot(120, lambda: self._finish_direct_open(generation))

    def _finish_direct_open(self, generation):
        if generation != self._success_generation or not self.isVisible():
            return
        self._ignore_focus_loss = False
        self._refresh_timer.start(5000)

    def _build_end_rect(self, anchor_global_pos):
        screen = None
        if hasattr(QApplication, "screenAt"):
            screen = QApplication.screenAt(anchor_global_pos)
        if screen is None:
            screen = QApplication.primaryScreen()

        screen_geo = screen.availableGeometry() if screen else None
        if screen_geo is None:
            cx = anchor_global_pos.x()
            cy = anchor_global_pos.y()
        else:
            cx = screen_geo.center().x()
            cy = screen_geo.center().y()

        return QRect(
            cx - self.DIALOG_WIDTH // 2,
            cy - self.DIALOG_HEIGHT // 2,
            self.DIALOG_WIDTH,
            self.DIALOG_HEIGHT,
        )

    def show_scan_success(self):
        if not self.isVisible():
            logging.info("QR 成功态跳过：QR 弹窗当前不可见")
            return
        if self._scan_success_shown:
            logging.info("QR 成功态跳过：已播放")
            return
        self._scan_success_shown = True
        self._closing_after_success = False
        self._success_generation += 1
        generation = self._success_generation
        self.success_overlay.setGeometry(self.qr_label.rect())
        self.success_overlay.play()
        QTimer.singleShot(1150, lambda: self._close_after_success(generation))

    def _close_after_success(self, generation):
        if (
            generation == self._success_generation
            and self._scan_success_shown
            and self.isVisible()
        ):
            self._closing_after_success = True
            self.close_with_animation()

    def _finish_close(self):
        self._refresh_timer.stop()
        self.setUpdatesEnabled(False)
        self._ignore_focus_loss = False
        self.container.show()
        if self._anim_end_rect is not None:
            self.setFixedSize(self.DIALOG_WIDTH, self.DIALOG_HEIGHT)
            self.setGeometry(self._anim_end_rect)
        self.setUpdatesEnabled(True)
        self.hide()
        self.success_overlay.reset()
        self._scan_success_shown = False
        self._closing_after_success = False

    def close_with_animation(self):
        if not self.isVisible():
            return
        self._refresh_timer.stop()
        self._finish_close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_with_animation()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """点击外部自动关闭"""
        # 延迟一帧检查，避免动画刚弹出就被自己 raise 触发关闭
        QTimer.singleShot(50, self._maybe_close_on_focus_loss)
        super().focusOutEvent(event)

    def _maybe_close_on_focus_loss(self):
        if self._ignore_focus_loss:
            return
        if self._scan_success_shown or self._closing_after_success:
            logging.info("QR 成功态期间忽略 focus-out 关闭")
            return
        if not self.isActiveWindow() and self.isVisible():
            self.close_with_animation()

    def mousePressEvent(self, event):
        """点弹窗内空白处不关闭，但点关闭按钮等已在子控件处理"""
        super().mousePressEvent(event)


class ModernTrayIcon(QSystemTrayIcon):
    """现代托盘图标"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 预先缓存图标
        self._icon_cache = {}
        # 记录当前生效的图标键，避免状态未变时重复 setIcon
        # （Linux SNI/AppIndicator 宿主每次 setIcon 都可能重建图标导致闪烁）
        self._current_icon_key = None
        self._init_icon_cache()
        # 预先创建菜单（避免首次打开慢）
        self.menu_widget = ModernMenuWidget()
        # 自定义菜单仅在非 Linux 平台使用；Linux 走原生菜单，无需预热其窗口。
        if get_platform() != "linux":
            # 预热渲染：强制 Qt 提前编译 stylesheet 和计算布局
            self.menu_widget.move(-10000, -10000)
            self.menu_widget.show()
            QTimer.singleShot(50, self.menu_widget.hide)
        # 预热 QR 弹窗与 QR pixmap，避免首次点击时同步生成图片和计算布局
        if state.qr_dialog is None:
            state.qr_dialog = QRCodeDialog()
            state.qr_dialog._populate_content()
            if get_platform() == "linux":
                # Wayland 禁止客户端自由定位顶层窗口，show() + move(-10000,-10000)
                # 会让窗口短暂可见地闪在屏幕左上角。这里只做样式与布局预热，不 show。
                state.qr_dialog.ensurePolished()
                if state.qr_dialog.layout() is not None:
                    state.qr_dialog.layout().activate()
            else:
                state.qr_dialog.move(-10000, -10000)
                state.qr_dialog.show()
                QTimer.singleShot(50, state.qr_dialog.hide)
        self.setup_icon()
        self.setup_menu()
        # 设置悬停提示
        self.setToolTip("Voicing")

    def _init_icon_cache(self):
        """预先生成并缓存所有状态的图标"""
        import io
        size = 256

        # 生成基础圆形图标
        bg_color = (26, 26, 46, 255)  # #1A1A2E
        base = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(base)
        draw.ellipse([0, 0, size-1, size-1], fill=bg_color)
        original = load_base_icon(size)
        base = Image.alpha_composite(base, original)
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
        base.putalpha(mask)

        # 缓存：正常状态
        self._icon_cache['normal'] = self._pil_to_qicon(base)

        # 缓存：暗淡状态（闪烁用）
        dim = base.copy()
        alpha = dim.split()[3]
        alpha = alpha.point(lambda x: int(x * 0.4))
        dim.putalpha(alpha)
        self._icon_cache['dim'] = self._pil_to_qicon(dim)

        # 缓存：灰度状态（暂停用）
        r, g, b, a = base.split()
        gray = base.convert('L')
        paused = Image.merge('RGBA', (gray, gray, gray, a))
        self._icon_cache['paused'] = self._pil_to_qicon(paused)

    def _pil_to_qicon(self, pil_image):
        """PIL Image 转 QIcon"""
        import io
        byte_data = io.BytesIO()
        pil_image.save(byte_data, format='PNG')
        byte_data.seek(0)
        qpix = QPixmap()
        qpix.loadFromData(byte_data.getvalue())
        return QIcon(qpix)

    def setup_icon(self):
        """设置图标 - 使用新的麦克风+声波图标"""
        import io
        
        # 加载基础图标
        icon = load_base_icon(32)
        
        # 转换为 QPixmap
        byte_data = io.BytesIO()
        icon.save(byte_data, format='PNG')
        byte_data.seek(0)
        qpix = QPixmap()
        qpix.loadFromData(byte_data.getvalue())

        self.setIcon(QIcon(qpix))

    def setup_menu(self):
        """设置菜单"""
        # 不使用 QMenu，而是自定义菜单
        self.activated.connect(self.on_tray_activated)
        if get_platform() == "linux":
            self._setup_native_context_menu()

    def _setup_native_context_menu(self):
        """Linux tray hosts may only show menus provided through setContextMenu."""
        self.native_menu = QMenu()
        # 默认 QMenu 给每项预留很大的水平 padding（实测 168px 宽 vs 文本 84px），
        # 右侧留白过多。收紧 item 内边距（左 20 留勾选框位、右 12 收窄），
        # 不改颜色/边框，保留 GTK 原生外观，只让宽度更贴合文字。
        self.native_menu.setStyleSheet(
            "QMenu::item { padding: 6px 12px 6px 20px; }"
        )

        qr_action = self.native_menu.addAction("显示 QR 码")
        qr_action.triggered.connect(self.menu_widget.show_qr_dialog)

        self.native_sync_action = self.native_menu.addAction("同步输入")
        self.native_sync_action.setCheckable(True)
        self.native_sync_action.triggered.connect(self.menu_widget.toggle_sync)

        self.native_paste_mode_action = self.native_menu.addAction(get_paste_mode_label())
        self.native_paste_mode_action.triggered.connect(self.menu_widget.cycle_paste_mode)

        self.native_startup_action = self.native_menu.addAction("开机自启")
        self.native_startup_action.setCheckable(True)
        self.native_startup_action.triggered.connect(self.menu_widget.toggle_startup)

        log_action = self.native_menu.addAction("打开日志")
        log_action.triggered.connect(self.menu_widget.open_log)

        quit_action = self.native_menu.addAction("退出应用")
        quit_action.triggered.connect(self.menu_widget.quit_app)

        self.native_menu.aboutToShow.connect(self._sync_native_context_menu_state)
        self._sync_native_context_menu_state()
        self.setContextMenu(self.native_menu)

    def _sync_native_context_menu_state(self):
        self.menu_widget.update_state()
        if hasattr(self, "native_sync_action"):
            self.native_sync_action.setChecked(state.sync_enabled)
        if hasattr(self, "native_paste_mode_action"):
            self.native_paste_mode_action.setText(get_paste_mode_label())
        if hasattr(self, "native_startup_action"):
            self.native_startup_action.setChecked(is_startup_enabled())

    @staticmethod
    def _uses_native_menu():
        """Linux 改用系统原生 QMenu，避免自定义 Popup 在 GNOME/Wayland 下的渲染与定位问题。"""
        return get_platform() == "linux"

    @staticmethod
    def _should_show_custom_menu_for_activation_reason(reason):
        """Windows/macOS：左键 / 双击 / 右键都弹出自定义 Fluent 菜单。"""
        return reason in (
            QSystemTrayIcon.Trigger,
            QSystemTrayIcon.DoubleClick,
            QSystemTrayIcon.Context,
        )

    @staticmethod
    def _should_popup_native_menu_for_activation_reason(reason):
        """Linux：左键 / 双击时手动弹出原生菜单。

        右键（Context）交给 setContextMenu 让宿主处理；若这里也 popup 会与
        宿主的原生右键菜单叠加，造成同时弹两个菜单。
        """
        return reason in (
            QSystemTrayIcon.Trigger,
            QSystemTrayIcon.DoubleClick,
        )

    def on_tray_activated(self, reason):
        """托盘图标激活事件。

        Linux 上由 setContextMenu + 左键 popup 共同提供原生菜单，右键完全交给
        宿主以避免双菜单叠加；其他平台沿用自定义菜单。
        """
        if self._uses_native_menu():
            if self._should_popup_native_menu_for_activation_reason(reason):
                self._popup_native_menu()
        elif self._should_show_custom_menu_for_activation_reason(reason):
            self.show_custom_menu()

    def _popup_native_menu(self):
        """弹出 Linux 原生托盘菜单，并同步开关状态。"""
        self._sync_native_context_menu_state()
        self.native_menu.popup(QCursor.pos())

    def show_custom_menu(self):
        """显示自定义菜单"""
        # 更新状态
        self.menu_widget.update_state()

        # 获取托盘图标位置并显示菜单（带动画）
        pos = QCursor.pos()
        self.menu_widget.show_at_position(pos)

    def update_icon(self, status, dim=False):
        """更新图标状态 - 使用缓存的图标，仅在目标图标真正变化时才 setIcon。

        Linux SNI/AppIndicator 宿主每次 setIcon 都可能重建图标导致托盘闪烁，
        因此记录当前生效的图标键，状态未变时跳过 setIcon。

        Args:
            status: 未使用，保留兼容
            dim: 是否为暗淡状态（用于闪烁效果）
        """
        if not state.sync_enabled:
            # 暂停状态
            icon_key = 'paused'
        elif len(state.connected_clients) == 0 and dim:
            # 等待连接 + 暗淡状态
            icon_key = 'dim'
        else:
            # 正常状态（已连接或等待连接的亮状态）
            icon_key = 'normal'
        if icon_key != self._current_icon_key:
            self._current_icon_key = icon_key
            self.setIcon(self._icon_cache[icon_key])


# ============================================================
# System Tray / 系统托盘 (保留兼容函数)
# ============================================================

def get_base_icon_path() -> str:
    """获取基础图标路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets', 'icon_1024.png')


def load_base_icon(size: int = 64) -> Image.Image:
    """加载并缩放基础图标"""
    icon_path = get_base_icon_path()
    try:
        icon = Image.open(icon_path)
        icon = icon.convert('RGBA')
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        return icon
    except Exception as e:
        logging.warning(f"无法加载图标 {icon_path}: {e}，使用备用图标")
        # 备用图标：简单的圆形
        fallback = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(fallback)
        draw.ellipse([4, 4, size-4, size-4], fill='#2196F3')
        return fallback


def run_tray():
    """Run the system tray application with PyQt5 / 使用PyQt5运行系统托盘应用"""
    # 创建 QApplication（如果不存在）
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    app.setQuitOnLastWindowClosed(False)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        raise RuntimeError("当前桌面环境不提供系统托盘，Voicing 无法继续运行。")

    if state.ui_signals is None:
        state.ui_signals = UiSignals()
    state.ui_signals.qr_scan_succeeded.connect(
        show_qr_scan_success,
        type=Qt.QueuedConnection,
    )

    # 创建现代托盘图标
    tray_icon = ModernTrayIcon()
    tray_icon.show()

    # 更新初始状态
    update_tray_icon_pyqt(tray_icon)

    # 保存到状态
    state.tray_icon = tray_icon

    # 定时更新图标状态
    update_timer = QTimer()
    update_timer.timeout.connect(lambda: update_tray_icon_pyqt(tray_icon))
    update_timer.start(200)  # 每200ms更新（闪烁）

    # 运行应用
    app.exec()


def update_tray_icon_pyqt(tray_icon):
    """更新 PyQt5 托盘图标状态"""
    # 判断是否需要闪烁（等待连接状态）
    if state.sync_enabled and len(state.connected_clients) == 0:
        # 等待连接 - 切换闪烁状态
        state.blink_state = not state.blink_state
        tray_icon.update_icon(None, dim=state.blink_state)
    else:
        # 其他状态 - 正常更新
        tray_icon.update_icon(None, dim=False)


# ============================================================
# Main Entry / 主入口
# ============================================================
def main():
    """Main entry point / 主入口"""
    # 初始化日志系统
    setup_logging()
    try:
        ensure_runtime_supported()
    except RuntimeError as exc:
        logging.error(str(exc))
        show_fatal_message("Voicing 无法启动", str(exc))
        return

    # Read-only warm-up: samples AT-SPI in the background, but never creates
    # a RemoteDesktop portal session, sends keys, or caches a paste decision.
    start_wayland_focus_prewarm()

    # Detect QR-advertisable interfaces at startup; the server thread refreshes
    # this snapshot at runtime for network changes.
    refresh_server_interfaces(log_changes=True)
    logging.info(f"当前首选服务地址: {get_primary_server_ip()}")

    # Start WebSocket server in background thread
    ws_thread = threading.Thread(target=run_server, daemon=True)
    ws_thread.start()

    try:
        run_tray()
    except RuntimeError as exc:
        logging.error(str(exc))
        show_fatal_message("Voicing 无法启动", str(exc))


def show_fatal_message(title: str, message: str) -> None:
    owns_app = QApplication.instance() is None
    app = QApplication.instance() if not owns_app else QApplication([])
    QMessageBox.critical(None, title, message)
    if owns_app:
        app.quit()


if __name__ == "__main__":
    # Development mode: run with --dev flag to skip single instance check
    # 开发模式：使用 --dev 参数跳过单实例检查，方便快速迭代
    DEV_MODE = "--dev" in sys.argv

    if not DEV_MODE:
        # Check single instance first (only in production)
        if not check_single_instance():
            show_already_running_message()
            sys.exit(0)
    else:
        print("=== Running in DEV MODE (single instance check disabled) ===")

    main()

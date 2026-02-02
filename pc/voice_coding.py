"""
Voice Coding - PC Application
语音编程 - 电脑端应用

A system tray application that receives text from phone and types it at cursor position.
系统托盘应用，接收手机发送的文本并在光标处输入。
"""

import asyncio
import socket
import sys
import os
import threading
import winreg
import json
import ctypes
import ssl
import shutil
from typing import Optional
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import mimetypes

# Third-party imports
import websockets
from websockets.server import serve
import pyautogui
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# ============================================================
# Single Instance Check / 单实例检查
# ============================================================
MUTEX_NAME = "VoiceCoding_SingleInstance_Mutex"

def check_single_instance() -> bool:
    """
    Check if another instance is already running / 检查是否已有实例在运行
    Returns True if this is the only instance, False if another is running.
    """
    # Try to create a named mutex
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = kernel32.GetLastError()
    
    # ERROR_ALREADY_EXISTS = 183
    if last_error == 183:
        # Another instance is already running
        kernel32.CloseHandle(mutex)
        return False
    
    # Store mutex handle globally to keep it alive
    global _mutex_handle
    _mutex_handle = mutex
    return True


def show_already_running_message():
    """Show message that app is already running / 显示程序已运行的提示"""
    ctypes.windll.user32.MessageBoxW(
        0,
        "Voice Coding 已经在运行中！\n\n请查看系统托盘图标。\n\nVoice Coding is already running!\nPlease check the system tray.",
        "Voice Coding",
        0x40  # MB_ICONINFORMATION
    )


# ============================================================
# Configuration / 配置
# ============================================================
APP_NAME = "VoiceCoding"
APP_VERSION = "1.0.0"
WS_PORT = 9527      # WebSocket port
HTTP_PORT = 9528    # HTTP port for web UI
HTTPS_PORT = 9529   # HTTPS port for web UI (PWA install requires HTTPS)
STARTUP_REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

# Disable pyautogui failsafe (moving to corner won't stop it)
pyautogui.FAILSAFE = False
# Small pause between keystrokes for stability
pyautogui.PAUSE = 0.01


# ============================================================
# Global State / 全局状态
# ============================================================
class AppState:
    """Application state management / 应用状态管理"""
    def __init__(self):
        self.sync_enabled = True
        self.running = True
        self.server = None
        self.tray_icon = None
        self.ws_port = WS_PORT
        self.http_port = HTTP_PORT
        self.https_port = HTTPS_PORT
        self.https_enabled = True  # Enable HTTPS by default for PWA install support
        self.connected_clients = set()
        self.blink_state = False  # For icon blinking / 图标闪烁状态
        self.blink_timer: Optional[threading.Timer] = None
        self.https_server = None  # HTTPS server instance for shutdown
        
state = AppState()


# ============================================================
# Network Configuration / 网络配置
# ============================================================
# Windows Mobile Hotspot default IP / Windows 移动热点默认 IP
DEFAULT_HOTSPOT_IP = "192.168.137.1"


def get_hotspot_ip() -> str:
    """
    Get the actual hotspot IP address / 获取热点的实际 IP 地址
    
    Windows Mobile Hotspot typically uses 192.168.137.1, but this function
    will try to detect the actual IP by looking for the hotspot adapter.
    """
    try:
        import socket
        
        # Method 1: Try to find hotspot adapter by checking common hotspot IP ranges
        for adapter_ip in get_all_local_ips():
            # Windows Mobile Hotspot typically uses 192.168.137.x
            if adapter_ip.startswith("192.168.137."):
                return adapter_ip
        
        # Method 2: Fallback to default
        return DEFAULT_HOTSPOT_IP
        
    except Exception as e:
        print(f"Error detecting hotspot IP: {e}")
        return DEFAULT_HOTSPOT_IP


def get_all_local_ips() -> list:
    """Get all local IP addresses / 获取所有本地 IP 地址"""
    ips = []
    try:
        import socket
        hostname = socket.gethostname()
        # Get all addresses associated with hostname
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except:
        pass
    
    # Also try to get IPs from network interfaces directly
    try:
        import subprocess
        result = subprocess.run(
            ['powershell', '-Command', 
             "Get-NetIPAddress -AddressFamily IPv4 | Select-Object -ExpandProperty IPAddress"],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in result.stdout.strip().split('\n'):
            ip = line.strip()
            if ip and not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except:
        pass
    
    return ips


# Will be set at runtime / 运行时设置
HOTSPOT_IP = DEFAULT_HOTSPOT_IP


# ============================================================
# Startup Management / 开机启动管理
# ============================================================
def get_exe_path() -> str:
    """Get the path of the running executable / 获取当前运行程序路径"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.abspath(__file__)


def is_startup_enabled() -> bool:
    """Check if app is set to start with Windows / 检查是否已设置开机启动"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REGISTRY_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_startup_enabled(enabled: bool) -> bool:
    """Enable or disable startup with Windows / 启用或禁用开机启动"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REGISTRY_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                exe_path = get_exe_path()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"Failed to modify startup setting: {e}")
        return False


# ============================================================
# Text Input / 文本输入
# ============================================================
def type_text(text: str):
    """
    Type text at current cursor position.
    在当前光标位置输入文本。
    
    Uses pyautogui.write for ASCII and pyperclip+paste for Unicode.
    """
    if not text or not state.sync_enabled:
        return
    
    try:
        # For Unicode support, use clipboard paste method
        import pyperclip
        
        # Save current clipboard
        try:
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""
        
        # Copy new text and paste
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        
        # Small delay then restore clipboard
        import time
        time.sleep(0.1)
        try:
            pyperclip.copy(old_clipboard)
        except:
            pass
            
    except Exception as e:
        print(f"Error typing text: {e}")


# ============================================================
# WebSocket Server / WebSocket 服务器
# ============================================================
async def handle_client(websocket):
    """Handle incoming WebSocket connections / 处理传入的WebSocket连接"""
    client_addr = websocket.remote_address
    state.connected_clients.add(websocket)
    print(f"Client connected: {client_addr}")
    
    # Update tray icon when client connects
    if state.tray_icon:
        try:
            update_tray_icon(state.tray_icon)
        except Exception as e:
            print(f"Error updating tray icon: {e}")
    
    try:
        # Get computer name for identification
        computer_name = socket.gethostname()
        
        # Send welcome message with current sync state and computer name
        await websocket.send(json.dumps({
            "type": "connected",
            "message": "Connected to Voice Coding server",
            "sync_enabled": state.sync_enabled,
            "computer_name": computer_name
        }))
        
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type", "")
                
                if msg_type == "text":
                    # Check if sync is enabled
                    if not state.sync_enabled:
                        await websocket.send(json.dumps({
                            "type": "sync_disabled",
                            "message": "Sync is disabled on PC"
                        }))
                        continue
                    
                    text = data.get("content", "")
                    if text:
                        # Type the received text
                        type_text(text)
                        # Send acknowledgment
                        await websocket.send(json.dumps({
                            "type": "ack",
                            "message": "Text received and typed"
                        }))
                        
                elif msg_type == "ping":
                    # Respond with pong and current sync state
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "sync_enabled": state.sync_enabled
                    }))
                    
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                if message.strip() and state.sync_enabled:
                    type_text(message)
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        state.connected_clients.discard(websocket)
        print(f"Client disconnected: {client_addr}")
        
        # Update tray icon when client disconnects
        if state.tray_icon:
            update_tray_icon(state.tray_icon)


async def broadcast_sync_state():
    """Broadcast sync state to all connected clients / 广播同步状态给所有客户端"""
    if not state.connected_clients:
        return
    
    message = json.dumps({
        "type": "sync_state",
        "sync_enabled": state.sync_enabled
    })
    
    for client in state.connected_clients.copy():
        try:
            await client.send(message)
        except:
            pass


async def start_server():
    """Start the WebSocket server / 启动WebSocket服务器"""
    try:
        async with serve(handle_client, "0.0.0.0", state.ws_port):
            print(f"WebSocket server started at ws://{HOTSPOT_IP}:{state.ws_port}")
            # Keep server running
            while state.running:
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Server error: {e}")


def run_server():
    """Run the server in a separate thread / 在单独线程中运行服务器"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())


# ============================================================
# HTTPS Certificate Management / HTTPS 证书管理
# ============================================================
def get_cert_dir() -> Path:
    """Get the certificate directory / 获取证书目录路径"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe - use AppData/Local
        app_data = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local'))
        cert_dir = app_data / 'VoiceCoding'
    else:
        # Running as script - use script directory
        cert_dir = Path(__file__).parent / 'certs'

    cert_dir.mkdir(parents=True, exist_ok=True)
    return cert_dir


def generate_self_signed_cert():
    """
    Generate a self-signed certificate for HTTPS.
    生成自签名证书用于 HTTPS。
    """
    cert_dir = get_cert_dir()
    cert_file = cert_dir / 'server.pem'
    key_file = cert_dir / 'server.key'

    # If certificate already exists and is valid, return
    if cert_file.exists() and key_file.exists():
        return str(cert_file), str(key_file)

    print("Generating self-signed certificate...")

    try:
        # Try using cryptography module
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime

        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VoiceCoding"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(socket.inet_aton("127.0.0.1")),
                x509.IPAddress(socket.inet_aton("192.168.137.1")),
                x509.IPAddress(socket.inet_aton("192.168.0.1")),
                x509.IPAddress(socket.inet_aton("192.168.1.1")),
                x509.IPAddress(socket.inet_aton("10.0.0.1")),
            ]),
            critical=False,
        ).sign(key, hashes.SHA256())

        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write key
        with open(key_file, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        print(f"Certificate generated: {cert_file}")
        return str(cert_file), str(key_file)

    except ImportError:
        # Fallback: use OpenSSL command if available
        print("cryptography module not found, trying OpenSSL...")
        try:
            import subprocess

            # Generate a combined PEM file (cert + key)
            combined_cert = cert_dir / 'server_combined.pem'

            # OpenSSL command to generate self-signed certificate
            cmd = [
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
                '-keyout', str(key_file), '-out', str(cert_file),
                '-days', '3650', '-nodes',
                '-subj', '/C=CN/ST=Beijing/L=Beijing/O=VoiceCoding/CN=localhost'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                # Combine cert and key for Python ssl module
                with open(combined_cert, 'wb') as combined:
                    with open(cert_file, 'rb') as f:
                        combined.write(f.read())
                    with open(key_file, 'rb') as f:
                        combined.write(f.read())

                print(f"Certificate generated using OpenSSL: {combined_cert}")
                return str(combined_cert), None
            else:
                print(f"OpenSSL failed: {result.stderr}")
                return None, None

        except FileNotFoundError:
            print("OpenSSL not found. Please install cryptography package:")
            print("  pip install cryptography")
            return None, None


def run_https_server():
    """Run HTTPS server for web UI / 运行HTTPS服务器提供网页界面"""
    cert_file, key_file = generate_self_signed_cert()

    if cert_file is None:
        print("Failed to generate certificate. HTTPS server not started.")
        print("PWA installation requires HTTPS. Install: pip install cryptography")
        return

    try:
        httpd = HTTPServer(('0.0.0.0', state.https_port), WebHandler)

        # Create SSL context
        if key_file:
            # Separate cert and key files
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        else:
            # Combined PEM file
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_file)

        # Wrap the socket with SSL
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        state.https_server = httpd

        print(f"HTTPS server started at https://{HOTSPOT_IP}:{state.https_port}")
        print(f"  Certificate: {cert_file}")
        print(f"  Note: You'll need to accept the security warning in your browser")

        while state.running:
            httpd.handle_request()

    except Exception as e:
        print(f"HTTPS server error: {e}")


# ============================================================
# HTTP Server for Web UI / HTTP服务器提供网页界面
# ============================================================
def get_web_dir() -> Path:
    """Get the web directory path / 获取网页目录路径"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys._MEIPASS) / 'web'
    else:
        # Running as script
        return Path(__file__).parent / 'web'


class WebHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving web files / 自定义HTTP处理器"""
    
    def __init__(self, *args, **kwargs):
        self.directory = str(get_web_dir())
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def log_message(self, format, *args):
        # Suppress HTTP logs
        pass
    
    def end_headers(self):
        # Add CORS headers for WebSocket
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def run_http_server():
    """Run HTTP server for web UI / 运行HTTP服务器提供网页界面"""
    try:
        server = HTTPServer(('0.0.0.0', state.http_port), WebHandler)
        print(f"HTTP server started at http://{HOTSPOT_IP}:{state.http_port}")
        while state.running:
            server.handle_request()
    except Exception as e:
        print(f"HTTP server error: {e}")


# ============================================================
# System Tray / 系统托盘
# ============================================================
def create_icon_connected() -> Image.Image:
    """Create connected state tray icon (green) / 创建已连接状态托盘图标（绿色）"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Green background circle - connected
    draw.ellipse([4, 4, size-4, size-4], fill='#4CAF50')
    
    # White "V" shape for Voice
    draw.polygon([
        (16, 20), (32, 44), (48, 20),
        (42, 20), (32, 36), (22, 20)
    ], fill='white')
    
    return image


def create_icon_waiting() -> Image.Image:
    """Create waiting state tray icon (blue) / 创建等待连接状态托盘图标（蓝色）"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Blue background circle - waiting for connection
    draw.ellipse([4, 4, size-4, size-4], fill='#2196F3')
    
    # White "V" shape for Voice
    draw.polygon([
        (16, 20), (32, 44), (48, 20),
        (42, 20), (32, 36), (22, 20)
    ], fill='white')
    
    return image


def create_icon_waiting_dim() -> Image.Image:
    """Create dim waiting state tray icon (dark blue) / 创建暗淡等待状态托盘图标（深蓝色）"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Darker blue background circle - for blinking effect
    draw.ellipse([4, 4, size-4, size-4], fill='#1565C0')
    
    # Dimmer white "V" shape
    draw.polygon([
        (16, 20), (32, 44), (48, 20),
        (42, 20), (32, 36), (22, 20)
    ], fill='#B3E5FC')
    
    return image


def create_icon_paused() -> Image.Image:
    """Create paused state tray icon / 创建暂停状态托盘图标"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Gray background circle
    draw.ellipse([4, 4, size-4, size-4], fill='#9E9E9E')
    
    # White pause bars
    draw.rectangle([20, 18, 28, 46], fill='white')
    draw.rectangle([36, 18, 44, 46], fill='white')
    
    return image


def toggle_sync(icon, menu_item):
    """Toggle sync on/off / 切换同步开关"""
    state.sync_enabled = not state.sync_enabled
    update_tray_icon(icon)
    
    # Broadcast sync state to all connected clients
    def send_sync_state():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast_sync_state())
        loop.close()
    
    threading.Thread(target=send_sync_state, daemon=True).start()


def toggle_startup(icon, menu_item):
    """Toggle startup with Windows / 切换开机启动"""
    current = is_startup_enabled()
    set_startup_enabled(not current)


def toggle_https(icon, menu_item):
    """Toggle HTTPS on/off / 切换HTTPS开关"""
    state.https_enabled = not state.https_enabled

    if state.https_enabled:
        # Start HTTPS server
        https_thread = threading.Thread(target=run_https_server, daemon=True)
        https_thread.start()
    else:
        # Shutdown HTTPS server
        if state.https_server:
            try:
                state.https_server.shutdown()
                state.https_server = None
            except:
                pass

    # Update notification with new URL
    show_ip_address(icon, menu_item)


def show_ip_address(icon, menu_item):
    """Show IP address notification and copy to clipboard / 显示IP地址并复制"""
    if state.https_enabled:
        web_url = f"https://{HOTSPOT_IP}:{state.https_port}"
        http_url = f"http://{HOTSPOT_IP}:{state.http_port}"
        message = f"📱 手机连接电脑热点后访问:\n{web_url}\n(HTTP: {http_url})\n\n注意: 首次访问需接受安全警告\n(已复制到剪贴板)"
    else:
        web_url = f"http://{HOTSPOT_IP}:{state.http_port}"
        message = f"📱 手机连接电脑热点后访问:\n{web_url}\n(已复制到剪贴板)"

    # Copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(web_url)
    except:
        pass

    icon.notify(message, "Voice Coding")


def quit_app(icon, menu_item):
    """Quit the application / 退出应用"""
    state.running = False
    stop_blink_timer()
    icon.stop()


def stop_blink_timer():
    """Stop the blink timer / 停止闪烁定时器"""
    if state.blink_timer:
        state.blink_timer.cancel()
        state.blink_timer = None


def start_blink_timer(icon):
    """Start the icon blink timer / 启动图标闪烁定时器"""
    stop_blink_timer()
    
    def blink():
        if not state.running:
            return
        if len(state.connected_clients) == 0 and state.sync_enabled:
            # Toggle blink state
            state.blink_state = not state.blink_state
            if state.blink_state:
                icon.icon = create_icon_waiting()
            else:
                icon.icon = create_icon_waiting_dim()
            # Schedule next blink
            state.blink_timer = threading.Timer(0.5, blink)
            state.blink_timer.daemon = True
            state.blink_timer.start()
    
    blink()


def update_tray_icon(icon):
    """Update tray icon based on state / 根据状态更新托盘图标"""
    stop_blink_timer()
    
    if not state.sync_enabled:
        # Sync disabled - gray icon
        icon.icon = create_icon_paused()
        icon.title = f"Voice Coding - Paused\nhttp://{HOTSPOT_IP}:{state.http_port}"
    elif len(state.connected_clients) > 0:
        # Has connected clients - green icon
        icon.icon = create_icon_connected()
        client_count = len(state.connected_clients)
        icon.title = f"Voice Coding - {client_count} Connected\nhttp://{HOTSPOT_IP}:{state.http_port}"
    else:
        # Waiting for connection - blue blinking icon
        icon.title = f"Voice Coding - Waiting\nhttp://{HOTSPOT_IP}:{state.http_port}"
        start_blink_timer(icon)


def get_sync_text(item):
    """Get dynamic menu text for sync toggle / 获取同步开关的动态菜单文本"""
    return "✓ Enable Sync / 启用同步" if state.sync_enabled else "  Enable Sync / 启用同步"


def create_menu():
    """Create the tray menu / 创建托盘菜单"""
    return pystray.Menu(
        item(
            '📋 Show IP / 显示IP',
            show_ip_address
        ),
        pystray.Menu.SEPARATOR,
        item(
            '✓ Enable Sync / 启用同步',
            toggle_sync,
            checked=lambda item: state.sync_enabled
        ),
        item(
            '🔒 Enable HTTPS (PWA) / 启用HTTPS',
            toggle_https,
            checked=lambda item: state.https_enabled
        ),
        item(
            '🚀 Start with Windows / 开机启动',
            toggle_startup,
            checked=lambda item: is_startup_enabled()
        ),
        pystray.Menu.SEPARATOR,
        item(
            '❌ Quit / 退出',
            quit_app
        )
    )


def run_tray():
    """Run the system tray application / 运行系统托盘应用"""
    icon = pystray.Icon(
        APP_NAME,
        create_icon_waiting(),  # Start with waiting icon / 启动时显示等待图标
        f"Voice Coding - Waiting\nhttp://{HOTSPOT_IP}:{state.http_port}",
        menu=create_menu()
    )
    state.tray_icon = icon
    
    # Show notification on start
    icon.run_detached()
    icon.notify(f"已启动！\n1. 开启电脑热点\n2. 手机连接热点\n3. 访问 http://{HOTSPOT_IP}:{state.http_port}", "Voice Coding")
    
    # Start blinking after icon is running
    import time
    time.sleep(0.5)  # Wait for icon to initialize
    update_tray_icon(icon)  # This will start the blinking
    
    # Keep main thread alive
    while state.running:
        time.sleep(0.5)
    
    stop_blink_timer()
    icon.stop()


# ============================================================
# Main Entry / 主入口
# ============================================================
def main():
    """Main entry point / 主入口"""
    global HOTSPOT_IP

    # Detect hotspot IP at startup
    HOTSPOT_IP = get_hotspot_ip()
    print(f"Detected hotspot IP: {HOTSPOT_IP}")

    # Start WebSocket server in background thread
    ws_thread = threading.Thread(target=run_server, daemon=True)
    ws_thread.start()

    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Start HTTPS server in background thread (for PWA install support)
    if state.https_enabled:
        https_thread = threading.Thread(target=run_https_server, daemon=True)
        https_thread.start()

    # Run tray icon in main thread
    run_tray()


if __name__ == "__main__":
    # Check single instance first
    if not check_single_instance():
        show_already_running_message()
        sys.exit(0)
    
    main()

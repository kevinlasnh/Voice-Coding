from __future__ import annotations

import ctypes
import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from platform_utils import ensure_runtime_supported, get_platform, is_wayland_session, system_subprocess_env


_PYAUTOGUI = None
_PORTAL_BACKEND = None

KEY_STATE_RELEASED = 0
KEY_STATE_PRESSED = 1

KEYSYM_RETURN = 0xFF0D
KEYSYM_CTRL_L = 0xFFE3
KEYSYM_SHIFT_L = 0xFFE1
KEYSYM_INSERT = 0xFF63
KEYSYM_V = 0x0076

REMOTE_DESKTOP_DEVICE_KEYBOARD = 1
PORTAL_REQUEST_TIMEOUT_MS = 60000
ATSPI_FOCUS_TIMEOUT_SEC = 0.8
ATSPI_FOCUS_SAMPLE_WINDOW_SEC = 0.5
ATSPI_FOCUS_SAMPLE_INTERVAL_SEC = 0.04
ATSPI_FOCUS_MAX_SAMPLES = 8
AUTO_PASTE_PRE_PORTAL_TIMEOUT_SEC = 0.7
AUTO_PASTE_RESOLVE_TIMEOUT_SEC = 1.6
AUTO_PASTE_RETRY_INTERVAL_SEC = 0.12
AUTO_PASTE_MIN_RELIABLE_VOTES = 2
AUTO_PASTE_MIN_VOTE_MARGIN = 2
WAYLAND_CLIPBOARD_RESTORE_DELAY_SEC = 0.35


class PasteMode(str, Enum):
    AUTO = "auto"
    NORMAL = "normal"
    TERMINAL = "terminal"
    COMPAT = "compat"


class _FocusKind(str, Enum):
    TERMINAL = "terminal"
    NORMAL = "normal"
    UNCERTAIN = "uncertain"


class _AutoPasteDecision(str, Enum):
    TERMINAL = "terminal"
    NORMAL = "normal"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class _AutoPasteResolution:
    decision: _AutoPasteDecision
    terminal_votes: int
    normal_votes: int
    uncertain_votes: int
    samples: tuple[dict[str, str] | None, ...]


PASTE_MODE_LABELS = {
    PasteMode.AUTO: "自动粘贴",
    PasteMode.NORMAL: "普通粘贴",
    PasteMode.TERMINAL: "终端粘贴",
    PasteMode.COMPAT: "兼容粘贴",
}

TERMINAL_APP_NAMES = {
    "alacritty",
    "com.mitchellh.ghostty",
    "com.raggesilver.blackbox",
    "blackbox",
    "console",
    "foot",
    "ghostty",
    "gnome-console",
    "gnome-terminal",
    "gnome-terminal-server",
    "io.elementary.terminal",
    "kitty",
    "kgx",
    "konsole",
    "org.gnome.console",
    "org.gnome.ptyxis",
    "org.gnome.terminal",
    "org.gnome.terminal.legacy",
    "org.kde.konsole",
    "org.wezfurlong.wezterm",
    "ptyxis",
    "qterminal",
    "rio",
    "tabby",
    "terminal",
    "terminator",
    "tilix",
    "wezterm",
    "xfce4-terminal",
}

IGNORED_ATSPI_APP_NAMES = {
    "gnome-shell",
    "org.gnome.shell",
    "xdg-desktop-portal-gnome",
    "xdg-desktop-portal-gtk",
}

UNRELIABLE_ATSPI_APP_NAMES = {
    "unnamed",
}

_PASTE_MODE = PasteMode.AUTO


def _dbus_uint(value: int):
    """Build a D-Bus ``u`` (uint32) argument.

    PyQt5 marshals a plain Python ``int`` as signed int32 ('i'). Several XDG
    RemoteDesktop portal fields (e.g. ``SelectDevices`` ``types`` and the
    ``state`` arg of ``NotifyKeyboardKeysym``) require unsigned 'u', so we
    build a typed ``QDBusArgument`` to force the right signature. This is used
    for top-level call arguments; for values inside an ``a{sv}`` map wrap the
    result via :func:`_dbus_uint_variant`.
    """
    from PyQt5.QtCore import QMetaType
    from PyQt5.QtDBus import QDBusArgument

    arg = QDBusArgument()
    arg.add(value, QMetaType.UInt)
    return arg


def _dbus_uint_variant(value: int):
    """uint32 wrapped as a variant, for use as a value in an ``a{sv}`` map."""
    from PyQt5.QtCore import QVariant

    return QVariant(_dbus_uint(value))


def _get_pyautogui():
    global _PYAUTOGUI
    if _PYAUTOGUI is None:
        import pyautogui

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        _PYAUTOGUI = pyautogui
    return _PYAUTOGUI


def get_paste_mode() -> PasteMode:
    return _PASTE_MODE


def set_paste_mode(mode: PasteMode | str) -> PasteMode:
    global _PASTE_MODE
    if not isinstance(mode, PasteMode):
        mode = PasteMode(str(mode))
    _PASTE_MODE = mode
    return _PASTE_MODE


def get_paste_mode_label(mode: PasteMode | None = None) -> str:
    return PASTE_MODE_LABELS[mode or _PASTE_MODE]


def _is_linux_wayland() -> bool:
    return get_platform() == "linux" and is_wayland_session()


def start_wayland_focus_prewarm() -> threading.Thread | None:
    """Warm the read-only AT-SPI probe without opening a portal session."""
    if not _is_linux_wayland():
        return None

    thread = threading.Thread(
        target=_prewarm_wayland_focus_probe,
        name="voicing-atspi-prewarm",
        daemon=True,
    )
    thread.start()
    return thread


def _prewarm_wayland_focus_probe() -> None:
    try:
        samples = _sample_focus_infos()
        resolution = _summarize_focus_samples(samples)
        ready = _has_reliable_focus_samples(samples)
        logging.log(
            logging.INFO if ready else logging.WARNING,
            "AT-SPI prewarm readiness=%s votes=terminal:%d,normal:%d,uncertain:%d samples=%s",
            "ready" if ready else "unresolved",
            resolution.terminal_votes,
            resolution.normal_votes,
            resolution.uncertain_votes,
            json.dumps(
                _safe_focus_samples(resolution.samples),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        )
    except Exception as exc:
        logging.warning("AT-SPI prewarm failed: %s", type(exc).__name__)


def get_paste_hotkey() -> tuple[str, str]:
    return ("command", "v") if get_platform() == "darwin" else ("ctrl", "v")


def press_enter() -> None:
    ensure_runtime_supported()
    if _is_linux_wayland():
        _get_remote_desktop_portal_backend().press_enter()
        return

    if get_platform() == "windows":
        try:
            _press_enter_windows()
            return
        except Exception:
            pass

    _get_pyautogui().press("enter")


def paste_from_clipboard(attempt_id: str | None = None) -> None:
    ensure_runtime_supported()
    if _is_linux_wayland():
        _get_remote_desktop_portal_backend().paste_from_clipboard(attempt_id=attempt_id)
        return

    _get_pyautogui().hotkey(*get_paste_hotkey(), interval=0.02)


def _paste_primary_selection_if_supported() -> str | None:
    if not _is_linux_wayland() or not shutil.which("wl-paste"):
        return None
    try:
        return subprocess.check_output(
            ["wl-paste", "--primary", "--no-newline"],
            env=system_subprocess_env(),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None


def _copy_to_primary_selection_if_supported(text: str) -> bool:
    if not _is_linux_wayland() or not shutil.which("wl-copy"):
        return False
    try:
        subprocess.run(
            ["wl-copy", "--primary"],
            input=text,
            env=system_subprocess_env(),
            text=True,
            check=True,
        )
        return True
    except Exception:
        return False


def type_text_at_cursor(
    text: str,
    auto_enter: bool = False,
    enter_delay_sec: float = 0.2,
    restore_delay_sec: float | None = None,
) -> None:
    """Paste Unicode text at the current cursor and optionally press Enter."""
    ensure_runtime_supported()
    clipboard = _get_clipboard_backend()
    attempt_id = uuid.uuid4().hex[:10]
    if restore_delay_sec is None:
        restore_delay_sec = WAYLAND_CLIPBOARD_RESTORE_DELAY_SEC if _is_linux_wayland() else 0.1

    old_clipboard: str | None = None
    old_clipboard_captured = False
    try:
        old_clipboard = clipboard.paste()
        old_clipboard_captured = True
    except Exception:
        logging.info("Paste attempt=%s clipboard previous text unavailable", attempt_id)
    old_primary = _paste_primary_selection_if_supported()

    copied_primary = False
    try:
        clipboard.copy(text)
        copied_text = clipboard.paste()
        if copied_text != text:
            raise RuntimeError("剪贴板文本写入验证失败，已取消粘贴以避免发送旧内容。")
        logging.info(
            "Paste attempt=%s clipboard_ready backend=%s text_length=%d",
            attempt_id,
            type(clipboard).__name__,
            len(text),
        )
        copied_primary = _copy_to_primary_selection_if_supported(text)
        paste_from_clipboard(attempt_id=attempt_id)

        if auto_enter:
            threading.Event().wait(enter_delay_sec)
            press_enter()
    finally:
        threading.Event().wait(restore_delay_sec)
        if old_clipboard_captured and old_clipboard is not None:
            try:
                clipboard.copy(old_clipboard)
            except Exception:
                logging.warning("Paste attempt=%s clipboard restore failed", attempt_id)
        if copied_primary and old_primary is not None:
            _copy_to_primary_selection_if_supported(old_primary)


class _PyperclipClipboardBackend:
    def paste(self) -> str:
        import pyperclip

        return pyperclip.paste()

    def copy(self, text: str) -> None:
        import pyperclip

        pyperclip.copy(text)


class _WlClipboardBackend:
    def paste(self) -> str:
        return subprocess.check_output(
            ["wl-paste", "--type", "text", "--no-newline"],
            env=system_subprocess_env(),
            text=True,
            stderr=subprocess.DEVNULL,
        )

    def copy(self, text: str) -> None:
        subprocess.run(
            ["wl-copy"],
            input=text,
            env=system_subprocess_env(),
            text=True,
            check=True,
        )


def _get_clipboard_backend():
    if _is_linux_wayland():
        if shutil.which("wl-copy") and shutil.which("wl-paste"):
            return _WlClipboardBackend()
        raise RuntimeError(
            "GNOME Wayland 需要 wl-clipboard 才能可靠写入文本剪贴板。"
            "请安装 wl-clipboard 后重试。"
        )
    return _PyperclipClipboardBackend()


def _get_remote_desktop_portal_backend():
    global _PORTAL_BACKEND
    if _PORTAL_BACKEND is None:
        _PORTAL_BACKEND = RemoteDesktopPortalKeyboardBackend()
    return _PORTAL_BACKEND


@dataclass
class _PortalRequestResult:
    response_code: int | None = None
    results: dict[str, Any] | None = None
    timed_out: bool = False


class RemoteDesktopPortalKeyboardBackend:
    """Keyboard backend for GNOME Wayland through XDG RemoteDesktop portal."""

    def __init__(self, request_timeout_ms: int = PORTAL_REQUEST_TIMEOUT_MS):
        self._session_handle: str | None = None
        self._request_timeout_ms = request_timeout_ms
        self._lock = threading.RLock()

    def is_available(self) -> bool:
        try:
            return self._available_device_types() & REMOTE_DESKTOP_DEVICE_KEYBOARD != 0
        except Exception:
            return False

    def paste_from_clipboard(self, attempt_id: str | None = None) -> None:
        attempt_id = attempt_id or uuid.uuid4().hex[:10]
        mode = get_paste_mode()
        pre_portal_resolution: _AutoPasteResolution | None = None
        session_was_started = bool(self._session_handle)

        if mode == PasteMode.AUTO and not session_was_started:
            pre_portal_resolution = _resolve_auto_paste_resolution(
                attempt_id=attempt_id,
                phase="pre_portal",
                timeout_sec=AUTO_PASTE_PRE_PORTAL_TIMEOUT_SEC,
            )

        self._ensure_started()

        auto_decision: _AutoPasteDecision | None = None
        if mode == PasteMode.AUTO:
            post_portal_resolution = _resolve_auto_paste_resolution(
                attempt_id=attempt_id,
                phase="post_portal" if not session_was_started else "runtime",
                timeout_sec=AUTO_PASTE_RESOLVE_TIMEOUT_SEC,
            )
            auto_decision = _reconcile_auto_paste_resolutions(
                pre_portal_resolution,
                post_portal_resolution,
                attempt_id=attempt_id,
            )

        sequence = _resolve_wayland_paste_sequence(auto_decision=auto_decision)
        sequence_name = _sequence_name(sequence)
        logging.info(
            "Paste attempt=%s portal_sequence=%s session_started_now=%s",
            attempt_id,
            sequence_name,
            not session_was_started,
        )
        self._send_key_sequence(sequence, attempt_id=attempt_id, sequence_name=sequence_name)

    def press_enter(self) -> None:
        self._ensure_started()
        self._send_key_sequence(
            (
                (KEYSYM_RETURN, KEY_STATE_PRESSED),
                (KEYSYM_RETURN, KEY_STATE_RELEASED),
            )
        )

    def _ensure_started(self) -> None:
        with self._lock:
            if self._session_handle:
                return

            if not self.is_available():
                raise RuntimeError(
                    "当前 Wayland 会话没有可用的 RemoteDesktop portal 键盘能力。"
                    "请确认 xdg-desktop-portal 与 GNOME portal 正在运行。"
                )

            session_token = "voicing" + uuid.uuid4().hex
            create_results = self._call_request(
                "CreateSession",
                {
                    "session_handle_token": session_token,
                },
            )
            session_handle = create_results.get("session_handle")
            if not session_handle:
                raise RuntimeError("RemoteDesktop portal 未返回 session handle。")
            self._session_handle = str(session_handle)

            try:
                self._call_request(
                    "SelectDevices",
                    self._dbus_object_path(self._session_handle),
                    {
                        "types": _dbus_uint_variant(REMOTE_DESKTOP_DEVICE_KEYBOARD),
                    },
                )
                self._call_request(
                    "Start",
                    self._dbus_object_path(self._session_handle),
                    "",
                    {},
                )
            except Exception:
                self._session_handle = None
                raise

    def _send_key_sequence(
        self,
        sequence: tuple[tuple[int, int], ...],
        attempt_id: str | None = None,
        sequence_name: str | None = None,
    ) -> None:
        session_handle = self._session_handle
        if not session_handle:
            raise RuntimeError("RemoteDesktop portal session 尚未启动。")

        iface = self._remote_desktop_interface()
        pressed_keys: list[int] = []
        try:
            for index, (keysym, state) in enumerate(sequence):
                reply = self._notify_keyboard_keysym(iface, session_handle, keysym, state)
                if reply.errorMessage():
                    raise RuntimeError(f"RemoteDesktop portal 键盘事件失败: {reply.errorMessage()}")
                if state == KEY_STATE_PRESSED:
                    if keysym not in pressed_keys:
                        pressed_keys.append(keysym)
                elif keysym in pressed_keys:
                    pressed_keys.remove(keysym)
                logging.debug(
                    "Paste attempt=%s portal_event=%d/%d keysym=0x%x state=%s",
                    attempt_id or "standalone",
                    index + 1,
                    len(sequence),
                    keysym,
                    "pressed" if state == KEY_STATE_PRESSED else "released",
                )
        except Exception:
            for keysym in reversed(pressed_keys):
                try:
                    self._notify_keyboard_keysym(
                        iface,
                        session_handle,
                        keysym,
                        KEY_STATE_RELEASED,
                    )
                except Exception:
                    pass
            self._session_handle = None
            logging.exception(
                "Paste attempt=%s portal_sequence_failed sequence=%s pending_keys=%s",
                attempt_id or "standalone",
                sequence_name or _sequence_name(sequence),
                [f"0x{keysym:x}" for keysym in pressed_keys],
            )
            raise

    def _notify_keyboard_keysym(self, iface, session_handle: str, keysym: int, state: int):
        return iface.call(
            "NotifyKeyboardKeysym",
            self._dbus_object_path(session_handle),
            {},
            int(keysym),
            _dbus_uint(int(state)),
        )

    def _call_request(self, method_name: str, *args):
        app, event_loop, timer, qobject, pyqt_slot, qdbus_connection, qdbus_interface = self._qt_imports()
        _ = app

        bus = qdbus_connection.sessionBus()
        if not bus.isConnected():
            raise RuntimeError("无法连接到 D-Bus session bus。")

        handle_token = "voicing" + uuid.uuid4().hex
        request_path = self._request_path(bus, handle_token)
        result = _PortalRequestResult()

        class RequestReceiver(qobject):
            @pyqt_slot("uint", "QVariantMap")
            def response(self, response_code, results):
                result.response_code = int(response_code)
                result.results = dict(results)
                loop.quit()

        receiver = RequestReceiver()
        connected = bus.connect(
            "",
            request_path,
            "org.freedesktop.portal.Request",
            "Response",
            receiver.response,
        )
        if not connected:
            raise RuntimeError("无法监听 RemoteDesktop portal 请求响应。")

        loop = event_loop()
        timeout = timer()
        timeout.setSingleShot(True)

        def on_timeout():
            result.timed_out = True
            loop.quit()

        timeout.timeout.connect(on_timeout)
        timeout.start(self._request_timeout_ms)

        call_args = list(args)
        options = dict(call_args[-1]) if call_args and isinstance(call_args[-1], dict) else {}
        options["handle_token"] = handle_token
        if call_args and isinstance(call_args[-1], dict):
            call_args[-1] = options
        else:
            call_args.append(options)

        iface = self._remote_desktop_interface()
        reply = iface.call(method_name, *call_args)
        if reply.errorMessage():
            timeout.stop()
            bus.disconnect(
                "",
                request_path,
                "org.freedesktop.portal.Request",
                "Response",
                receiver.response,
            )
            raise RuntimeError(f"RemoteDesktop portal {method_name} 调用失败: {reply.errorMessage()}")

        loop.exec()
        timeout.stop()
        bus.disconnect(
            "",
            request_path,
            "org.freedesktop.portal.Request",
            "Response",
            receiver.response,
        )

        if result.timed_out:
            raise RuntimeError(f"RemoteDesktop portal {method_name} 请求超时。")
        if result.response_code != 0:
            raise RuntimeError(f"RemoteDesktop portal {method_name} 请求被拒绝或取消。")
        return result.results or {}

    def _available_device_types(self) -> int:
        _app, _event_loop, _timer, _qobject, _pyqt_slot, qdbus_connection, qdbus_interface = self._qt_imports()
        bus = qdbus_connection.sessionBus()
        if not bus.isConnected():
            return 0
        iface = qdbus_interface(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.DBus.Properties",
            bus,
        )
        reply = iface.call("Get", "org.freedesktop.portal.RemoteDesktop", "AvailableDeviceTypes")
        if reply.errorMessage() or not reply.arguments():
            return 0
        return int(reply.arguments()[0])

    def _remote_desktop_interface(self):
        _app, _event_loop, _timer, _qobject, _pyqt_slot, qdbus_connection, qdbus_interface = self._qt_imports()
        return qdbus_interface(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.RemoteDesktop",
            qdbus_connection.sessionBus(),
        )

    def _dbus_object_path(self, path: str):
        from PyQt5.QtDBus import QDBusObjectPath

        return QDBusObjectPath(path)

    def _request_path(self, bus, handle_token: str) -> str:
        unique_name = bus.baseService().replace(":", "").replace(".", "_")
        return f"/org/freedesktop/portal/desktop/request/{unique_name}/{handle_token}"

    def _qt_imports(self):
        from PyQt5.QtCore import QCoreApplication, QEventLoop, QObject, QTimer, pyqtSlot
        from PyQt5.QtDBus import QDBusConnection, QDBusInterface

        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication([])
        return app, QEventLoop, QTimer, QObject, pyqtSlot, QDBusConnection, QDBusInterface


def _resolve_wayland_paste_sequence(
    auto_decision: _AutoPasteDecision | None = None,
) -> tuple[tuple[int, int], ...]:
    mode = get_paste_mode()
    if mode == PasteMode.AUTO:
        auto_decision = auto_decision or _resolve_auto_paste_mode()
        if auto_decision == _AutoPasteDecision.UNRESOLVED:
            raise RuntimeError(
                "无法可靠判断当前焦点是终端还是普通窗口，已取消粘贴以避免发送错误快捷键。"
                "请保持目标窗口获得焦点后重试，或临时选择明确的粘贴模式。"
            )
        mode = PasteMode(auto_decision.value)
    if mode == PasteMode.TERMINAL:
        return _ctrl_shift_v_sequence()
    if mode == PasteMode.COMPAT:
        return _shift_insert_sequence()
    return _ctrl_v_sequence()


def _ctrl_v_sequence() -> tuple[tuple[int, int], ...]:
    return (
        (KEYSYM_CTRL_L, KEY_STATE_PRESSED),
        (KEYSYM_V, KEY_STATE_PRESSED),
        (KEYSYM_V, KEY_STATE_RELEASED),
        (KEYSYM_CTRL_L, KEY_STATE_RELEASED),
    )


def _ctrl_shift_v_sequence() -> tuple[tuple[int, int], ...]:
    return (
        (KEYSYM_CTRL_L, KEY_STATE_PRESSED),
        (KEYSYM_SHIFT_L, KEY_STATE_PRESSED),
        (KEYSYM_V, KEY_STATE_PRESSED),
        (KEYSYM_V, KEY_STATE_RELEASED),
        (KEYSYM_SHIFT_L, KEY_STATE_RELEASED),
        (KEYSYM_CTRL_L, KEY_STATE_RELEASED),
    )


def _shift_insert_sequence() -> tuple[tuple[int, int], ...]:
    return (
        (KEYSYM_SHIFT_L, KEY_STATE_PRESSED),
        (KEYSYM_INSERT, KEY_STATE_PRESSED),
        (KEYSYM_INSERT, KEY_STATE_RELEASED),
        (KEYSYM_SHIFT_L, KEY_STATE_RELEASED),
    )


def _sequence_name(sequence: tuple[tuple[int, int], ...]) -> str:
    if sequence == _ctrl_shift_v_sequence():
        return "ctrl_shift_v"
    if sequence == _shift_insert_sequence():
        return "shift_insert"
    if sequence == _ctrl_v_sequence():
        return "ctrl_v"
    if sequence == (
        (KEYSYM_RETURN, KEY_STATE_PRESSED),
        (KEYSYM_RETURN, KEY_STATE_RELEASED),
    ):
        return "enter"
    return "custom"


def is_current_focus_terminal() -> bool:
    return _resolve_auto_paste_mode() == _AutoPasteDecision.TERMINAL


def _resolve_auto_paste_mode(
    timeout_sec: float = AUTO_PASTE_RESOLVE_TIMEOUT_SEC,
    initial_samples: list[dict[str, str] | None] | None = None,
) -> _AutoPasteDecision:
    return _resolve_auto_paste_resolution(
        timeout_sec=timeout_sec,
        initial_samples=initial_samples,
    ).decision


def _resolve_auto_paste_resolution(
    attempt_id: str | None = None,
    phase: str = "runtime",
    timeout_sec: float = AUTO_PASTE_RESOLVE_TIMEOUT_SEC,
    initial_samples: list[dict[str, str] | None] | None = None,
) -> _AutoPasteResolution:
    samples = list(initial_samples or [])
    deadline = time.monotonic() + max(0.0, timeout_sec)

    while True:
        resolution = _summarize_focus_samples(samples)
        if resolution.decision != _AutoPasteDecision.UNRESOLVED:
            _log_auto_paste_resolution(attempt_id, phase, resolution)
            return resolution

        if time.monotonic() >= deadline:
            _log_auto_paste_resolution(attempt_id, phase, resolution, level=logging.WARNING)
            return resolution

        samples.extend(_sample_focus_infos())
        resolution = _summarize_focus_samples(samples)
        if resolution.decision != _AutoPasteDecision.UNRESOLVED:
            _log_auto_paste_resolution(attempt_id, phase, resolution)
            return resolution

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            _log_auto_paste_resolution(attempt_id, phase, resolution, level=logging.WARNING)
            return resolution
        time.sleep(min(AUTO_PASTE_RETRY_INTERVAL_SEC, remaining))


def _summarize_focus_samples(samples: list[dict[str, str] | None]) -> _AutoPasteResolution:
    terminal_votes = 0
    normal_votes = 0
    uncertain_votes = 0

    for info in samples:
        kind = _classify_focus_info(info)
        if kind == _FocusKind.TERMINAL:
            terminal_votes += 1
        elif kind == _FocusKind.NORMAL:
            normal_votes += 1
        else:
            uncertain_votes += 1

    decision = _AutoPasteDecision.UNRESOLVED
    if terminal_votes >= AUTO_PASTE_MIN_RELIABLE_VOTES:
        if normal_votes == 0 or terminal_votes - normal_votes >= AUTO_PASTE_MIN_VOTE_MARGIN:
            decision = _AutoPasteDecision.TERMINAL
    if normal_votes >= AUTO_PASTE_MIN_RELIABLE_VOTES:
        if terminal_votes == 0 or normal_votes - terminal_votes >= AUTO_PASTE_MIN_VOTE_MARGIN:
            decision = _AutoPasteDecision.NORMAL

    return _AutoPasteResolution(
        decision=decision,
        terminal_votes=terminal_votes,
        normal_votes=normal_votes,
        uncertain_votes=uncertain_votes,
        samples=tuple(samples),
    )


def _reconcile_auto_paste_resolutions(
    pre_portal: _AutoPasteResolution | None,
    post_portal: _AutoPasteResolution,
    attempt_id: str | None = None,
) -> _AutoPasteDecision:
    if pre_portal is None:
        decision = post_portal.decision
    elif pre_portal.decision == _AutoPasteDecision.UNRESOLVED:
        decision = post_portal.decision
    elif post_portal.decision == _AutoPasteDecision.UNRESOLVED:
        decision = pre_portal.decision
    elif pre_portal.decision == post_portal.decision:
        decision = post_portal.decision
    else:
        decision = _AutoPasteDecision.UNRESOLVED

    logging.log(
        logging.WARNING if decision == _AutoPasteDecision.UNRESOLVED else logging.INFO,
        "Paste attempt=%s auto_reconcile pre=%s post=%s final=%s",
        attempt_id or "standalone",
        pre_portal.decision.value if pre_portal else "not_sampled",
        post_portal.decision.value,
        decision.value,
    )
    return decision


def _log_auto_paste_resolution(
    attempt_id: str | None,
    phase: str,
    resolution: _AutoPasteResolution,
    level: int = logging.INFO,
) -> None:
    safe_samples = _safe_focus_samples(resolution.samples)
    logging.log(
        level,
        "Paste attempt=%s focus_phase=%s decision=%s votes=terminal:%d,normal:%d,uncertain:%d samples=%s",
        attempt_id or "standalone",
        phase,
        resolution.decision.value,
        resolution.terminal_votes,
        resolution.normal_votes,
        resolution.uncertain_votes,
        json.dumps(safe_samples, ensure_ascii=False, separators=(",", ":")),
    )


def _safe_focus_samples(
    samples: tuple[dict[str, str] | None, ...] | list[dict[str, str] | None],
) -> list[dict[str, str] | None]:
    safe_samples = []
    for info in samples:
        if not info:
            safe_samples.append(None)
            continue
        safe_samples.append(
            {
                "app": str(info.get("app_name", ""))[:80],
                "process": str(info.get("process_name", ""))[:80],
                "role": str(info.get("role", ""))[:80],
                "source": str(info.get("source", ""))[:40],
                "reason": str(info.get("reason", ""))[:80],
            }
        )
    return safe_samples


def _sample_focus_infos() -> list[dict[str, str] | None]:
    samples = _sample_focus_infos_in_process()
    if _has_reliable_focus_samples(samples):
        return samples
    system_samples = _sample_focus_infos_from_system_python()
    if _has_reliable_focus_samples(system_samples):
        return system_samples
    if system_samples:
        return system_samples
    if samples:
        return samples
    return [_get_focused_accessible_info()]


def _has_reliable_focus_samples(samples: list[dict[str, str] | None]) -> bool:
    return any(_classify_focus_info(info) != _FocusKind.UNCERTAIN for info in samples)


def _sample_focus_infos_in_process() -> list[dict[str, str] | None]:
    try:
        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi
    except Exception:
        return []
    return _collect_focus_samples(lambda: _scan_atspi_desktop(Atspi))


def _collect_focus_samples(probe) -> list[dict[str, str] | None]:
    samples: list[dict[str, str] | None] = []
    deadline = time.monotonic() + ATSPI_FOCUS_SAMPLE_WINDOW_SEC

    while len(samples) < ATSPI_FOCUS_MAX_SAMPLES:
        try:
            samples.append(probe())
        except Exception:
            samples.append(None)

        if len(samples) >= ATSPI_FOCUS_MAX_SAMPLES:
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(ATSPI_FOCUS_SAMPLE_INTERVAL_SEC, remaining))

    return samples


def _classify_focus_info(info: dict[str, str] | None) -> _FocusKind:
    if info is None or bool(str(info.get("reason", "")).strip()):
        return _FocusKind.UNCERTAIN
    if _is_terminal_accessible_info(info):
        return _FocusKind.TERMINAL
    if _should_scan_active_fallback(info):
        return _FocusKind.UNCERTAIN
    return _FocusKind.NORMAL


def _normalize_terminal_app_name(value: str) -> str:
    normalized = value.strip().lower()
    if normalized.endswith(".desktop"):
        normalized = normalized[:-8]
    return normalized


def _get_focused_accessible_info(deadline: float | None = None) -> dict[str, str] | None:
    info = _get_focused_accessible_info_in_process()
    if info is not None:
        return info
    return _get_focused_accessible_info_from_system_python(timeout_sec=_remaining_atspi_timeout(deadline))


def _remaining_atspi_timeout(deadline: float | None) -> float:
    if deadline is None:
        return ATSPI_FOCUS_TIMEOUT_SEC
    return max(0.05, min(ATSPI_FOCUS_TIMEOUT_SEC, deadline - time.monotonic()))


def _get_focused_accessible_info_in_process() -> dict[str, str] | None:
    try:
        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi
    except Exception:
        return None
    try:
        return _scan_atspi_desktop(Atspi)
    except Exception:
        return None


def _get_focused_accessible_info_from_system_python(timeout_sec: float | None = None) -> dict[str, str] | None:
    samples = _sample_focus_infos_from_system_python(timeout_sec=timeout_sec, single_sample=True)
    if not samples:
        return None
    return samples[0]


def _sample_focus_infos_from_system_python(
    timeout_sec: float | None = None,
    single_sample: bool = False,
) -> list[dict[str, str] | None]:
    python = _find_system_python_with_atspi()
    if not python:
        logging.warning("AT-SPI system helper unavailable: no alternate system Python")
        return []
    if timeout_sec is None:
        timeout_sec = ATSPI_FOCUS_SAMPLE_WINDOW_SEC + ATSPI_FOCUS_TIMEOUT_SEC
    helper = _ATSPI_SINGLE_FOCUS_HELPER if single_sample else _ATSPI_FOCUS_SAMPLE_HELPER
    try:
        result = subprocess.run(
            [python, "-c", helper],
            text=True,
            capture_output=True,
            env=system_subprocess_env(),
            timeout=timeout_sec,
            check=False,
        )
    except Exception as exc:
        logging.warning("AT-SPI system helper execution failed: %s", type(exc).__name__)
        return []
    if result.returncode != 0 or not result.stdout.strip():
        stderr = result.stderr.strip().replace("\n", " ")[:240]
        logging.warning(
            "AT-SPI system helper returned no samples: returncode=%d stderr=%s",
            result.returncode,
            stderr or "none",
        )
        return []
    try:
        data = json.loads(result.stdout)
    except Exception as exc:
        logging.warning("AT-SPI system helper JSON decode failed: %s", type(exc).__name__)
        return []
    if single_sample:
        if not isinstance(data, dict):
            return []
        return [_normalize_accessible_info(data)]
    if not isinstance(data, list):
        return []
    return [_normalize_accessible_info(item) if isinstance(item, dict) else None for item in data]


def _normalize_accessible_info(data: dict[str, Any]) -> dict[str, str]:
    return {
        "app_name": str(data.get("app_name", "")),
        "process_name": str(data.get("process_name", "")),
        "role": str(data.get("role", "")),
        "name": str(data.get("name", "")),
        "source": str(data.get("source", "")),
        "reason": str(data.get("reason", "")),
    }


def _find_system_python_with_atspi() -> str | None:
    current_executable = os.path.abspath(sys.executable)
    for candidate in ("/usr/bin/python3", shutil.which("python3")):
        if not candidate:
            continue
        candidate = os.path.abspath(candidate)
        if candidate == current_executable:
            continue
        if os.path.exists(candidate):
            return candidate
    return None


def _scan_atspi_desktop(Atspi) -> dict[str, str] | None:
    desktop = Atspi.get_desktop(0)
    active_candidates = _find_state_accessibles(
        Atspi,
        desktop,
        Atspi.StateType.ACTIVE,
        max_depth=4,
        max_children=80,
    )
    selected_active, active_reason = _select_active_window_candidate(Atspi, active_candidates)

    if selected_active is not None:
        focused = _find_focused_accessible(Atspi, selected_active)
        if focused is not None:
            focused_info = _accessible_info(Atspi, focused)
            if not _is_ignored_atspi_info(focused_info):
                return _with_focus_metadata(focused_info, source="active_subtree_focused")
        return _with_focus_metadata(
            _accessible_info(Atspi, selected_active),
            source="active_window",
        )

    focused_candidates = _find_state_accessibles(
        Atspi,
        desktop,
        Atspi.StateType.FOCUSED,
        max_depth=7,
        max_children=120,
    )
    focused_infos = [
        _accessible_info(Atspi, accessible)
        for accessible in focused_candidates
    ]
    focused_infos = [info for info in focused_infos if not _is_ignored_atspi_info(info)]
    reason = active_reason or "no_active_window"
    if focused_infos:
        reason = f"{reason};focused_without_active"
        sample = focused_infos[0]
    else:
        sample = {"app_name": "", "role": "", "name": ""}
    return _with_focus_metadata(sample, source="unresolved", reason=reason)


def _is_terminal_accessible_info(info: dict[str, str]) -> bool:
    if str(info.get("role", "")).lower() == "terminal":
        return True
    identity_names = {
        _normalize_terminal_app_name(str(info.get(key, "")))
        for key in ("app_name", "process_name")
    }
    return bool(identity_names & TERMINAL_APP_NAMES)


def _should_scan_active_fallback(info: dict[str, str] | None) -> bool:
    if not info:
        return True
    app_name = _normalize_terminal_app_name(str(info.get("app_name", "")))
    process_name = _normalize_terminal_app_name(str(info.get("process_name", "")))
    role = str(info.get("role", "")).strip().lower()
    if not app_name and not process_name:
        return True
    if app_name in UNRELIABLE_ATSPI_APP_NAMES and not process_name:
        return True
    return (
        app_name in IGNORED_ATSPI_APP_NAMES
        or process_name in IGNORED_ATSPI_APP_NAMES
        or role in {
        "desktop frame",
        "desktop icon",
        }
    )


def _find_focused_accessible(Atspi, root, max_depth: int = 7):
    stack = [(root, 0)]
    while stack:
        accessible, depth = stack.pop()
        try:
            state_set = accessible.get_state_set()
            if state_set.contains(Atspi.StateType.FOCUSED):
                return accessible
            child_count = accessible.get_child_count()
        except Exception:
            continue
        if depth >= max_depth:
            continue
        for index in range(min(child_count, 120) - 1, -1, -1):
            try:
                stack.append((accessible.get_child_at_index(index), depth + 1))
            except Exception:
                pass
    return None


def _find_state_accessibles(
    Atspi,
    root,
    state_type,
    max_depth: int,
    max_children: int,
) -> list:
    matches = []
    stack = [(root, 0)]
    while stack:
        accessible, depth = stack.pop()
        try:
            state_set = accessible.get_state_set()
            if state_set.contains(state_type):
                matches.append(accessible)
            child_count = accessible.get_child_count()
        except Exception:
            continue
        if depth >= max_depth:
            continue
        for index in range(min(child_count, max_children) - 1, -1, -1):
            try:
                stack.append((accessible.get_child_at_index(index), depth + 1))
            except Exception:
                pass
    return matches


def _select_active_window_candidate(Atspi, candidates: list) -> tuple[Any | None, str]:
    usable: list[tuple[Any, dict[str, str]]] = []
    for accessible in candidates:
        try:
            info = _accessible_info(Atspi, accessible)
        except Exception:
            continue
        if _is_ignored_atspi_info(info):
            continue
        usable.append((accessible, info))

    if not usable:
        return None, "no_non_shell_active_window"

    usable.sort(key=lambda item: _active_candidate_rank(item[1]))
    best_rank = _active_candidate_rank(usable[0][1])[0]
    best = [item for item in usable if _active_candidate_rank(item[1])[0] == best_rank]
    if len(best) != 1:
        return None, "multiple_non_shell_active_windows"

    return best[0][0], ""


def _active_candidate_rank(info: dict[str, str]) -> tuple[int, int]:
    role = str(info.get("role", "")).strip().lower()
    role_rank = (
        0
        if role in {"alert", "dialog"}
        else 1
        if role == "frame"
        else 2
        if role == "window"
        else 3
    )
    return (
        role_rank,
        0 if str(info.get("name", "")).strip() else 1,
    )


def _is_ignored_atspi_info(info: dict[str, str] | None) -> bool:
    if not info:
        return True
    identity_names = {
        _normalize_terminal_app_name(str(info.get(key, "")))
        for key in ("app_name", "process_name")
    }
    role = str(info.get("role", "")).strip().lower()
    if any(
        name in IGNORED_ATSPI_APP_NAMES or name.startswith("xdg-desktop-portal-")
        for name in identity_names
        if name
    ):
        return True
    return role in {"desktop frame", "desktop icon"}


def _with_focus_metadata(
    info: dict[str, str],
    source: str,
    reason: str = "",
) -> dict[str, str]:
    result = dict(info)
    result["source"] = source
    result["reason"] = reason
    return result


def _accessible_info(Atspi, accessible) -> dict[str, str]:
    app_name = ""
    try:
        app = accessible.get_application()
        if app is not None:
            app_name = app.get_name() or ""
    except Exception:
        pass
    try:
        role = accessible.get_role_name() or ""
    except Exception:
        role = ""
    try:
        name = accessible.get_name() or ""
    except Exception:
        name = ""
    return {
        "app_name": app_name,
        "process_name": _accessible_process_name(accessible),
        "role": role,
        "name": name,
    }


def _accessible_process_name(accessible) -> str:
    application = None
    try:
        application = accessible.get_application()
    except Exception:
        pass

    for candidate in (accessible, application):
        if candidate is None:
            continue
        try:
            process_id = int(candidate.get_process_id())
        except Exception:
            continue
        if process_id > 0:
            process_name = _process_name_from_pid(process_id)
            if process_name:
                return process_name
    return ""


def _process_name_from_pid(process_id: int) -> str:
    try:
        return os.path.basename(os.readlink(f"/proc/{process_id}/exe"))[:120]
    except Exception:
        pass

    try:
        with open(f"/proc/{process_id}/comm", encoding="utf-8", errors="replace") as stream:
            process_name = stream.read().strip()
        if process_name:
            return os.path.basename(process_name)[:120]
    except Exception:
        pass

    try:
        with open(f"/proc/{process_id}/cmdline", "rb") as stream:
            command = stream.read().split(b"\0", 1)[0].decode("utf-8", "replace")
        return os.path.basename(command)[:120]
    except Exception:
        return ""


_ATSPI_FOCUS_HELPER_COMMON = r"""
import json
import os
import time
import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

SAMPLE_WINDOW_SEC = 0.5
SAMPLE_INTERVAL_SEC = 0.04
MAX_SAMPLES = 8

def process_name_from_pid(process_id):
    try:
        return os.path.basename(os.readlink(f"/proc/{process_id}/exe"))[:120]
    except Exception:
        pass
    try:
        with open(f"/proc/{process_id}/comm", encoding="utf-8", errors="replace") as stream:
            process_name = stream.read().strip()
        if process_name:
            return os.path.basename(process_name)[:120]
    except Exception:
        pass
    try:
        with open(f"/proc/{process_id}/cmdline", "rb") as stream:
            command = stream.read().split(b"\0", 1)[0].decode("utf-8", "replace")
        return os.path.basename(command)[:120]
    except Exception:
        return ""

def accessible_process_name(accessible):
    application = None
    try:
        application = accessible.get_application()
    except Exception:
        pass
    for candidate in (accessible, application):
        if candidate is None:
            continue
        try:
            process_id = int(candidate.get_process_id())
        except Exception:
            continue
        if process_id > 0:
            process_name = process_name_from_pid(process_id)
            if process_name:
                return process_name
    return ""

def info(accessible):
    app_name = ""
    try:
        app = accessible.get_application()
        if app is not None:
            app_name = app.get_name() or ""
    except Exception:
        pass
    try:
        role = accessible.get_role_name() or ""
    except Exception:
        role = ""
    try:
        name = accessible.get_name() or ""
    except Exception:
        name = ""
    return {
        "app_name": app_name,
        "process_name": accessible_process_name(accessible),
        "role": role,
        "name": name,
    }

def find_focused(root, max_depth=7):
    stack = [(root, 0)]
    while stack:
        accessible, depth = stack.pop()
        try:
            state_set = accessible.get_state_set()
            if state_set.contains(Atspi.StateType.FOCUSED):
                return accessible
            child_count = accessible.get_child_count()
        except Exception:
            continue
        if depth >= max_depth:
            continue
        for index in range(min(child_count, 120) - 1, -1, -1):
            try:
                stack.append((accessible.get_child_at_index(index), depth + 1))
            except Exception:
                pass
    return None

IGNORED_APPS = {
    "gnome-shell", "org.gnome.shell", "xdg-desktop-portal-gnome",
    "xdg-desktop-portal-gtk",
}
def normalize_app_name(value):
    value = str(value or "").strip().lower()
    if value.endswith(".desktop"):
        value = value[:-8]
    return value

def is_ignored(item):
    if not item:
        return True
    identity_names = {
        normalize_app_name(item.get("app_name", "")),
        normalize_app_name(item.get("process_name", "")),
    }
    role = str(item.get("role", "")).strip().lower()
    if any(
        name in IGNORED_APPS or name.startswith("xdg-desktop-portal-")
        for name in identity_names
        if name
    ):
        return True
    return role in {"desktop frame", "desktop icon"}

def find_state(root, state_type, max_depth, max_children):
    matches = []
    stack = [(root, 0)]
    while stack:
        accessible, depth = stack.pop()
        try:
            state_set = accessible.get_state_set()
            if state_set.contains(state_type):
                matches.append(accessible)
            child_count = accessible.get_child_count()
        except Exception:
            continue
        if depth >= max_depth:
            continue
        for index in range(min(child_count, max_children) - 1, -1, -1):
            try:
                stack.append((accessible.get_child_at_index(index), depth + 1))
            except Exception:
                pass
    return matches

def active_rank(item):
    role = str(item.get("role", "")).strip().lower()
    role_rank = (
        0 if role in {"alert", "dialog"}
        else 1 if role == "frame"
        else 2 if role == "window"
        else 3
    )
    return (role_rank, 0 if str(item.get("name", "")).strip() else 1)

def select_active(candidates):
    usable = []
    for accessible in candidates:
        try:
            item = info(accessible)
        except Exception:
            continue
        if not is_ignored(item):
            usable.append((accessible, item))
    if not usable:
        return None, "no_non_shell_active_window"

    usable.sort(key=lambda pair: active_rank(pair[1]))
    best_rank = active_rank(usable[0][1])[0]
    best = [pair for pair in usable if active_rank(pair[1])[0] == best_rank]
    if len(best) != 1:
        return None, "multiple_non_shell_active_windows"
    return best[0][0], ""

def with_meta(item, source, reason=""):
    result = dict(item)
    result["source"] = source
    result["reason"] = reason
    return result

def scan_desktop():
    desktop = Atspi.get_desktop(0)
    active, active_reason = select_active(
        find_state(desktop, Atspi.StateType.ACTIVE, max_depth=4, max_children=80)
    )
    if active is not None:
        focused = find_focused(active)
        if focused is not None:
            focused_info = info(focused)
            if not is_ignored(focused_info):
                return with_meta(focused_info, "active_subtree_focused")
        return with_meta(info(active), "active_window")

    focused_infos = []
    for focused in find_state(desktop, Atspi.StateType.FOCUSED, max_depth=7, max_children=120):
        focused_info = info(focused)
        if not is_ignored(focused_info):
            focused_infos.append(focused_info)
    reason = active_reason or "no_active_window"
    if focused_infos:
        return with_meta(focused_infos[0], "unresolved", reason + ";focused_without_active")
    return with_meta({"app_name": "", "role": "", "name": ""}, "unresolved", reason)
"""


_ATSPI_SINGLE_FOCUS_HELPER = _ATSPI_FOCUS_HELPER_COMMON + r"""
result = scan_desktop()
if result is not None:
    print(json.dumps(result))
"""


_ATSPI_FOCUS_SAMPLE_HELPER = _ATSPI_FOCUS_HELPER_COMMON + r"""
samples = []
deadline = time.monotonic() + SAMPLE_WINDOW_SEC
while len(samples) < MAX_SAMPLES:
    samples.append(scan_desktop())
    if len(samples) >= MAX_SAMPLES:
        break
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        break
    time.sleep(min(SAMPLE_INTERVAL_SEC, remaining))
print(json.dumps(samples))
"""


def _press_enter_windows() -> None:
    input_keyboard = 1
    keyeventf_keyup = 0x0002
    vk_return = 0x0D
    ulong_ptr = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ulong_ptr),
        ]

    class _INPUTUNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("data",)
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("data", _INPUTUNION),
        ]

    def build_keyboard_input(vk_code: int, flags: int = 0) -> "INPUT":
        return INPUT(
            type=input_keyboard,
            ki=KEYBDINPUT(
                wVk=vk_code,
                wScan=0,
                dwFlags=flags,
                time=0,
                dwExtraInfo=0,
            ),
        )

    inputs = (
        build_keyboard_input(vk_return),
        build_keyboard_input(vk_return, keyeventf_keyup),
    )
    sent = ctypes.windll.user32.SendInput(
        len(inputs),
        (INPUT * len(inputs))(*inputs),
        ctypes.sizeof(INPUT),
    )
    if sent != len(inputs):
        raise ctypes.WinError(ctypes.get_last_error())

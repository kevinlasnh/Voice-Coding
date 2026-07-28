import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import platform_keyboard


class PlatformKeyboardTests(unittest.TestCase):
    def test_get_paste_hotkey_macos_uses_command(self):
        with patch("platform_keyboard.get_platform", return_value="darwin"):
            self.assertEqual(platform_keyboard.get_paste_hotkey(), ("command", "v"))

    def test_get_paste_hotkey_non_macos_uses_ctrl(self):
        with patch("platform_keyboard.get_platform", return_value="linux"):
            self.assertEqual(platform_keyboard.get_paste_hotkey(), ("ctrl", "v"))

    def test_start_wayland_focus_prewarm_skips_non_wayland(self):
        with patch("platform_keyboard._is_linux_wayland", return_value=False):
            with patch("platform_keyboard.threading.Thread") as thread_factory:
                self.assertIsNone(platform_keyboard.start_wayland_focus_prewarm())

        thread_factory.assert_not_called()

    def test_start_wayland_focus_prewarm_uses_daemon_thread(self):
        thread = MagicMock()
        with patch("platform_keyboard._is_linux_wayland", return_value=True):
            with patch("platform_keyboard.threading.Thread", return_value=thread) as thread_factory:
                self.assertIs(platform_keyboard.start_wayland_focus_prewarm(), thread)

        thread_factory.assert_called_once_with(
            target=platform_keyboard._prewarm_wayland_focus_probe,
            name="voicing-atspi-prewarm",
            daemon=True,
        )
        thread.start.assert_called_once()

    def test_prewarm_logs_readiness_without_window_title(self):
        samples = [
            {
                "role": "frame",
                "app_name": "ghostty",
                "name": "secret-window-title",
                "source": "active_window",
            },
            {
                "role": "frame",
                "app_name": "ghostty",
                "name": "secret-window-title",
                "source": "active_window",
            },
        ]
        with patch("platform_keyboard._sample_focus_infos", return_value=samples):
            with self.assertLogs(level="INFO") as captured:
                platform_keyboard._prewarm_wayland_focus_probe()

        output = "\n".join(captured.output)
        self.assertIn("readiness=ready", output)
        self.assertIn("ghostty", output)
        self.assertNotIn("secret-window-title", output)

    def test_prewarm_probe_failure_is_non_fatal(self):
        with patch("platform_keyboard._sample_focus_infos", side_effect=RuntimeError("boom")):
            with self.assertLogs(level="WARNING") as captured:
                platform_keyboard._prewarm_wayland_focus_probe()

        self.assertIn("AT-SPI prewarm failed: RuntimeError", "\n".join(captured.output))

    def test_paste_from_clipboard_uses_pyautogui_hotkey(self):
        backend = MagicMock()
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard._get_pyautogui", return_value=backend):
                    with patch("platform_keyboard.get_paste_hotkey", return_value=("ctrl", "v")):
                        platform_keyboard.paste_from_clipboard()
        backend.hotkey.assert_called_once_with("ctrl", "v", interval=0.02)

    def test_paste_from_clipboard_wayland_uses_portal(self):
        backend = MagicMock()
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=True):
                with patch("platform_keyboard._get_remote_desktop_portal_backend", return_value=backend):
                    platform_keyboard.paste_from_clipboard()
        backend.paste_from_clipboard.assert_called_once_with(attempt_id=None)

    def test_press_enter_wayland_uses_portal(self):
        backend = MagicMock()
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=True):
                with patch("platform_keyboard._get_remote_desktop_portal_backend", return_value=backend):
                    platform_keyboard.press_enter()
        backend.press_enter.assert_called_once()

    def test_type_text_at_cursor_restores_clipboard_and_auto_enters(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "hello"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                with patch("platform_keyboard.paste_from_clipboard") as mock_paste:
                    with patch("platform_keyboard.press_enter") as mock_enter:
                        with patch("platform_keyboard.threading.Event") as event_factory:
                            event_factory.return_value.wait = MagicMock()
                            platform_keyboard.type_text_at_cursor(
                                "hello",
                                auto_enter=True,
                                enter_delay_sec=0.3,
                                restore_delay_sec=0.4,
                            )

        self.assertEqual(clipboard.paste.call_count, 2)
        self.assertEqual(clipboard.copy.call_args_list[0].args, ("hello",))
        self.assertEqual(clipboard.copy.call_args_list[1].args, ("old",))
        mock_paste.assert_called_once()
        mock_enter.assert_called_once()
        self.assertEqual(event_factory.return_value.wait.call_args_list[0].args, (0.3,))
        self.assertEqual(event_factory.return_value.wait.call_args_list[1].args, (0.4,))

    def test_type_text_at_cursor_without_auto_enter(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "hello"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                    with patch("platform_keyboard.paste_from_clipboard"):
                        with patch("platform_keyboard.press_enter") as mock_enter:
                            with patch("platform_keyboard.threading.Event") as event_factory:
                                event_factory.return_value.wait = MagicMock()
                                platform_keyboard.type_text_at_cursor("hello", auto_enter=False)

        mock_enter.assert_not_called()
        event_factory.return_value.wait.assert_called_once_with(0.1)

    def test_type_text_at_cursor_wayland_uses_long_default_restore_delay(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "hello"]
        with (
            patch("platform_keyboard.ensure_runtime_supported"),
            patch("platform_keyboard._is_linux_wayland", return_value=True),
            patch("platform_keyboard._get_clipboard_backend", return_value=clipboard),
            patch("platform_keyboard._paste_primary_selection_if_supported", return_value=None),
            patch("platform_keyboard._copy_to_primary_selection_if_supported", return_value=False),
            patch("platform_keyboard.paste_from_clipboard"),
            patch("platform_keyboard.threading.Event") as event_factory,
        ):
            event_factory.return_value.wait = MagicMock()
            platform_keyboard.type_text_at_cursor("hello")

        event_factory.return_value.wait.assert_called_once_with(
            platform_keyboard.WAYLAND_CLIPBOARD_RESTORE_DELAY_SEC
        )

    def test_type_text_at_cursor_restores_clipboard_when_paste_fails(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "hello"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                    with patch("platform_keyboard.paste_from_clipboard", side_effect=RuntimeError("boom")):
                        with patch("platform_keyboard.threading.Event") as event_factory:
                            event_factory.return_value.wait = MagicMock()
                            with self.assertRaises(RuntimeError):
                                platform_keyboard.type_text_at_cursor("hello")

        self.assertEqual(clipboard.copy.call_args_list[0].args, ("hello",))
        self.assertEqual(clipboard.copy.call_args_list[1].args, ("old",))
        event_factory.return_value.wait.assert_called_once_with(0.1)

    def test_type_text_at_cursor_does_not_paste_when_clipboard_verification_fails(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "still-old"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                    with patch("platform_keyboard.paste_from_clipboard") as mock_paste:
                        with patch("platform_keyboard.threading.Event") as event_factory:
                            event_factory.return_value.wait = MagicMock()
                            with self.assertRaisesRegex(RuntimeError, "剪贴板文本写入验证失败"):
                                platform_keyboard.type_text_at_cursor("hello")

        mock_paste.assert_not_called()
        self.assertEqual(clipboard.copy.call_args_list[-1].args, ("old",))

    def test_type_text_at_cursor_does_not_restore_unknown_previous_clipboard(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = [RuntimeError("not text"), "hello"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                    with patch("platform_keyboard.paste_from_clipboard"):
                        with patch("platform_keyboard.threading.Event") as event_factory:
                            event_factory.return_value.wait = MagicMock()
                            platform_keyboard.type_text_at_cursor("hello")

        self.assertEqual(clipboard.copy.call_args_list, [call("hello")])

    def test_remote_desktop_portal_availability_checks_keyboard_bit(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        with patch.object(backend, "_available_device_types", return_value=7):
            self.assertTrue(backend.is_available())

    def test_remote_desktop_portal_availability_rejects_missing_keyboard_bit(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        with patch.object(backend, "_available_device_types", return_value=2):
            self.assertFalse(backend.is_available())

    def test_remote_desktop_portal_paste_sequence(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        with patch.object(backend, "_ensure_started") as mock_started:
            with patch.object(backend, "_send_key_sequence") as mock_send:
                with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.NORMAL):
                    backend.paste_from_clipboard()
        mock_started.assert_called_once()
        mock_send.assert_called_once_with(
            platform_keyboard._ctrl_v_sequence(),
            attempt_id=mock_send.call_args.kwargs["attempt_id"],
            sequence_name="ctrl_v",
        )

    def test_remote_desktop_portal_auto_uses_terminal_sequence_for_terminal_focus(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        backend._session_handle = "/session"
        with patch.object(backend, "_ensure_started"):
            with patch.object(backend, "_send_key_sequence") as mock_send:
                with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
                    with patch(
                        "platform_keyboard._sample_focus_infos",
                        return_value=[
                            {"role": "frame", "app_name": "ghostty"},
                            {"role": "frame", "app_name": "ghostty"},
                        ],
                    ):
                        backend.paste_from_clipboard()
        self.assertEqual(mock_send.call_args.args[0], platform_keyboard._ctrl_shift_v_sequence())
        self.assertEqual(mock_send.call_args.kwargs["sequence_name"], "ctrl_shift_v")

    def test_remote_desktop_portal_auto_uses_normal_sequence_for_non_terminal_focus(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        backend._session_handle = "/session"
        with patch.object(backend, "_ensure_started"):
            with patch.object(backend, "_send_key_sequence") as mock_send:
                with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
                    with patch(
                        "platform_keyboard._sample_focus_infos",
                        return_value=[
                            {"role": "entry", "app_name": "Google Chrome"},
                            {"role": "entry", "app_name": "Google Chrome"},
                        ],
                    ):
                        backend.paste_from_clipboard()
        self.assertEqual(mock_send.call_args.args[0], platform_keyboard._ctrl_v_sequence())
        self.assertEqual(mock_send.call_args.kwargs["sequence_name"], "ctrl_v")

    def test_remote_desktop_portal_auto_uses_pre_portal_when_post_is_unresolved(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        terminal = platform_keyboard._summarize_focus_samples(
            [
                {"role": "frame", "app_name": "ghostty"},
                {"role": "frame", "app_name": "ghostty"},
            ]
        )
        unresolved = platform_keyboard._summarize_focus_samples([None, None])
        with patch.object(backend, "_ensure_started"):
            with patch.object(backend, "_send_key_sequence") as mock_send:
                with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
                    with patch(
                        "platform_keyboard._resolve_auto_paste_resolution",
                        side_effect=[terminal, unresolved],
                    ):
                        backend.paste_from_clipboard(attempt_id="attempt")

        self.assertEqual(mock_send.call_args.args[0], platform_keyboard._ctrl_shift_v_sequence())

    def test_remote_desktop_portal_auto_rejects_conflicting_pre_and_post_focus(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        terminal = platform_keyboard._summarize_focus_samples(
            [
                {"role": "frame", "app_name": "ghostty"},
                {"role": "frame", "app_name": "ghostty"},
            ]
        )
        normal = platform_keyboard._summarize_focus_samples(
            [
                {"role": "entry", "app_name": "Google Chrome"},
                {"role": "entry", "app_name": "Google Chrome"},
            ]
        )
        with patch.object(backend, "_ensure_started"):
            with patch.object(backend, "_send_key_sequence") as mock_send:
                with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
                    with patch(
                        "platform_keyboard._resolve_auto_paste_resolution",
                        side_effect=[terminal, normal],
                    ):
                        with self.assertRaisesRegex(RuntimeError, "无法可靠判断"):
                            backend.paste_from_clipboard(attempt_id="attempt")

        mock_send.assert_not_called()

    def test_remote_desktop_portal_auto_rejects_unresolved_runtime_focus(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        backend._session_handle = "/session"
        unresolved = platform_keyboard._summarize_focus_samples([None, None])
        with patch.object(backend, "_ensure_started"):
            with patch.object(backend, "_send_key_sequence") as mock_send:
                with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
                    with patch(
                        "platform_keyboard._resolve_auto_paste_resolution",
                        return_value=unresolved,
                    ):
                        with self.assertRaisesRegex(RuntimeError, "无法可靠判断"):
                            backend.paste_from_clipboard(attempt_id="attempt")

        mock_send.assert_not_called()

    def test_remote_desktop_portal_terminal_mode_uses_ctrl_shift_v(self):
        with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.TERMINAL):
            self.assertEqual(
                platform_keyboard._resolve_wayland_paste_sequence(),
                platform_keyboard._ctrl_shift_v_sequence(),
            )

    def test_remote_desktop_portal_compat_mode_uses_shift_insert(self):
        with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.COMPAT):
            self.assertEqual(
                platform_keyboard._resolve_wayland_paste_sequence(),
                platform_keyboard._shift_insert_sequence(),
            )

    def test_remote_desktop_portal_enter_sequence(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        with patch.object(backend, "_ensure_started") as mock_started:
            with patch.object(backend, "_send_key_sequence") as mock_send:
                backend.press_enter()
        mock_started.assert_called_once()
        mock_send.assert_called_once_with(
            (
                (platform_keyboard.KEYSYM_RETURN, platform_keyboard.KEY_STATE_PRESSED),
                (platform_keyboard.KEYSYM_RETURN, platform_keyboard.KEY_STATE_RELEASED),
            )
        )

    def test_remote_desktop_portal_ensure_started_runs_portal_flow(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        with patch.object(backend, "is_available", return_value=True):
            with patch.object(
                backend,
                "_call_request",
                side_effect=[
                    {"session_handle": "/org/freedesktop/portal/desktop/session/test"},
                    {},
                    {},
                ],
            ) as mock_call:
                with patch.object(backend, "_dbus_object_path", side_effect=lambda value: f"path:{value}"):
                    backend._ensure_started()

        self.assertEqual(backend._session_handle, "/org/freedesktop/portal/desktop/session/test")
        self.assertEqual(mock_call.call_args_list[0].args[0], "CreateSession")
        self.assertEqual(mock_call.call_args_list[1].args[0], "SelectDevices")
        self.assertEqual(mock_call.call_args_list[2].args[0], "Start")
        # 'types' 必须是 uint 变体（QVariant 包裹的 QDBusArgument），否则
        # portal 会以 "Expected type 'u' ... got 'i'" 拒绝 SelectDevices。
        select_options = mock_call.call_args_list[1].args[2]
        self.assertIn("types", select_options)
        from PyQt5.QtCore import QVariant
        self.assertIsInstance(select_options["types"], QVariant)

    def test_remote_desktop_portal_ensure_started_requires_keyboard_capability(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        with patch.object(backend, "is_available", return_value=False):
            with self.assertRaises(RuntimeError):
                backend._ensure_started()

    def test_remote_desktop_portal_send_key_sequence_uses_notify_keysym(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        backend._session_handle = "/session"
        reply = MagicMock()
        reply.errorMessage.return_value = ""
        iface = MagicMock()
        iface.call.return_value = reply

        with patch.object(backend, "_remote_desktop_interface", return_value=iface):
            with patch.object(backend, "_dbus_object_path", side_effect=lambda value: f"path:{value}"):
                backend._send_key_sequence(((1, platform_keyboard.KEY_STATE_PRESSED),))

        self.assertEqual(iface.call.call_count, 1)
        call_args = iface.call.call_args.args
        self.assertEqual(call_args[0], "NotifyKeyboardKeysym")
        self.assertEqual(call_args[1], "path:/session")
        self.assertEqual(call_args[2], {})
        # keysym 保持普通 int（本机 portal 内省期望 'i'）；state 必须是 uint
        # QDBusArgument，否则会被以 "got 'i'" 拒绝。
        self.assertEqual(call_args[3], 1)
        from PyQt5.QtDBus import QDBusArgument
        self.assertIsInstance(call_args[4], QDBusArgument)

    def test_remote_desktop_portal_send_key_sequence_resets_session_on_error(self):
        backend = platform_keyboard.RemoteDesktopPortalKeyboardBackend()
        backend._session_handle = "/session"
        pressed_reply = MagicMock()
        pressed_reply.errorMessage.return_value = ""
        failed_reply = MagicMock()
        failed_reply.errorMessage.return_value = "boom"
        release_reply = MagicMock()
        release_reply.errorMessage.return_value = ""
        iface = MagicMock()
        iface.call.side_effect = [pressed_reply, failed_reply, release_reply]

        with patch.object(backend, "_remote_desktop_interface", return_value=iface):
            with patch.object(backend, "_dbus_object_path", side_effect=lambda value: value):
                with self.assertRaises(RuntimeError):
                    backend._send_key_sequence(
                        (
                            (platform_keyboard.KEYSYM_CTRL_L, platform_keyboard.KEY_STATE_PRESSED),
                            (platform_keyboard.KEYSYM_V, platform_keyboard.KEY_STATE_PRESSED),
                        )
                    )

        self.assertIsNone(backend._session_handle)
        self.assertEqual(iface.call.call_count, 3)
        compensation_args = iface.call.call_args_list[2].args
        self.assertEqual(compensation_args[3], platform_keyboard.KEYSYM_CTRL_L)

    def test_wl_clipboard_backend_uses_wl_tools(self):
        backend = platform_keyboard._WlClipboardBackend()
        with patch("platform_keyboard.system_subprocess_env", return_value={"PATH": "/usr/bin"}):
            with patch("platform_keyboard.subprocess.check_output", return_value="old") as mock_paste:
                self.assertEqual(backend.paste(), "old")
        mock_paste.assert_called_once_with(
            ["wl-paste", "--type", "text", "--no-newline"],
            env={"PATH": "/usr/bin"},
            text=True,
            stderr=platform_keyboard.subprocess.DEVNULL,
        )

        with patch("platform_keyboard.system_subprocess_env", return_value={"PATH": "/usr/bin"}):
            with patch("platform_keyboard.subprocess.run") as mock_run:
                backend.copy("new")
        mock_run.assert_called_once_with(
            ["wl-copy"],
            input="new",
            env={"PATH": "/usr/bin"},
            text=True,
            check=True,
        )

    def test_type_text_at_cursor_copies_wayland_text_to_primary_selection(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "hello"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                with patch("platform_keyboard.paste_from_clipboard"):
                    with patch("platform_keyboard._is_linux_wayland", return_value=True):
                        with patch("platform_keyboard.shutil.which", return_value="/usr/bin/wl-copy"):
                            with patch("platform_keyboard._paste_primary_selection_if_supported", return_value=None):
                                with patch("platform_keyboard.system_subprocess_env", return_value={"PATH": "/usr/bin"}):
                                    with patch("platform_keyboard.subprocess.run") as mock_run:
                                        platform_keyboard.type_text_at_cursor("hello")

        mock_run.assert_called_once_with(
            ["wl-copy", "--primary"],
            input="hello",
            env={"PATH": "/usr/bin"},
            text=True,
            check=True,
        )

    def test_type_text_at_cursor_restores_primary_selection_when_available(self):
        clipboard = MagicMock()
        clipboard.paste.side_effect = ["old", "hello"]
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._get_clipboard_backend", return_value=clipboard):
                with patch("platform_keyboard.paste_from_clipboard"):
                    with patch("platform_keyboard._is_linux_wayland", return_value=True):
                        with patch("platform_keyboard.shutil.which", return_value="/usr/bin/wl-copy"):
                            with patch("platform_keyboard._paste_primary_selection_if_supported", return_value="old-primary"):
                                with patch("platform_keyboard.system_subprocess_env", return_value={"PATH": "/usr/bin"}):
                                    with patch("platform_keyboard.subprocess.run") as mock_run:
                                        platform_keyboard.type_text_at_cursor("hello")

        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual(mock_run.call_args_list[0].kwargs["input"], "hello")
        self.assertEqual(mock_run.call_args_list[0].kwargs["env"], {"PATH": "/usr/bin"})
        self.assertEqual(mock_run.call_args_list[1].kwargs["input"], "old-primary")
        self.assertEqual(mock_run.call_args_list[1].kwargs["env"], {"PATH": "/usr/bin"})

    def test_atspi_system_python_uses_system_env(self):
        result = MagicMock()
        result.returncode = 0
        result.stdout = '{"app_name": "ghostty", "role": "terminal", "name": ""}'
        with patch("platform_keyboard._find_system_python_with_atspi", return_value="/usr/bin/python3"):
            with patch("platform_keyboard.system_subprocess_env", return_value={"PATH": "/usr/bin"}):
                with patch("platform_keyboard.subprocess.run", return_value=result) as mock_run:
                    info = platform_keyboard._get_focused_accessible_info_from_system_python()

        self.assertEqual(info["app_name"], "ghostty")
        self.assertEqual(mock_run.call_args.kwargs["env"], {"PATH": "/usr/bin"})

    def test_atspi_system_python_sample_helper_returns_multiple_samples(self):
        result = MagicMock()
        result.returncode = 0
        result.stdout = (
            '[{"app_name": "Google Chrome", "role": "frame", "name": "A"}, '
            '{"app_name": "ghostty", "role": "frame", "name": "B"}, null]'
        )
        with patch("platform_keyboard._find_system_python_with_atspi", return_value="/usr/bin/python3"):
            with patch("platform_keyboard.system_subprocess_env", return_value={"PATH": "/usr/bin"}):
                with patch("platform_keyboard.subprocess.run", return_value=result) as mock_run:
                    samples = platform_keyboard._sample_focus_infos_from_system_python(timeout_sec=1.3)

        self.assertEqual(samples[0]["app_name"], "Google Chrome")
        self.assertEqual(samples[1]["app_name"], "ghostty")
        self.assertIsNone(samples[2])
        self.assertEqual(mock_run.call_args.args[0][2], platform_keyboard._ATSPI_FOCUS_SAMPLE_HELPER)
        self.assertEqual(mock_run.call_args.kwargs["timeout"], 1.3)

    def test_normalize_accessible_info_preserves_process_name(self):
        info = platform_keyboard._normalize_accessible_info(
            {
                "app_name": "Unnamed",
                "process_name": "ghostty",
                "role": "frame",
                "name": "private-title",
            }
        )

        self.assertEqual(info["process_name"], "ghostty")

    def test_process_name_from_pid_prefers_executable_basename(self):
        with patch("platform_keyboard.os.readlink", return_value="/usr/bin/ghostty"):
            self.assertEqual(platform_keyboard._process_name_from_pid(1234), "ghostty")

    def test_accessible_process_name_uses_application_pid(self):
        accessible = MagicMock()
        application = MagicMock()
        accessible.get_application.return_value = application
        accessible.get_process_id.side_effect = RuntimeError("no direct pid")
        application.get_process_id.return_value = 1234

        with patch("platform_keyboard._process_name_from_pid", return_value="ghostty") as resolver:
            self.assertEqual(platform_keyboard._accessible_process_name(accessible), "ghostty")

        resolver.assert_called_once_with(1234)

    def test_auto_paste_mode_detects_terminal_role(self):
        decision = platform_keyboard._resolve_auto_paste_mode(
            timeout_sec=0,
            initial_samples=[{"role": "terminal"}, {"role": "terminal"}],
        )
        self.assertEqual(decision, platform_keyboard._AutoPasteDecision.TERMINAL)

    def test_auto_paste_mode_detects_terminal_app_name(self):
        samples = [
            {"role": "frame", "app_name": "org.gnome.Console.desktop"},
            {"role": "frame", "app_name": "org.gnome.Console.desktop"},
        ]
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(timeout_sec=0, initial_samples=samples),
            platform_keyboard._AutoPasteDecision.TERMINAL,
        )

    def test_auto_paste_mode_detects_terminal_process_when_app_is_unnamed(self):
        samples = [
            {"role": "frame", "app_name": "Unnamed", "process_name": "ghostty"},
            {"role": "frame", "app_name": "Unnamed", "process_name": "ghostty"},
        ]
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(timeout_sec=0, initial_samples=samples),
            platform_keyboard._AutoPasteDecision.TERMINAL,
        )

    def test_auto_paste_mode_treats_unnamed_without_process_as_unresolved(self):
        samples = [
            {"role": "frame", "app_name": "Unnamed"},
            {"role": "frame", "app_name": "Unnamed"},
        ]
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(timeout_sec=0, initial_samples=samples),
            platform_keyboard._AutoPasteDecision.UNRESOLVED,
        )

    def test_auto_paste_mode_accepts_unnamed_with_normal_process_identity(self):
        samples = [
            {"role": "frame", "app_name": "Unnamed", "process_name": "normal-editor"},
            {"role": "frame", "app_name": "Unnamed", "process_name": "normal-editor"},
        ]
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(timeout_sec=0, initial_samples=samples),
            platform_keyboard._AutoPasteDecision.NORMAL,
        )

    def test_auto_paste_mode_requires_more_than_one_sparse_normal_sample(self):
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(
                timeout_sec=0,
                initial_samples=[{"role": "entry", "app_name": "Google Chrome"}, None, None],
            ),
            platform_keyboard._AutoPasteDecision.UNRESOLVED,
        )

    def test_auto_paste_mode_uses_confident_normal_majority(self):
        samples = [
            {"role": "frame", "app_name": "ghostty"},
            {"role": "entry", "app_name": "Google Chrome"},
            {"role": "entry", "app_name": "Google Chrome"},
            {"role": "entry", "app_name": "Google Chrome"},
        ]
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(timeout_sec=0, initial_samples=samples),
            platform_keyboard._AutoPasteDecision.NORMAL,
        )

    def test_auto_paste_mode_treats_tied_votes_as_unresolved(self):
        samples = [
            {"role": "frame", "app_name": "ghostty"},
            {"role": "entry", "app_name": "Google Chrome"},
        ]
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(timeout_sec=0, initial_samples=samples),
            platform_keyboard._AutoPasteDecision.UNRESOLVED,
        )

    def test_auto_paste_mode_treats_all_uncertain_as_unresolved(self):
        self.assertEqual(
            platform_keyboard._resolve_auto_paste_mode(
                timeout_sec=0,
                initial_samples=[None, None, {"reason": "no_active_window"}],
            ),
            platform_keyboard._AutoPasteDecision.UNRESOLVED,
        )

    def test_auto_paste_resolution_retries_until_terminal_is_reliable(self):
        with patch(
            "platform_keyboard._sample_focus_infos",
            return_value=[
                {"role": "frame", "app_name": "ghostty"},
                {"role": "frame", "app_name": "ghostty"},
            ],
        ) as mock_sample:
            with patch("platform_keyboard.time.monotonic", side_effect=[0.0, 0.0]):
                resolution = platform_keyboard._resolve_auto_paste_resolution(
                    timeout_sec=1.0,
                    initial_samples=[None],
                )

        self.assertEqual(resolution.decision, platform_keyboard._AutoPasteDecision.TERMINAL)
        mock_sample.assert_called_once()

    def test_auto_paste_log_does_not_include_window_title(self):
        resolution = platform_keyboard._summarize_focus_samples(
            [
                {
                    "role": "frame",
                    "app_name": "ghostty",
                    "name": "secret-window-title",
                    "source": "active_window",
                },
                {
                    "role": "frame",
                    "app_name": "ghostty",
                    "name": "secret-window-title",
                    "source": "active_window",
                },
            ]
        )
        with self.assertLogs(level="INFO") as captured:
            platform_keyboard._log_auto_paste_resolution("attempt", "runtime", resolution)

        output = "\n".join(captured.output)
        self.assertIn("ghostty", output)
        self.assertNotIn("secret-window-title", output)

    def test_auto_paste_log_uses_safe_process_name_for_unnamed_app(self):
        resolution = platform_keyboard._summarize_focus_samples(
            [
                {
                    "role": "frame",
                    "app_name": "Unnamed",
                    "process_name": "ghostty",
                    "name": "secret-window-title",
                    "source": "active_window",
                },
                {
                    "role": "frame",
                    "app_name": "Unnamed",
                    "process_name": "ghostty",
                    "name": "secret-window-title",
                    "source": "active_window",
                },
            ]
        )
        with self.assertLogs(level="INFO") as captured:
            platform_keyboard._log_auto_paste_resolution("attempt", "runtime", resolution)

        output = "\n".join(captured.output)
        self.assertIn('"process":"ghostty"', output)
        self.assertNotIn("secret-window-title", output)

    def test_collect_focus_samples_uses_window_and_max_samples(self):
        monotonic_values = [10.0]
        monotonic_values.extend(10.01 + index * 0.01 for index in range(20))
        probe = MagicMock(return_value={"role": "entry", "app_name": "Google Chrome"})
        with patch("platform_keyboard.time.monotonic", side_effect=monotonic_values):
            with patch("platform_keyboard.time.sleep") as mock_sleep:
                samples = platform_keyboard._collect_focus_samples(probe)

        self.assertEqual(len(samples), platform_keyboard.ATSPI_FOCUS_MAX_SAMPLES)
        self.assertEqual(probe.call_count, platform_keyboard.ATSPI_FOCUS_MAX_SAMPLES)
        self.assertEqual(mock_sleep.call_count, platform_keyboard.ATSPI_FOCUS_MAX_SAMPLES - 1)

    def test_resolve_auto_paste_sequence_uses_explicit_auto_decision(self):
        with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
            self.assertEqual(
                platform_keyboard._resolve_wayland_paste_sequence(
                    auto_decision=platform_keyboard._AutoPasteDecision.TERMINAL
                ),
                platform_keyboard._ctrl_shift_v_sequence(),
            )

    def test_resolve_auto_paste_sequence_rejects_unresolved(self):
        with patch("platform_keyboard.get_paste_mode", return_value=platform_keyboard.PasteMode.AUTO):
            with self.assertRaisesRegex(RuntimeError, "无法可靠判断"):
                platform_keyboard._resolve_wayland_paste_sequence(
                    auto_decision=platform_keyboard._AutoPasteDecision.UNRESOLVED
                )

    def test_sample_focus_infos_falls_back_when_in_process_is_all_uncertain(self):
        system_samples = [
            {"role": "frame", "app_name": "ghostty"},
            {"role": "frame", "app_name": "ghostty"},
        ]
        with patch("platform_keyboard._sample_focus_infos_in_process", return_value=[None, None]):
            with patch(
                "platform_keyboard._sample_focus_infos_from_system_python",
                return_value=system_samples,
            ) as mock_system:
                self.assertEqual(platform_keyboard._sample_focus_infos(), system_samples)
        mock_system.assert_called_once()

    def test_select_active_window_filters_shell_and_uses_real_app(self):
        fake_atspi = MagicMock()
        shell = object()
        terminal = object()
        infos = {
            shell: {"role": "window", "app_name": "gnome-shell", "name": ""},
            terminal: {"role": "frame", "app_name": "ghostty", "name": "Terminal"},
        }
        with patch("platform_keyboard._accessible_info", side_effect=lambda _a, obj: infos[obj]):
            selected, reason = platform_keyboard._select_active_window_candidate(
                fake_atspi,
                [shell, terminal],
            )
        self.assertIs(selected, terminal)
        self.assertEqual(reason, "")

    def test_select_active_window_rejects_multiple_real_active_apps(self):
        fake_atspi = MagicMock()
        chrome = object()
        terminal = object()
        infos = {
            chrome: {"role": "frame", "app_name": "Google Chrome", "name": "Browser"},
            terminal: {"role": "frame", "app_name": "ghostty", "name": "Terminal"},
        }
        with patch("platform_keyboard._accessible_info", side_effect=lambda _a, obj: infos[obj]):
            selected, reason = platform_keyboard._select_active_window_candidate(
                fake_atspi,
                [chrome, terminal],
            )
        self.assertIsNone(selected)
        self.assertEqual(reason, "multiple_non_shell_active_windows")

    def test_select_active_window_rejects_two_active_windows_from_same_app(self):
        fake_atspi = MagicMock()
        first = object()
        second = object()
        infos = {
            first: {"role": "frame", "app_name": "ghostty", "name": "Terminal A"},
            second: {"role": "frame", "app_name": "ghostty", "name": "Terminal B"},
        }
        with patch("platform_keyboard._accessible_info", side_effect=lambda _a, obj: infos[obj]):
            selected, reason = platform_keyboard._select_active_window_candidate(
                fake_atspi,
                [first, second],
            )
        self.assertIsNone(selected)
        self.assertEqual(reason, "multiple_non_shell_active_windows")

    def test_scan_atspi_desktop_uses_active_terminal_not_stale_global_focus(self):
        fake_atspi = MagicMock()
        fake_root = object()
        terminal = object()
        fake_atspi.get_desktop.return_value = fake_root
        fake_atspi.StateType.ACTIVE = object()
        fake_atspi.StateType.FOCUSED = object()
        with patch("platform_keyboard._find_state_accessibles", return_value=[terminal]) as mock_states:
            with patch(
                "platform_keyboard._select_active_window_candidate",
                return_value=(terminal, ""),
            ):
                with patch("platform_keyboard._find_focused_accessible", return_value=None):
                    with patch(
                        "platform_keyboard._accessible_info",
                        return_value={"role": "frame", "app_name": "ghostty", "name": "Terminal"},
                    ):
                        info = platform_keyboard._scan_atspi_desktop(fake_atspi)

        self.assertEqual(info["app_name"], "ghostty")
        self.assertEqual(info["source"], "active_window")
        self.assertEqual(mock_states.call_count, 1)

    def test_scan_atspi_desktop_uses_active_normal_not_stale_terminal_focus(self):
        fake_atspi = MagicMock()
        fake_root = object()
        active_normal = object()
        fake_atspi.get_desktop.return_value = fake_root
        fake_atspi.StateType.ACTIVE = object()
        fake_atspi.StateType.FOCUSED = object()
        with patch("platform_keyboard._find_state_accessibles", return_value=[active_normal]):
            with patch(
                "platform_keyboard._select_active_window_candidate",
                return_value=(active_normal, ""),
            ):
                with patch("platform_keyboard._find_focused_accessible", return_value=None):
                    with patch(
                        "platform_keyboard._accessible_info",
                        return_value={"role": "frame", "app_name": "Google Chrome", "name": "Browser"},
                    ):
                        info = platform_keyboard._scan_atspi_desktop(fake_atspi)

        self.assertEqual(platform_keyboard._classify_focus_info(info), platform_keyboard._FocusKind.NORMAL)

    def test_scan_atspi_desktop_uses_terminal_control_inside_active_window(self):
        fake_atspi = MagicMock()
        fake_root = object()
        active_window = object()
        focused_terminal = object()
        fake_atspi.get_desktop.return_value = fake_root
        fake_atspi.StateType.ACTIVE = object()
        fake_atspi.StateType.FOCUSED = object()
        infos = {
            active_window: {"role": "frame", "app_name": "Unnamed", "name": "Window"},
            focused_terminal: {"role": "terminal", "app_name": "Unnamed", "name": ""},
        }
        with patch("platform_keyboard._find_state_accessibles", return_value=[active_window]):
            with patch(
                "platform_keyboard._select_active_window_candidate",
                return_value=(active_window, ""),
            ):
                with patch(
                    "platform_keyboard._find_focused_accessible",
                    return_value=focused_terminal,
                ):
                    with patch(
                        "platform_keyboard._accessible_info",
                        side_effect=lambda _a, obj: infos[obj],
                    ):
                        info = platform_keyboard._scan_atspi_desktop(fake_atspi)

        self.assertEqual(platform_keyboard._classify_focus_info(info), platform_keyboard._FocusKind.TERMINAL)
        self.assertEqual(info["source"], "active_subtree_focused")

    def test_scan_atspi_desktop_marks_focused_without_active_as_unresolved(self):
        fake_atspi = MagicMock()
        fake_root = object()
        stale_terminal = object()
        fake_atspi.get_desktop.return_value = fake_root
        fake_atspi.StateType.ACTIVE = object()
        fake_atspi.StateType.FOCUSED = object()
        with patch(
            "platform_keyboard._find_state_accessibles",
            side_effect=[[], [stale_terminal]],
        ):
            with patch(
                "platform_keyboard._select_active_window_candidate",
                return_value=(None, "no_non_shell_active_window"),
            ):
                with patch(
                    "platform_keyboard._accessible_info",
                    return_value={"role": "frame", "app_name": "ghostty", "name": "Terminal"},
                ):
                    info = platform_keyboard._scan_atspi_desktop(fake_atspi)

        self.assertEqual(platform_keyboard._classify_focus_info(info), platform_keyboard._FocusKind.UNCERTAIN)
        self.assertIn("focused_without_active", info["reason"])

    def test_get_clipboard_backend_prefers_wl_tools_on_wayland(self):
        with patch("platform_keyboard._is_linux_wayland", return_value=True):
            with patch("platform_keyboard.shutil.which", side_effect=lambda command: f"/usr/bin/{command}"):
                self.assertIsInstance(platform_keyboard._get_clipboard_backend(), platform_keyboard._WlClipboardBackend)

    def test_get_clipboard_backend_rejects_missing_wl_tools_on_wayland(self):
        with patch("platform_keyboard._is_linux_wayland", return_value=True):
            with patch("platform_keyboard.shutil.which", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "wl-clipboard"):
                    platform_keyboard._get_clipboard_backend()

    def test_get_clipboard_backend_uses_pyperclip_off_wayland(self):
        with patch("platform_keyboard._is_linux_wayland", return_value=False):
            self.assertIsInstance(
                platform_keyboard._get_clipboard_backend(),
                platform_keyboard._PyperclipClipboardBackend,
            )

    def test_press_enter_windows_prefers_sendinput(self):
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard.get_platform", return_value="windows"):
                    with patch("platform_keyboard._press_enter_windows") as mock_windows:
                        platform_keyboard.press_enter()
        mock_windows.assert_called_once()

    def test_press_enter_windows_falls_back_to_pyautogui(self):
        backend = MagicMock()
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard.get_platform", return_value="windows"):
                    with patch("platform_keyboard._press_enter_windows", side_effect=RuntimeError("boom")):
                        with patch("platform_keyboard._get_pyautogui", return_value=backend):
                            platform_keyboard.press_enter()
        backend.press.assert_called_once_with("enter")

    def test_press_enter_non_windows_uses_pyautogui(self):
        backend = MagicMock()
        with patch("platform_keyboard.ensure_runtime_supported"):
            with patch("platform_keyboard._is_linux_wayland", return_value=False):
                with patch("platform_keyboard.get_platform", return_value="linux"):
                    with patch("platform_keyboard._get_pyautogui", return_value=backend):
                        platform_keyboard.press_enter()
        backend.press.assert_called_once_with("enter")


if __name__ == "__main__":
    unittest.main()

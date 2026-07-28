import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QSystemTrayIcon

from voice_coding import ModernTrayIcon


class TrayActivationTests(unittest.TestCase):
    def test_common_tray_activation_reasons_open_custom_menu(self):
        self.assertTrue(
            ModernTrayIcon._should_show_custom_menu_for_activation_reason(QSystemTrayIcon.Context)
        )
        self.assertTrue(
            ModernTrayIcon._should_show_custom_menu_for_activation_reason(QSystemTrayIcon.Trigger)
        )
        self.assertTrue(
            ModernTrayIcon._should_show_custom_menu_for_activation_reason(QSystemTrayIcon.DoubleClick)
        )

    def test_middle_click_does_not_open_custom_menu(self):
        self.assertFalse(
            ModernTrayIcon._should_show_custom_menu_for_activation_reason(QSystemTrayIcon.MiddleClick)
        )


class TrayNativeMenuTests(unittest.TestCase):
    def test_native_menu_pops_on_left_and_double_click(self):
        # Linux 原生菜单在左键 / 双击时手动 popup
        self.assertTrue(
            ModernTrayIcon._should_popup_native_menu_for_activation_reason(QSystemTrayIcon.Trigger)
        )
        self.assertTrue(
            ModernTrayIcon._should_popup_native_menu_for_activation_reason(QSystemTrayIcon.DoubleClick)
        )

    def test_native_menu_skips_context_to_avoid_double_menu(self):
        # 右键交给 setContextMenu / 宿主；这里再 popup 会同时弹两个菜单
        self.assertFalse(
            ModernTrayIcon._should_popup_native_menu_for_activation_reason(QSystemTrayIcon.Context)
        )

    def test_native_menu_skips_middle_click(self):
        self.assertFalse(
            ModernTrayIcon._should_popup_native_menu_for_activation_reason(QSystemTrayIcon.MiddleClick)
        )

    def test_custom_menu_filter_still_independent_of_platform(self):
        # 自定义菜单过滤器保持不变，供 Windows/macOS 使用
        self.assertTrue(
            ModernTrayIcon._should_show_custom_menu_for_activation_reason(QSystemTrayIcon.Context)
        )


class CustomMenuLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt5.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_custom_menu_has_no_separator_items(self):
        # 自定义 Fluent 菜单（Windows/macOS）不再在项之间插入分隔横条。
        # container 内应恰好 6 个功能项：QR / 同步输入 / 粘贴模式 / 开机自启 / 打开日志 / 退出应用。
        from voice_coding import ModernMenuWidget
        menu = ModernMenuWidget()
        self.assertEqual(menu.container.layout().count(), 6)

    def test_custom_menu_width_tightens_to_content(self):
        # 菜单内容尺寸应等于 sizeHint；setFixedWidth(sizeHint) 收紧掉 adjustSize 的多余宽度。
        from voice_coding import ModernMenuWidget
        menu = ModernMenuWidget()
        menu.adjustSize()
        menu.setFixedWidth(menu.sizeHint().width())
        self.assertEqual(menu.width(), menu.sizeHint().width())
        # 宽度应在最长项内容附近，不应是 adjustSize 默认的偏大值（约 200）。
        self.assertLess(menu.width(), 190)

    def test_custom_menu_cycles_paste_mode(self):
        import voice_coding
        import platform_keyboard

        from voice_coding import ModernMenuWidget
        old_mode = platform_keyboard.get_paste_mode()
        menu = ModernMenuWidget()
        try:
            platform_keyboard.set_paste_mode(platform_keyboard.PasteMode.AUTO)
            with patch.object(menu, "close_with_animation"):
                menu.cycle_paste_mode()
            self.assertEqual(
                platform_keyboard.get_paste_mode(),
                platform_keyboard.PasteMode.NORMAL,
            )
            self.assertEqual(menu.paste_mode_btn.text_label.text(), "普通粘贴")
        finally:
            platform_keyboard.set_paste_mode(old_mode)
            menu.hide()
            menu.deleteLater()


class QRCodeDialogOpenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt5.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_qr_dialog_opens_directly_at_center_rect(self):
        from voice_coding import QRCodeDialog
        dialog = QRCodeDialog()
        end_rect = QRect(100, 120, dialog.DIALOG_WIDTH, dialog.DIALOG_HEIGHT)
        dialog._populate_content = MagicMock()
        dialog._build_end_rect = MagicMock(return_value=end_rect)

        try:
            dialog.show_from(QPoint(20, 30))

            dialog._populate_content.assert_called_once_with()
            dialog._build_end_rect.assert_called_once()
            self.assertEqual(dialog.geometry(), end_rect)
            self.assertEqual(dialog._anim_end_rect, end_rect)
            self.assertTrue(dialog._ignore_focus_loss)
        finally:
            dialog.hide()
            dialog.deleteLater()


class SyncStateBroadcastTests(unittest.TestCase):
    def test_schedule_sync_state_broadcast_uses_server_loop(self):
        import voice_coding

        old_loop = voice_coding.state.server_loop
        loop = MagicMock()
        loop.is_closed.return_value = False
        future = MagicMock()
        broadcast_call = object()
        try:
            voice_coding.state.server_loop = loop
            with (
                patch.object(
                    voice_coding,
                    "broadcast_sync_state",
                    new=MagicMock(return_value=broadcast_call),
                ) as broadcast,
                patch.object(
                    voice_coding.asyncio,
                    "run_coroutine_threadsafe",
                    return_value=future,
                ) as run_coroutine_threadsafe,
            ):
                voice_coding.schedule_sync_state_broadcast()

            broadcast.assert_called_once_with()
            run_coroutine_threadsafe.assert_called_once_with(broadcast_call, loop)
            future.add_done_callback.assert_called_once()
        finally:
            voice_coding.state.server_loop = old_loop

    def test_schedule_sync_state_broadcast_skips_when_loop_missing(self):
        import voice_coding

        old_loop = voice_coding.state.server_loop
        try:
            voice_coding.state.server_loop = None
            with (
                patch.object(
                    voice_coding,
                    "broadcast_sync_state",
                    new=MagicMock(),
                ) as broadcast,
                patch.object(
                    voice_coding.asyncio,
                    "run_coroutine_threadsafe",
                ) as run_coroutine_threadsafe,
            ):
                voice_coding.schedule_sync_state_broadcast()

            broadcast.assert_not_called()
            run_coroutine_threadsafe.assert_not_called()
        finally:
            voice_coding.state.server_loop = old_loop


class MainStartupTests(unittest.TestCase):
    def test_main_starts_focus_prewarm_before_network_and_server(self):
        import voice_coding

        events = []
        server_thread = MagicMock()
        with (
            patch.object(voice_coding, "setup_logging"),
            patch.object(
                voice_coding,
                "ensure_runtime_supported",
                side_effect=lambda: events.append("runtime"),
            ),
            patch.object(
                voice_coding,
                "start_wayland_focus_prewarm",
                side_effect=lambda: events.append("prewarm"),
            ) as prewarm,
            patch.object(
                voice_coding,
                "refresh_server_interfaces",
                side_effect=lambda **_kwargs: events.append("network"),
            ),
            patch.object(voice_coding, "get_primary_server_ip", return_value="127.0.0.1"),
            patch.object(
                voice_coding.threading,
                "Thread",
                return_value=server_thread,
            ) as thread_factory,
            patch.object(
                voice_coding,
                "run_tray",
                side_effect=lambda: events.append("tray"),
            ),
        ):
            voice_coding.main()

        self.assertEqual(events, ["runtime", "prewarm", "network", "tray"])
        prewarm.assert_called_once_with()
        thread_factory.assert_called_once_with(target=voice_coding.run_server, daemon=True)
        server_thread.start.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

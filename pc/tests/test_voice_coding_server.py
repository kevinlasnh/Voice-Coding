import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import voice_coding
from voicing_protocol import TYPE_TEXT, TEXT_SEND_MODE_COMMIT, TEXT_SEND_MODE_SUBMIT


class FakeWebSocket:
    remote_address = ("127.0.0.1", 12345)

    def __init__(self, messages):
        self._messages = list(messages)
        self.sent = []

    async def send(self, message):
        self.sent.append(json.loads(message))

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration
        return self._messages.pop(0)


class HandleClientTests(unittest.TestCase):
    def test_failed_text_injection_ack_does_not_clear_phone_input(self):
        message = json.dumps(
            {
                "type": TYPE_TEXT,
                "content": "hello",
                "send_mode": TEXT_SEND_MODE_SUBMIT,
                "auto_enter": False,
            }
        )
        websocket = FakeWebSocket([message])
        old_sync_enabled = voice_coding.state.sync_enabled
        old_clients = set(voice_coding.state.connected_clients)
        try:
            voice_coding.state.sync_enabled = True
            voice_coding.state.connected_clients.clear()
            with (
                patch("voice_coding.type_text", return_value=False),
                patch("voice_coding.get_or_create_device_identity") as identity,
            ):
                identity.return_value.name = "PC"
                identity.return_value.device_id = "device"
                identity.return_value.os = "linux"
                asyncio.run(voice_coding.handle_client(websocket))
        finally:
            voice_coding.state.sync_enabled = old_sync_enabled
            voice_coding.state.connected_clients.clear()
            voice_coding.state.connected_clients.update(old_clients)

        self.assertEqual(websocket.sent[-1]["type"], "ack")
        self.assertFalse(websocket.sent[-1]["clear_input"])

    def test_commit_auto_enter_ack_clears_after_enter_succeeds(self):
        message = json.dumps(
            {
                "type": TYPE_TEXT,
                "content": "",
                "send_mode": TEXT_SEND_MODE_COMMIT,
                "auto_enter": True,
            }
        )
        websocket = FakeWebSocket([message])
        old_sync_enabled = voice_coding.state.sync_enabled
        old_clients = set(voice_coding.state.connected_clients)
        try:
            voice_coding.state.sync_enabled = True
            voice_coding.state.connected_clients.clear()
            with (
                patch("voice_coding.press_enter_after_settle", return_value=True) as mock_enter,
                patch("voice_coding.get_or_create_device_identity") as identity,
            ):
                identity.return_value.name = "PC"
                identity.return_value.device_id = "device"
                identity.return_value.os = "linux"
                asyncio.run(voice_coding.handle_client(websocket))
        finally:
            voice_coding.state.sync_enabled = old_sync_enabled
            voice_coding.state.connected_clients.clear()
            voice_coding.state.connected_clients.update(old_clients)

        mock_enter.assert_called_once()
        self.assertEqual(websocket.sent[-1]["type"], "ack")
        self.assertTrue(websocket.sent[-1]["clear_input"])

    def test_commit_auto_enter_ack_keeps_input_after_enter_fails(self):
        message = json.dumps(
            {
                "type": TYPE_TEXT,
                "content": "",
                "send_mode": TEXT_SEND_MODE_COMMIT,
                "auto_enter": True,
            }
        )
        websocket = FakeWebSocket([message])
        old_sync_enabled = voice_coding.state.sync_enabled
        old_clients = set(voice_coding.state.connected_clients)
        try:
            voice_coding.state.sync_enabled = True
            voice_coding.state.connected_clients.clear()
            with (
                patch("voice_coding.press_enter_after_settle", return_value=False) as mock_enter,
                patch("voice_coding.get_or_create_device_identity") as identity,
            ):
                identity.return_value.name = "PC"
                identity.return_value.device_id = "device"
                identity.return_value.os = "linux"
                asyncio.run(voice_coding.handle_client(websocket))
        finally:
            voice_coding.state.sync_enabled = old_sync_enabled
            voice_coding.state.connected_clients.clear()
            voice_coding.state.connected_clients.update(old_clients)

        mock_enter.assert_called_once()
        self.assertEqual(websocket.sent[-1]["type"], "ack")
        self.assertFalse(websocket.sent[-1]["clear_input"])


class TypeTextTests(unittest.TestCase):
    def test_type_text_uses_platform_specific_clipboard_restore_delay(self):
        old_sync_enabled = voice_coding.state.sync_enabled
        try:
            voice_coding.state.sync_enabled = True
            with patch("voice_coding.type_text_at_cursor") as type_at_cursor:
                self.assertTrue(voice_coding.type_text("hello", auto_enter=True))
        finally:
            voice_coding.state.sync_enabled = old_sync_enabled

        type_at_cursor.assert_called_once_with(
            "hello",
            auto_enter=True,
            enter_delay_sec=voice_coding.AUTO_ENTER_SETTLE_DELAY_SEC,
        )


if __name__ == "__main__":
    unittest.main()

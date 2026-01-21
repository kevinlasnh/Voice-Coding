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
# Configuration / 配置
# ============================================================
APP_NAME = "VoiceCoding"
APP_VERSION = "1.0.0"
WS_PORT = 9527      # WebSocket port
HTTP_PORT = 9528    # HTTP port for web UI
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
        self.connected_clients = set()
        self.blink_state = False  # For icon blinking / 图标闪烁状态
        self.blink_timer: Optional[threading.Timer] = None
        
state = AppState()


# ============================================================
# Network Configuration / 网络配置
# ============================================================
# Windows Mobile Hotspot default IP / Windows 移动热点默认 IP
HOTSPOT_IP = "192.168.137.1"


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
        update_tray_icon(state.tray_icon)
    
    try:
        # Send welcome message with current sync state
        await websocket.send(json.dumps({
            "type": "connected",
            "message": "Connected to Voice Coding server",
            "sync_enabled": state.sync_enabled
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


def show_ip_address(icon, menu_item):
    """Show IP address notification and copy to clipboard / 显示IP地址并复制"""
    web_url = f"http://{HOTSPOT_IP}:{state.http_port}"
    
    # Copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(web_url)
    except:
        pass
    
    icon.notify(f"📱 手机连接电脑热点后访问:\n{web_url}\n(已复制到剪贴板)", "Voice Coding")


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
    # Start WebSocket server in background thread
    ws_thread = threading.Thread(target=run_server, daemon=True)
    ws_thread.start()
    
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Run tray icon in main thread
    run_tray()


if __name__ == "__main__":
    main()

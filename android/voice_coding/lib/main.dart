import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const VoiceCodingApp());
}

class VoiceCodingApp extends StatelessWidget {
  const VoiceCodingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Voice Coding',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFFD97757),
          secondary: const Color(0xFFD97757),
          surface: const Color(0xFF343330),
          background: const Color(0xFF000000),
          error: const Color(0xFFE85C4A),
        ),
        scaffoldBackgroundColor: const Color(0xFF000000),
        cardColor: const Color(0xFF343330),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF2D2B28),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: Color(0xFFD97757)),
          ),
          hintStyle: const TextStyle(color: Color(0xFF6B6B6B)),
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Color(0xFFECECEC), fontSize: 16),
          bodyMedium: TextStyle(color: Color(0xFFECECEC), fontSize: 14),
          titleLarge: TextStyle(color: Color(0xFFECECEC), fontSize: 20, fontWeight: FontWeight.bold),
        ),
      ),
      home: const MainPage(),
    );
  }
}

class MainPage extends StatefulWidget {
  const MainPage({super.key});

  @override
  State<MainPage> createState() => _MainPageState();
}

class _MainPageState extends State<MainPage> with WidgetsBindingObserver, TickerProviderStateMixin {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final GlobalKey _menuButtonKey = GlobalKey();  // 用于获取按钮位置

  WebSocketChannel? _channel;
  ConnectionStatus _status = ConnectionStatus.disconnected;
  String _deviceName = '';
  bool _syncEnabled = true;
  Timer? _reconnectTimer;
  String _serverIp = '192.168.137.1';  // 默认 IP，会被 UDP 发现覆盖
  int _serverPort = 9527;
  String _lastSentText = '';  // 保存上次发送的文本
  bool _showMenu = false;  // 是否显示下拉菜单
  RawDatagramSocket? _udpSocket;  // UDP 监听套接字
  StreamSubscription<RawSocketEvent>? _udpSubscription;  // UDP 订阅
  static const int _udpBroadcastPort = 9530;  // UDP 广播端口

  // 动画相关
  late AnimationController _menuAnimationController;
  late Animation<double> _menuSlideAnimation;
  late Animation<double> _menuFadeAnimation;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // 初始化菜单动画
    _menuAnimationController = AnimationController(
      duration: const Duration(milliseconds: 250),
      vsync: this,
    );
    _menuSlideAnimation = CurvedAnimation(
      parent: _menuAnimationController,
      curve: Curves.easeOutCubic,
    );
    _menuFadeAnimation = CurvedAnimation(
      parent: _menuAnimationController,
      curve: Curves.easeOut,
    );

    // 启动 UDP 发现监听
    _startUdpDiscovery();

    // 开始连接（可能在 UDP 发现后会被重新触发）
    _connect();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _textController.dispose();
    _scrollController.dispose();
    _menuAnimationController.dispose();
    _udpSubscription?.cancel();
    _udpSocket?.close();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // When app returns to foreground, cancel pending reconnect and try immediately
    if (state == AppLifecycleState.resumed) {
      _reconnectTimer?.cancel();
      if (_status != ConnectionStatus.connected) {
        _connect();
      }
    }
  }

  void _connect() {
    setState(() => _status = ConnectionStatus.connecting);

    // Close old connection if exists
    _channel?.sink.close();

    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://$_serverIp:$_serverPort'),
      );

      _channel!.stream.listen(
        (message) {
          _handleMessage(message);
        },
        onError: (error) {
          print('WebSocket error: $error');
          _handleDisconnect();
        },
        onDone: () {
          _handleDisconnect();
        },
      );
    } catch (e) {
      print('Connection error: $e');
      _handleDisconnect();
    }
  }

  void _handleMessage(dynamic message) {
    try {
      final data = json.decode(message);
      final type = data['type'];

      if (type == 'connected') {
        setState(() {
          _status = ConnectionStatus.connected;
          _syncEnabled = data['sync_enabled'] ?? true;
          _deviceName = data['computer_name'] ?? '';
        });
      } else if (type == 'ack') {
        _textController.clear();
      } else if (type == 'sync_state' || type == 'pong') {
        setState(() {
          _syncEnabled = data['sync_enabled'] ?? true;
        });
      }
    } catch (e) {
      print('Message parse error: $e');
    }
  }

  void _handleDisconnect() {
    setState(() {
      _status = ConnectionStatus.disconnected;
      _syncEnabled = true;
      _deviceName = '';
    });

    // Reconnect after 3 seconds
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      if (_status == ConnectionStatus.disconnected) {
        _connect();
      }
    });
  }

  /// 启动 UDP 发现监听
  /// 监听 PC 端的 UDP 广播，自动获取服务器 IP 和端口
  void _startUdpDiscovery() async {
    try {
      _udpSocket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, _udpBroadcastPort);
      _udpSocket!.broadcastEnabled = true;
      _udpSocket!.multicastLoopback = true;

      print('UDP 发现监听已启动，端口: $_udpBroadcastPort');

      _udpSubscription = _udpSocket!.listen((RawSocketEvent event) {
        if (event == RawSocketEvent.read) {
          final datagram = _udpSocket!.receive();
          if (datagram != null) {
            final message = utf8.decode(datagram.data);
            _handleUdpDiscovery(message, datagram.address.address);
          }
        }
      });
    } catch (e) {
      print('UDP 发现启动失败: $e');
      // 如果 UDP 启动失败，仍然可以使用默认 IP 连接
    }
  }

  /// 处理 UDP 发现消息
  void _handleUdpDiscovery(String message, String sourceIp) {
    try {
      final data = json.decode(message);
      if (data['type'] == 'voice_coding_server') {
        final discoveredIp = data['ip'] as String?;
        final discoveredPort = data['port'] as int?;

        if (discoveredIp != null && discoveredPort != null) {
          // 检查是否与当前配置不同
          if (_serverIp != discoveredIp || _serverPort != discoveredPort) {
            print('UDP 发现服务器: $discoveredIp:$discoveredPort (来源: $sourceIp)');
            setState(() {
              _serverIp = discoveredIp;
              _serverPort = discoveredPort;
            });

            // 如果当前未连接，立即尝试连接新发现的服务器
            if (_status != ConnectionStatus.connected) {
              _reconnectTimer?.cancel();
              _connect();
            }
          }
        }
      }
    } catch (e) {
      print('UDP 消息解析失败: $e');
    }
  }

  void _sendText() {
    final text = _textController.text.trim();
    if (text.isEmpty || _status != ConnectionStatus.connected || !_syncEnabled) {
      return;
    }

    try {
      _channel!.sink.add(json.encode({
        'type': 'text',
        'content': text,
      }));
      // 保存文本用于撤回（发送成功后再保存）
      _lastSentText = text;
    } catch (e) {
      // 发送失败，不保存文本
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 主界面
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _buildHeader(),
                  SizedBox(height: 13.5),
                  Expanded(
                    child: _buildInputArea(),
                  ),
                  const SizedBox(height: 16),
                  _buildEnterHint(),
                ],
              ),
            ),
          ),
          // 下拉菜单（最顶层）
          if (_showMenu) _buildDropdownMenuOverlay(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    // 连接状态
    Color connectionDotColor;
    String connectionText;
    final bool showSyncWarning = _status == ConnectionStatus.connected && !_syncEnabled;

    if (_status == ConnectionStatus.connected) {
      connectionDotColor = showSyncWarning ? const Color(0xFFE5A84B) : const Color(0xFF5CB87A);
      connectionText = showSyncWarning ? '同步关闭' : '已连接';
    } else {
      connectionDotColor = const Color(0xFFE85C4A);
      connectionText = '未连接';
    }

    return Row(
      children: [
        // 左侧：连接状态
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF3D3B37),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                _buildStatusDot(connectionDotColor),
                const SizedBox(width: 8),
                Text(
                  connectionText,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: connectionDotColor,
                  ),
                ),
              ],
            ),
          ),
        ),
        SizedBox(width: 12.5),
        // 右侧：更多菜单按钮
        Expanded(
          child: _buildMenuButton(),
        ),
      ],
    );
  }

  void _refreshConnection() {
    // 关闭现有连接
    _reconnectTimer?.cancel();
    _channel?.sink.close();

    // 重新连接
    _connect();
  }

  void _recallLastText() {
    // 从本地恢复上次发送的文本
    if (_lastSentText.isNotEmpty) {
      _textController.text = _lastSentText;
      // 移动光标到末尾
      _textController.selection = TextSelection.fromPosition(
        TextPosition(offset: _lastSentText.length),
      );
    }
  }

  Widget _buildMenuButton() {
    return GestureDetector(
      key: _menuButtonKey,
      onTap: () {
        if (_showMenu) {
          // 关闭菜单
          _menuAnimationController.reverse().then((_) {
            setState(() => _showMenu = false);
          });
        } else {
          // 打开菜单
          setState(() => _showMenu = true);
          _menuAnimationController.forward();
        }
      },
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF3D3B37),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            // 箭头图标（带旋转动画）
            AnimatedBuilder(
              animation: _menuAnimationController,
              builder: (context, child) {
                return Transform.rotate(
                  angle: _menuAnimationController.value * 1.5708,  // 90度 = π/2 ≈ 1.5708
                  child: const Icon(
                    Icons.chevron_right,
                    color: Colors.white,
                    size: 18,
                  ),
                );
              },
            ),
            const SizedBox(width: 8),
            const Text(
              '更多功能操作',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDropdownMenuOverlay() {
    // 获取按钮位置和大小
    final RenderBox? renderBox =
        _menuButtonKey.currentContext?.findRenderObject() as RenderBox?;
    if (renderBox == null) return const SizedBox.shrink();

    final Offset offset = renderBox.localToGlobal(Offset.zero);
    final Size size = renderBox.size;

    return FadeTransition(
      opacity: _menuFadeAnimation,
      child: GestureDetector(
        onTap: () {
          _menuAnimationController.reverse().then((_) {
            setState(() => _showMenu = false);
          });
        },
        behavior: HitTestBehavior.translucent,
        child: Container(
          color: Colors.black.withOpacity(0.3 * _menuFadeAnimation.value),  // 半透明遮罩
          child: Stack(
            children: [
              // 下拉菜单
              Positioned(
                left: offset.dx,
                top: offset.dy + size.height + 10,  // 按钮下方 + 间距
                width: size.width,
                child: AnimatedBuilder(
                  animation: _menuSlideAnimation,
                  builder: (context, child) {
                    return Transform.translate(
                      offset: Offset(0, -20 * (1 - _menuSlideAnimation.value)),  // 从上往下滑入
                      child: Opacity(
                        opacity: _menuSlideAnimation.value,
                        child: child,
                      ),
                    );
                  },
                  child: Material(
                    color: Colors.transparent,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 刷新连接
                        _buildMenuItem(
                          icon: Icons.refresh,
                          text: '刷新连接',
                          onTap: () {
                            _menuAnimationController.reverse().then((_) {
                              setState(() => _showMenu = false);
                            });
                            _refreshConnection();
                          },
                        ),
                        // 间距
                        const SizedBox(height: 10),
                        // 撤回上次输入
                        _buildMenuItem(
                          icon: Icons.undo,
                          text: '撤回上次输入',
                          onTap: () {
                            _menuAnimationController.reverse().then((_) {
                              setState(() => _showMenu = false);
                            });
                            _recallLastText();
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String text,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF3D3B37),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(icon, color: Colors.white, size: 18),
            const SizedBox(width: 8),
            Text(
              text,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusDot(Color color) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: 10,
      height: 10,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.5),
            blurRadius: 4,
            spreadRadius: 2,
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF3D3B37),
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(14),
      child: TextField(
        controller: _textController,
        maxLines: null,
        expands: true,
        decoration: const InputDecoration(
          hintText: '输入文字或使用语音...',
          border: InputBorder.none,
          enabledBorder: InputBorder.none,
          focusedBorder: InputBorder.none,
          filled: false,
          contentPadding: EdgeInsets.zero,
          isDense: true,
          hintStyle: TextStyle(color: Color(0xFF6B6B6B)),
        ),
        style: const TextStyle(
          fontSize: 16,
          color: Color(0xFFECECEC),
        ),
        cursorColor: const Color(0xFFD97757),
        textInputAction: TextInputAction.send,
        onSubmitted: (_) => _sendText(),
      ),
    );
  }

  Widget _buildEnterHint() {
    return Center(
      child: Text(
        '按回车键发送',
        style: TextStyle(
          fontSize: 13,
          color: Color(0xFF6B6B6B),
        ),
      ),
    );
  }
}

enum ConnectionStatus {
  disconnected,
  connecting,
  connected,
}

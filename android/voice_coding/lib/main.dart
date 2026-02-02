import 'dart:async';
import 'dart:convert';
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

class _MainPageState extends State<MainPage> with WidgetsBindingObserver {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  WebSocketChannel? _channel;
  ConnectionStatus _status = ConnectionStatus.disconnected;
  String _deviceName = '';
  bool _syncEnabled = true;
  Timer? _reconnectTimer;
  String _serverIp = '192.168.137.1';
  final int _serverPort = 9527;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _connect();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _textController.dispose();
    _scrollController.dispose();
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
    } catch (e) {
      // Silently fail
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              _buildHeader(),
              const SizedBox(height: 16),
              Expanded(
                child: _buildInputArea(),
              ),
              const SizedBox(height: 16),
              _buildEnterHint(),
            ],
          ),
        ),
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
        const SizedBox(width: 12),
        // 右侧：刷新按钮
        Expanded(
          child: GestureDetector(
            onTap: _refreshConnection,
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF3D3B37),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.refresh,
                    color: Colors.white,
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '刷新连接',
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
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

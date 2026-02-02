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

class _MainPageState extends State<MainPage> {
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
    _connect();
  }

  @override
  void dispose() {
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _connect() {
    setState(() => _status = ConnectionStatus.connecting);

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
        _showToast('✓ 已发送');
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
    if (text.isEmpty) {
      _showToast('请输入内容');
      return;
    }
    if (_status != ConnectionStatus.connected) {
      _showToast('未连接到电脑');
      return;
    }
    if (!_syncEnabled) {
      _showToast('电脑端同步已关闭');
      return;
    }

    try {
      _channel!.sink.add(json.encode({
        'type': 'text',
        'content': text,
      }));
    } catch (e) {
      _showToast('发送出错');
    }
  }

  void _showToast(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: const Color(0xFF3D3B37),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(milliseconds: 1500),
      ),
    );
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
              _buildStatusCard(),
              const SizedBox(height: 16),
              _buildSyncAlert(),
              const SizedBox(height: 16),
              Expanded(
                child: _buildInputArea(),
              ),
              const SizedBox(height: 16),
              _buildButtons(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFFD97757),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Center(
            child: Text(
              'V',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w800,
                fontSize: 18,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Voice Coding',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFFECECEC),
                ),
              ),
              Text(
                '语音输入助手',
                style: TextStyle(
                  fontSize: 12,
                  color: Color(0xFF6B6B6B),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatusCard() {
    Color dotColor;
    String statusText;

    switch (_status) {
      case ConnectionStatus.connected:
        dotColor = const Color(0xFF5CB87A);
        statusText = _syncEnabled ? '已连接' : '已连接 · 同步关闭';
        break;
      case ConnectionStatus.connecting:
        dotColor = const Color(0xFFE5A84B);
        statusText = '正在连接...';
        break;
      default:
        dotColor = const Color(0xFFE85C4A);
        statusText = '未连接';
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF3D3B37),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          _buildStatusDot(dotColor),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: dotColor,
                  ),
                ),
                if (_deviceName.isNotEmpty)
                  Text(
                    '设备: $_deviceName',
                    style: const TextStyle(
                      fontSize: 12,
                      color: Color(0xFF6B6B6B),
                    ),
                  ),
              ],
            ),
          ),
        ],
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

  Widget _buildSyncAlert() {
    if (_status == ConnectionStatus.connected && !_syncEnabled) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFE85C4A).withOpacity(0.15),
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Center(
          child: Text(
            '⚠️ 电脑端同步已关闭，无法发送',
            style: TextStyle(
              fontSize: 13,
              color: Color(0xFFE85C4A),
            ),
          ),
        ),
      );
    }
    return const SizedBox.shrink();
  }

  Widget _buildInputArea() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF2D2B28),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF4A4844)),
      ),
      padding: const EdgeInsets.all(14),
      child: TextField(
        controller: _textController,
        maxLines: null,
        expands: true,
        decoration: const InputDecoration(
          hintText: '输入文字或使用语音...',
          border: InputBorder.none,
          hintStyle: TextStyle(color: Color(0xFF6B6B6B)),
        ),
        style: const TextStyle(
          fontSize: 16,
          color: Color(0xFFECECEC),
        ),
        textInputAction: TextInputAction.send,
        onSubmitted: (_) => _sendText(),
      ),
    );
  }

  Widget _buildButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          height: 48,
          child: FilledButton(
            onPressed: _status == ConnectionStatus.connected && _syncEnabled
                ? _sendText
                : null,
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFFD97757),
              disabledBackgroundColor: const Color(0xFF5C4A42),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: const Text(
              '发送到电脑',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          height: 44,
          child: OutlinedButton(
            onPressed: () {
              _textController.clear();
            },
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFFECECEC),
              side: const BorderSide(color: Color(0xFF4A4844)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: const Text('清空'),
          ),
        ),
      ],
    );
  }
}

enum ConnectionStatus {
  disconnected,
  connecting,
  connected,
}

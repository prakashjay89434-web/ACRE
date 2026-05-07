import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(const ACREApp());
}

class ACREApp extends StatelessWidget {
  const ACREApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ACRE - AI Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00D4FF),
          surface: Color(0xFF1A1A2E),
        ),
        scaffoldBackgroundColor: const Color(0xFF1A1A2E),
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  WebSocketChannel? _channel;
  bool _isLoading = false;

  void _sendMessage() {
    final query = _controller.text.trim();
    if (query.isEmpty) return;

    setState(() {
      _messages.add({"role": "user", "text": query});
      _isLoading = true;
      _controller.clear();
    });

    _channel = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8000/stream'),
    );

    _channel!.sink.add(jsonEncode({"query": query}));

    String response = "";

    _channel!.stream.listen(
      (message) {
        final data = jsonDecode(message);
        setState(() {
          if (data["type"] == "status") {
            response += "⚡ ${data['message']}\n";
          } else if (data["type"] == "plan") {
            response += "\n📋 Plan:\n";
            for (var step in data["steps"]) {
              response += "  • $step\n";
            }
          } else if (data["type"] == "code") {
            response += "\n💻 Output: ${data['output']}\n";
          } else if (data["type"] == "result") {
            response += "\n✅ Score: ${data['verification_score']}/100";
            _isLoading = false;
          }
          _updateLastBotMessage(response);
        });
      },
      onDone: () => setState(() => _isLoading = false),
      onError: (e) => setState(() {
        _isLoading = false;
        response += "\n❌ Error: $e";
        _updateLastBotMessage(response);
      }),
    );

    _messages.add({"role": "bot", "text": ""});
  }

  void _updateLastBotMessage(String text) {
    final lastBot = _messages.lastIndexWhere((m) => m["role"] == "bot");
    if (lastBot != -1) {
      _messages[lastBot]["text"] = text;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF16213E),
        title: const Row(
          children: [
            Text("🤖", style: TextStyle(fontSize: 24)),
            SizedBox(width: 10),
            Text("ACRE — AI Assistant",
                style: TextStyle(color: Color(0xFF00D4FF))),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg["role"] == "user";
                return Align(
                  alignment: isUser
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.75,
                    ),
                    decoration: BoxDecoration(
                      color: isUser
                          ? const Color(0xFF00D4FF)
                          : const Color(0xFF16213E),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      msg["text"],
                      style: TextStyle(
                        color: isUser ? Colors.black : Colors.white,
                        fontSize: 14,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8),
              child: CircularProgressIndicator(color: Color(0xFF00D4FF)),
            ),
          Container(
            padding: const EdgeInsets.all(12),
            color: const Color(0xFF16213E),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: "Ask a math or code question...",
                      hintStyle: const TextStyle(color: Colors.grey),
                      filled: true,
                      fillColor: const Color(0xFF0F3460),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(25),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 12),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton(
                  onPressed: _sendMessage,
                  backgroundColor: const Color(0xFF00D4FF),
                  child: const Icon(Icons.send, color: Colors.black),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _channel?.sink.close();
    _controller.dispose();
    super.dispose();
  }
}
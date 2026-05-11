import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
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
      home: const MainScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const ChatScreen(),
    const HistoryScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          Container(
            width: 220,
            color: const Color(0xFF0F3460),
            child: Column(
              children: [
                const SizedBox(height: 40),
                const Text("🤖 ACRE",
                    style: TextStyle(
                        color: Color(0xFF00D4FF),
                        fontSize: 22,
                        fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                const Text("AI Assistant",
                    style: TextStyle(color: Colors.grey, fontSize: 12)),
                const SizedBox(height: 30),
                _sidebarItem(Icons.chat, "Chat", 0),
                _sidebarItem(Icons.history, "History", 1),
                _sidebarItem(Icons.settings, "Settings", 2),
                const Spacer(),
                Container(
                  margin: const EdgeInsets.all(12),
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF16213E),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.circle, color: Colors.green, size: 10),
                      SizedBox(width: 8),
                      Text("Backend Connected",
                          style: TextStyle(color: Colors.grey, fontSize: 11)),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
          Expanded(child: _screens[_selectedIndex]),
        ],
      ),
    );
  }

  Widget _sidebarItem(IconData icon, String label, int index) {
    final isSelected = _selectedIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedIndex = index),
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF00D4FF).withOpacity(0.2)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: isSelected
              ? Border.all(color: const Color(0xFF00D4FF), width: 1)
              : null,
        ),
        child: Row(
          children: [
            Icon(icon,
                color: isSelected ? const Color(0xFF00D4FF) : Colors.grey,
                size: 20),
            const SizedBox(width: 12),
            Text(label,
                style: TextStyle(
                    color: isSelected ? const Color(0xFF00D4FF) : Colors.grey)),
          ],
        ),
      ),
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
  final ScrollController _scrollController = ScrollController();
  final List<Map<String, dynamic>> _messages = [];
  WebSocketChannel? _channel;
  bool _isLoading = false;

  // Voice
  final SpeechToText _speech = SpeechToText();
  final FlutterTts _tts = FlutterTts();
  bool _isListening = false;
  bool _speechAvailable = false;

  @override
  void initState() {
    super.initState();
    _initSpeech();
    _initTts();
  }

  Future<void> _initSpeech() async {
    _speechAvailable = await _speech.initialize();
    setState(() {});
  }

  Future<void> _initTts() async {
    await _tts.setLanguage("en-US");
    await _tts.setSpeechRate(0.5);
    await _tts.setVolume(1.0);
  }

  Future<void> _startListening() async {
    if (!_speechAvailable) return;
    await _speech.listen(
      onResult: (result) {
        setState(() {
          _controller.text = result.recognizedWords;
        });
      },
    );
    setState(() => _isListening = true);
  }

  Future<void> _stopListening() async {
    await _speech.stop();
    setState(() => _isListening = false);
  }

  Future<void> _speak(String text) async {
    final clean = text
        .replaceAll(RegExp(r'[⚡📋💻✅🔍🧠]'), '')
        .replaceAll('•', '')
        .trim();
    await _tts.speak(clean);
  }

  void _sendMessage() {
    final query = _controller.text.trim();
    if (query.isEmpty || _isLoading) return;

    setState(() {
      _messages.add({"role": "user", "text": query});
      _isLoading = true;
      _controller.clear();
    });

    _scrollToBottom();

    _channel = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8000/stream'),
    );

    _channel!.sink.add(jsonEncode({"query": query}));
    String response = "";
    _messages.add({"role": "bot", "text": "..."});

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
            response += "\n💻 Answer:\n${data['output']}\n";
          } else if (data["type"] == "result") {
            if (data['verification_score'] > 0) {
              response += "\n✅ Verified: ${data['verification_score']}/100";
            }
            _isLoading = false;
            _speak(response);
          }
          _updateLastBotMessage(response);
        });
        _scrollToBottom();
      },
      onDone: () => setState(() => _isLoading = false),
      onError: (e) => setState(() {
        _isLoading = false;
        _updateLastBotMessage("❌ Connection error. Is backend running?");
      }),
    );
  }

  void _updateLastBotMessage(String text) {
    final lastBot = _messages.lastIndexWhere((m) => m["role"] == "bot");
    if (lastBot != -1) _messages[lastBot]["text"] = text;
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          color: const Color(0xFF16213E),
          child: const Row(
            children: [
              Icon(Icons.chat, color: Color(0xFF00D4FF)),
              SizedBox(width: 10),
              Text("Chat",
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold)),
              Spacer(),
              Text("Ask anything — math, code, or general questions",
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
            ],
          ),
        ),
        Expanded(
          child: _messages.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text("🤖", style: TextStyle(fontSize: 60)),
                      SizedBox(height: 16),
                      Text("Ask me anything!",
                          style:
                              TextStyle(color: Colors.grey, fontSize: 18)),
                      SizedBox(height: 8),
                      Text(
                          "Math • Code • General Knowledge • Web Search • Voice",
                          style:
                              TextStyle(color: Colors.grey, fontSize: 12)),
                    ],
                  ),
                )
              : ListView.builder(
                  controller: _scrollController,
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
                        margin: const EdgeInsets.symmetric(vertical: 6),
                        padding: const EdgeInsets.all(14),
                        constraints: BoxConstraints(
                          maxWidth:
                              MediaQuery.of(context).size.width * 0.65,
                        ),
                        decoration: BoxDecoration(
                          color: isUser
                              ? const Color(0xFF00D4FF)
                              : const Color(0xFF16213E),
                          borderRadius: BorderRadius.only(
                            topLeft: const Radius.circular(16),
                            topRight: const Radius.circular(16),
                            bottomLeft:
                                Radius.circular(isUser ? 16 : 4),
                            bottomRight:
                                Radius.circular(isUser ? 4 : 16),
                          ),
                        ),
                        child: Text(
                          msg["text"],
                          style: TextStyle(
                            color: isUser ? Colors.black : Colors.white,
                            fontSize: 14,
                            height: 1.5,
                          ),
                        ),
                      ),
                    );
                  },
                ),
        ),
        if (_isLoading)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Color(0xFF00D4FF))),
                SizedBox(width: 10),
                Text("ACRE is thinking...",
                    style: TextStyle(color: Colors.grey)),
              ],
            ),
          ),
        Container(
          padding: const EdgeInsets.all(12),
          color: const Color(0xFF16213E),
          child: Row(
            children: [
              // Mic button
              GestureDetector(
                onTapDown: (_) => _startListening(),
                onTapUp: (_) {
                  _stopListening();
                  if (_controller.text.isNotEmpty) _sendMessage();
                },
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: _isListening
                        ? Colors.red
                        : const Color(0xFF0F3460),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _isListening ? Icons.mic : Icons.mic_none,
                    color: _isListening ? Colors.white : Colors.grey,
                    size: 22,
                  ),
                ),
              ),
              Expanded(
                child: TextField(
                  controller: _controller,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: "Ask anything or hold mic to speak...",
                    hintStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: const Color(0xFF0F3460),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(25),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20, vertical: 14),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 8),
              FloatingActionButton(
                onPressed: _isLoading ? null : _sendMessage,
                backgroundColor:
                    _isLoading ? Colors.grey : const Color(0xFF00D4FF),
                child: Icon(
                    _isLoading ? Icons.hourglass_empty : Icons.send,
                    color: Colors.black),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _channel?.sink.close();
    _controller.dispose();
    _scrollController.dispose();
    _tts.stop();
    super.dispose();
  }
}

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> _history = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/history'),
      );
      final data = jsonDecode(response.body);
      setState(() {
        _history = data['history'].reversed.toList();
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          color: const Color(0xFF16213E),
          child: Row(
            children: [
              const Icon(Icons.history, color: Color(0xFF00D4FF)),
              const SizedBox(width: 10),
              const Text("Chat History",
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold)),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.refresh, color: Colors.grey),
                onPressed: () {
                  setState(() => _loading = true);
                  _loadHistory();
                },
              ),
            ],
          ),
        ),
        Expanded(
          child: _loading
              ? const Center(
                  child: CircularProgressIndicator(
                      color: Color(0xFF00D4FF)))
              : _history.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.history, size: 60, color: Colors.grey),
                          SizedBox(height: 16),
                          Text("No history yet",
                              style: TextStyle(
                                  color: Colors.grey, fontSize: 18)),
                          SizedBox(height: 8),
                          Text("Start chatting to see history here",
                              style: TextStyle(
                                  color: Colors.grey, fontSize: 12)),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: _history.length,
                      itemBuilder: (context, index) {
                        final item = _history[index];
                        return Container(
                          margin: const EdgeInsets.only(bottom: 10),
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0xFF16213E),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    item['type'] == 'technical'
                                        ? Icons.code
                                        : Icons.public,
                                    color: item['type'] == 'technical'
                                        ? Colors.orange
                                        : const Color(0xFF00D4FF),
                                    size: 16,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    item['type'] == 'technical'
                                        ? 'Technical'
                                        : 'General',
                                    style: TextStyle(
                                      color: item['type'] == 'technical'
                                          ? Colors.orange
                                          : const Color(0xFF00D4FF),
                                      fontSize: 11,
                                    ),
                                  ),
                                  const Spacer(),
                                  Text(
                                    item['timestamp'] ?? '',
                                    style: const TextStyle(
                                        color: Colors.grey, fontSize: 11),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                "Q: ${item['query']}",
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                "A: ${item['answer']?.toString().substring(0, item['answer'].toString().length.clamp(0, 150))}...",
                                style: const TextStyle(
                                    color: Colors.grey, fontSize: 12),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
        ),
      ],
    );
  }
}

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Settings",
              style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          _settingTile("🤖 Model", "qwen2.5-coder:1.5b"),
          _settingTile("🌐 Backend", "localhost:8000"),
          _settingTile("🧠 Memory", "Last 5 exchanges"),
          _settingTile("🔍 Search", "DuckDuckGo (local)"),
          _settingTile("📚 RAG", "Qdrant vector DB"),
          _settingTile("🔬 Verification", "sympy + numpy"),
          _settingTile("🎤 Voice", "Speech to Text + TTS"),
        ],
      ),
    );
  }

  Widget _settingTile(String label, String value) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF16213E),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: const TextStyle(color: Colors.white, fontSize: 14)),
          Text(value,
              style:
                  const TextStyle(color: Color(0xFF00D4FF), fontSize: 14)),
        ],
      ),
    );
  }
}
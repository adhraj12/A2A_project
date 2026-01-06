class ChatMessage {
  final String text;
  final bool isUser;
  final List<String> actions; // Log of AI tools used (Thinking process)

  ChatMessage({
    required this.text,
    required this.isUser,
    this.actions = const [],
  });
}

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Replace this with your ngrok URL for mobile, or http://10.0.2.2:8000 for Android Emulator
  // static const String BASE_URL = "https://your-ngrok-url.ngrok-free.app"; 
  static const String BASE_URL = "http://10.0.2.2:8000"; // Emulator default

  static Future<Map<String, dynamic>> sendMessage(String message) async {
    final prefs = await SharedPreferences.getInstance();
    
    final location = prefs.getString('location') ?? "411038";
    final contact = prefs.getString('contact') ?? "user@demo.com";
    
    try {
      final response = await http.post(
        Uri.parse('$BASE_URL/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'message': message,
          'user_location': location,
          'user_contact': contact,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load response: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}

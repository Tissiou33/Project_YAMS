import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Tokens stockés dans le keystore/keychain de l'appareil (jamais en clair).
class TokenStorage {
  static const _s = FlutterSecureStorage();
  static Future<void> save(String access, String refresh) async {
    await _s.write(key: 'access', value: access);
    await _s.write(key: 'refresh', value: refresh);
  }

  static Future<String?> get access => _s.read(key: 'access');
  static Future<String?> get refresh => _s.read(key: 'refresh');
  static Future<void> clear() => _s.deleteAll();
}

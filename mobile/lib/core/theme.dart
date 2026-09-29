import 'package:flutter/material.dart';

class AppTheme {
  static const _seed = Color(0xFF7A4B1E); // brun igname
  static final light = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: _seed),
    inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder()),
  );
}

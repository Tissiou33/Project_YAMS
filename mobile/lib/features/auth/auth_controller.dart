import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/storage.dart';

class AuthState {
  final String? role;
  final String? phone;
  final bool loading;
  final String? error;
  const AuthState({this.role, this.phone, this.loading = false, this.error});

  AuthState copyWith({String? role, String? phone, bool? loading, String? error}) =>
      AuthState(
        role: role ?? this.role,
        phone: phone ?? this.phone,
        loading: loading ?? this.loading,
        error: error,
      );
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._dio) : super(const AuthState());
  final Dio _dio;
  String _pendingRole = 'client';

  Future<bool> requestOtp(String phone, String role) async {
    state = state.copyWith(loading: true, phone: phone);
    _pendingRole = role;
    try {
      await _dio.post('/auth/otp/request', data: {'phone': phone});
      state = state.copyWith(loading: false);
      return true;
    } on DioException catch (e) {
      state = state.copyWith(loading: false, error: _msg(e));
      return false;
    }
  }

  Future<void> verifyOtp(String code) async {
    state = state.copyWith(loading: true);
    try {
      final r = await _dio.post('/auth/otp/verify',
          data: {'phone': state.phone, 'code': code, 'role': _pendingRole});
      await TokenStorage.save(r.data['access_token'], r.data['refresh_token']);
      state = state.copyWith(loading: false, role: _roleFromJwt(r.data['access_token']));
    } on DioException catch (e) {
      state = state.copyWith(loading: false, error: _msg(e));
    }
  }

  Future<void> logout() async {
    await TokenStorage.clear();
    state = const AuthState();
  }

  String _roleFromJwt(String jwt) {
    final payload = jwt.split('.')[1];
    final json = utf8.decode(base64Url.decode(base64Url.normalize(payload)));
    return (jsonDecode(json) as Map<String, dynamic>)['role'] as String;
  }

  String _msg(DioException e) => e.response?.data is Map
      ? (e.response!.data['detail']?.toString() ?? 'Erreur')
      : 'Connexion impossible';
}

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>(
    (ref) => AuthController(ref.watch(dioProvider)));

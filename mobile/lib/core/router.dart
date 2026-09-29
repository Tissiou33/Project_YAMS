import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/auth_controller.dart';
import '../features/auth/login_page.dart';
import '../features/auth/otp_page.dart';
import '../features/carrier/carrier_home_page.dart';
import '../features/client/client_home_page.dart';
import '../features/seller/seller_home_page.dart';

/// Une seule base de code, parcours différenciés selon le rôle (cahier des charges §5.1).
final routerProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authControllerProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final loggedIn = auth.role != null;
      final onAuth = state.matchedLocation == '/login' || state.matchedLocation == '/otp';
      if (!loggedIn) return onAuth ? null : '/login';
      if (onAuth) {
        switch (auth.role) {
          case 'seller':
            return '/seller';
          case 'carrier':
            return '/carrier';
          default:
            return '/client';
        }
      }
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginPage()),
      GoRoute(path: '/otp', builder: (_, __) => const OtpPage()),
      GoRoute(path: '/client', builder: (_, __) => const ClientHomePage()),
      GoRoute(path: '/seller', builder: (_, __) => const SellerHomePage()),
      GoRoute(path: '/carrier', builder: (_, __) => const CarrierHomePage()),
    ],
  );
});

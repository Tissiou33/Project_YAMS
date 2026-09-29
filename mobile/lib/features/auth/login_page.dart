import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'auth_controller.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});
  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _phone = TextEditingController(text: '+228');
  String _role = 'client';

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Igname Express')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          const Text('Connexion par numéro de téléphone', style: TextStyle(fontSize: 18)),
          const SizedBox(height: 16),
          TextField(
            controller: _phone,
            keyboardType: TextInputType.phone,
            decoration: const InputDecoration(labelText: 'Numéro (+228…)'),
          ),
          const SizedBox(height: 16),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'client', label: Text('Client')),
              ButtonSegment(value: 'seller', label: Text('Vendeur')),
              ButtonSegment(value: 'carrier', label: Text('Livreur')),
            ],
            selected: {_role},
            onSelectionChanged: (s) => setState(() => _role = s.first),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: auth.loading
                ? null
                : () async {
                    final ok = await ref
                        .read(authControllerProvider.notifier)
                        .requestOtp(_phone.text.trim(), _role);
                    if (ok && context.mounted) context.go('/otp');
                  },
            child: Text(auth.loading ? '…' : 'Recevoir le code SMS'),
          ),
          if (auth.error != null)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(auth.error!, style: const TextStyle(color: Colors.red)),
            ),
        ]),
      ),
    );
  }
}

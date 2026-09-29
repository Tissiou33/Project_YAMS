import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'auth_controller.dart';

class OtpPage extends ConsumerStatefulWidget {
  const OtpPage({super.key});
  @override
  ConsumerState<OtpPage> createState() => _OtpPageState();
}

class _OtpPageState extends ConsumerState<OtpPage> {
  final _code = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Vérification')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Text('Code envoyé au ${auth.phone ?? ''}'),
          const SizedBox(height: 16),
          TextField(
            controller: _code,
            keyboardType: TextInputType.number,
            maxLength: 6,
            decoration: const InputDecoration(labelText: 'Code à 6 chiffres'),
          ),
          FilledButton(
            onPressed: auth.loading
                ? null
                : () => ref.read(authControllerProvider.notifier).verifyOtp(_code.text.trim()),
            child: const Text('Valider'),
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

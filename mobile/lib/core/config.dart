class AppConfig {
  // Émulateur Android -> 10.0.2.2 ; appareil réel -> IP de la machine ou domaine HTTPS
  static const apiBaseUrl =
      String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000/api/v1');
}

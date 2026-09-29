# Igname Express 🍠

Plateforme nationale de commande et de livraison d'ignames au Togo
(clients ↔ vendeurs ↔ sociétés de transport) — base de code issue du cahier des charges v1.0.

> Le plan de réalisation complet est dans **[`todo.md`](./todo.md)**.

## Structure

```
igname-express/
├── backend/   API FastAPI + PostgreSQL (+ tests)
├── mobile/    Application Flutter (Client / Vendeur / Transporteur)
├── admin/     Back-office React (Vite)
├── docs/      Architecture, rôles & permissions
├── infra/     (réservé : Nginx, CI/CD, IaC)
├── docker-compose.yml   PostGIS + Redis + API
└── todo.md
```

## Démarrage rapide

```bash
cp .env.example .env

# 1. Base + Redis + API
docker compose up --build
docker compose exec backend python seed.py                       # régions / préfectures / villes
docker compose exec backend python create_admin.py +22890000000  # premier admin
# Docs interactives : http://localhost:8000/docs

# 2. Back-office
cd admin && npm install && npm run dev        # http://localhost:5173

# 3. Mobile (Flutter installé)
cd mobile && flutter create . --platforms=android,ios   # génère android/ et ios/ (une seule fois)
flutter pub get && flutter run --dart-define=API_URL=http://10.0.2.2:8000/api/v1
```

En mode `DEBUG=true`, le code OTP est renvoyé dans la réponse de `/auth/otp/request` et affiché dans les logs
(aucun SMS n'est réellement envoyé tant que le fournisseur n'est pas branché).

## Tests

```bash
cd backend && pip install -r requirements.txt && pytest -q
```

## État

Squelette de départ : le code n'a pas encore été exécuté de bout en bout — voir la Phase 0 de `todo.md`
pour la première vérification.

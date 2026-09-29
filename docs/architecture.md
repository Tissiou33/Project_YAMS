# Architecture — Igname Express

```
 ┌────────────────────┐   ┌───────────────────┐
 │ App mobile Flutter │   │ Back-office React │
 │ Client/Vendeur/    │   │ (admin, 2FA)      │
 │ Transporteur       │   │                   │
 └─────────┬──────────┘   └─────────┬─────────┘
           │  HTTPS (TLS ≥ 1.2) + JWT
           ▼
 ┌──────────────────────────────────────────────┐
 │ API FastAPI  (/api/v1)                       │
 │ auth · geo · shops/products · orders ·       │
 │ deliveries · admin                           │
 └───┬───────────┬───────────┬──────────────┬───┘
     ▼           ▼           ▼              ▼
 PostgreSQL     Redis    Stockage objet   Services externes
 (+PostGIS)   (OTP, rate  (photos, KYC     (SMS/OTP, Mobile Money
              limit, file) chiffrés)        Flooz/T-Money, Maps, FCM)
```

## Structure du dépôt

| Dossier | Rôle |
|---|---|
| `backend/app/core` | config, DB, sécurité (JWT, hachage), dépendances RBAC |
| `backend/app/models` | modèle de données (géo, users, boutiques, commandes, livraisons, litiges, audit) |
| `backend/app/services` | logique métier pure : OTP, tarification, machine à états, audit |
| `backend/app/api/v1` | routes par domaine |
| `mobile/lib/features` | un dossier par rôle : `auth`, `client`, `seller`, `carrier` |
| `admin/src/pages` | pages du back-office |

## Choix structurants (issus du cahier des charges)

- **Montants en FCFA entiers** : pas de décimales, pas d'erreurs d'arrondi.
- **Codes à usage unique** (remise vendeur→livreur, livraison client→livreur) : stockés **hachés**, affichés une seule fois.
- **Découpage géographique en base** (région → préfecture → ville) : extension sans redéveloppement.
- **Paramètres métier** (commission, tarifs) dans `platform_settings`, modifiables depuis le back-office.
- **Aucune donnée de paiement** stockée : tout est délégué à la passerelle certifiée.
- **Journal d'audit** pour toute action sensible.

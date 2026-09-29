# TODO — Igname Express

Plan de réalisation dérivé du cahier des charges v1.0 (phases §10, sécurité §6, périmètre §2).

Légende : `[x]` déjà présent dans le squelette (code écrit, **pas encore exécuté de bout en bout**) · `[ ]` à faire · 🔒 exigence de sécurité · ❓ décision à prendre

---

## Phase 0 — Cadrage & vérification du socle *(3–4 semaines)*

### Vérifier le squelette
- [ ] `docker compose up --build` démarre db + redis + API sans erreur
- [ ] `pytest -q` passe (tests écrits, jamais lancés)
- [ ] `/docs` (Swagger) accessible, tables créées, `seed.py` et `create_admin.py` fonctionnent
- [ ] Générer `android/` et `ios/` (`flutter create .`), lancer l'app et faire un login OTP complet
- [ ] `npm install && npm run dev` pour le back-office, login admin OK

### Décisions à prendre
- [ ] ❓ Passerelle de paiement Mobile Money (CinetPay, PayGate ou API directes Flooz / T-Money)
- [ ] ❓ Fournisseur SMS/OTP (Africa's Talking ou agrégateur local)
- [ ] ❓ Cartographie : Google Maps Platform ou OpenStreetMap
- [ ] ❓ Hébergement : cloud régional ou datacenter local (localisation des données à évaluer, loi n°2019-014)
- [ ] ❓ Taux de commission initial (fourchette du CDC : 5 % – 10 %) et grille tarifaire de livraison
- [ ] ❓ Nom définitif (« Igname Express » = nom de travail)
- [ ] Wireframes des parcours principaux (client, vendeur, transporteur, admin)
- [ ] Devis prestataires / choix de l'équipe, contractualisation
- [ ] Rédiger CGU/CGV et politique de confidentialité (à faire relire juridiquement)

### Hygiène de projet
- [ ] Dépôt Git + stratégie de branches
- [ ] CI (lint + tests backend, `flutter analyze`, build admin)
- [ ] Alembic : initialiser les migrations (remplace `create_all`) — dossier `infra/` pour CI/CD
- [ ] Séparer les environnements dev / préprod / prod (🔒 accès et données distincts)

---

## Phase 1 — Conception UX/UI *(3–4 semaines)*
- [ ] Maquettes détaillées : parcours client (recherche → panier → paiement → suivi)
- [ ] Maquettes vendeur (boutique, annonces, stock, commandes, finances)
- [ ] Maquettes transporteur (courses, navigation, codes, gains)
- [ ] Maquettes back-office (comptes, litiges, stats, paramètres)
- [ ] Design system (couleurs, icônes explicites, parcours de commande court)
- [ ] Tests d'ergonomie avec de vrais vendeuses/vendeurs et clients
- [ ] Contraintes : téléphones d'entrée de gamme, faible consommation de données, français (ewé/kabyè plus tard)

---

## Phase 2 — Développement du MVP *(10–14 semaines)*

### 2.1 Fondations backend
- [x] Structure FastAPI, config, connexion DB async, CORS
- [x] Modèles : régions/préfectures/villes, users, boutiques, produits, prix dégressifs, adresses, commandes, livraisons, litiges, avis, audit, paramètres
- [x] Health check `/health`
- [ ] Migrations Alembic + jeu de données géographiques complet (`seed.py` contient un extrait)
- [ ] Quartiers (niveau géographique sous la ville) si nécessaire
- [ ] Remplacer `lat/lng` par PostGIS (`Geography`) pour les recherches de proximité
- [ ] Gestion d'erreurs uniforme, logs structurés

### 2.2 Authentification & comptes (§3.1.1, §3.2.1, §6.1)
- [x] OTP SMS : demande / vérification, expiration, tentatives limitées, délai entre deux envois
- [x] JWT access + refresh, RBAC (`require_roles`, `require_active`)
- [x] Inscription : client actif d'emblée, vendeur/transporteur `pending`
- [ ] Stockage OTP dans Redis (actuellement en mémoire)
- [ ] Branchement réel du fournisseur SMS
- [ ] 🔒 Rate limiting Redis sur `/auth/otp/*`, connexion, paiement
- [ ] 🔒 Verrouillage temporaire après échecs (champs présents dans `User`, logique à écrire)
- [ ] 🔒 Révocation des tokens (perte de terminal)
- [ ] Complétion du profil (nom, sexe, date de naissance, photo, localisation)
- [ ] Upload KYC : pièce d'identité (CNI / carte d'électeur / passeport), RCCM optionnel → stockage objet chiffré
- [ ] Connexion Google/Apple (option client)
- [ ] Suppression de compte et de données à la demande (droit à l'effacement)

### 2.3 Module Vendeur (§3.1)
- [x] Création de boutique (+ zones de livraison), annonces (variété, unité, prix, stock, photos, prix dégressifs)
- [x] Mise à jour / retrait logique d'une annonce, isolation entre vendeurs
- [x] Accepter / refuser (avec motif) / préparer une commande, génération du code de remise
- [ ] Horaires et jours de disponibilité
- [ ] Alerte de stock faible (push)
- [ ] Proposition de modification d'une commande (quantité indisponible)
- [ ] Décrémenter le stock à l'acceptation / restituer à l'annulation
- [ ] Mise en avant payante d'une annonce (`featured_until` existe, paiement à brancher)
- [ ] Tableau de bord ventes (jour / semaine / mois), commissions, net à percevoir
- [ ] Demande de retrait vers Mobile Money / compte bancaire

### 2.4 Module Client (§3.2)
- [x] Recherche catalogue : variété, fourchette de prix, vendeurs vérifiés, pagination
- [x] Création de commande : calcul du sous-total (prix dégressifs), frais de livraison, commission, code de livraison, historique horodaté
- [x] Annulation tant que la commande est `pending`
- [ ] Recherche par localisation (proximité) et par zone de livraison desservie
- [ ] Filtre par note du vendeur
- [ ] Gestion des adresses (CRUD) et des moyens de paiement enregistrés
- [ ] Panier côté mobile, fiche produit, écrans de commande
- [ ] Avis / notation vendeur et livreur
- [ ] Ouverture de litige depuis une commande
- [ ] Support : chat intégré, FAQ, numéro d'assistance
- [ ] Mode hors-ligne partiel (cache du catalogue déjà chargé)

### 2.5 Module Transporteur (§3.3)
- [x] Modèle livraison, liste des courses disponibles, acceptation
- [x] Confirmation de prise en charge (code vendeur) et de livraison (code client), usage unique
- [x] Mise à jour de la position, déclaration d'incident
- [ ] Inscription société de transport (avec livreurs rattachés) vs livreur indépendant
- [ ] Vérification des documents : permis, carte grise, assurance, agrément/RCCM
- [ ] Filtrer les courses par zone couverte et proximité
- [ ] Affectation automatique au livreur le plus proche (validation semi-manuelle possible au début)
- [ ] Calcul et enregistrement de `distance_km` / `fee_fcfa` à la création de la course
- [ ] Navigation guidée (enlèvement puis livraison)
- [ ] Tableau de bord gains + demandes de règlement

### 2.6 Paiement (§5.3, §6.5)
- [ ] 🔒 Intégration passerelle Mobile Money (Flooz / T-Money) — aucune donnée de paiement stockée chez nous
- [ ] Carte bancaire (option, passerelle PCI-DSS)
- [ ] Paiement à la livraison (selon zone et niveau de risque)
- [ ] Webhooks de confirmation + idempotence
- [ ] Libération des fonds / reversements vendeurs et transporteurs à la livraison confirmée

### 2.7 Livraison & suivi (§8)
- [x] Machine à états des commandes + tests
- [ ] Différencier livraison locale / longue distance inter-régions
- [ ] Suivi temps réel de la position (WebSocket ou SSE) + ETA, carte côté client
- [ ] Procédures : client absent, produit endommagé/non conforme, zone non couverte (message clair avant commande)

### 2.8 Notifications
- [ ] Push (Firebase Cloud Messaging) à chaque changement d'étape
- [ ] SMS pour événements critiques (nouvelle commande, livraison)
- [ ] E-mail (reçus, rapports)

### 2.9 Back-office admin (§3.4)
- [x] Squelette React : login, tableau de bord, comptes en attente, litiges, paramètres
- [x] API : approuver / rejeter / suspendre-radier un compte, litiges ouverts, stats, paramètres
- [ ] Création du premier admin ✔ (`create_admin.py`) — puis gestion des admins
- [ ] Visualisation des pièces KYC avant décision
- [ ] Modération des annonces (contenu, photos, prix anormaux)
- [ ] Arbitrage des litiges : historique horodaté, remboursement total/partiel, sanction
- [ ] Faire lire `commission_rate`, tarifs et zones depuis `platform_settings` (aujourd'hui lus depuis `.env`)
- [ ] Statistiques : taux de livraison réussie, délai moyen par région, cartographie d'activité
- [ ] Gestion financière : flux, reversements, validation des retraits, exports comptables/fiscaux
- [ ] Gestion du découpage géographique et activation progressive des régions

### 2.10 Application mobile
- [x] Projet Flutter, thème, client HTTP (Dio), stockage sécurisé des tokens, routage par rôle, login OTP
- [ ] Écrans Client, Vendeur, Transporteur (pour l'instant : pages d'accueil vides)
- [ ] Rafraîchissement automatique du token sur 401
- [ ] Optimisation des images et des flux de données (réseau 3G)
- [ ] Internationalisation (`intl`) — français d'abord
- [ ] Tests widgets / intégration

---

## Phase 3 — Sécurisation & tests *(3–4 semaines)*
- [ ] 🔒 TLS ≥ 1.2 partout, aucune communication en clair
- [ ] 🔒 Chiffrement au repos des données sensibles (pièces d'identité, coordonnées précises)
- [ ] 🔒 Validation stricte des entrées (injections SQL, XSS) — revue systématique des schémas
- [ ] 🔒 2FA : obligatoire pour les admins, recommandée pour les vendeurs
- [ ] 🔒 Journal d'audit complet (`audit_logs` alimenté sur les actions clés — à étendre aux paiements et modifications de compte)
- [ ] 🔒 Détection de fraude : comptes multiples par appareil, schémas de commandes anormaux, notes suspectes
- [ ] 🔒 Plafonds / vérification manuelle des montants inhabituels
- [ ] 🔒 WAF, en-têtes de sécurité, restriction réseau du back-office
- [ ] Rapprochement quotidien des transactions avec les prestataires de paiement
- [ ] Anonymisation / pseudonymisation des données statistiques
- [ ] Tests fonctionnels bout en bout (parcours complet commande → livraison → paiement)
- [ ] Tests de charge (objectif : réponse < 2 s même en 3G)
- [ ] Audit de code + **test d'intrusion** avant lancement
- [ ] Sauvegardes automatiques + test de restauration, PRA documenté
- [ ] Supervision et alertes (disponibilité cible 99,5 %)
- [ ] Suivi des vulnérabilités des dépendances (CVE)

## Phase 4 — Pilote régional *(6–8 semaines)*
- [ ] Périmètre : Kara + Lomé, nombre limité de vendeurs et transporteurs
- [ ] Signer les premiers accords de partenariat transport (tarifs, zones, qualité de service)
- [ ] Onboarder et former les vendeurs pilotes (KYC assisté)
- [ ] Publier les apps (Play Store / App Store)
- [ ] Support opérationnel, suivi quotidien des incidents
- [ ] Collecter les retours, ajuster commission et frais de livraison

## Phase 5 — Déploiement national *(en continu)*
- [ ] Activer progressivement Plateaux, Centrale, Maritime, Savanes
- [ ] Montée en charge de l'infrastructure (découplage des services)
- [ ] Version 1.1 : séquestre (escrow) des fonds, 2FA élargie
- [ ] Abonnement « vendeur premium » (stats avancées, badge, support prioritaire)
- [ ] Langues locales (éwé, kabyè)
- [ ] Pentests annuels

---

## Livrables (§9) — suivi
- [ ] Application mobile Client
- [ ] Espace / application Vendeur
- [ ] Application Transporteur
- [ ] Back-office Administrateur
- [x] API backend (squelette) + documentation OpenAPI automatique
- [ ] Documentation technique (architecture ✔ amorcée dans `docs/`, schéma BDD, guide de déploiement, guide de sécurité)
- [ ] Guides utilisateurs par profil
- [ ] CGU/CGV et politique de confidentialité

## Hors périmètre phase 1 (rappel §2.4)
Autres produits agricoles · flotte de véhicules en propre · export international

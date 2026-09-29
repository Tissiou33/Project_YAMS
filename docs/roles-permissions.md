# Rôles et permissions (RBAC)

| Action | Client | Vendeur | Transporteur | Admin |
|---|:-:|:-:|:-:|:-:|
| Consulter le catalogue | ✅ | ✅ | ✅ | ✅ |
| Passer / annuler (avant acceptation) une commande | ✅ | – | – | – |
| Créer boutique / annonces | – | ✅ (compte validé) | – | – |
| Accepter / refuser / préparer une commande | – | ✅ (les siennes) | – | – |
| Voir / accepter des courses, confirmer remise & livraison | – | – | ✅ (compte validé) | – |
| Valider / rejeter / suspendre des comptes | – | – | – | ✅ |
| Litiges, statistiques, paramètres | – | – | – | ✅ |

Règles : un vendeur n'accède jamais aux données d'un autre vendeur ; un client ne voit que ses commandes ;
vendeurs et transporteurs restent `pending` tant que l'admin n'a pas validé le KYC.

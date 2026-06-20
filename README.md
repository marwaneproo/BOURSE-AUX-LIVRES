<div align="center">

#  Bourse aux Livres — EMSI

### Plateforme web d'échange de livres académiques entre étudiants

*Vente · Don · Échange · Mise en relation directe entre étudiants*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-0C4B33?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.15-ff1709?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Channels](https://img.shields.io/badge/Django%20Channels-4.x-44B78B?style=flat-square)](https://channels.readthedocs.io/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/Licence-Académique-lightgrey?style=flat-square)]()

**Projet de Fin d'Année (PFA) — 3ᵉ année Ingénierie Informatique et Réseaux**
**EMSI — École Marocaine des Sciences de l'Ingénieur · Année universitaire 2025/2026**

</div>

<br>

---

## 
Table des matières

1. [Présentation du projet](#-1-présentation-du-projet)
2. [Problématique & objectifs](#-2-problématique--objectifs)
3. [Aperçu fonctionnel](#-3-aperçu-fonctionnel)
4. [Stack technique](#-4-stack-technique)
5. [Architecture du projet](#-5-architecture-du-projet)
6. [Structure des dossiers](#-6-structure-des-dossiers)
7. [Modèle de données](#-7-modèle-de-données)
8. [API REST — Endpoints](#-8-api-rest--endpoints)
9. [Authentification & sécurité](#-9-authentification--sécurité)
10. [Temps réel — WebSocket & notifications](#-10-temps-réel--websocket--notifications)
11. [Installation & démarrage](#-11-installation--démarrage)
12. [Variables d'environnement](#-12-variables-denvironnement)
13. [Tests](#-13-tests)
14. [Captures d'écran](#-14-captures-décran)
15. [Limites connues](#-15-limites-connues)
16. [Roadmap & perspectives](#-16-roadmap--perspectives)
17. [Équipe & encadrement](#-17-équipe--encadrement)
18. [Licence](#-18-licence)

<br>

---

##  1. Présentation du projet

**Bourse aux Livres EMSI** est une plateforme web full-stack permettant aux étudiants de l'EMSI d'**acheter**, **vendre**, **donner** ou **échanger** leurs livres et manuels académiques entre eux, sans intermédiaire commercial.

Le projet a été conçu et développé comme une véritable marketplace : catalogue filtrable, système de commandes avec cycle de vie complet, messagerie intégrée, notifications en temps réel, système d'évaluation des vendeurs, modération de contenu et panel d'administration complet.

> Plutôt qu'une simple liste d'annonces, l'objectif a été de reproduire l'architecture et la rigueur d'une marketplace e-commerce réelle, à l'échelle d'un campus universitaire.

<br>

##  2. Problématique & objectifs

### Le problème

| Constat | Conséquence |
|---|---|
| Manuels académiques coûteux, utilisés en moyenne **un seul semestre** | Dépense répétée chaque année pour chaque étudiant |
| Aucune plateforme centralisée dédiée à l'EMSI | Échanges informels, dispersés (groupes WhatsApp, affichage papier) |
| Pas de structure pour les annonces existantes | Difficulté à trouver un livre précis, pas de filtres, pas de suivi |
| Aucune garantie de confiance entre étudiants | Pas de messagerie, pas d'évaluation, pas de modération |

### Les objectifs du projet

-  **Faciliter l'échange** de livres entre étudiants (vente, don, échange)
-  **Centraliser les annonces** sur une plateforme unique, propre à l'EMSI
-  **Simplifier l'accès aux ressources** via un catalogue filtrable (matière, niveau, prix, recherche)
-  **Sécuriser les échanges** grâce à l'authentification, la modération et les évaluations
-  **Démontrer une maîtrise d'ingénierie logicielle complète** : conception, base de données, API REST, temps réel, sécurité, administration

<br>

##  3. Aperçu fonctionnel

<table>
<tr>
<td width="33%" valign="top">

###  Espace étudiant
- Inscription / connexion sécurisée
- Profil personnalisable (photo, ville, téléphone)
- Rôles **acheteur** et **vendeur** simultanés
- Statistiques personnelles (note moyenne, historique)

</td>
<td width="33%" valign="top">

###  Gestion des livres
- Publication d'annonces avec photos multiples
- États : `Neuf` · `Bon` · `Usagé`
- Types : `Vente` · `Don` · `Échange`
- Catalogue avec filtres avancés et recherche
- Système de favoris

</td>
<td width="33%" valign="top">

###  Commandes & transactions
- Cycle de vie complet de la commande
- Acceptation / refus par le vendeur
- Suivi de livraison
- Confirmation de réception
- Évaluation du vendeur (1 à 5 étoiles)

</td>
</tr>
<tr>
<td width="33%" valign="top">

###  Communication
- Messagerie privée intégrée
- Infrastructure WebSocket (Django Channels)
- Indicateur de messages non lus
- Notifications en temps réel (polling)

</td>
<td width="33%" valign="top">

###  Modération & confiance
- Signalement d'annonces par les utilisateurs
- Traitement des signalements par l'admin
- Bannissement des comptes frauduleux
- Journal d'audit (Django `LogEntry`)

</td>
<td width="33%" valign="top">

###  Panel d'administration
- Tableau de bord avec statistiques visuelles
- Graphiques SVG (répartition des états des livres)
- Gestion des utilisateurs (ban / déban / suppression)
- Gestion centralisée des signalements

</td>
</tr>
</table>

<br>

##  4. Stack technique

<table>
<tr><th>Couche</th><th>Technologie</th><th>Rôle dans le projet</th></tr>
<tr>
<td rowspan="2"><b>Backend</b></td>
<td><code>Django 5.1</code></td>
<td>Framework principal — ORM, migrations, admin natif, sécurité</td>
</tr>
<tr>
<td><code>Django REST Framework</code></td>
<td>Construction de l'API REST (serializers, viewsets, permissions)</td>
</tr>
<tr>
<td rowspan="2"><b>Temps réel</b></td>
<td><code>Django Channels 4.x</code></td>
<td>Gestion des connexions WebSocket (protocole ASGI)</td>
</tr>
<tr>
<td><code>Daphne</code></td>
<td>Serveur ASGI de production, remplace le serveur WSGI classique</td>
</tr>
<tr>
<td><b>Authentification</b></td>
<td><code>djangorestframework-simplejwt</code></td>
<td>Authentification stateless par tokens JWT (access + refresh)</td>
</tr>
<tr>
<td><b>Base de données</b></td>
<td><code>SQLite</code></td>
<td>Base relationnelle embarquée, adaptée au développement académique</td>
</tr>
<tr>
<td><b>Médias</b></td>
<td><code>Pillow</code></td>
<td>Traitement et validation des images uploadées (photos de livres/profils)</td>
</tr>
<tr>
<td rowspan="3"><b>Frontend</b></td>
<td><code>HTML5</code></td>
<td>Structure sémantique des pages</td>
</tr>
<tr>
<td><code>CSS3</code></td>
<td>Style académique blanc / vert, design responsive</td>
</tr>
<tr>
<td><code>JavaScript Vanilla</code></td>
<td>Logique client, appels API via <code>fetch()</code>, gestion JWT</td>
</tr>
<tr>
<td><b>Environnement</b></td>
<td><code>Nix Flakes</code></td>
<td>Environnement de développement reproductible</td>
</tr>
</table>

<br>

##  5. Architecture du projet

L'application suit une **architecture trois tiers** classique, avec un backend organisé en **applications Django modulaires** indépendantes par domaine métier.

```
┌──────────────────────┐         ┌──────────────────────────┐           ┌───────────────────────┐
│       FRONTEND          │        │          BACKEND         │         │     BASE DE DONNÉES        │
│  HTML / CSS / JS        │ ───▶ │   Django REST Framework  │  ───▶    │         SQLite             │
│                         │       │                          │          │                            │
│ • Pages publiques       │      │ • 7 apps modulaires       │          │ • 11 tables relationnelles │
│ • Espace utilisateur    │      │ • API REST + WebSocket     │         │ • ORM Django               │
│ • fetch() + JWT         │◀──  │ • Authentification JWT    │  ◀───    │ • Migrations versionnées   │
└──────────────────────┘         └──────────────────────────┘            └───────────────────────┘
```

**Flux d'une requête type :**
`Utilisateur` → `Frontend (requête fetch)` → `API Django REST (ViewSet + Serializer)` → `Base de données (ORM)` → `Réponse JSON` → `Mise à jour de l'interface`

### Apps Django et responsabilités

| Application | Responsabilité |
|---|---|
| `core/` | Configuration centrale du projet (settings, URLs racine, ASGI/WSGI) |
| `apps/accounts` | Modèle `Profile`, inscription, connexion JWT, gestion du profil utilisateur |
| `apps/books` | Modèles `Livre`, `ImageLivre`, `Favori`, `Evaluation` — CRUD annonces, filtres, favoris |
| `apps/orders` | Modèles `Commande`, `Livraison` — cycle de vie complet de la transaction |
| `apps/messaging` | Modèle `Message`, API REST + `ChatConsumer` WebSocket (Django Channels) |
| `apps/notifications` | Modèle `Notification` — 9 types d'alertes, polling REST, marquage lu/non lu |
| `apps/moderation` | Modèle `Signalement`, panel d'administration, statistiques, audit |
| `apps/web` | Vues Django servant les templates HTML (aucune logique métier) |
| `marketplace/` | Module legacy conservé pour compatibilité des migrations historiques |

<br>

## 📁 6. Structure des dossiers

```
bourse-aux-livres/
│
├── core/                          # Configuration centrale Django
│   ├── settings.py                # Paramètres globaux (apps, middlewares, JWT, DB)
│   ├── urls.py                    # Routeur principal de l'application
│   ├── asgi.py                    # Point d'entrée ASGI (HTTP + WebSocket)
│   └── wsgi.py                    # Point d'entrée WSGI (déploiement classique)
│
├── apps/                          # Applications métier modulaires
│   ├── accounts/                  # Authentification & profils utilisateurs
│   │   ├── models.py              # Profile (OneToOne avec User)
│   │   ├── serializers.py         # UserSerializer, ProfileSerializer, JWT custom
│   │   ├── views.py               # Inscription, connexion, gestion du profil
│   │   └── migrations/
│   │
│   ├── books/                     # Cœur de la marketplace
│   │   ├── models.py              # Livre, ImageLivre, Favori, Evaluation
│   │   ├── serializers.py
│   │   ├── views.py               # CRUD annonces, filtres, favoris, évaluations
│   │   └── migrations/
│   │
│   ├── orders/                    # Commandes et livraisons
│   │   ├── models.py              # Commande, Livraison
│   │   ├── serializers.py
│   │   ├── views.py               # Cycle de vie : créer, accepter, refuser, livrer
│   │   └── migrations/
│   │
│   ├── messaging/                 # Messagerie temps réel
│   │   ├── models.py              # Message
│   │   ├── consumers.py           # ChatConsumer (WebSocket)
│   │   ├── routing.py             # Routes WebSocket
│   │   ├── views.py               # API REST de secours (polling)
│   │   └── migrations/
│   │
│   ├── notifications/             # Système d'alertes
│   │   ├── models.py              # Notification (9 types)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── migrations/
│   │
│   ├── moderation/                # Modération & administration
│   │   ├── models.py              # Signalement
│   │   ├── views.py               # Panel admin, stats, ban, audit
│   │   └── migrations/
│   │
│   └── web/                       # Frontend servi par Django
│       ├── views.py               # Vues de rendu des templates
│       ├── templates/web/         # Pages HTML (catalogue, profil, admin...)
│       └── static/web/
│           ├── css/               # Feuilles de style (thème blanc/vert)
│           ├── js/                # api.js, gestion JWT, logique des pages
│           └── images/            # Logo EMSI, visuels statiques
│
├── marketplace/                   # Module legacy (compatibilité migrations)
│   ├── management/commands/       # Commande create_admin
│   └── migrations/
│
├── media/                         # Fichiers uploadés par les utilisateurs
│   ├── livres/images/             # Photos des annonces
│   └── profiles/                  # Photos de profil
│
├── manage.py                      # Point d'entrée Django CLI
├── requirements.txt                # Dépendances Python
├── flake.nix / flake.lock         # Environnement de développement Nix
└── README.md                      # Ce fichier
```

<br>

## 🗄️ 7. Modèle de données

La base de données relationnelle est structurée autour de **11 tables principales**, reliées au modèle natif `User` de Django.

<table>
<tr><th>Table</th><th>Rôle</th><th>Relations clés</th></tr>
<tr><td><code>auth_user</code></td><td>Authentification native Django (identité, mot de passe hashé)</td><td>Référencée par tout le schéma</td></tr>
<tr><td><code>marketplace_profile</code></td><td>Extension du profil : photo, téléphone, ville, rôles, statut</td><td><code>OneToOne → User</code></td></tr>
<tr><td><code>marketplace_livre</code></td><td>Cœur de la marketplace : titre, matière, prix, état, statut</td><td><code>ForeignKey → User</code> (vendeur)</td></tr>
<tr><td><code>marketplace_imagelivre</code></td><td>Images associées à une annonce (plusieurs par livre)</td><td><code>ForeignKey → Livre</code></td></tr>
<tr><td><code>marketplace_commande</code></td><td>Transaction entre un acheteur et un livre</td><td><code>ForeignKey → Livre, User</code></td></tr>
<tr><td><code>marketplace_livraison</code></td><td>Détails logistiques d'une commande</td><td><code>OneToOne → Commande</code></td></tr>
<tr><td><code>marketplace_message</code></td><td>Message privé entre deux utilisateurs</td><td><code>ForeignKey → User</code> ×2</td></tr>
<tr><td><code>marketplace_notification</code></td><td>Alerte système ciblée pour un utilisateur</td><td><code>ForeignKey → User, Commande</code></td></tr>
<tr><td><code>marketplace_signalement</code></td><td>Rapport de contenu inapproprié</td><td><code>ForeignKey → Livre, User</code> ×3</td></tr>
<tr><td><code>marketplace_favori</code></td><td>Table de jointure utilisateur ↔ livre favori</td><td><code>unique_together</code></td></tr>
<tr><td><code>marketplace_evaluation</code></td><td>Note (1-5) laissée après une commande livrée</td><td><code>ForeignKey → Commande</code>, unique par commande</td></tr>
</table>

### Statuts et cycles de vie

```
Livre        : DISPONIBLE → VENDU → (ARCHIVEE si signalé/retiré)
Commande     : EN_ATTENTE → CONFIRMEE → EN_COURS_DE_LIVRAISON → LIVREE
                          ↘ REFUSEE (le livre redevient DISPONIBLE)
Signalement  : PENDING → ACCEPTED (livre archivé) / REJECTED (avec justification admin)
```

<br>

## 🔌 8. API REST — Endpoints

L'API suit les conventions REST avec des **ViewSets** Django REST Framework, exposés sous le préfixe `/api/`.

| Ressource | Endpoint principal | Description |
|---|---|---|
| Authentification | `POST /api/token/` | Connexion — émission du token JWT (access + refresh) |
| Inscription | `POST /api/register/` | Création d'un nouveau compte étudiant |
| Profil | `GET/PATCH /api/profile/` | Consultation et mise à jour du profil connecté |
| Livres | `GET/POST /api/livres/` | Liste filtrée du catalogue / publication d'une annonce |
| Livre (détail) | `GET/PUT/DELETE /api/livres/{id}/` | Détail, modification, suppression d'une annonce |
| Favoris | `POST /api/favoris/` | Ajout / retrait d'un livre en favori |
| Commandes | `GET/POST /api/commandes/` | Liste des commandes / création |
| Action commande | `POST /api/commandes/{id}/accepter/` | Transition d'état (accepter, refuser, livrer...) |
| Messagerie | `GET/POST /api/messages/` | Envoi et consultation des messages |
| Notifications | `GET /api/notifications/` | Liste des notifications de l'utilisateur connecté |
| Évaluations | `POST /api/evaluations/` | Notation d'un vendeur après livraison |
| Signalements | `GET/POST /api/signalements/` | Création et traitement des signalements (admin) |

> L'ensemble des endpoints protégés exige un en-tête `Authorization: Bearer <access_token>`.

<br>

## 🔐 9. Authentification & sécurité

- **Double mécanisme** : JWT (`SimpleJWT`) pour l'API REST, sessions Django classiques pour les vues serveur.
- **Tokens** : access token valable 1 jour, refresh token valable 7 jours.
- **Vérification du bannissement** effectuée à **deux niveaux** avant l'émission du token : dans la vue de connexion et dans le serializer JWT personnalisé — un compte banni ne peut jamais obtenir de token.
- **Permissions par rôle** : permission personnalisée `IsAdminProfile` pour réserver les actions sensibles aux administrateurs (`profile.est_administrateur` ou `user.is_staff`).
- **Contrôle de propriété** : un vendeur ne peut modifier ou supprimer que ses propres annonces (vérification explicite dans les vues, sinon `PermissionDenied`).
- **Protection CSRF** sur les requêtes non-GET côté frontend, token injecté automatiquement par `api.js`.
- **Contraintes d'intégrité en base** : `unique_together` pour empêcher les évaluations en double, `on_delete=PROTECT` pour empêcher la suppression d'un livre lié à une commande active.
- **Journal d'audit** : toutes les actions sensibles de modération sont historisées via le `LogEntry` natif de Django.

<br>

## ⚡ 10. Temps réel — WebSocket & notifications

| Composant | Détail |
|---|---|
| `ChatConsumer` | Consumer asynchrone Django Channels gérant les connexions WebSocket de messagerie |
| `Daphne` | Serveur ASGI assurant le support des protocoles HTTP et WebSocket simultanément |
| `InMemoryChannelLayer` | Couche de messages en mémoire utilisée en développement (à remplacer par Redis en production) |
| Notifications | Implémentées en **polling REST** côté frontend (intervalle de 10 secondes), bien que l'infrastructure WebSocket backend soit pleinement opérationnelle |

```
core/asgi.py
   └─ ProtocolTypeRouter
        ├─ http        → Django classique
        └─ websocket    → AuthMiddlewareStack → ChatConsumer
```

<br>

##  11. Installation & démarrage

### Prérequis

- Python ≥ 3.12
- pip ou environnement Nix (flake fourni)

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone <url-du-depot>
cd bourse-aux-livres

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un compte administrateur
python manage.py create_admin

# 6. Lancer le serveur de développement
python manage.py runserver
```

L'application est accessible sur **http://127.0.0.1:8000/**

### Avec Nix (environnement reproductible)

```bash
nix develop
python manage.py migrate
python manage.py runserver
```

<br>

## ⚙️ 12. Variables d'environnement

| Variable | Description | Valeur par défaut |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clé secrète Django (signature des sessions et tokens) | Clé de développement (à remplacer en production) |
| `DJANGO_DEBUG` | Active le mode debug | `True` en développement |
| `DJANGO_ALLOWED_HOSTS` | Hôtes autorisés à servir l'application | `localhost,127.0.0.1` |

> ⚠️ En production, `DJANGO_SECRET_KEY` doit impérativement être définie via une variable d'environnement et jamais committée dans le code source.

<br>

##  13. Tests

```bash
python manage.py test
```

Chaque application dispose de son fichier `tests.py` couvrant les scénarios de base (création de modèles, accès aux endpoints critiques, permissions).

<br>

## 🖼️ 14. Captures d'écran

> *Section à compléter avec les captures de l'interface : catalogue, fiche livre, messagerie, panel d'administration.*

| Page | Aperçu |
|---|---|
| Catalogue de livres | `assets/screenshot-catalogue.png` |
| Fiche détaillée d'un livre | `assets/screenshot-fiche-livre.png` |
| Messagerie | `assets/screenshot-messagerie.png` |
| Panel d'administration | `assets/screenshot-admin.png` |

<br>

## ⚠️ 15. Limites connues

- Les notifications utilisent du **polling REST** plutôt que les WebSockets pourtant disponibles côté backend.
- `InMemoryChannelLayer` ne supporte qu'un seul processus serveur (non adapté à un déploiement multi-instances).
- `SQLite` est adapté au développement mais non recommandé pour un usage en production à forte concurrence.
- Le type de notification `FAVORI_DEVENU_DISPONIBLE` est défini dans le modèle mais sa logique d'émission automatique n'est pas encore implémentée.
- Absence de système de paiement en ligne intégré.

<br>

## 🔭 16. Roadmap & perspectives

- [ ] Migration des notifications du polling REST vers de vrais WebSockets
- [ ] Passage de SQLite vers **PostgreSQL** en production
- [ ] Intégration de **Redis** comme channel layer pour le scaling horizontal
- [ ] Ajout d'un système de **paiement en ligne** (CMI, PayPal)
- [ ] Déclenchement automatique des notifications de favoris redevenus disponibles
- [ ] Développement d'une **application mobile** compagnon
- [ ] Couverture de tests automatisés étendue (CI/CD)

<br>

## 👥 17. Équipe & encadrement

<table>
<tr><th>Rôle</th><th>Nom</th></tr>
<tr><td> Réalisation</td><td>Marwane EL ABBADI</td></tr>
<tr><td> Réalisation</td><td>Aissam HASSAN</td></tr>
<tr><td> Encadrant</td><td>EBOBISSE DJENE Yves Frédéric</td></tr>
<tr><td> Membre du jury</td><td>OUARHIM Asmaa</td></tr>
</table>

**Établissement :** EMSI — École Marocaine des Sciences de l'Ingénieur
**Filière :** Ingénierie Informatique et Réseaux — 3ᵉ année (3IIR)
**Année universitaire :** 2025 / 2026

<br>

## 📄 18. Licence

Projet académique réalisé dans le cadre du Projet de Fin d'Année (PFA) à l'EMSI. Tous droits réservés aux auteurs et à l'établissement. Usage pédagogique uniquement, toute réutilisation commerciale est exclue.

<br>

---

<div align="center">

**Bourse aux Livres EMSI** — *Donner une seconde vie aux livres académiques.*

</div>

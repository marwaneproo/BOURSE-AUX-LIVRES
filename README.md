# Bourse aux Livres EMSI

Application Django pour la vente, le don et l'échange de livres entre étudiants.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_admin
```

## Démarrage

```bash
python manage.py runserver
```

L'application est disponible sur http://127.0.0.1:8000/.

## Tests

```bash
python manage.py test
```

## Applications

- `accounts`: authentification et profils
- `books`: livres, favoris et évaluations
- `orders`: commandes et livraisons
- `messaging`: conversations et WebSocket
- `notifications`: notifications utilisateur
- `moderation`: signalements et administration
- `web`: pages, templates et fichiers statiques

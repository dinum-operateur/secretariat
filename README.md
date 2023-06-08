# Secrétariat opérateur

## Introduction

Ce produit contiendra des utilitaires pour les agents et presta de l'opérateur DINUM.

## Démarrage rapide après installation

```bash
. venv/bin/activate
python manage.py runserver
```

## Installation

### Installer l'environnement

Création d'un venv et installation des dépendances : 

```
cp .env.example .env
python -m venv venv 
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configurer la base de données

Installer PostgreSQL en fonction de votre OS : https://www.postgresql.org/download/

Puis lancez l'invite de commande PostgreSQL :

```
psql
```

Dans l'invite de commande psql, vous pouvez à présent créer la base de données et l'utilisateur :

```sql
CREATE USER secretariat_team PASSWORD 'secretariat_pwd';
CREATE DATABASE secretariat_db OWNER secretariat_team;
ALTER USER secretariat_team CREATEDB;
```

Vous pouvez à présent quitter l'invite de commande psql.

Pour finir, lancez les migrations pour initialiser la base de données :

```bash
python manage.py migrate
```

### Installation de pre-commit

[Pre-commit](https://pre-commit.com/) permet de linter et formatter votre code avant chaque commit. Par défaut ici, il exécute :

- [black](https://github.com/psf/black) pour formatter automatiquement vos fichiers .py en conformité avec la PEP 8 (gestion des espaces, longueur des lignes, etc)
- [flake8](https://github.com/pycqa/flake8) pour soulever les "infractions" restantes (import non utilisés, etc)
- [isort](https://github.com/pycqa/isort) pour ordonner vos imports

Pour l'installer :

```bash
pre-commit install
```

Vous pouvez effectuer un premier passage sur tous les fichiers du repo avec :

```bash
pre-commit run --all-files
```

### Exécuter les tests manuellement

```bash
python manage.py test
```

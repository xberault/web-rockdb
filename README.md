## 1. Initialisation du virtualenv

À l'extérieur du dossier on installe un **virtualenv**.

`virtualenv -p python3 venv`

On active le virtualenv :

`source venv/bin/activate`

## 2. Installation des librairies

Ce projet, pour fonctionner a besoin de plusieurs librairies, dont **flask**.
On les installe avec **pip** dans le virtualenv.

`pip install -r requirements.txt`

## 3. Utilisation

Il existe plusieurs commandes :

- `flask syncdb` pour créer les tables de la base de données
- `flask loaddb <data.yml>` pour générer la base de données à l'aide d'un fichier yml
- `flask run` pour lancer l'application
- `flask newuser <username> <password>` pour créer un nouvel utilisateur
- `flask passwd <username> <new_password>` pour modifier le mot de passe d'un utilisateur

Pour plus d'informations : `flask` ou `flask [nom_commande] --help`

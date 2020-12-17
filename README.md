## 1. Initialisation du virtualenv

À l'extérieur du dossier on installe un **virtualenv**.

`virtualenv -p python3 venv`

On active le virtualenv :

`source venv/bin/activate`

## 2. Installation des librairies

Ce projet, pour fonctionner a besoin de plusieurs librairies, dont **flask**.
On les installe avec **pip** dans le virtualenv.

- `pip install flask`
- `pip install flask_bootstrap`
- `pip install flask_sqlalchemy`
- `pip install flask_login`
- `pip install python-dotenv`
- `pip install pyyaml`

## 3. Utilisation

Pour générer la base de données : `flask loaddb`

Pour lancer l'application : `flask run`

Pour plus d'informations : `flask` ou `flask --help`

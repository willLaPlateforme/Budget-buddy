"""
Budget Buddy — main.py
Point d'entrée unique de l'application.

Prérequis :
    pip install customtkinter mysql-connector-python bcrypt

Avant le premier lancement :
    1. Configurer database.py avec vos identifiants MySQL (host, user, password)
    2. Exécuter schema.sql dans MySQL :
           mysql -u root -p < schema.sql
    3. Lancer l'application :
           python main.py
"""

from register import App as AuthApp


def main():
    # Lance l'écran de connexion/inscription (MySQL + bcrypt).
    # Après auth réussie, le dashboard (Window.py) s'ouvre automatiquement.
    AuthApp().mainloop()


if __name__ == "__main__":
    main()

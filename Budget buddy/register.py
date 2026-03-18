# app.py
import re  # --- AJOUT: import pour validation email/mot de passe
import sys
import customtkinter as ctk
from database import (
    get_connection,
    create_user,
    get_user_by_email,
    hash_password,
    verify_password,
)
import mysql.connector

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ----------------------------
# Fonctions utilitaires ajoutées
# ----------------------------
def is_valid_email(email: str) -> bool:
    """
    --- AJOUT: validation simple du format d'email
    """
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None


def is_strong_password(pw: str) -> bool:
    """
    --- AJOUT: validation de la force du mot de passe selon le cahier des charges
    - Au moins 10 caractères
    - Au moins une majuscule
    - Au moins une minuscule
    - Au moins un chiffre
    - Au moins un caractère spécial
    """
    if len(pw) < 10:
        return False
    if not re.search(r"[A-Z]", pw):
        return False
    if not re.search(r"[a-z]", pw):
        return False
    if not re.search(r"\d", pw):
        return False
    if not re.search(r"[^\w\s]", pw):  # caractère spécial
        return False
    return True


# ----------------------------
# Login Screen
# ----------------------------
class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, switch_to_register, switch_to_menu):
        super().__init__(master)
        self.switch_to_register = switch_to_register
        self.switch_to_menu = switch_to_menu

        ctk.CTkLabel(self, text="Bienvenue au Goulag", font=("Gigi", 50)).pack(pady=20)
        self.entry_email = ctk.CTkEntry(self, width=300, placeholder_text="Email")
        self.entry_email.pack(pady=10)
        self.entry_password = ctk.CTkEntry(self, width=300, placeholder_text="Mot de passe", show="*")
        self.entry_password.pack(pady=10)
        self.label_message = ctk.CTkLabel(self, text="", text_color="red")
        self.label_message.pack(pady=10)

        ctk.CTkButton(self, text="Se connecter", width=220, command=self.login_user).pack(pady=6)
        ctk.CTkButton(self, text="Créer un compte", width=220, fg_color="gray", command=self.switch_to_register).pack(pady=4)

    def login_user(self):
        email = self.entry_email.get().strip().lower()
        mot_de_passe = self.entry_password.get()

        if not email or not mot_de_passe:
            self.label_message.configure(text="❌ Remplis email et mot de passe", text_color="red")
            return

        try:
            user = get_user_by_email(email)
        except Exception as e:
            print("Erreur get_user_by_email (login):", repr(e))
            self.label_message.configure(text="❌ Erreur base de données", text_color="red")
            return

        if user is None:
            self.label_message.configure(text="❌ Utilisateur introuvable", text_color="red")
            return

        try:
            if verify_password(mot_de_passe, user["password_hash"]):
                self.label_message.configure(text="✔ Connexion réussie", text_color="green")
                self.switch_to_menu(user)
            else:
                self.label_message.configure(text="❌ Mot de passe incorrect", text_color="red")
        except Exception as e:
            print("Erreur verify_password:", repr(e))
            self.label_message.configure(text="❌ Erreur lors de la vérification", text_color="red")


# ----------------------------
# Register Screen
# ----------------------------
class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, switch_to_login):
        super().__init__(master)
        self.switch_to_login = switch_to_login

        ctk.CTkLabel(self, text="Créer un compte", font=("Gigi", 50)).pack(pady=20)
        self.entry_nom = ctk.CTkEntry(self, width=300, placeholder_text="Nom")
        self.entry_nom.pack(pady=8)
        self.entry_prenom = ctk.CTkEntry(self, width=300, placeholder_text="Prénom")
        self.entry_prenom.pack(pady=8)
        self.entry_email = ctk.CTkEntry(self, width=300, placeholder_text="Email")
        self.entry_email.pack(pady=8)
        self.entry_password = ctk.CTkEntry(self, width=300, placeholder_text="Mot de passe", show="*")
        self.entry_password.pack(pady=8)
        self.label_message = ctk.CTkLabel(self, text="", text_color="red")
        self.label_message.pack(pady=12)

        ctk.CTkButton(self, text="Créer le compte", width=220, command=self.register_user).pack(pady=6)
        ctk.CTkButton(self, text="Retour", width=220, fg_color="gray", command=self.switch_to_login).pack(pady=4)

        # --- AJOUT: Indication visuelle des règles de mot de passe (optionnel)
        self.password_rules = ctk.CTkLabel(self, text="Mot de passe: 10 caractères ou plus, maj, min, chiffre, spécial", text_color="gray")
        self.password_rules.pack(pady=(0, 8))

    def register_user(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        email = self.entry_email.get().strip().lower()
        mot_de_passe = self.entry_password.get()

        if not nom or not prenom or not email or not mot_de_passe:
            self.label_message.configure(text="❌ Tous les champs sont obligatoires", text_color="red")
            return

        # --- AJOUT: validation format email
        if not is_valid_email(email):
            self.label_message.configure(text="❌ Email invalide", text_color="red")
            return

        # --- AJOUT: validation force mot de passe selon le cahier des charges
        if not is_strong_password(mot_de_passe):
            self.label_message.configure(text="❌ Mot de passe trop faible (10+, maj, min, chiffre, spécial)", text_color="red")
            return

        # Vérifier si l'email existe déjà via la fonction existante
        try:
            if get_user_by_email(email) is not None:
                self.label_message.configure(text="❌ Cet email existe déjà", text_color="red")
                return
        except Exception as e:
            print("Erreur get_user_by_email (vérif):", repr(e))
            self.label_message.configure(text="❌ Erreur base de données (vérif)", text_color="red")
            return

        # Hash du mot de passe
        try:
            password_hash = hash_password(mot_de_passe)
        except Exception as e:
            print("Erreur hash_password:", repr(e))
            self.label_message.configure(text="❌ Erreur lors du hash", text_color="red")
            return

        # INSERT direct via get_connection pour s'assurer du commit et diagnostiquer
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = """
                INSERT INTO users (nom, prenom, email, password_hash, profile_picture)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nom, prenom, email, password_hash, None))
            conn.commit()
            last_id = cursor.lastrowid
            print(f"[INFO] Insert direct OK, id={last_id}")
        except mysql.connector.IntegrityError as ie:
            print("IntegrityError insert direct:", repr(ie))
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
            self.label_message.configure(text="❌ Cet email existe déjà (contrainte SQL)", text_color="red")
            return
        except Exception as e:
            print("Erreur insert direct:", repr(e))
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
            self.label_message.configure(text="❌ Erreur lors de la création (voir console)", text_color="red")
            return
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                pass

        # Vérifier insertion via get_user_by_email
        try:
            created = get_user_by_email(email)
        except Exception as e:
            print("Erreur get_user_by_email après insert:", repr(e))
            self.label_message.configure(text="✔ Compte créé (vérification impossible)", text_color="green")
            self._clear_fields()
            return

        if created is None:
            print("Alerte: utilisateur non trouvé après création.")
            self.label_message.configure(text="❌ Échec inattendu : utilisateur non trouvé après création", text_color="red")
            return

        # Succès : ouvrir le menu automatiquement
        self.label_message.configure(text="✔ Compte créé — connexion...", text_color="green")
        self._clear_fields()
        try:
            self.master.show_menu(created)
        except Exception as e:
            print("Erreur ouverture menu après création:", repr(e))
            self.switch_to_login()

    def _clear_fields(self):
        self.entry_nom.delete(0, "end")
        self.entry_prenom.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_password.delete(0, "end")


# ----------------------------
# Main Menu
# ----------------------------
class MainMenu(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master)
        prenom = user.get("prenom", "") if isinstance(user, dict) else ""
        ctk.CTkLabel(self, text=f"Bienvenue {prenom} 👋", font=("Gigi", 50)).pack(pady=20)
        ctk.CTkButton(self, text="Voir mes dépenses").pack(pady=10)
        ctk.CTkButton(self, text="Voir mes revenus").pack(pady=10)
        ctk.CTkButton(self, text="Mon profil").pack(pady=10)
        ctk.CTkButton(self, text="Déconnexion", fg_color="red", command=master.show_login).pack(pady=20)


# ----------------------------
# Application
# ----------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Buddy")
        self.geometry("500x500")
        self.current_frame = None
        self.show_login()

    def show_frame(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(expand=True, fill="both")

    def show_login(self):
        self.show_frame(LoginScreen, self.show_register, self.show_menu)

    def show_register(self):
        self.show_frame(RegisterScreen, self.show_login)

    def show_menu(self, user):
        self.show_frame(MainMenu, user)


if __name__ == "__main__":
    app = App()
    app.mainloop()

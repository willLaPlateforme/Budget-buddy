import re
import customtkinter as ctk
from Couleurs import C

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Règles de validation

def valider_nom(valeur):
    if not valeur.strip():
        return "Ce champ est obligatoire."
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\-' ]+", valeur):
        return "Lettres uniquement (pas de chiffres ni de caractères spéciaux)."
    return None

def valider_email(valeur):
    if not valeur.strip():
        return "Ce champ est obligatoire."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valeur):
        return "Format invalide (ex: jean@exemple.com)."
    return None

def valider_mdp(valeur):
    if not valeur:
        return "Ce champ est obligatoire."
    erreurs = []
    if len(valeur) < 10:
        erreurs.append("10 caractères minimum")
    if not re.search(r"[A-Z]", valeur):
        erreurs.append("1 majuscule")
    if not re.search(r"[a-z]", valeur):
        erreurs.append("1 minuscule")
    if not re.search(r"\d", valeur):
        erreurs.append("1 chiffre")
    if not re.search(r"[^A-Za-z0-9]", valeur):
        erreurs.append("1 caractère spécial")
    if erreurs:
        return "Requis : " + ", ".join(erreurs) + "."
    return None

# Widget champ avec label + erreur intégrés

class ChampValide(ctk.CTkFrame):
    def __init__(self, parent, label, placeholder, show=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        ctk.CTkLabel(self, text=label,
            font=ctk.CTkFont("Helvetica", 11), text_color=C["dim"]
        ).pack(anchor="w")

        self.entry = ctk.CTkEntry(self,
            placeholder_text=placeholder,
            fg_color=C["panneau"], border_color=C["bordure"],
            text_color=C["texte"], placeholder_text_color=C["dim"],
            height=38, corner_radius=8, show=show or ""
        )
        self.entry.pack(fill="x", pady=(4, 2))

        self.err_label = ctk.CTkLabel(self, text="",
            font=ctk.CTkFont("Helvetica", 10), text_color=C["rouge"],
            anchor="w", justify="left", wraplength=280
        )
        self.err_label.pack(anchor="w")

    def get(self):
        return self.entry.get()

    def set_erreur(self, msg):
        self.err_label.configure(text=msg or "")
        self.entry.configure(border_color=C["rouge"] if msg else C["vert"])

    def reset(self):
        self.err_label.configure(text="")
        self.entry.configure(border_color=C["bordure"])


# Application principale

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Buddy")
        self.geometry("420x580")
        self.resizable(False, False)
        self.configure(fg_color=C["fond"])
        self.mode = "login"
        self._build()

    def _build(self):
        pad = {"padx": 32}

        self.card = ctk.CTkFrame(self, fg_color=C["carte"], corner_radius=16,
            border_width=1, border_color=C["bordure"], width=360)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        ctk.CTkLabel(self.card, text="💰  Budget Buddy",
            font=ctk.CTkFont("Helvetica", 18, "bold"), text_color=C["cyan"]
        ).pack(pady=(30, 4), **pad, anchor="w")

        ctk.CTkLabel(self.card, text="Bienvenue",
            font=ctk.CTkFont("Helvetica", 20, "bold"), text_color=C["texte"]
        ).pack(pady=(4, 0), **pad, anchor="w")

        ctk.CTkLabel(self.card, text="Accédez à votre espace financier",
            font=ctk.CTkFont("Helvetica", 12), text_color=C["dim"]
        ).pack(pady=(2, 16), **pad, anchor="w")

        # Onglets
        tab_frame = ctk.CTkFrame(self.card, fg_color=C["panneau"], corner_radius=8)
        tab_frame.pack(fill="x", **pad, pady=(0, 18))
        tab_frame.columnconfigure((0, 1), weight=1)

        self.btn_login = ctk.CTkButton(tab_frame, text="Connexion",
            corner_radius=6, height=32,
            fg_color=C["bleu"], hover_color=C["cyan"], text_color=C["texte"],
            font=ctk.CTkFont("Helvetica", 13, "bold"), command=self._show_login)
        self.btn_login.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.btn_reg = ctk.CTkButton(tab_frame, text="Nouveau compte",
            corner_radius=6, height=32,
            fg_color="transparent", hover_color=C["bordure"], text_color=C["dim"],
            font=ctk.CTkFont("Helvetica", 13, "bold"), command=self._show_register)
        self.btn_reg.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Frame CONNEXION
        self.frame_login = ctk.CTkFrame(self.card, fg_color="transparent")

        self.login_email = ChampValide(self.frame_login, "Email", "jean@exemple.com")
        self.login_email.pack(fill="x", padx=32, pady=(0, 8))

        self.login_pass = ChampValide(self.frame_login, "Mot de passe", "••••••••", show="•")
        self.login_pass.pack(fill="x", padx=32, pady=(0, 16))

        ctk.CTkButton(self.frame_login, text="Se connecter", height=42,
            corner_radius=8, fg_color=C["bleu"], hover_color=C["cyan"],
            text_color=C["texte"], font=ctk.CTkFont("Helvetica", 14, "bold"),
            command=self._submit
        ).pack(fill="x", padx=32, pady=(0, 30))

        # Frame INSCRIPTION
        self.frame_register = ctk.CTkFrame(self.card, fg_color="transparent")

        # Rangée prénom/nom
        name_row = ctk.CTkFrame(self.frame_register, fg_color="transparent")
        name_row.pack(fill="x", padx=32, pady=(0, 8))
        name_row.columnconfigure((0, 1), weight=1)

        self.reg_first = ChampValide(name_row, "Prénom", "Jean")
        self.reg_first.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.reg_last = ChampValide(name_row, "Nom", "Dupont")
        self.reg_last.grid(row=0, column=1, sticky="ew")

        self.reg_email = ChampValide(self.frame_register, "Email", "jean@exemple.com")
        self.reg_email.pack(fill="x", padx=32, pady=(0, 8))

        self.reg_pass = ChampValide(self.frame_register, "Mot de passe", "••••••••", show="•")
        self.reg_pass.pack(fill="x", padx=32, pady=(0, 16))

        ctk.CTkButton(self.frame_register, text="Créer mon compte", height=42,
            corner_radius=8, fg_color=C["bleu"], hover_color=C["cyan"],
            text_color=C["texte"], font=ctk.CTkFont("Helvetica", 14, "bold"),
            command=self._submit
        ).pack(fill="x", padx=32, pady=(0, 30))

        self.frame_login.pack(fill="x")

    # Switchs d'onglets

    def _show_login(self):
        self.mode = "login"
        self.frame_register.pack_forget()
        self.frame_login.pack(fill="x")
        self.btn_login.configure(fg_color=C["bleu"], text_color=C["texte"])
        self.btn_reg.configure(fg_color="transparent", text_color=C["dim"])
        for champ in (self.login_email, self.login_pass):
            champ.reset()

    def _show_register(self):
        self.mode = "register"
        self.frame_login.pack_forget()
        self.frame_register.pack(fill="x")
        self.btn_reg.configure(fg_color=C["bleu"], text_color=C["texte"])
        self.btn_login.configure(fg_color="transparent", text_color=C["dim"])
        for champ in (self.reg_first, self.reg_last, self.reg_email, self.reg_pass):
            champ.reset()

    # Validation & soumission

    def _submit(self):
        if self.mode == "login":
            e1 = valider_email(self.login_email.get())
            e2 = valider_mdp(self.login_pass.get())
            self.login_email.set_erreur(e1)
            self.login_pass.set_erreur(e2)
            if not e1 and not e2:
                print(f"[Connexion] {self.login_email.get()}")

        else:
            e1 = valider_nom(self.reg_first.get())
            e2 = valider_nom(self.reg_last.get())
            e3 = valider_email(self.reg_email.get())
            e4 = valider_mdp(self.reg_pass.get())
            self.reg_first.set_erreur(e1)
            self.reg_last.set_erreur(e2)
            self.reg_email.set_erreur(e3)
            self.reg_pass.set_erreur(e4)
            if not any([e1, e2, e3, e4]):
                print(f"[Nouveau compte] {self.reg_first.get()} {self.reg_last.get()} | {self.reg_email.get()}")

if __name__ == "__main__":
    LoginApp().mainloop()
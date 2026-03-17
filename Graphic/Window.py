import tkinter as tk
import customtkinter as ctk


class App(ctk.CTk):

    def __init__(self):

        super().__init__()
        self.title("Dashboard")
        self.geometry("1200x750")
        self.configure(fg_color=C["fond"])
        self._build()

    def _build(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, fg_color=C["panneau"], corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="PopularBank", font=("Arial", 18, "bold"),
        text_color=C["bleu"]).pack(padx=20, pady=24, anchor="w")
        ctk.CTkFrame(sidebar, height=1, fg_color=C["bordure"]).pack(fill="x", padx=16)

        for label, actif in [("Vue Globale", True), ("Transactions", False),
        ("Budgets", False), ("Épargne", False)]:
            
            ctk.CTkButton(sidebar, text=label, anchor="w",
            fg_color="#1D3A6E" if actif else "transparent",
            hover_color=C["carte"],
            text_color=C["texte"] if actif else C["dim"],
            corner_radius=8, height=40,
            font=("Arial", 13)).pack(fill="x", padx=10, pady=2)

        # Contenu
        contenu = ctk.CTkScrollableFrame(self, fg_color=C["fond"])
        contenu.pack(side="left", fill="both", expand=True)

        # Titre
        titre_ligne = ctk.CTkFrame(contenu, fg_color="transparent")
        titre_ligne.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(titre_ligne, text="Vue Globale", font=("Arial", 24, "bold"),
        text_color=C["texte"]).pack(side="left")

        ctk.CTkButton(titre_ligne, text="+ Ajouter compte",
        fg_color=C["bleu"], corner_radius=8,
        height=34, font=("Arial", 12)).pack(side="right")

        # KPIs
        kpis_frame = ctk.CTkFrame(contenu, fg_color="transparent")
        kpis_frame.pack(fill="x", padx=24, pady=(16, 0))
        for i in range(4):
            kpis_frame.columnconfigure(i, weight=1, uniform="kpi")
        for i, (titre, val, col) in enumerate([
            ("Solde Total", "€0", C["bleu"]),
            ("Dépenses ce mois", "€0", C["rouge"]),
            ("Épargne ce mois", "€0", C["vert"]),
            ("Prochains débits", "€0", C["orange"]),
        ]):
            carte_kpi(kpis_frame, titre, val, col).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        # Alertes
        ctk.CTkLabel(contenu, text="Alertes & Notifications",
        font=("Arial", 15, "bold"),
        text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))

        alertes_frame = ctk.CTkFrame(contenu, fg_color="transparent")
        alertes_frame.pack(fill="x", padx=24)
        for i in range(len(ALERTES)):
            alertes_frame.columnconfigure(i, weight=1)
        for i, (ico, tit, desc, col) in enumerate(ALERTES):
            carte_alerte(alertes_frame, ico, tit, desc, col).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        # Comptes
        ctk.CTkLabel(contenu, text="Comptes",
        font=("Arial", 15, "bold"),
        text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))
        comptes_frame = ctk.CTkFrame(contenu, fg_color="transparent")
        comptes_frame.pack(fill="x", padx=24)
        for i in range(len(COMPTES)):
            comptes_frame.columnconfigure(i, weight=1)
        for i, (nom, solde, col) in enumerate(COMPTES):
            carte_compte(comptes_frame, nom, solde, col).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        # Graphique
        ctk.CTkLabel(contenu, text="Revenus vs Dépenses",
        font=("Arial", 15, "bold"),
        text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))
        graph_card = ctk.CTkFrame(contenu, fg_color=C["carte"], corner_radius=12,
        border_width=1, border_color=C["bordure"])
        graph_card.pack(fill="x", padx=24, pady=(0, 28))
        GraphiqueBarres(graph_card, height=230).pack(
            fill="both", expand=True, padx=8, pady=8)


if __name__ == "__main__":
    App().mainloop()
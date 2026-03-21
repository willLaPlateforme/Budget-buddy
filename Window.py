"""
Budget Buddy — Window.py
Dashboard principal 100% MySQL.
Reçoit le dict user depuis register.py après authentification.
"""

import tkinter as tk
import customtkinter as ctk
import datetime
from Menu_General import (
    C, PALETTE_COMPTES,
    carte_kpi, carte_alerte, carte_compte, GraphiqueBarres,
)
from database import get_comptes_user, creer_compte_par_defaut, add_compte
from transactions import get_stats_mensuelles, filtrer_transactions

NAV_ITEMS = [
    ("vue_globale",  "🏠", "Vue Globale"),
    ("transactions", "📋", "Transactions"),
    ("budgets",      "📊", "Budgets"),
    ("epargne",      "💰", "Épargne"),
]


class App(ctk.CTk):

    def __init__(self, user: dict):
        super().__init__()
        self.user = user

        # Créer le compte principal MySQL si l'utilisateur n'en a pas encore
        creer_compte_par_defaut(user["id"])

        self.title("Budget Buddy")
        self.geometry("1280x780")
        self.minsize(960, 600)
        self.configure(fg_color=C["fond"])
        self._page_actuelle = "vue_globale"
        self._build()
        self._afficher("vue_globale")

    # ── Construction ──────────────────────────────────────────

    def _build(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=C["panneau"],
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.main = ctk.CTkFrame(self, fg_color=C["fond"], corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)

        self.pages = {}
        self._creer_page_vue_globale()
        self._creer_page_transactions()
        self._creer_page_budgets()
        self._creer_page_epargne()

    def _build_sidebar(self):
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", padx=16, pady=(24, 8))
        ctk.CTkLabel(logo, text="💰", font=("Arial", 26)).pack(side="left")
        ctk.CTkLabel(logo, text="Budget Buddy", font=("Arial", 16, "bold"),
                     text_color=C["bleu"]).pack(side="left", padx=8)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=C["bordure"]).pack(
            fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(self.sidebar,
                     text=f"{self.user.get('prenom','')} {self.user.get('nom','')}",
                     font=("Arial", 12, "bold"), text_color=C["texte"]).pack(
            anchor="w", padx=16)
        ctk.CTkLabel(self.sidebar, text=self.user.get("email", ""),
                     font=("Arial", 10), text_color=C["dim"]).pack(
            anchor="w", padx=16, pady=(0, 16))

        ctk.CTkFrame(self.sidebar, height=1, fg_color=C["bordure"]).pack(
            fill="x", padx=16, pady=(0, 8))

        self.nav_btns = {}
        for key, ico, label in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {ico}  {label}", anchor="w",
                fg_color="transparent", hover_color=C["carte"],
                text_color=C["dim"], corner_radius=8, height=42,
                font=("Arial", 13),
                command=lambda k=key: self._afficher(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_btns[key] = btn

        ctk.CTkFrame(self.sidebar, height=1, fg_color=C["bordure"]).pack(
            fill="x", padx=16, side="bottom", pady=(0, 8))
        ctk.CTkButton(
            self.sidebar, text="  ⎋  Déconnexion", anchor="w",
            fg_color="transparent", hover_color=C["carte"],
            text_color=C["dim"], corner_radius=8, height=40,
            font=("Arial", 12), command=self._deconnexion,
        ).pack(fill="x", padx=10, pady=4, side="bottom")

    # ── Pages ─────────────────────────────────────────────────

    def _creer_page_vue_globale(self):
        page = ctk.CTkScrollableFrame(self.main, fg_color=C["fond"])
        self.pages["vue_globale"] = page

        comptes     = get_comptes_user(self.user["id"])
        solde_total = sum(float(c["solde"]) for c in comptes)

        mois_debut = datetime.date.today().strftime("%Y-%m") + "-01"
        depenses_mois = 0.0
        epargne_mois  = 0.0
        for c in comptes:
            for t in filtrer_transactions(c["id"], date_debut=mois_debut):
                if t.montant < 0 and t.type_op == "retrait":
                    depenses_mois += abs(t.montant)
                if t.categorie == "épargne" and t.montant > 0:
                    epargne_mois  += t.montant

        # Titre
        titre_ligne = ctk.CTkFrame(page, fg_color="transparent")
        titre_ligne.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(titre_ligne, text="Vue Globale", font=("Arial", 24, "bold"),
                     text_color=C["texte"]).pack(side="left")
        ctk.CTkButton(titre_ligne, text="+ Ajouter compte",
                      fg_color=C["bleu"], corner_radius=8, height=34,
                      font=("Arial", 12),
                      command=self._popup_ajouter_compte).pack(side="right")

        # KPIs
        kpis_frame = ctk.CTkFrame(page, fg_color="transparent")
        kpis_frame.pack(fill="x", padx=24, pady=(16, 0))
        for i in range(4):
            kpis_frame.columnconfigure(i, weight=1, uniform="kpi")
        for i, (titre, val, col) in enumerate([
            ("Solde Total",      f"€{solde_total:,.2f}",   C["bleu"]),
            ("Dépenses ce mois", f"€{depenses_mois:,.2f}", C["rouge"]),
            ("Épargne ce mois",  f"€{epargne_mois:,.2f}",  C["vert"]),
            ("Comptes actifs",   str(len(comptes)),         C["orange"]),
        ]):
            carte_kpi(kpis_frame, titre, val, col).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        # Alertes
        ctk.CTkLabel(page, text="Alertes & Notifications",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))
        alertes = self._generer_alertes(comptes, solde_total, depenses_mois)
        alertes_frame = ctk.CTkFrame(page, fg_color="transparent")
        alertes_frame.pack(fill="x", padx=24)
        for i in range(len(alertes)):
            alertes_frame.columnconfigure(i, weight=1)
        for i, (ico, tit, desc, col) in enumerate(alertes):
            carte_alerte(alertes_frame, ico, tit, desc, col).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        # Comptes
        ctk.CTkLabel(page, text="Mes Comptes",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))
        comptes_frame = ctk.CTkFrame(page, fg_color="transparent")
        comptes_frame.pack(fill="x", padx=24)
        if comptes:
            for i in range(len(comptes)):
                comptes_frame.columnconfigure(i, weight=1)
            for i, c in enumerate(comptes):
                col = PALETTE_COMPTES[i % len(PALETTE_COMPTES)]
                carte_compte(comptes_frame, c["libelle"],
                             float(c["solde"]), col).grid(
                    row=0, column=i, sticky="nsew",
                    padx=(0 if i == 0 else 8, 0))
        else:
            ctk.CTkLabel(comptes_frame,
                         text="Aucun compte. Cliquez sur + Ajouter compte.",
                         text_color=C["dim"]).pack()

        # Graphique
        ctk.CTkLabel(page, text="Revenus vs Dépenses",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))
        graph_card = ctk.CTkFrame(page, fg_color=C["carte"], corner_radius=12,
                                  border_width=1, border_color=C["bordure"])
        graph_card.pack(fill="x", padx=24, pady=(0, 28))

        stats = get_stats_mensuelles(comptes[0]["id"]) if comptes else []
        MOIS_FR = {"01":"Jan","02":"Fév","03":"Mar","04":"Avr","05":"Mai","06":"Jun",
                   "07":"Jul","08":"Aoû","09":"Sep","10":"Oct","11":"Nov","12":"Déc"}
        mois_lbl = [MOIS_FR.get(s["mois"][5:7], s["mois"][5:7]) + " " + s["mois"][2:4]
                    for s in stats] or ["—"]
        revenus  = [s["revenus"]  for s in stats] or [0]
        depenses = [s["depenses"] for s in stats] or [0]
        GraphiqueBarres(graph_card, mois=mois_lbl, revenus=revenus,
                        depenses=depenses, height=230).pack(
            fill="both", expand=True, padx=8, pady=8)

    def _creer_page_transactions(self):
        from ui_transactions import PageTransactions
        page = PageTransactions(self.main, self.user)
        self.pages["transactions"] = page

    def _creer_page_budgets(self):
        page = ctk.CTkScrollableFrame(self.main, fg_color=C["fond"])
        self.pages["budgets"] = page

        # Titre
        titre_ligne = ctk.CTkFrame(page, fg_color="transparent")
        titre_ligne.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(titre_ligne, text="Budgets", font=("Arial", 24, "bold"),
                     text_color=C["texte"]).pack(side="left")

        # Résumé dépenses par catégorie
        ctk.CTkLabel(page, text="Dépenses par catégorie",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))

        from transactions import filtrer_transactions
        comptes = get_comptes_user(self.user["id"])

        # Calculer les dépenses par catégorie tous comptes confondus
        depenses_cat = {}
        total_depenses = 0.0
        for c in comptes:
            txs = filtrer_transactions(c["id"])
            for t in txs:
                if t.montant < 0:
                    cat = t.categorie.capitalize()
                    depenses_cat[cat] = depenses_cat.get(cat, 0) + abs(t.montant)
                    total_depenses += abs(t.montant)

        if not depenses_cat:
            ctk.CTkLabel(page, text="Aucune dépense enregistrée.",
                         font=("Arial", 13), text_color=C["dim"]).pack(pady=20)
        else:
            # Grille de cartes par catégorie
            grid = ctk.CTkFrame(page, fg_color="transparent")
            grid.pack(fill="x", padx=24, pady=(0, 16))
            cols = 3
            for i in range(cols):
                grid.columnconfigure(i, weight=1)

            couleurs_cat = [C["bleu"], C["rouge"], C["orange"],
                            C["vert"], C["cyan"], C["bleu"],
                            C["orange"], C["rouge"], C["vert"]]

            for idx, (cat, montant) in enumerate(
                    sorted(depenses_cat.items(), key=lambda x: x[1], reverse=True)):
                col_idx = idx % cols
                row_idx = idx // cols
                pct = (montant / total_depenses * 100) if total_depenses > 0 else 0
                couleur = couleurs_cat[idx % len(couleurs_cat)]

                cadre = ctk.CTkFrame(grid, fg_color=C["carte"], corner_radius=10,
                                     border_width=1, border_color=C["bordure"])
                cadre.grid(row=row_idx, column=col_idx, sticky="nsew",
                           padx=(0 if col_idx == 0 else 8, 0), pady=(0, 8))
                ctk.CTkLabel(cadre, text=cat, font=("Arial", 12),
                             text_color=C["dim"]).pack(anchor="w", padx=14, pady=(12, 0))
                ctk.CTkLabel(cadre, text=f"€{montant:,.2f}",
                             font=("Arial", 18, "bold"),
                             text_color=couleur).pack(anchor="w", padx=14, pady=(2, 0))
                ctk.CTkLabel(cadre, text=f"{pct:.1f}% des dépenses",
                             font=("Arial", 10),
                             text_color=C["dim"]).pack(anchor="w", padx=14, pady=(0, 12))

        # Total
        ctk.CTkFrame(page, height=1, fg_color=C["bordure"]).pack(
            fill="x", padx=24, pady=(8, 8))
        total_frame = ctk.CTkFrame(page, fg_color=C["carte"], corner_radius=10,
                                   border_width=1, border_color=C["bordure"])
        total_frame.pack(fill="x", padx=24, pady=(0, 28))
        ctk.CTkLabel(total_frame, text="Total dépensé",
                     font=("Arial", 12), text_color=C["dim"]).pack(
            anchor="w", padx=14, pady=(12, 0))
        ctk.CTkLabel(total_frame, text=f"€{total_depenses:,.2f}",
                     font=("Arial", 22, "bold"),
                     text_color=C["rouge"]).pack(anchor="w", padx=14, pady=(2, 14))

    def _creer_page_epargne(self):
        page = ctk.CTkScrollableFrame(self.main, fg_color=C["fond"])
        self.pages["epargne"] = page

        # Titre
        ctk.CTkLabel(page, text="Épargne", font=("Arial", 24, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 0))

        comptes = get_comptes_user(self.user["id"])
        solde_total = sum(float(c["solde"]) for c in comptes)

        # KPIs épargne
        kpis = ctk.CTkFrame(page, fg_color="transparent")
        kpis.pack(fill="x", padx=24, pady=(16, 0))
        for i in range(3):
            kpis.columnconfigure(i, weight=1)

        from transactions import filtrer_transactions
        total_entrees = 0.0
        total_sorties = 0.0
        for c in comptes:
            for t in filtrer_transactions(c["id"]):
                if t.montant > 0:
                    total_entrees += t.montant
                else:
                    total_sorties += abs(t.montant)

        taux = ((total_entrees - total_sorties) / total_entrees * 100
                if total_entrees > 0 else 0)

        for i, (titre, val, col) in enumerate([
            ("Solde disponible",  f"€{solde_total:,.2f}", C["bleu"]),
            ("Total entrants",    f"€{total_entrees:,.2f}", C["vert"]),
            ("Taux d'épargne",  f"{max(taux, 0):.1f}%", C["cyan"]),
        ]):
            carte_kpi(kpis, titre, val, col).grid(
                row=0, column=i, sticky="nsew",
                padx=(0 if i == 0 else 8, 0))

        # Conseil selon le solde
        ctk.CTkLabel(page, text="Analyse",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(24, 6))

        if solde_total < 0:
            ico, msg, col = "⚠️", f"Attention : solde négatif (€{solde_total:,.2f}). Réduisez vos dépenses.", C["rouge"]
        elif solde_total < 500:
            ico, msg, col = "💡", "Solde faible. Pensez à constituer une épargne de précaution.", C["orange"]
        elif taux >= 20:
            ico, msg, col = "🎯", f"Excellent ! Votre taux d'épargne est de {taux:.1f}%.", C["vert"]
        else:
            ico, msg, col = "📈", f"Taux d'épargne : {max(taux,0):.1f}%. Objectif recommandé : 20%.", C["bleu"]

        conseil = ctk.CTkFrame(page, fg_color=C["carte"], corner_radius=10,
                               border_width=1, border_color=col)
        conseil.pack(fill="x", padx=24, pady=(0, 28))
        ligne = ctk.CTkFrame(conseil, fg_color="transparent")
        ligne.pack(fill="x", padx=12, pady=(10, 2))
        ctk.CTkLabel(ligne, text=ico, font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(ligne, text="Conseil", font=("Arial", 12, "bold"),
                     text_color=col).pack(side="left", padx=8)
        ctk.CTkLabel(conseil, text=msg, font=("Arial", 11),
                     text_color=C["dim"], wraplength=900).pack(
            anchor="w", padx=12, pady=(0, 12))

    def _creer_page_placeholder(self, key, titre, msg):
        page = ctk.CTkFrame(self.main, fg_color=C["fond"])
        ctk.CTkLabel(page, text=titre, font=("Arial", 22, "bold"),
                     text_color=C["texte"]).pack(pady=(80, 12))
        ctk.CTkLabel(page, text=msg, font=("Arial", 14),
                     text_color=C["dim"]).pack()
        self.pages[key] = page

    # ── Navigation ────────────────────────────────────────────

    def _afficher(self, key: str):
        self._page_actuelle = key
        for k, btn in self.nav_btns.items():
            btn.configure(
                fg_color="#1D3A6E" if k == key else "transparent",
                text_color=C["texte"] if k == key else C["dim"],
            )
        for p in self.pages.values():
            p.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        if key == "transactions":
            try:
                self.pages["transactions"].rafraichir()
            except Exception:
                pass
        if key == "vue_globale":
            try:
                self._rafraichir_vue_globale()
            except Exception:
                pass
        if key == "budgets":
            try:
                old = self.pages.get("budgets")
                if old: old.pack_forget(); old.destroy()
                self._creer_page_budgets()
                self.pages["budgets"].pack(fill="both", expand=True)
            except Exception:
                pass
        if key == "epargne":
            try:
                old = self.pages.get("epargne")
                if old: old.pack_forget(); old.destroy()
                self._creer_page_epargne()
                self.pages["epargne"].pack(fill="both", expand=True)
            except Exception:
                pass

    # ── Actions ───────────────────────────────────────────────

    def _popup_ajouter_compte(self):
        dial = ctk.CTkToplevel(self)
        dial.title("Nouveau compte")
        dial.geometry("380x220")
        dial.configure(fg_color=C["fond"])
        dial.resizable(False, False)
        dial.grab_set()

        ctk.CTkLabel(dial, text="Nouveau compte", font=("Arial", 16, "bold"),
                     text_color=C["texte"]).pack(pady=(24, 4))
        ctk.CTkLabel(dial, text="Libellé", font=("Arial", 11),
                     text_color=C["dim"]).pack(anchor="w", padx=32)
        e = ctk.CTkEntry(dial, placeholder_text="Ex : Livret A", height=38,
                         corner_radius=8, border_color=C["bordure"],
                         fg_color=C["panneau"])
        e.pack(fill="x", padx=32, pady=(4, 4))
        lbl = ctk.CTkLabel(dial, text="", font=("Arial", 11), text_color=C["rouge"])
        lbl.pack()

        def creer():
            lib = e.get().strip()
            if not lib:
                lbl.configure(text="Libellé requis.")
                return
            add_compte(self.user["id"], lib)
            dial.destroy()
            self._rafraichir_vue_globale()

        ctk.CTkButton(dial, text="Créer", height=40, fg_color=C["bleu"],
                      corner_radius=8, font=("Arial", 12, "bold"),
                      command=creer).pack(padx=32, pady=10, fill="x")

    def _generer_alertes(self, comptes, solde_total, depenses_mois):
        alertes = []
        for c in comptes:
            if float(c["solde"]) < 0:
                alertes.append(("⚠️", "Découvert détecté",
                                 f"{c['libelle']} : €{float(c['solde']):.2f}",
                                 C["rouge"]))
        if not alertes:
            alertes.append(("✅", "Comptes sains",
                             "Aucun découvert détecté.", C["vert"]))
        if solde_total < 200:
            alertes.append(("💡", "Solde faible",
                             f"Total : €{solde_total:.2f}", C["orange"]))
        else:
            alertes.append(("📈", "Dépenses du mois",
                             f"€{depenses_mois:.2f} dépensés ce mois.", C["bleu"]))
        if len(alertes) < 3:
            alertes.append(("📅", "Bilan disponible",
                             "Consultez l'onglet Transactions.", C["cyan"]))
        return alertes[:3]

    def _rafraichir_vue_globale(self):
        old = self.pages.get("vue_globale")
        if old:
            old.pack_forget()
            old.destroy()
        self._creer_page_vue_globale()
        if self._page_actuelle == "vue_globale":
            self.pages["vue_globale"].pack(fill="both", expand=True)

    def _deconnexion(self):
        self.destroy()
        from register import App as AuthApp
        AuthApp().mainloop()
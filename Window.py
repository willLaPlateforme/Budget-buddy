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
        import tkinter as tk
        page = ctk.CTkScrollableFrame(self.main, fg_color=C["fond"])
        self.pages["budgets"] = page

        from transactions import filtrer_transactions
        comptes = get_comptes_user(self.user["id"])

        # ── Calcul dépenses et dépôts par catégorie ──────────
        depenses_cat = {}
        depots_cat   = {}
        total_dep    = 0.0
        total_dep_tx = 0.0

        for c in comptes:
            for t in filtrer_transactions(c["id"]):
                cat = t.categorie.capitalize()
                if t.montant < 0:
                    depenses_cat[cat] = depenses_cat.get(cat, 0) + abs(t.montant)
                    total_dep += abs(t.montant)
                else:
                    depots_cat[cat] = depots_cat.get(cat, 0) + t.montant
                    total_dep_tx += t.montant

        # Palette de couleurs hex pour le graphique
        COULEURS_HEX = [
            "#3B82F6", "#EF4444", "#F59E0B", "#22C55E",
            "#06B6D4", "#A855F7", "#F97316", "#EC4899",
            "#14B8A6", "#6366F1",
        ]

        # ── Titre ────────────────────────────────────────────
        titre_ligne = ctk.CTkFrame(page, fg_color="transparent")
        titre_ligne.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(titre_ligne, text="Budgets", font=("Arial", 24, "bold"),
                     text_color=C["texte"]).pack(side="left")

        # ── Graphique camembert (Canvas tkinter) ──────────────
        ctk.CTkLabel(page, text="Répartition des dépenses & dépôts",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(20, 6))

        graph_card = ctk.CTkFrame(page, fg_color=C["carte"], corner_radius=12,
                                  border_width=1, border_color=C["bordure"])
        graph_card.pack(fill="x", padx=24, pady=(0, 16))

        canvas_frame = ctk.CTkFrame(graph_card, fg_color="transparent")
        canvas_frame.pack(fill="x", padx=16, pady=16)

        # ── Camembert dépenses ────────────────────────────────
        col_dep = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        col_dep.pack(side="left", expand=True, fill="both", padx=(0, 8))
        ctk.CTkLabel(col_dep, text="Dépenses", font=("Arial", 12, "bold"),
                     text_color=C["rouge"]).pack(pady=(0, 6))

        c_dep = tk.Canvas(col_dep, width=220, height=220,
                          bg=C["carte"], highlightthickness=0)
        c_dep.pack()

        if depenses_cat:
            self._dessiner_camembert(c_dep, depenses_cat, total_dep, COULEURS_HEX)
        else:
            c_dep.create_text(110, 110, text="Aucune dépense",
                              fill=C["dim"], font=("Arial", 12), justify="center")

        # Légende dépenses
        leg_dep = ctk.CTkFrame(col_dep, fg_color="transparent")
        leg_dep.pack(pady=(8, 0), anchor="w")
        for idx, (cat, montant) in enumerate(
                sorted(depenses_cat.items(), key=lambda x: x[1], reverse=True)):
            pct = montant / total_dep * 100 if total_dep > 0 else 0
            col_hex = COULEURS_HEX[idx % len(COULEURS_HEX)]
            row = ctk.CTkFrame(leg_dep, fg_color="transparent")
            row.pack(anchor="w", pady=1)
            tk.Label(row, bg=col_hex, width=2, height=1).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=f"{cat}  {pct:.1f}%  (€{montant:,.2f})",
                         font=("Arial", 10), text_color=C["dim"]).pack(side="left")

        # ── Séparateur vertical ───────────────────────────────
        sep = ctk.CTkFrame(canvas_frame, fg_color=C["bordure"], width=1)
        sep.pack(side="left", fill="y", padx=8)

        # ── Camembert dépôts ──────────────────────────────────
        col_dot = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        col_dot.pack(side="left", expand=True, fill="both", padx=(8, 0))
        ctk.CTkLabel(col_dot, text="Dépôts", font=("Arial", 12, "bold"),
                     text_color=C["vert"]).pack(pady=(0, 6))

        c_dot = tk.Canvas(col_dot, width=220, height=220,
                          bg=C["carte"], highlightthickness=0)
        c_dot.pack()

        if depots_cat:
            self._dessiner_camembert(c_dot, depots_cat, total_dep_tx, COULEURS_HEX)
        else:
            c_dot.create_text(110, 110, text="Aucun dépôt",
                              fill=C["dim"], font=("Arial", 12), justify="center")

        # Légende dépôts
        leg_dot = ctk.CTkFrame(col_dot, fg_color="transparent")
        leg_dot.pack(pady=(8, 0), anchor="w")
        for idx, (cat, montant) in enumerate(
                sorted(depots_cat.items(), key=lambda x: x[1], reverse=True)):
            pct = montant / total_dep_tx * 100 if total_dep_tx > 0 else 0
            col_hex = COULEURS_HEX[idx % len(COULEURS_HEX)]
            row = ctk.CTkFrame(leg_dot, fg_color="transparent")
            row.pack(anchor="w", pady=1)
            tk.Label(row, bg=col_hex, width=2, height=1).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=f"{cat}  {pct:.1f}%  (€{montant:,.2f})",
                         font=("Arial", 10), text_color=C["dim"]).pack(side="left")

        # ── Cartes par catégorie ──────────────────────────────
        ctk.CTkLabel(page, text="Détail par catégorie",
                     font=("Arial", 15, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=24, pady=(16, 6))

        toutes_cats = sorted(
            set(list(depenses_cat.keys()) + list(depots_cat.keys()))
        )

        if not toutes_cats:
            ctk.CTkLabel(page, text="Aucune transaction enregistrée.",
                         font=("Arial", 13), text_color=C["dim"]).pack(pady=16)
        else:
            grid = ctk.CTkFrame(page, fg_color="transparent")
            grid.pack(fill="x", padx=24, pady=(0, 16))
            cols = 3
            for i in range(cols):
                grid.columnconfigure(i, weight=1)

            for idx, cat in enumerate(toutes_cats):
                dep = depenses_cat.get(cat, 0.0)
                dot = depots_cat.get(cat, 0.0)
                pct_dep = dep / total_dep * 100 if total_dep > 0 else 0
                pct_dot = dot / total_dep_tx * 100 if total_dep_tx > 0 else 0
                col_hex = COULEURS_HEX[idx % len(COULEURS_HEX)]

                cadre = ctk.CTkFrame(grid, fg_color=C["carte"], corner_radius=10,
                                     border_width=1, border_color=C["bordure"])
                cadre.grid(row=idx // cols, column=idx % cols, sticky="nsew",
                           padx=(0 if idx % cols == 0 else 8, 0), pady=(0, 8))

                # Barre colorée en haut
                ctk.CTkFrame(cadre, fg_color=col_hex, height=4,
                             corner_radius=0).pack(fill="x")

                ctk.CTkLabel(cadre, text=cat, font=("Arial", 12, "bold"),
                             text_color=C["texte"]).pack(anchor="w", padx=14, pady=(10, 0))

                if dep > 0:
                    ctk.CTkLabel(cadre,
                                 text=f"↓ Dépenses : €{dep:,.2f}  ({pct_dep:.1f}%)",
                                 font=("Arial", 10), text_color=C["rouge"]).pack(
                        anchor="w", padx=14, pady=(2, 0))
                if dot > 0:
                    ctk.CTkLabel(cadre,
                                 text=f"↑ Dépôts   : €{dot:,.2f}  ({pct_dot:.1f}%)",
                                 font=("Arial", 10), text_color=C["vert"]).pack(
                        anchor="w", padx=14, pady=(2, 0))

                solde_cat = dot - dep
                coul_s = C["vert"] if solde_cat >= 0 else C["rouge"]
                signe  = "+" if solde_cat >= 0 else ""
                ctk.CTkLabel(cadre,
                             text=f"Net : {signe}€{solde_cat:,.2f}",
                             font=("Arial", 11, "bold"),
                             text_color=coul_s).pack(anchor="w", padx=14, pady=(4, 12))

        # ── Totaux ────────────────────────────────────────────
        ctk.CTkFrame(page, height=1, fg_color=C["bordure"]).pack(
            fill="x", padx=24, pady=(4, 8))

        tot_frame = ctk.CTkFrame(page, fg_color="transparent")
        tot_frame.pack(fill="x", padx=24, pady=(0, 28))
        for i in range(3):
            tot_frame.columnconfigure(i, weight=1)

        for i, (titre, val, col) in enumerate([
            ("Total dépensé",  f"€{total_dep:,.2f}",    C["rouge"]),
            ("Total déposé",   f"€{total_dep_tx:,.2f}", C["vert"]),
            ("Solde net",      f"{'+'if total_dep_tx>=total_dep else ''}€{total_dep_tx-total_dep:,.2f}",
             C["vert"] if total_dep_tx >= total_dep else C["rouge"]),
        ]):
            c2 = ctk.CTkFrame(tot_frame, fg_color=C["carte"], corner_radius=10,
                              border_width=1, border_color=C["bordure"])
            c2.grid(row=0, column=i, sticky="nsew",
                    padx=(0 if i == 0 else 8, 0))
            ctk.CTkLabel(c2, text=titre, font=("Arial", 11),
                         text_color=C["dim"]).pack(anchor="w", padx=14, pady=(12, 0))
            ctk.CTkLabel(c2, text=val, font=("Arial", 18, "bold"),
                         text_color=col).pack(anchor="w", padx=14, pady=(2, 14))

    def _dessiner_camembert(self, canvas, data: dict, total: float, couleurs: list):
        """Dessine un camembert sur un Canvas tkinter."""
        import math
        W, H  = 220, 220
        cx, cy, r = W // 2, H // 2, 85
        angle = -90.0  # départ en haut

        items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        for idx, (cat, val) in enumerate(items):
            pct   = val / total if total > 0 else 0
            sweep = pct * 360
            col   = couleurs[idx % len(couleurs)]
            if sweep >= 359.9:
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                   fill=col, outline=C["fond"], width=2)
            else:
                canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                  start=angle, extent=sweep,
                                  fill=col, outline=C["fond"], width=2,
                                  style="pieslice")
            # Label % au centre de la part si assez grande
            if pct > 0.07:
                mid_a = math.radians(-(angle + sweep / 2))
                lx = cx + (r * 0.65) * math.cos(mid_a)
                ly = cy + (r * 0.65) * math.sin(mid_a)
                canvas.create_text(lx, ly, text=f"{pct*100:.0f}%",
                                   fill="white", font=("Arial", 9, "bold"))
            angle += sweep

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
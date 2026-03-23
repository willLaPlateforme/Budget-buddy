import tkinter as tk
import customtkinter as ctk
from transactions import (
    deposer, retirer, transferer,
    get_historique, filtrer_transactions, get_solde,
    TYPES_VALIDES, CATEGORIES_VALIDES,
)
from database import get_comptes_user

C = {
    "fond":    "#0D1117",
    "panneau": "#161B22",
    "carte":   "#1C2333",
    "bleu":    "#3B82F6",
    "vert":    "#22C55E",
    "rouge":   "#EF4444",
    "orange":  "#F59E0B",
    "cyan":    "#06B6D4",
    "texte":   "#F1F5F9",
    "dim":     "#64748B",
    "bordure": "#2D3748",
}
TYPE_COLORS = {"dépôt": C["vert"], "retrait": C["rouge"], "transfert": C["orange"]}


#  Popup formulaire opération 

class PopupOperation(ctk.CTkToplevel):
    MODES = {
        "depot":     ("Nouveau dépôt",     C["vert"],   "Déposer"),
        "retrait":   ("Nouveau retrait",   C["rouge"],  "Retirer"),
        "transfert": ("Nouveau transfert", C["orange"], "Transférer"),
    }

    def __init__(self, parent, mode, compte_id, user_id, on_done):
        super().__init__(parent)
        self.mode, self.compte_id, self.on_done = mode, compte_id, on_done
        self.user_id = user_id
        titre, self.color, self.btn_lbl = self.MODES[mode]
        self.title(titre)
        self.geometry("420x500")
        self.configure(fg_color=C["fond"])
        self.resizable(False, False)
        self.grab_set()
        self._build(titre)

    def _build(self, titre):
        ctk.CTkFrame(self, fg_color=self.color, height=4,
                     corner_radius=0).pack(fill="x")
        fr = ctk.CTkFrame(self, fg_color="transparent")
        fr.pack(fill="both", expand=True, padx=28, pady=20)
        ctk.CTkLabel(fr, text=titre, font=("Arial", 18, "bold"),
                     text_color=self.color).pack(anchor="w", pady=(0, 14))

        def row(lbl, ph, show=""):
            ctk.CTkLabel(fr, text=lbl, font=("Arial", 10),
                         text_color=C["dim"], anchor="w").pack(anchor="w")
            e = ctk.CTkEntry(fr, placeholder_text=ph, height=36, corner_radius=8,
                             border_color=C["bordure"], fg_color=C["panneau"], show=show)
            e.pack(fill="x", pady=(2, 8))
            return e

        self.e_montant = row("Montant (€)", "0.00")
        self.e_desc    = row("Description", "Ex : courses...")

        ctk.CTkLabel(fr, text="Catégorie", font=("Arial", 10),
                     text_color=C["dim"], anchor="w").pack(anchor="w")
        self.v_cat = tk.StringVar(value=CATEGORIES_VALIDES[0])
        ctk.CTkComboBox(fr, variable=self.v_cat, values=list(CATEGORIES_VALIDES),
                        height=36, corner_radius=8, border_color=C["bordure"],
                        fg_color=C["panneau"], button_color=C["bleu"],
                        dropdown_fg_color=C["carte"],
                        dropdown_hover_color=C["panneau"]).pack(fill="x", pady=(2, 8))

        if self.mode == "transfert":
            ctk.CTkLabel(fr, text="Compte destinataire", font=("Arial", 10),
                         text_color=C["dim"], anchor="w").pack(anchor="w")
            from database import get_comptes_user
            tous_comptes = get_comptes_user(self.user_id)
            autres = [c for c in tous_comptes if c["id"] != self.compte_id]
            if autres:
                noms_dest = [f"{c['libelle']} (#{c['id']}) — €{float(c['solde']):,.2f}"
                             for c in autres]
                self._comptes_dest = autres
                self.v_dest = tk.StringVar(value=noms_dest[0])
                ctk.CTkComboBox(fr, variable=self.v_dest, values=noms_dest,
                                height=36, corner_radius=8,
                                border_color=C["bordure"], fg_color=C["panneau"],
                                button_color=C["bleu"],
                                dropdown_fg_color=C["carte"],
                                dropdown_hover_color=C["panneau"]).pack(fill="x", pady=(2, 8))
            else:
                self._comptes_dest = []
                self.v_dest = tk.StringVar(value="")
                ctk.CTkLabel(fr, text="⚠️ Aucun autre compte disponible.",
                             font=("Arial", 11), text_color=C["orange"]).pack(anchor="w")

        self.lbl_msg = ctk.CTkLabel(fr, text="", font=("Arial", 11),
                                    text_color=C["rouge"], wraplength=360)
        self.lbl_msg.pack(pady=(4, 0))

        btn_r = ctk.CTkFrame(fr, fg_color="transparent")
        btn_r.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(btn_r, text=self.btn_lbl, height=40, fg_color=self.color,
                      corner_radius=8, font=("Arial", 12, "bold"),
                      command=self._submit).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_r, text="Annuler", height=40, fg_color=C["carte"],
                      corner_radius=8, font=("Arial", 12),
                      command=self.destroy).pack(side="left")

    def _submit(self):
        try:
            montant = float(self.e_montant.get().replace(",", "."))
            desc    = self.e_desc.get().strip() or self.mode.capitalize()
            cat     = self.v_cat.get()
            if   self.mode == "depot":
                deposer(self.compte_id, montant, desc, cat)
            elif self.mode == "retrait":
                retirer(self.compte_id, montant, desc, cat)
            elif self.mode == "transfert":
                if not self._comptes_dest:
                    raise ValueError("Aucun compte destinataire disponible.")
                # Trouver le compte sélectionné dans la liste
                dest_id = None
                for c in self._comptes_dest:
                    label = f"{c['libelle']} (#{c['id']}) — €{float(c['solde']):,.2f}"
                    if self.v_dest.get() == label:
                        dest_id = c["id"]
                        break
                if dest_id is None:
                    dest_id = self._comptes_dest[0]["id"]
                transferer(self.compte_id, dest_id, montant, desc, cat)
            self.lbl_msg.configure(text="✓ Opération effectuée.", text_color=C["vert"])
            self.after(800, lambda: (self.destroy(), self.on_done()))
        except (ValueError, TypeError) as e:
            self.lbl_msg.configure(text=str(e), text_color=C["rouge"])


#  Page Transactions dans Window.py

class PageTransactions(ctk.CTkFrame):
    """Utilisée par Window.py : PageTransactions(parent, user)"""

    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color=C["fond"])
        self.user    = user
        self.comptes = get_comptes_user(user["id"])
        self.compte_actif     = self.comptes[0]["id"] if self.comptes else None
        self._filtres_ouverts = False
        self._build()

    def _build(self):
        # ── En-tête ──
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(20, 0))

        g = ctk.CTkFrame(top, fg_color="transparent")
        g.pack(side="left", fill="y")
        ctk.CTkLabel(g, text="Transactions", font=("Arial", 22, "bold"),
                     text_color=C["texte"]).pack(anchor="w")
        self.lbl_sub = ctk.CTkLabel(g, text="", font=("Arial", 12),
                                    text_color=C["dim"])
        self.lbl_sub.pack(anchor="w")

        dr = ctk.CTkFrame(top, fg_color="transparent")
        dr.pack(side="right")
        # Sélecteur de compte — toujours visible
        noms = [f"{c['libelle']} (#{c['id']})" for c in self.comptes]
        self.v_compte = tk.StringVar(value=noms[0] if noms else "")
        self.combo_compte = ctk.CTkComboBox(
            dr, variable=self.v_compte,
            values=noms if noms else ["Aucun compte"],
            width=240, height=36, fg_color=C["carte"],
            border_color=C["bordure"], button_color=C["bleu"],
            dropdown_fg_color=C["carte"],
            dropdown_hover_color=C["panneau"],
            command=self._changer_compte,
        )
        self.combo_compte.pack(pady=(0, 6))

        sf = ctk.CTkFrame(dr, fg_color=C["carte"], corner_radius=10,
                          border_width=1, border_color=C["bordure"])
        sf.pack()
        ctk.CTkLabel(sf, text="Solde", font=("Arial", 10),
                     text_color=C["dim"]).pack(padx=16, pady=(10, 0))
        self.lbl_solde = ctk.CTkLabel(sf, text="—", font=("Arial", 20, "bold"),
                                      text_color=C["texte"])
        self.lbl_solde.pack(padx=16, pady=(2, 10))

        # ── Boutons d'action ──
        ac = ctk.CTkFrame(self, fg_color="transparent")
        ac.pack(fill="x", padx=28, pady=12)
        ctk.CTkButton(ac, text="＋  Dépôt",    width=120, height=38, fg_color=C["vert"],
                      corner_radius=8, font=("Arial", 12, "bold"),
                      command=lambda: self._popup("depot")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(ac, text="－  Retrait",  width=120, height=38, fg_color=C["rouge"],
                      corner_radius=8, font=("Arial", 12, "bold"),
                      command=lambda: self._popup("retrait")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(ac, text="⇄  Transfert",width=130, height=38, fg_color=C["orange"],
                      corner_radius=8, font=("Arial", 12, "bold"),
                      command=lambda: self._popup("transfert")).pack(side="left", padx=(0, 16))
        ctk.CTkFrame(ac, fg_color=C["bordure"], width=1).pack(side="left", fill="y", padx=8)
        ctk.CTkButton(ac, text="🔍  Filtres",  width=110, height=38, fg_color=C["bleu"],
                      corner_radius=8, font=("Arial", 12, "bold"),
                      command=self._toggle_filtres).pack(side="left", padx=(8, 0))
        self.lbl_nb = ctk.CTkLabel(ac, text="", font=("Arial", 11), text_color=C["dim"])
        self.lbl_nb.pack(side="right")

        #  Panneau filtres (caché par défaut) 
        self.panel_filtres = ctk.CTkFrame(self, fg_color=C["panneau"], corner_radius=10,
                                           border_width=1, border_color=C["bordure"])
        self._build_filtres()

        #  Tableau 
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=(4, 20))

        hdr = ctk.CTkFrame(wrap, fg_color=C["panneau"], corner_radius=8)
        hdr.pack(fill="x", pady=(0, 2))
        for txt, w in [("Référence",150),("Date",90),("Type",90),
                       ("Catégorie",100),("Description",0),("Montant",120)]:
            ctk.CTkLabel(hdr, text=txt, font=("Arial", 10, "bold"), text_color=C["dim"],
                         width=w if w else 1, anchor="w").pack(side="left", padx=10, pady=8)

        self.scroll = ctk.CTkScrollableFrame(wrap, fg_color=C["carte"], corner_radius=10,
                                              border_width=1, border_color=C["bordure"])
        self.scroll.pack(fill="both", expand=True)
        self._charger()

    def _build_filtres(self):
        f = self.panel_filtres
        ctk.CTkLabel(f, text="Filtres avancés", font=("Arial", 13, "bold"),
                     text_color=C["texte"]).pack(anchor="w", padx=16, pady=(12, 4))
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)

        def hf(parent, lbl, ph="", w=150):
            col = ctk.CTkFrame(parent, fg_color="transparent")
            col.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(col, text=lbl, font=("Arial", 9), text_color=C["dim"]).pack(anchor="w")
            e = ctk.CTkEntry(col, placeholder_text=ph, height=32, width=w, corner_radius=6,
                             border_color=C["bordure"], fg_color=C["panneau"])
            e.pack(anchor="w", pady=(2, 0))
            return e

        def hc(parent, lbl, opts, w=140):
            col = ctk.CTkFrame(parent, fg_color="transparent")
            col.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(col, text=lbl, font=("Arial", 9), text_color=C["dim"]).pack(anchor="w")
            v = tk.StringVar(value=opts[0])
            ctk.CTkComboBox(col, variable=v, values=opts, width=w, height=32, corner_radius=6,
                            border_color=C["bordure"], fg_color=C["panneau"],
                            button_color=C["bleu"], dropdown_fg_color=C["carte"],
                            dropdown_hover_color=C["panneau"]).pack(pady=(2, 0))
            return v

        self.ff_debut = hf(row, "Date début", "AAAA-MM-JJ")
        self.ff_fin   = hf(row, "Date fin",   "AAAA-MM-JJ")
        self.v_type   = hc(row, "Type",
                           ["Tous"] + [t.capitalize() for t in TYPES_VALIDES])
        self.v_cat    = hc(row, "Catégorie",
                           ["Toutes"] + [c.capitalize() for c in CATEGORIES_VALIDES], 150)
        self.v_tri    = hc(row, "Tri montant",
                           ["Défaut", "Croissant ↑", "Décroissant ↓"], 150)

        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(4, 12))
        ctk.CTkButton(row2, text="Rechercher", width=120, height=32, fg_color=C["bleu"],
                      corner_radius=6, font=("Arial", 11, "bold"),
                      command=self._filtrer).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row2, text="Réinitialiser", width=110, height=32, fg_color=C["carte"],
                      corner_radius=6, font=("Arial", 11),
                      command=self._reset_filtres).pack(side="left")

    def _charger(self, transactions=None):
        for w in self.scroll.winfo_children():
            w.destroy()

        if transactions is None and self.compte_actif:
            transactions = get_historique(self.compte_actif)
        transactions = transactions or []

        # Solde
        try:
            s  = get_solde(self.compte_actif)
            sg = "+" if s > 0 else ""
            self.lbl_solde.configure(text=f"{sg}{s:,.2f} €",
                                     text_color=C["vert"] if s >= 0 else C["rouge"])
        except Exception:
            pass

        n = len(transactions)
        self.lbl_sub.configure(text=f"{n} opération(s)")
        self.lbl_nb.configure(text=f"{n} résultat(s)" if self._filtres_ouverts else "")

        if not transactions:
            ctk.CTkLabel(self.scroll, text="Aucune transaction.",
                         font=("Arial", 12), text_color=C["dim"]).pack(pady=40)
            return

        for i, t in enumerate(transactions):
            bg = C["carte"] if i % 2 == 0 else C["panneau"]
            ct = TYPE_COLORS.get(t.type_op, C["dim"])
            cm = C["vert"] if t.montant >= 0 else C["rouge"]
            sg = "+" if t.montant >= 0 else ""
            lig = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=6, height=40)
            lig.pack(fill="x", pady=1, padx=2)
            lig.pack_propagate(False)
            for txt, w, col, bold in [
                (t.reference[:18],         150, C["dim"],   False),
                (t.date,                    90, C["dim"],   False),
                (t.type_op.capitalize(),    90, ct,         True),
                (t.categorie.capitalize(), 100, C["dim"],   False),
                (t.description[:28],         0, C["texte"], False),
                (f"{sg}{t.montant:,.2f} €", 120, cm,        True),
            ]:
                ctk.CTkLabel(lig, text=txt,
                             font=("Arial", 10, "bold") if bold else ("Arial", 10),
                             text_color=col, width=w if w else 1,
                             anchor="w").pack(side="left", padx=10)

    def _toggle_filtres(self):
        self._filtres_ouverts = not self._filtres_ouverts
        if self._filtres_ouverts:
            self.panel_filtres.pack(fill="x", padx=28, pady=(0, 8),
                                    before=self.scroll.master)
        else:
            self.panel_filtres.pack_forget()
            self._charger()

    def _filtrer(self):
        tm  = {"Tous": None}
        tm.update({t.capitalize(): t for t in TYPES_VALIDES})
        cm  = {"Toutes": None}
        cm.update({c.capitalize(): c for c in CATEGORIES_VALIDES})
        trm = {"Défaut": None, "Croissant ↑": "asc", "Décroissant ↓": "desc"}
        try:
            res = filtrer_transactions(
                self.compte_actif,
                date_debut  = self.ff_debut.get().strip() or None,
                date_fin    = self.ff_fin.get().strip()   or None,
                type_op     = tm.get(self.v_type.get()),
                categorie   = cm.get(self.v_cat.get()),
                tri_montant = trm.get(self.v_tri.get()),
            )
            self._charger(res)
        except ValueError:
            pass

    def _reset_filtres(self):
        self.ff_debut.delete(0, "end")
        self.ff_fin.delete(0, "end")
        self.v_type.set("Tous")
        self.v_cat.set("Toutes")
        self.v_tri.set("Défaut")
        self._charger()

    def _popup(self, mode):
        if not self.compte_actif:
            return
        PopupOperation(self, mode, self.compte_actif,
                       self.user["id"], self._charger)

    def _changer_compte(self, choix):
        for c in self.comptes:
            if f"#{c['id']}" in choix:
                self.compte_actif = c["id"]
                break
        self._charger()

    def rafraichir(self):
        """Appelé par Window.py lors du changement d'onglet."""
        self.comptes = get_comptes_user(self.user["id"])
        if self.comptes:
            if not self.compte_actif:
                self.compte_actif = self.comptes[0]["id"]
            # Mettre à jour la liste déroulante des comptes
            try:
                noms = [f"{c['libelle']} (#{c['id']})" for c in self.comptes]
                self.combo_compte.configure(values=noms)
                # Garder le compte actif sélectionné
                for c in self.comptes:
                    if c["id"] == self.compte_actif:
                        self.v_compte.set(f"{c['libelle']} (#{c['id']})")
                        break
            except Exception:
                pass
        self._charger()

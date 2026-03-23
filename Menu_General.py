"""
Budget Buddy — Menu_General.py
Constantes partagées, widgets KPI/alertes/comptes, graphique barres.
Pas d'import Window (évite l'import circulaire).
"""

import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

PALETTE_COMPTES = [C["bleu"], C["vert"], C["rouge"], C["cyan"], C["orange"]]


def carte_kpi(parent, titre, valeur, couleur):
    cadre = ctk.CTkFrame(parent, fg_color=C["carte"], corner_radius=10,
                         border_width=1, border_color=C["bordure"])
    ctk.CTkLabel(cadre, text=titre, font=("Arial", 11),
                 text_color=C["dim"]).pack(anchor="w", padx=14, pady=(12, 0))
    ctk.CTkLabel(cadre, text=valeur, font=("Arial", 20, "bold"),
                 text_color=couleur).pack(anchor="w", padx=14, pady=(2, 14))
    return cadre


def carte_alerte(parent, icone, titre, description, couleur):
    cadre = ctk.CTkFrame(parent, fg_color=C["carte"], corner_radius=10,
                         border_width=1, border_color=couleur)
    ligne = ctk.CTkFrame(cadre, fg_color="transparent")
    ligne.pack(fill="x", padx=12, pady=(10, 2))
    ctk.CTkLabel(ligne, text=icone, font=("Arial", 15)).pack(side="left")
    ctk.CTkLabel(ligne, text=titre, font=("Arial", 11, "bold"),
                 text_color=couleur).pack(side="left", padx=6)
    ctk.CTkLabel(cadre, text=description, font=("Arial", 10),
                 text_color=C["dim"]).pack(anchor="w", padx=12, pady=(0, 10))
    return cadre


def carte_compte(parent, nom, solde, couleur):
    cadre = ctk.CTkFrame(parent, fg_color=C["carte"], corner_radius=10,
                         border_width=1, border_color=C["bordure"])
    ctk.CTkFrame(cadre, fg_color=couleur, height=4,
                 corner_radius=10).pack(fill="x", padx=1, pady=(1, 0))
    ctk.CTkLabel(cadre, text=nom, font=("Arial", 11),
                 text_color=C["dim"]).pack(anchor="w", padx=12, pady=(8, 0))
    couleur_solde = C["rouge"] if solde < 0 else C["texte"]
    signe = "−" if solde < 0 else ""
    ctk.CTkLabel(cadre, text=f"{signe}€{abs(solde):,.2f}",
                 font=("Arial", 16, "bold"),
                 text_color=couleur_solde).pack(anchor="w", padx=12, pady=(4, 12))
    return cadre


class GraphiqueBarres(tk.Canvas):
    """Histogramme Revenus vs Dépenses avec données dynamiques."""

    def __init__(self, parent, mois=None, revenus=None, depenses=None, **kwargs):
        super().__init__(parent, bg=C["carte"], highlightthickness=0, **kwargs)
        self.mois     = mois     or ["—"]
        self.revenus  = revenus  or [0]
        self.depenses = depenses or [0]
        self.bind("<Configure>", lambda e: self._dessiner())

    def mettre_a_jour(self, mois, revenus, depenses):
        self.mois, self.revenus, self.depenses = mois, revenus, depenses
        self._dessiner()

    def _dessiner(self):
        self.delete("all")
        W, H = self.winfo_width(), self.winfo_height()
        if W < 10 or H < 10:
            return

        ml, mr, mt, mb = 56, 20, 30, 45
        larg = W - ml - mr
        haut = H - mt - mb
        vmax = max(max(self.revenus or [1]), max(self.depenses or [1])) * 1.2 or 1

        for i in range(5):
            y = mt + haut - haut * i / 4
            self.create_line(ml, y, W - mr, y, fill=C["bordure"], dash=(4, 6))
            v = int(vmax * i / 4)
            self.create_text(ml - 5, y,
                             text=f"{v//1000}k" if v >= 1000 else str(v),
                             fill=C["dim"], font=("Arial", 9), anchor="e")

        n  = max(len(self.mois), 1)
        bw = max(6, (larg / n) * 0.28)
        for i, mois in enumerate(self.mois):
            xc = ml + (i + 0.5) * larg / n
            yb = mt + haut
            hr = (self.revenus[i]  / vmax * haut) if i < len(self.revenus)  else 0
            hd = (self.depenses[i] / vmax * haut) if i < len(self.depenses) else 0
            self.create_rectangle(xc-bw-2, yb-hr, xc-2,    yb, fill=C["vert"],  outline="")
            self.create_rectangle(xc+2,    yb-hd, xc+2+bw, yb, fill=C["rouge"], outline="")
            self.create_text(xc, H - mb + 14, text=mois, fill=C["dim"], font=("Arial", 9))

        self.create_rectangle(ml,    8, ml+12, 18, fill=C["vert"],  outline="")
        self.create_text(ml+16, 13, text="Revenus",  fill=C["dim"], font=("Arial", 10), anchor="w")
        self.create_rectangle(ml+80, 8, ml+92, 18, fill=C["rouge"], outline="")
        self.create_text(ml+96, 13, text="Dépenses", fill=C["dim"], font=("Arial", 10), anchor="w")

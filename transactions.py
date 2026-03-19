

from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass, field
from database import get_connection

TYPES_VALIDES = ("dépôt", "retrait", "transfert")
CATEGORIES_VALIDES = (
    "loisir", "repas", "transport", "logement",
    "santé", "salaire", "épargne", "pot-de-vin", "autre",
)


#  Modèle 

@dataclass
class Transaction:
    """Représente une transaction bancaire."""
    reference      : str
    description    : str
    montant        : float
    date           : str
    type_op        : str
    categorie      : str           = "autre"
    compte_id      : int           = 0
    compte_dest_id : Optional[int] = None
    id             : Optional[int] = field(default=None)

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ["id","reference","description","montant","date",
                 "type_op","categorie","compte_id","compte_dest_id"]}


#  Helpers internes 

def _row_to_transaction(row: dict) -> Transaction:
    return Transaction(
        id=row["id"], reference=row["reference"],
        description=row["description"],
        montant=float(row["montant"]),
        date=str(row["date"]),
        type_op=row["type_op"],
        categorie=row["categorie"],
        compte_id=row["compte_id"],
        compte_dest_id=row.get("compte_dest_id"),
    )

def _get_solde(cursor, compte_id: int) -> float:
    cursor.execute("SELECT solde FROM comptes WHERE id = %s", (compte_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Compte #{compte_id} introuvable.")
    return float(row["solde"])

def _verifier_montant(montant: float):
    if montant <= 0:
        raise ValueError("Le montant doit être strictement positif.")

def _verifier_categorie(categorie: str):
    if categorie not in CATEGORIES_VALIDES:
        raise ValueError(f"Catégorie invalide : '{categorie}'.")

def _verifier_type(type_op: str):
    if type_op not in TYPES_VALIDES:
        raise ValueError(f"Type invalide : '{type_op}'.")

def _generer_reference(type_op: str) -> str:
    prefix = {"dépôt": "DEP", "retrait": "RET", "transfert": "TRF"}[type_op]
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]}"


# ── Opérations bancaires ──────────────────────────────────────

def deposer(compte_id: int, montant: float, description: str = "Dépôt",
            categorie: str = "autre") -> Transaction:
    """Crédite montant sur le compte. Retourne la Transaction."""
    _verifier_montant(montant)
    _verifier_categorie(categorie)

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        s = _get_solde(cursor, compte_id)
        cursor.execute("UPDATE comptes SET solde = %s WHERE id = %s",
                       (s + montant, compte_id))
        ref = _generer_reference("dépôt")
        auj = date.today().isoformat()
        cursor.execute(
            "INSERT INTO transactions"
            "(reference,description,montant,date,type_op,categorie,compte_id)"
            " VALUES(%s,%s,%s,%s,'dépôt',%s,%s)",
            (ref, description, montant, auj, categorie, compte_id))
        conn.commit()
        return Transaction(id=cursor.lastrowid, reference=ref,
            description=description, montant=montant, date=auj,
            type_op="dépôt", categorie=categorie, compte_id=compte_id)
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()


def retirer(compte_id: int, montant: float, description: str = "Retrait",
            categorie: str = "autre") -> Transaction:
    """Débite montant du compte. Lève ValueError si solde insuffisant."""
    _verifier_montant(montant)
    _verifier_categorie(categorie)

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        s = _get_solde(cursor, compte_id)
        if s < montant:
            raise ValueError(
                f"Solde insuffisant : {s:.2f}€ disponible, {montant:.2f}€ demandé.")
        cursor.execute("UPDATE comptes SET solde = %s WHERE id = %s",
                       (s - montant, compte_id))
        ref = _generer_reference("retrait")
        auj = date.today().isoformat()
        cursor.execute(
            "INSERT INTO transactions"
            "(reference,description,montant,date,type_op,categorie,compte_id)"
            " VALUES(%s,%s,%s,%s,'retrait',%s,%s)",
            (ref, description, -montant, auj, categorie, compte_id))
        conn.commit()
        return Transaction(id=cursor.lastrowid, reference=ref,
            description=description, montant=-montant, date=auj,
            type_op="retrait", categorie=categorie, compte_id=compte_id)
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()


def transferer(source_id: int, dest_id: int, montant: float,
               description: str = "Transfert", categorie: str = "autre") -> tuple:
    """Transfère montant de source vers dest. Retourne (tx_src, tx_dst)."""
    if source_id == dest_id:
        raise ValueError("Les comptes source et destination doivent être différents.")
    _verifier_montant(montant)
    _verifier_categorie(categorie)

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        ss = _get_solde(cursor, source_id)
        if ss < montant:
            raise ValueError(f"Solde insuffisant : {ss:.2f}€ disponible.")
        sd = _get_solde(cursor, dest_id)

        cursor.execute("UPDATE comptes SET solde = %s WHERE id = %s",
                       (ss - montant, source_id))
        cursor.execute("UPDATE comptes SET solde = %s WHERE id = %s",
                       (sd + montant, dest_id))

        auj = date.today().isoformat()
        rs  = _generer_reference("transfert")
        rd  = _generer_reference("transfert")

        cursor.execute(
            "INSERT INTO transactions"
            "(reference,description,montant,date,type_op,categorie,compte_id,compte_dest_id)"
            " VALUES(%s,%s,%s,%s,'transfert',%s,%s,%s)",
            (rs, description, -montant, auj, categorie, source_id, dest_id))
        id_src = cursor.lastrowid

        cursor.execute(
            "INSERT INTO transactions"
            "(reference,description,montant,date,type_op,categorie,compte_id,compte_dest_id)"
            " VALUES(%s,%s,%s,%s,'transfert',%s,%s,%s)",
            (rd, description, montant, auj, categorie, dest_id, source_id))
        id_dst = cursor.lastrowid

        conn.commit()
        t_src = Transaction(id=id_src, reference=rs, description=description,
            montant=-montant, date=auj, type_op="transfert",
            categorie=categorie, compte_id=source_id, compte_dest_id=dest_id)
        t_dst = Transaction(id=id_dst, reference=rd, description=description,
            montant=montant, date=auj, type_op="transfert",
            categorie=categorie, compte_id=dest_id, compte_dest_id=source_id)
        return t_src, t_dst
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()


# Lecture & filtrage ─

def get_historique(compte_id: int) -> list:
    """Toutes les transactions du plus récent au plus ancien."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE compte_id = %s"
            " ORDER BY date DESC, id DESC",
            (compte_id,))
        return [_row_to_transaction(r) for r in cursor.fetchall()]
    finally:
        cursor.close(); conn.close()


def filtrer_transactions(compte_id: int, date_debut: Optional[str] = None,
                         date_fin: Optional[str] = None,
                         type_op: Optional[str] = None,
                         categorie: Optional[str] = None,
                         tri_montant: Optional[str] = None) -> list:
    """
    Recherche multi-critères combinables.
      date_debut  : YYYY-MM-DD
      date_fin    : YYYY-MM-DD
      type_op     : 'dépôt' | 'retrait' | 'transfert'
      categorie   : ex. 'loisir', 'repas', ...
      tri_montant : 'asc' | 'desc'
    """
    if type_op:   _verifier_type(type_op)
    if categorie: _verifier_categorie(categorie)
    if tri_montant and tri_montant not in ("asc", "desc"):
        raise ValueError("tri_montant doit être 'asc' ou 'desc'.")

    q = "SELECT * FROM transactions WHERE compte_id = %s"
    p = [compte_id]

    if date_debut: q += " AND date >= %s";      p.append(date_debut)
    if date_fin:   q += " AND date <= %s";      p.append(date_fin)
    if type_op:    q += " AND type_op = %s";    p.append(type_op)
    if categorie:  q += " AND categorie = %s";  p.append(categorie)

    if tri_montant:
        q += f" ORDER BY ABS(montant) {'ASC' if tri_montant == 'asc' else 'DESC'}"
    else:
        q += " ORDER BY date DESC, id DESC"

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(q, p)
        return [_row_to_transaction(r) for r in cursor.fetchall()]
    finally:
        cursor.close(); conn.close()


def get_solde(compte_id: int) -> float:
    """Retourne le solde actuel d'un compte."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        return _get_solde(cursor, compte_id)
    finally:
        cursor.close(); conn.close()


def get_stats_mensuelles(compte_id: int) -> list:
    """Revenus et dépenses agrégés par mois (7 derniers mois)."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT DATE_FORMAT(date, '%%Y-%%m') AS mois,
                   SUM(CASE WHEN montant > 0 THEN montant ELSE 0 END)        AS revenus,
                   SUM(CASE WHEN montant < 0 THEN ABS(montant) ELSE 0 END)   AS depenses
            FROM transactions
            WHERE compte_id = %s
            GROUP BY mois
            ORDER BY mois DESC
            LIMIT 7
        """, (compte_id,))
        rows = cursor.fetchall()
        return [{"mois": r["mois"],
                 "revenus":  float(r["revenus"]  or 0),
                 "depenses": float(r["depenses"] or 0)} for r in reversed(rows)]
    finally:
        cursor.close(); conn.close()

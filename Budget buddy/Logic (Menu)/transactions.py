
import sqlite3
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional



#  Modèle de données


TYPES_VALIDES = ("dépôt", "retrait", "transfert")
CATEGORIES_VALIDES = (
    "loisir", "repas", "transport", "logement",
    "santé", "salaire", "épargne", "pot-de-vin", "autre"
)


@dataclass
class Transaction:
    """Représente une transaction bancaire."""
    reference: str
    description: str
    montant: float          # positif pour dépôt/transfert entrant, négatif pour retrait/transfert sortant
    date: str               # format ISO : YYYY-MM-DD
    type_op: str            # 'dépôt', 'retrait', 'transfert'
    categorie: str = "autre"
    compte_id: int = 0
    compte_dest_id: Optional[int] = None   # pour les transferts
    id: Optional[int] = field(default=None)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "reference": self.reference,
            "description": self.description,
            "montant": self.montant,
            "date": self.date,
            "type_op": self.type_op,
            "categorie": self.categorie,
            "compte_id": self.compte_id,
            "compte_dest_id": self.compte_dest_id,
        }



#  Connexion à la base de données


def get_connection(db_path: str = "budget_buddy.db") -> sqlite3.Connection:
    """Retourne une connexion SQLite avec les foreign keys activées."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_tables(db_path: str = "budget_buddy.db"):
    """Crée les tables si elles n'existent pas encore (pour les tests locaux)."""
    conn = get_connection(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                nom      TEXT NOT NULL,
                prenom   TEXT NOT NULL,
                email    TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comptes (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER NOT NULL REFERENCES users(id),
                solde    REAL NOT NULL DEFAULT 0.0,
                libelle  TEXT NOT NULL DEFAULT 'Compte principal'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                reference       TEXT NOT NULL,
                description     TEXT NOT NULL,
                montant         REAL NOT NULL,
                date            TEXT NOT NULL,
                type_op         TEXT NOT NULL CHECK(type_op IN ('dépôt','retrait','transfert')),
                categorie       TEXT NOT NULL DEFAULT 'autre',
                compte_id       INTEGER NOT NULL REFERENCES comptes(id),
                compte_dest_id  INTEGER REFERENCES comptes(id)
            )
        """)
    conn.close()



#  Helpers internes


def _row_to_transaction(row: sqlite3.Row) -> Transaction:
    return Transaction(
        id=row["id"],
        reference=row["reference"],
        description=row["description"],
        montant=row["montant"],
        date=row["date"],
        type_op=row["type_op"],
        categorie=row["categorie"],
        compte_id=row["compte_id"],
        compte_dest_id=row["compte_dest_id"],
    )


def _get_solde(conn: sqlite3.Connection, compte_id: int) -> float:
    row = conn.execute("SELECT solde FROM comptes WHERE id = ?", (compte_id,)).fetchone()
    if row is None:
        raise ValueError(f"Compte {compte_id} introuvable.")
    return row["solde"]


def _verifier_type(type_op: str):
    if type_op not in TYPES_VALIDES:
        raise ValueError(f"Type invalide '{type_op}'. Valeurs possibles : {TYPES_VALIDES}")


def _verifier_categorie(categorie: str):
    if categorie not in CATEGORIES_VALIDES:
        raise ValueError(f"Catégorie invalide '{categorie}'. Valeurs possibles : {CATEGORIES_VALIDES}")


def _verifier_montant(montant: float):
    if montant <= 0:
        raise ValueError("Le montant doit être strictement positif.")


def _generer_reference(type_op: str) -> str:
    prefix = {"dépôt": "DEP", "retrait": "RET", "transfert": "TRF"}[type_op]
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]}"



#  Opérations bancaires


def deposer(
    compte_id: int,
    montant: float,
    description: str = "Dépôt",
    categorie: str = "autre",
    db_path: str = "budget_buddy.db",
) -> Transaction:
    """
    Dépose `montant` sur le compte `compte_id`.
    Retourne la Transaction créée.
    """
    _verifier_montant(montant)
    _verifier_categorie(categorie)

    conn = get_connection(db_path)
    with conn:
        solde = _get_solde(conn, compte_id)
        nouveau_solde = solde + montant
        conn.execute("UPDATE comptes SET solde = ? WHERE id = ?", (nouveau_solde, compte_id))

        ref = _generer_reference("dépôt")
        aujourd_hui = date.today().isoformat()
        cur = conn.execute(
            """INSERT INTO transactions
               (reference, description, montant, date, type_op, categorie, compte_id)
               VALUES (?, ?, ?, ?, 'dépôt', ?, ?)""",
            (ref, description, montant, aujourd_hui, categorie, compte_id),
        )
        t = Transaction(
            id=cur.lastrowid,
            reference=ref,
            description=description,
            montant=montant,
            date=aujourd_hui,
            type_op="dépôt",
            categorie=categorie,
            compte_id=compte_id,
        )
    conn.close()
    return t


def retirer(
    compte_id: int,
    montant: float,
    description: str = "Retrait",
    categorie: str = "autre",
    db_path: str = "budget_buddy.db",
) -> Transaction:
    """
    Retire `montant` du compte `compte_id`.
    Lève une ValueError si solde insuffisant.
    """
    _verifier_montant(montant)
    _verifier_categorie(categorie)

    conn = get_connection(db_path)
    with conn:
        solde = _get_solde(conn, compte_id)
        if solde < montant:
            conn.close()
            raise ValueError(
                f"Solde insuffisant : {solde:.2f} € disponible, {montant:.2f} € demandé."
            )
        conn.execute("UPDATE comptes SET solde = ? WHERE id = ?", (solde - montant, compte_id))

        ref = _generer_reference("retrait")
        aujourd_hui = date.today().isoformat()
        cur = conn.execute(
            """INSERT INTO transactions
               (reference, description, montant, date, type_op, categorie, compte_id)
               VALUES (?, ?, ?, ?, 'retrait', ?, ?)""",
            (ref, description, -montant, aujourd_hui, categorie, compte_id),
        )
        t = Transaction(
            id=cur.lastrowid,
            reference=ref,
            description=description,
            montant=-montant,
            date=aujourd_hui,
            type_op="retrait",
            categorie=categorie,
            compte_id=compte_id,
        )
    conn.close()
    return t


def transferer(
    compte_source_id: int,
    compte_dest_id: int,
    montant: float,
    description: str = "Transfert",
    categorie: str = "autre",
    db_path: str = "budget_buddy.db",
) -> tuple[Transaction, Transaction]:
    """
    Transfère `montant` du compte source vers le compte destination.
    Retourne un tuple (transaction_débitée, transaction_créditée).
    """
    if compte_source_id == compte_dest_id:
        raise ValueError("Les comptes source et destination doivent être différents.")
    _verifier_montant(montant)
    _verifier_categorie(categorie)

    conn = get_connection(db_path)
    with conn:
        solde_src = _get_solde(conn, compte_source_id)
        if solde_src < montant:
            conn.close()
            raise ValueError(
                f"Solde insuffisant : {solde_src:.2f} € disponible, {montant:.2f} € demandé."
            )
        _get_solde(conn, compte_dest_id)  # vérifie que le compte destination existe

        conn.execute("UPDATE comptes SET solde = ? WHERE id = ?",
                     (solde_src - montant, compte_source_id))
        solde_dest = _get_solde(conn, compte_dest_id)
        conn.execute("UPDATE comptes SET solde = ? WHERE id = ?",
                     (solde_dest + montant, compte_dest_id))

        ref_src = _generer_reference("transfert")
        ref_dst = _generer_reference("transfert")
        aujourd_hui = date.today().isoformat()

        cur_src = conn.execute(
            """INSERT INTO transactions
               (reference, description, montant, date, type_op, categorie, compte_id, compte_dest_id)
               VALUES (?, ?, ?, ?, 'transfert', ?, ?, ?)""",
            (ref_src, description, -montant, aujourd_hui, categorie, compte_source_id, compte_dest_id),
        )
        cur_dst = conn.execute(
            """INSERT INTO transactions
               (reference, description, montant, date, type_op, categorie, compte_id, compte_dest_id)
               VALUES (?, ?, ?, ?, 'transfert', ?, ?, ?)""",
            (ref_dst, description, montant, aujourd_hui, categorie, compte_dest_id, compte_source_id),
        )

        t_src = Transaction(
            id=cur_src.lastrowid, reference=ref_src, description=description,
            montant=-montant, date=aujourd_hui, type_op="transfert",
            categorie=categorie, compte_id=compte_source_id, compte_dest_id=compte_dest_id,
        )
        t_dst = Transaction(
            id=cur_dst.lastrowid, reference=ref_dst, description=description,
            montant=montant, date=aujourd_hui, type_op="transfert",
            categorie=categorie, compte_id=compte_dest_id, compte_dest_id=compte_source_id,
        )
    conn.close()
    return t_src, t_dst



#  Lecture et filtrage de l'historique


def get_historique(
    compte_id: int,
    db_path: str = "budget_buddy.db",
) -> list[Transaction]:
    """Retourne toutes les transactions d'un compte, du plus récent au plus ancien."""
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM transactions WHERE compte_id = ? ORDER BY date DESC, id DESC",
        (compte_id,),
    ).fetchall()
    conn.close()
    return [_row_to_transaction(r) for r in rows]


def filtrer_transactions(
    compte_id: int,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    type_op: Optional[str] = None,
    categorie: Optional[str] = None,
    tri_montant: Optional[str] = None,   # 'asc' ou 'desc'
    db_path: str = "budget_buddy.db",
) -> list[Transaction]:
    """
    Recherche multi-critères sur l'historique d'un compte.

    Paramètres (tous optionnels, combinables) :
    - date_debut   : filtre les transactions à partir de cette date (YYYY-MM-DD)
    - date_fin     : filtre jusqu'à cette date (YYYY-MM-DD)
    - type_op      : 'dépôt', 'retrait' ou 'transfert'
    - categorie    : ex. 'loisir', 'repas', ...
    - tri_montant  : 'asc' (croissant) ou 'desc' (décroissant) sur la valeur absolue
    """
    if type_op:
        _verifier_type(type_op)
    if categorie:
        _verifier_categorie(categorie)
    if tri_montant and tri_montant not in ("asc", "desc"):
        raise ValueError("tri_montant doit être 'asc' ou 'desc'.")

    query = "SELECT * FROM transactions WHERE compte_id = ?"
    params: list = [compte_id]

    if date_debut:
        query += " AND date >= ?"
        params.append(date_debut)

    if date_fin:
        query += " AND date <= ?"
        params.append(date_fin)

    if type_op:
        query += " AND type_op = ?"
        params.append(type_op)

    if categorie:
        query += " AND categorie = ?"
        params.append(categorie)

    if tri_montant:
        order = "ASC" if tri_montant == "asc" else "DESC"
        query += f" ORDER BY ABS(montant) {order}"
    else:
        query += " ORDER BY date DESC, id DESC"

    conn = get_connection(db_path)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_transaction(r) for r in rows]


def get_solde(compte_id: int, db_path: str = "budget_buddy.db") -> float:
    """Retourne le solde actuel d'un compte."""
    conn = get_connection(db_path)
    solde = _get_solde(conn, compte_id)
    conn.close()
    return solde
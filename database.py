import mysql.connector
import bcrypt

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="PopulaireBank",
        password="StAliNe254vpQ!?",
        database="budget_buddy"
    )

def create_user(nom, prenom, email, password_hash, profile_picture):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO users (nom, prenom, email, password_hash, profile_picture)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nom, prenom, email, password_hash, profile_picture))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ── Helpers comptes ───────────────────────────────────────────

def get_comptes_user(user_id: int) -> list:
    """Retourne tous les comptes d'un utilisateur."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM comptes WHERE user_id = %s", (user_id,))
    comptes = cursor.fetchall()
    cursor.close()
    conn.close()
    return comptes


def creer_compte_par_defaut(user_id: int) -> int:
    """Crée un compte principal si l'utilisateur n'en a pas encore."""
    comptes = get_comptes_user(user_id)
    if comptes:
        return comptes[0]["id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comptes (user_id, libelle, solde) VALUES (%s, %s, %s)",
        (user_id, "Compte principal", 0.0),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def add_compte(user_id: int, libelle: str) -> int:
    """Ajoute un nouveau compte bancaire. Retourne son id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comptes (user_id, libelle, solde) VALUES (%s, %s, %s)",
        (user_id, libelle.strip(), 0.0),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id
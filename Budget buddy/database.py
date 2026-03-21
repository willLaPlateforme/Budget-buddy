import mysql.connector
import bcrypt

# Poivre global
PEPPER = "X9f$2!k@P0ivreUltraSecret"

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
    # Ajouter le poivre
    password_peppered = (password + PEPPER).encode('utf-8')

    # Hasher avec bcrypt (qui ajoute déjà un sel)
    hashed = bcrypt.hashpw(password_peppered, bcrypt.gensalt())

    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    # Ajouter le poivre avant vérification
    password_peppered = (password + PEPPER).encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')

    return bcrypt.checkpw(password_peppered, hashed_bytes)

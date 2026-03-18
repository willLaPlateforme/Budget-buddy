import mysql.connector
import bcrypt

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="",
        password="",
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

    # Convertir le mot de passe en bytes
    password_bytes= password.encode('utf-8')

    # Générer un sel et hasher le mot de passe
    hashed= bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Retourner le hash sous forme de string
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    password_bytes= password.encode('utf-8')
    hashed_bytes= hashed.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)

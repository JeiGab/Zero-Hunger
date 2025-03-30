import mysql.connector as sql
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
}

try:
    con = sql.connect(**DB_CONFIG)
    cursor = con.cursor()
    cursor.execute('SELECT DATABASE()')
    row = cursor.fetchone()
    print('Conexión exitosa desde la base de datos')
    con.close()
except Exception as e:
    print(f'Error en la conexión: {e}')

def insert_user(data):
    try:
        name, email, password, role, empresa_nombre = data 
                        
        if email_exists(email):
            print('Error: Email ya registrado')
            return 'Email ya registrado'
        
        
        if role not in ['empresa donante', 'organizacion benefica']:
            print('Error: Rol inválido')
            return 'Rol inválido'
        
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("INSERT INTO user (name, email, password, role, empresa_nombre) VALUES (%s, %s, %s, %s, %s)", (name, email, password, role, empresa_nombre))
        con.commit()
        con.close()
        print('Usuario insertado')
        return True
    except Exception as e:
        print(f'Error en la inserción: {e}')
        return False


def insert_admin(data):
    try:
        name, email, password, role = data 

        if email_exists(email):
            print('Error: Email ya registrado')
            return 'Email ya registrado'
        
        role = 'administrador'
        
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, password, role))
        con.commit()
        con.close()
        print('Usuario insertado')
        return True
    except Exception as e:
        print(f'Error en la inserción: {e}')
        return False

def ocultar_usuario_por_email(email):
    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("UPDATE user SET hidden = 1 WHERE email = %s", (email,))
        con.commit()
        con.close()
        print('Usuario ocultado')
        return True
    except Exception as e:
        print(f'Error al ocultar usuario: {e}')
        return False

def conectar_db():
    return sql.connect(**DB_CONFIG)


def email_exists(email):
    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        con.close()
        return user is not None
    except Exception as e:
        print(f'Error en la consulta: {e}')
        return False

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def validate_login(email,password):
    con = sql.connect(**DB_CONFIG)
    if con:
        cursor = con.cursor()
        cursor.execute("SELECT password FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        con.close()
        
        if user and check_password(password, user[0]):
            print('Login exitoso')
            return True
        else:
            print('Error: Credenciales inválidas')
            return False
    else:
        print('Error en la conexión')
        return False

def get_user_by_email(email):
    con = sql.connect(**DB_CONFIG)
    cursor = con.cursor()
    cursor.execute("SELECT id, name, email, password, role, empresa_nombre FROM user WHERE email = %s", (email,))
    row = cursor.fetchone()
    con.close()

    if row:
        return {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'password': row[3],
            'role': row[4],
            'empresa_nombre': row[5]
        }
    return None

def obtener_usuarios():
    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("SELECT id, name, email, role, empresa_nombre  FROM user WHERE hidden = 0")  # Mostrar solo usuarios visibles
        usuarios = cursor.fetchall()
        con.close()

        print("Usuarios visibles obtenidos:")
        return usuarios
    except Exception as e:
        print(f'Error al obtener usuarios: {e}')
        return []


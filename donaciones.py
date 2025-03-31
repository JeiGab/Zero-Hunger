from flask import flash
import mysql.connector as sql
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
    print('Conexión exitosa desde las donaciones')
    con.close()
except Exception as e:
    print(f'Error en la conexión: {e}')

def conectar_db():
    return sql.connect(**DB_CONFIG)

def agregar_donacion(empresa_nombre, correo_empresa, numero_contacto, tipo_alimento, cantidad_productos, estado_producto):
    try:
        con = conectar_db()
        cursor = con.cursor()

        query = """
        INSERT INTO donaciones (empresa_nombre, correo_empresa, numero_contacto, tipo_alimento, cantidad_productos, estado_producto, fecha_donacion)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        valores = (empresa_nombre, correo_empresa, numero_contacto, tipo_alimento, cantidad_productos, estado_producto)

        cursor.execute(query, valores)
        con.commit()
        con.close()

        return True
    except Exception as e:
        print(f'Error al agregar donación: {e}')
        return False

def eliminar_donacion(empresa_nombre, correo_empresa, tipo_alimento):
    try:
        con = conectar_db()
        cursor = con.cursor()
        
        query = """
        DELETE FROM donaciones 
        WHERE empresa_nombre = %s 
        AND correo_empresa = %s 
        AND tipo_alimento = %s
        """
        
        cursor.execute(query, (empresa_nombre, correo_empresa, tipo_alimento))
        con.commit()
        return cursor.rowcount > 0  # Retorna True si se eliminó alguna fila
        
    except Exception as e:
        print(f'Error al eliminar donación: {e}')
        return False
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def obtener_donaciones():
    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("SELECT empresa_nombre, correo_empresa, numero_contacto, tipo_alimento, cantidad_productos, estado_producto, fecha_donacion FROM donaciones")
        datos = cursor.fetchall()
        con.close()
        return datos
    except Exception as e:
        print(f'Error al obtener donaciones: {e}')
        return []

def agregar_solicitud(empresa_nombre, organizacion, tipo_alimento, cantidad_productos, estado_producto, correo_empresa, numero_contacto):
    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        query = """
        INSERT INTO solicitudes 
        (empresa_nombre, organizacion, tipo_alimento, cantidad_productos, estado_producto, correo_empresa, numero_contacto) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (empresa_nombre, organizacion, tipo_alimento, cantidad_productos, estado_producto, correo_empresa, numero_contacto))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(f"Error al agregar la solicitud: {e}")
        return False

def obtener_solicitudes():
    try:
        con = conectar_db()
        cursor = con.cursor()
        query = """
            SELECT 
                organizacion, tipo_alimento, cantidad_productos, 
                estado_producto, fecha_solicitud, empresa_nombre,
                correo_empresa, numero_contacto
            FROM 
                solicitudes
            ORDER BY 
                fecha_solicitud DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener solicitudes: {e}")
        return []
    
def agregar_aceptacion(empresa_nombre, organizacion, tipo_alimento, cantidad_productos, 
                      estado_producto, correo_empresa, numero_contacto):
    try:
        con = conectar_db()
        cursor = con.cursor()
        
        query = """
            INSERT INTO aceptaciones 
            (empresa_nombre, organizacion, tipo_alimento, cantidad_productos,
             estado_producto, correo_empresa, numero_contacto, fecha_aceptacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (empresa_nombre, organizacion, tipo_alimento, cantidad_productos,
                             estado_producto, correo_empresa, numero_contacto))
        con.commit()
        return True
    except Exception as e:
        print(f"Error al aceptar solicitud: {e}")
        return False
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def obtener_aceptaciones():
    try:
        con = conectar_db()
        cursor = con.cursor()
        query = """
            SELECT 
                empresa_nombre, organizacion, tipo_alimento, 
                cantidad_productos, estado_producto, fecha_aceptacion,
                correo_empresa, numero_contacto
            FROM 
                aceptaciones
            ORDER BY 
                fecha_aceptacion DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener aceptaciones: {e}")
        return []

def eliminar_solicitud(organizacion, tipo_alimento, cantidad_productos, estado_producto):
    try:
        con = conectar_db()
        cursor = con.cursor()
        
        query = """
            DELETE FROM solicitudes 
            WHERE organizacion = %s 
            AND tipo_alimento = %s 
            AND cantidad_productos = %s 
            AND estado_producto = %s
        """
        
        cursor.execute(query, (organizacion, tipo_alimento, cantidad_productos, estado_producto))
        con.commit()
        return cursor.rowcount > 0  # Retorna True si se eliminó alguna fila
    except Exception as e:
        print(f'Error al eliminar solicitud: {e}')
        return False
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
       
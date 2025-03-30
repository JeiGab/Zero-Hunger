from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from database import email_exists, ocultar_usuario_por_email, obtener_usuarios, insert_user, hash_password, get_user_by_email, check_password, insert_admin
from donaciones import  eliminar_solicitud, agregar_aceptacion, obtener_aceptaciones, eliminar_donacion, obtener_donaciones, obtener_solicitudes, agregar_solicitud, agregar_donacion
from functools import wraps
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

app = Flask(__name__)
app.secret_key = 'super secret key'  

try:
    con = sql.connect(**DB_CONFIG)
    cursor = con.cursor()
    cursor.execute('SELECT DATABASE()')
    row = cursor.fetchone()
    print('Conexión exitosa desde el archivo main')
    con.close()
except Exception as e:
    print(f'Error en la conexión: {e}')

@app.route('/')
def index():
    return render_template('index.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session or 'role' not in session or not session['email'] or not session['role']:
            session.clear() 
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email_exists(email):
            return jsonify({"success": False, "message": "El correo no está registrado."})

        user = get_user_by_email(email)
        if not check_password(password, user['password']):
            return jsonify({"success": False, "message": "Contraseña incorrecta."})

        if ocultar_usuario_por_email(email):
            print("Usuario ocultado correctamente.")

        session['email'] = user['email']
        session['role'] = user['role']
        session['empresa_nombre'] = user['empresa_nombre']

        if user['role'] == 'administrador':
            redirect_url = url_for('inicio_admin')
        elif user['role'] == 'empresa donante':
            redirect_url = url_for('inicio_donante')
            print(user['empresa_nombre'])
        elif user['role'] == 'organizacion benefica':
            redirect_url = url_for('inicio_benefica')
        else:
            return jsonify({"success": False, "message": "Rol inválido."})

        return jsonify({"success": True, "message": "Inicio de sesión exitoso.", "redirect": redirect_url})

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        empresa_nombre = request.form['empresa_nombre']

        # Validación de contraseña
        if len(password) < 6 or len(password) > 12:
            return jsonify({"success": False, "message": "La contraseña debe tener entre 6 y 12 caracteres."})

        # Verificar si el rol es válido
        if role not in ['empresa donante', 'organizacion benefica']:
            return jsonify({"success": False, "message": "Rol inválido."})

        # Verificar si el email ya existe
        if email_exists(email):
            return jsonify({"success": False, "message": "El correo ya está registrado."})


        # Hash de la contraseña antes de guardarla
        hashed_password = hash_password(password).decode('utf-8')

        # Intentar registrar el usuario
        result = insert_user((name, email, hashed_password, role, empresa_nombre))

        if result == True:
            return jsonify({"success": True, "message": "Usuario registrado con éxito."})
        else:
            return jsonify({"success": False, "message": "Error al registrar usuario."})

    return render_template('register.html')

@app.route('/logout')
def logout():
    email = session.get('email')
    if email:
        try:
            con = sql.connect(**DB_CONFIG)
            cursor = con.cursor()
            cursor.execute("UPDATE user SET hidden = 0 WHERE email = %s", (email,)) 
            con.commit()
            con.close()
        except Exception as e:
            print(f"Error al restablecer visibilidad del usuario al cerrar sesión: {e}")

    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))

@app.route('/registro_admin', methods=['GET', 'POST'])
@login_required
def registro_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = 'administrador' 

        # Validación de contraseña
        if len(password) < 6 or len(password) > 12:
            flash('La contraseña debe tener entre 6 y 12 caracteres.', 'error')
            return redirect(url_for('registro_admin'))

        # Hash de la contraseña
        hashed_password = hash_password(password)

        # Verificar si el email ya existe
        if email_exists(email):
            flash('El correo ya está registrado.', 'error')
            return redirect(url_for('registro_admin'))

        if insert_admin((name, email, hashed_password.decode('utf-8'), role)):
            flash('Administrador registrado con éxito.', 'success')
            return redirect(url_for('registro_admin'))
        else:
            flash('Error al registrar administrador.', 'error')
            return redirect(url_for('registro_admin'))

    return render_template('registro_admin.html')

@app.route('/agregar_donacion', methods=['POST'])
@login_required
def agregar_donacion_route():
    if request.method == 'POST':
        empresa_nombre = request.form['empresa_nombre']
        correo_empresa = request.form['correo_empresa']
        numero_contacto = request.form['numero_contacto']
        tipo_alimento = request.form['tipo_alimento']
        cantidad_productos = request.form['cantidad_productos']
        estado_producto = request.form['estado_producto']

        if agregar_donacion(empresa_nombre, correo_empresa, numero_contacto, tipo_alimento, cantidad_productos, estado_producto):
            flash('Donación agregada con éxito.', 'success')
        else:
            flash('Error al agregar donación.', 'error')

        return redirect(url_for('donaciones'))
    
    
@app.route('/donaciones_disponibles')
@login_required
def donaciones_disponibles():
    return render_template('donaciones_disponibles.html' , donaciones=obtener_donaciones())


@app.route('/aceptar_solicitud', methods=['POST'])
@login_required
def aceptar_solicitud():
    # Obtener datos del formulario
    empresa_nombre = request.form['empresa_nombre']
    organizacion = request.form['organizacion']
    tipo_alimento = request.form['tipo_alimento']
    cantidad_productos = request.form['cantidad_productos']
    estado_producto = request.form['estado_producto']
    correo_empresa = request.form['correo_empresa']
    numero_contacto = request.form['numero_contacto']

    # Primero agregar la aceptación
    if agregar_aceptacion(empresa_nombre, organizacion, tipo_alimento, 
                        cantidad_productos, estado_producto, 
                        correo_empresa, numero_contacto):
        
        # Luego eliminar la solicitud correspondiente
        if eliminar_solicitud(organizacion, tipo_alimento, cantidad_productos, estado_producto):
            flash('Solicitud aceptada.', 'success')
        else:
            flash('La solicitud fue aceptada pero no se pudo eliminar de la lista de solicitudes.', 'warning')
    else:
        flash('Error al aceptar la solicitud.', 'error')

    return redirect(url_for('solicitudes'))


@app.route('/solicitar_donacion', methods=['POST'])
@login_required
def solicitar_donacion():
    # Obtener datos del formulario
    empresa_nombre = request.form['empresa_nombre']
    organizacion = request.form['organizacion']
    tipo_alimento = request.form['tipo_alimento']
    cantidad_productos = request.form['cantidad_productos']
    estado_producto = request.form['estado_producto']
    correo_empresa = request.form['correo_empresa']
    numero_contacto = request.form['numero_contacto']
    
    # Primero agregar la solicitud
    if agregar_solicitud(empresa_nombre, organizacion, tipo_alimento, 
                        cantidad_productos, estado_producto, 
                        correo_empresa, numero_contacto):
        
        # Luego eliminar la donación disponible
        if eliminar_donacion(empresa_nombre, correo_empresa, tipo_alimento):
            flash('Solicitud enviada (Donación ya no disponible)', 'success')
        else:
            flash('Solicitud enviada pero no se pudo eliminar la donación.', 'warning')
    else:
        flash('Error al enviar la solicitud.', 'error')

    return redirect(url_for('donaciones_disponibles'))

@app.route('/admin_datos')
@login_required
def admin_datos():
    aceptaciones = obtener_aceptaciones()
    
    # Contar total de donaciones, empresas únicas y organizaciones beneficiadas
    total_donaciones = len(aceptaciones)
    empresas_unicas = len(set([a[1] for a in aceptaciones])) if aceptaciones else 0
    organizaciones_beneficiadas = len(set([a[2] for a in aceptaciones])) if aceptaciones else 0
    
    return render_template('admin_datos.html', 
                         aceptaciones=aceptaciones,
                         total_donaciones=total_donaciones,
                         empresas_unicas=empresas_unicas,
                         organizaciones_beneficiadas=organizaciones_beneficiadas)

@app.route('/eliminar_usuario', methods=['POST'])
@login_required
def eliminar_usuario():
    email = request.form.get('email')  
    
    if not email:
        flash('No se recibió un correo válido para eliminar.', 'error')
        return redirect(url_for('bd_admin'))
    
    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("DELETE FROM user WHERE email = %s", (email,))
        con.commit()
        con.close()
        flash(f"Usuario con email {email} eliminado correctamente.", 'success')
    except Exception as e:
        flash(f"Error al eliminar usuario: {e}", 'error')
    
    return redirect(url_for('bd_admin'))

@app.route('/editar_role', methods=['POST'])
@login_required
def editar_role():
    email = request.form.get('email')  
    nuevo_role = request.form.get('nuevo_role') 
    
    if not email or nuevo_role not in ['administrador', 'organizacion benefica', 'empresa donante']:
        flash("Datos inválidos para actualizar rol.", 'error')
        return redirect(url_for('bd_admin'))
    
    user = get_user_by_email(email)
    if user['role'] == 'administrador':
        flash("Ya el usuario es administrador.", 'error')
        return redirect(url_for('bd_admin'))

    try:
        con = sql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("UPDATE user SET role = %s WHERE email = %s", (nuevo_role, email))
        con.commit()
        con.close()
        flash(f"Rol de usuario {email} actualizado correctamente a {nuevo_role}.", 'success')
    except Exception as e:
        flash(f"Error al actualizar el rol: {e}", 'error')
    
    return redirect(url_for('bd_admin'))


@app.route('/solicitudes')
@login_required
def solicitudes():
    lista_solicitudes = obtener_solicitudes()
    return render_template('solicitudes.html', solicitudes=lista_solicitudes)

@app.route('/inicio_admin')
@login_required
def inicio_admin():
    return render_template('inicio_admin.html')

@app.route('/inicio_donante')
@login_required
def inicio_donante():
    return render_template('inicio_donante.html')

@app.route('/inicio_benefica')
@login_required
def inicio_benefica():
    return render_template('inicio_benefica.html')

@app.route('/notificaciones_benefica')
@login_required
def notificaciones_benefica():
    return render_template('notificaciones_benefica.html', donaciones=obtener_donaciones(), aceptaciones=obtener_aceptaciones())

@app.route('/donaciones')
@login_required
def donaciones():   
    return render_template('donaciones.html')

@app.route('/bd_admin')
@login_required
def bd_admin():
    lista_usuarios = obtener_usuarios()
    return render_template('bd_admin.html', usuarios=lista_usuarios)

if __name__ == "__main__":
    app.run(debug=True)

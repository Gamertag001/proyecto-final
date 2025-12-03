from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from src.models.ModelUser import ModelUser
from src.models.entities.user import User
import config
from src.database import get_db
from src.utils.auditoria import log_action


def index():
    """
    Redirige directamente a la página de login.
    Se utiliza como ruta raíz ('/') del sitio.
    """
    return redirect(url_for('login'))


def login():
    """
    Controla el proceso de inicio de sesión de un usuario.
    """

    if request.method == 'POST':
        # Se crea un objeto User temporal con los datos del formulario
        user = User(
            0,  # ID temporal (aún no existe en BD)
            request.form['nombre'],  # Nombre de usuario (campo del formulario)
            request.form['password'],  # Contraseña (campo del formulario)
            "",  # Correo, usar get para evitar KeyError si no está
            0,  # ID de rol (aún no se asigna)
            ""  # Fullname, usar get para evitar KeyError si no está
        )

        # Se obtiene la conexión a la base de datos
        db = get_db()

        # Uso un bloque try/finally para asegurar que la conexión se cierre.
        try:
            # Se verifica si las credenciales son correctas en la base de datos
            logged_user = ModelUser.login(db, user)

            # Si el usuario existe y la contraseña es válida
            if logged_user:
                # Flask-Login guarda la sesión del usuario
                login_user(logged_user)

                # Registrar login en auditoría
                log_action(f"Inicio de sesión exitoso - Usuario: {logged_user.username}", logged_user.id)
                
                # Redirige según el rol del usuario
                match logged_user.id_rol:
                    case 1:
                        return redirect(url_for('home'))  # Donador
                    case 2:
                        return redirect(url_for('panel'))  # Administrador
                    case 3:
                        return redirect(
                            url_for('panel_coordinador'))  # Coordinador
                    case 4:
                        return redirect(
                            url_for('panel_auditor'))  # Auditor
                    case 5:
                        return redirect(
                            url_for('disabled_page'))  # Desactivado
                    # Si el rol no está reconocido
                    case _:
                        flash("Rol no reconocido", "warning")
                        logout_user()  # Cierra la sesión si el rol es inválido

            # Si las credenciales no coinciden, muestra un mensaje
            else:
                flash("Usuario o contraseña incorrectos", "danger")

        finally:
            # Cerramos la conexión, OBLIGATORIO
            if db:
                db.close()

    # Renderiza la plantilla del login si es un GET o si hubo error
    return render_template('auth/login.html')


def logout():
    """
    Cierra la sesión del usuario actual y redirige al login.
    """
    if current_user.is_authenticated:
        log_action(f"Cierre de sesión - Usuario: {current_user.username}")
    logout_user()
    return redirect(url_for('login'))


def register():
    """
    Controla el proceso de registro de nuevos usuarios.
    """

    if request.method == 'POST':
        # Se crea un objeto User con los datos del formulario
        user = User(
            0,  # ID temporal
            request.form['username'],  # Nombre de usuario
            request.form['password'],  # Contraseña (se encripta en el modelo)
            request.form['correo'],  # Correo
            1,  # Rol por defecto: Donador (1)
            request.form.get('fullname', '')  # Nombre completo
        )

        # Conexión a la base de datos
        db = get_db()

        # Uso un bloque try/finally para asegurar que la conexión se cierre.
        try:
            # Se intenta registrar el usuario
            if ModelUser.register(db, user):
                log_action(f"Nuevo usuario registrado: {user.username}")
                flash(
                    'Usuario registrado correctamente. Por favor, inicia sesión.',
                    'success')
                return redirect(url_for('login'))
            else:
                # CORRECCIÓN CLAVE: Muestra el mensaje de error de la BD si la función devuelve False
                flash(
                    'El registro falló. El nombre de usuario o correo ya existen, o hay un problema con la base de datos.',
                    'danger')

        finally:
            # Cierra la conexión, OBLIGATORIO
            if db:
                db.close()

    # Renderiza el formulario si es un GET o si hubo error
    return render_template('auth/register.html')

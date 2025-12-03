from flask import Flask, redirect, url_for, flash, render_template
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config
from src.database import get_db # Importamos la función de conexión
import sys # Necesario para salir si hay un error crítico
import psycopg2 # Necesario para manejar la excepción de PostgreSQL
import os

# Controladores
from src.controllers import auth_controller # Asumo que auth_controller existe
from src.controllers import admin_controller, donador_controller, disabled_controller # Asumo que existen
from src.controllers import coordinador_controller
from src.controllers import proyecto_controller
from src.controllers import donacion_controller
from src.controllers import reportes_controller
from src.controllers import gasto_controller
from src.controllers import proyecto_detalle_controller
from src.controllers import auditor_controller
from src.models.ModelUser import ModelUser

app = Flask(__name__)
# Cargar configuración según el entorno (production o development)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['development']))

# Seguridad y login
csrf = CSRFProtect(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = 'login'


# Cargar usuario activo (usado por Flask-Login)
@login_manager_app.user_loader
def load_user(id):
    # La conexión debe abrirse y cerrarse en esta función
    db = get_db() 
    if db is None:
        # Si la conexión falla aquí, retornamos None
        return None 
        
    # Asumo que ModelUser.get_by_id puede manejar la conexión (db)
    user = ModelUser.get_by_id(db, id)
    db.close()
    return user


# ---------------------- RUTAS PRINCIPALES ----------------------

# rutas de AUTH
app.add_url_rule('/', view_func=auth_controller.index)
app.add_url_rule('/login', view_func=auth_controller.login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=auth_controller.logout)
app.add_url_rule('/register', view_func=auth_controller.register, methods=['GET', 'POST'])

# rutas de ADMIN
app.add_url_rule('/admin', view_func=admin_controller.panel)
app.add_url_rule('/admin/usuarios', view_func=admin_controller.manage_user)
app.add_url_rule('/admin/usuarios/editar/<int:user_id>', view_func=admin_controller.edit_user, methods=['GET', 'POST'])
app.add_url_rule('/admin/usuarios/eliminar/<int:user_id>', view_func=admin_controller.delete_user)
app.add_url_rule('/admin/usuarios/activar/<int:user_id>', view_func=admin_controller.toggle_user_status, methods=['POST'])
app.add_url_rule('/admin/reportes', view_func=reportes_controller.reportes)


# rutas de DONADOR
app.add_url_rule('/home', view_func=donador_controller.home)
app.add_url_rule('/mi-informacion', view_func=donador_controller.mi_informacion, methods=['GET', 'POST'])

# ruta de USUARIO DESACTIVADO
app.add_url_rule('/disabled', view_func=disabled_controller.disabled_page)

#rutas de COORDINADOR
app.add_url_rule('/coordinador', view_func=coordinador_controller.panel_coordinador)
app.add_url_rule('/coordinador/proyecto/crear', view_func=coordinador_controller.crear_proyecto, methods=['GET','POST'])
app.add_url_rule('/coordinador/proyecto/editar/<int:id_proyecto>', view_func=coordinador_controller.editar_proyecto, methods=['GET','POST'])
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/donaciones', view_func=coordinador_controller.ver_donaciones_proyecto)
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/archivar', view_func=coordinador_controller.archivar_proyecto, methods=['POST'])
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/desarchivar', view_func=coordinador_controller.desarchivar_proyecto, methods=['POST'])
app.add_url_rule('/coordinador/reportes', view_func=coordinador_controller.reportes_coordinador)

# rutas de GASTOS
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/gastos', view_func=gasto_controller.listar_gastos_proyecto)
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/gastos/crear', view_func=gasto_controller.crear_gasto, methods=['GET','POST'])
app.add_url_rule('/coordinador/gasto/<int:id_gasto>/editar', view_func=gasto_controller.editar_gasto, methods=['GET','POST'])
app.add_url_rule('/coordinador/gasto/<int:id_gasto>/eliminar', view_func=gasto_controller.eliminar_gasto, methods=['POST'])
app.add_url_rule('/coordinador/gasto/<int:id_gasto>/comprobante', view_func=gasto_controller.descargar_comprobante)

# rutas de GESTION DE PROYECTO (objetivos, actividades, responsables, tareas)
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/gestion', view_func=proyecto_detalle_controller.detalle_gestion_proyecto)
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/estado', view_func=proyecto_detalle_controller.actualizar_estado_proyecto, methods=['POST'])
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/objetivo/crear', view_func=proyecto_detalle_controller.crear_objetivo, methods=['POST'])
app.add_url_rule('/coordinador/objetivo/<int:id_objetivo>/toggle', view_func=proyecto_detalle_controller.toggle_objetivo, methods=['POST'])
app.add_url_rule('/coordinador/objetivo/<int:id_objetivo>/eliminar', view_func=proyecto_detalle_controller.eliminar_objetivo, methods=['POST'])
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/actividad/crear', view_func=proyecto_detalle_controller.crear_actividad, methods=['POST'])
app.add_url_rule('/coordinador/actividad/<int:id_actividad>/estado', view_func=proyecto_detalle_controller.actualizar_estado_actividad, methods=['POST'])
app.add_url_rule('/coordinador/actividad/<int:id_actividad>/eliminar', view_func=proyecto_detalle_controller.eliminar_actividad, methods=['POST'])
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/responsable/crear', view_func=proyecto_detalle_controller.agregar_responsable, methods=['POST'])
app.add_url_rule('/coordinador/responsable/<int:id_responsable>/eliminar', view_func=proyecto_detalle_controller.eliminar_responsable, methods=['POST'])
app.add_url_rule('/coordinador/proyecto/<int:id_proyecto>/tarea/crear', view_func=proyecto_detalle_controller.crear_tarea, methods=['POST'])
app.add_url_rule('/coordinador/tarea/<int:id_tarea>/estado', view_func=proyecto_detalle_controller.actualizar_estado_tarea, methods=['POST'])
app.add_url_rule('/coordinador/tarea/<int:id_tarea>/eliminar', view_func=proyecto_detalle_controller.eliminar_tarea, methods=['POST'])

# rutas de PROYECTOS PUBLICOS
app.add_url_rule('/proyectos', view_func=proyecto_controller.listar_proyectos)
app.add_url_rule('/proyecto/<int:id_proyecto>', view_func=proyecto_controller.detalle_proyecto)
app.add_url_rule('/proyecto/<int:id_proyecto>/donar', view_func=proyecto_controller.formulario_donacion, methods=['GET','POST'])

# rutas de DONACIONES
app.add_url_rule('/donaciones/historial', view_func=donacion_controller.historial_donaciones_usuario)

# rutas de AUDITOR
app.add_url_rule('/auditor', view_func=auditor_controller.panel_auditor, endpoint='panel_auditor')
app.add_url_rule('/auditor/auditoria', view_func=auditor_controller.ver_auditoria, endpoint='ver_auditoria')
app.add_url_rule('/auditor/donaciones', view_func=auditor_controller.reportes_donaciones, endpoint='auditor_reportes_donaciones')
app.add_url_rule('/auditor/gastos', view_func=auditor_controller.reportes_gastos, endpoint='auditor_reportes_gastos')
app.add_url_rule('/auditor/donaciones/excel', view_func=auditor_controller.exportar_donaciones_excel, endpoint='exportar_donaciones_excel')
app.add_url_rule('/auditor/donaciones/pdf', view_func=auditor_controller.exportar_donaciones_pdf, endpoint='exportar_donaciones_pdf')
app.add_url_rule('/auditor/gastos/excel', view_func=auditor_controller.exportar_gastos_excel, endpoint='exportar_gastos_excel')
app.add_url_rule('/auditor/gastos/pdf', view_func=auditor_controller.exportar_gastos_pdf, endpoint='exportar_gastos_pdf')
app.add_url_rule('/auditor/auditoria/excel', view_func=auditor_controller.exportar_auditoria_excel, endpoint='exportar_auditoria_excel')

# ---------------------- MANEJADORES DE ERRORES ----------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

# Manejo de error de conexión de base de datos
def init_db_connection():
    '''Verifica si la base de datos está disponible antes de ejecutar la aplicación'''
    try:
        db = get_db()
        if db is None:
            print("⚠️  WARNING: No database connection available")
            print("   The app will start but database operations will fail")
            print("   To set up the database:")
            print("   1. Click 'Database' in the left sidebar")
            print("   2. Click 'Create a database'")
            print("   3. Run: python scripts/init_db.py")
            return False
        db.close()
        print("✅ Database connection verified")
        return True
    except (psycopg2.OperationalError, Exception) as e:
        print(f"⚠️  WARNING: Could not connect to database: {e}")
        print("   The app will start but database operations will fail")
        print("   To set up the database:")
        print("   1. Click 'Database' in the left sidebar")
        print("   2. Click 'Create a database'")
        print("   3. Run: python scripts/init_db.py")
        return False

if __name__ == '__main__':
    init_db_connection()
    app.run(host='0.0.0.0', port=5000, debug=True)

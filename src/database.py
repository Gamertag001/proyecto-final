import psycopg2
import os
from config import config

# Obtener la configuración según el entorno
env = os.environ.get('FLASK_ENV', 'development')
CURRENT_CONFIG = config.get(env, config['development'])


def get_db():
    """Establece y retorna una conexión activa a la base de datos PostgreSQL."""
    # Check if credentials are configured before attempting connection
    if not all([CURRENT_CONFIG.PG_HOST, CURRENT_CONFIG.PG_USER, CURRENT_CONFIG.PG_PASSWORD, CURRENT_CONFIG.PG_DB]):
        # Return None gracefully when credentials are not set
        return None
    
    try:
        connection = psycopg2.connect(
            host=CURRENT_CONFIG.PG_HOST,
            user=CURRENT_CONFIG.PG_USER,
            password=CURRENT_CONFIG.PG_PASSWORD,
            database=CURRENT_CONFIG.PG_DB,
            port=getattr(CURRENT_CONFIG, "PG_PORT", 5432)
        )

        # Return active connection
        return connection

    except psycopg2.OperationalError as e:
        print(f"❌ Error al conectar a la base de datos PostgreSQL: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al conectar a la base de datos: {e}")
        return None


# =======================================================
# BLOQUE DE PRUEBA (if __name__ == '__main__':)
# =======================================================

if __name__ == "__main__":
    conn = get_db()

    if conn:
        print("✅ Conexión exitosa a la base de datos PostgreSQL.")

        try:
            # Creamos un cursor para ejecutar comandos SQL
            cursor = conn.cursor()

            # Consulta SQL para obtener todos los datos de la tabla 'usuarios'
            cursor.execute("SELECT * FROM usuarios LIMIT 1")

            # Obtenemos la descripción de las columnas desde el cursor
            column_names = [desc[0] for desc in cursor.description]

            print("\n--- Columnas de la tabla 'usuarios' ---")
            print(column_names)
            print("-------------------------------------")

        except psycopg2.Error as e:
            print(f"❌ Error al intentar leer la tabla 'usuarios': {e}")

        finally:
            # Cerrar la conexión después de usarla
            cursor.close()
            conn.close()
            print("Conexión a la BD cerrada.")
    else:
        print("⚠️  No hay credenciales de base de datos configuradas.")
        print("   Para configurar la base de datos:")
        print("   1. Crea una base de datos PostgreSQL en Replit")
        print("   2. Ejecuta: python scripts/init_db.py")

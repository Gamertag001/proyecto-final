"""
Script to initialize the database schema for the donation management platform.
Creates all required tables and inserts default data including roles and admin user.
"""
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

def get_db_connection():
    """Get database connection using configuration"""
    env = os.environ.get('FLASK_ENV', 'development')
    cfg = config.get(env, config['development'])
    
    # Check if credentials are set
    if not all([cfg.PG_HOST, cfg.PG_USER, cfg.PG_PASSWORD, cfg.PG_DB]):
        print("❌ ERROR: Database credentials not configured")
        print("\nPlease ensure PostgreSQL database is created and environment variables are set:")
        print("  - PGHOST")
        print("  - PGUSER")
        print("  - PGPASSWORD")
        print("  - PGDATABASE")
        print("  - PGPORT (optional, defaults to 5432)")
        print("\nTo create a database in Replit:")
        print("  1. Click on 'Database' in the left sidebar")
        print("  2. Click 'Create a database'")
        print("  3. The environment variables will be set automatically")
        sys.exit(1)
    
    try:
        connection = psycopg2.connect(
            host=cfg.PG_HOST,
            user=cfg.PG_USER,
            password=cfg.PG_PASSWORD,
            database=cfg.PG_DB,
            port=cfg.PG_PORT
        )
        return connection
    except psycopg2.OperationalError as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        print("\nAsegúrese de que:")
        print("  1. La base de datos PostgreSQL está creada en Replit")
        print("  2. Las variables de entorno están configuradas correctamente")
        print(f"\nCredenciales detectadas:")
        print(f"  Host: {cfg.PG_HOST}")
        print(f"  User: {cfg.PG_USER}")
        print(f"  Database: {cfg.PG_DB}")
        print(f"  Port: {cfg.PG_PORT}")
        sys.exit(1)

def init_database():
    """Initialize database schema and default data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔧 Creando esquema de base de datos...")
        
        # Create roles table
        print("  → Creando tabla 'roles'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id_rol INTEGER PRIMARY KEY,
                nombre_rol VARCHAR(50) NOT NULL UNIQUE
            )
        """)
        
        # Create usuarios table
        print("  → Creando tabla 'usuarios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                correo VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                fullname VARCHAR(255) NOT NULL,
                id_rol INTEGER NOT NULL,
                FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
            )
        """)
        
        # Create proyectos table
        print("  → Creando tabla 'proyectos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id_proyecto SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT,
                monto_objetivo DECIMAL(12, 2) NOT NULL,
                monto_recaudado DECIMAL(12, 2) DEFAULT 0,
                estado VARCHAR(50) DEFAULT 'activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id_usuario INTEGER NOT NULL,
                archivado BOOLEAN DEFAULT FALSE,
                archivado_en TIMESTAMP,
                archivado_por INTEGER,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE RESTRICT,
                FOREIGN KEY (archivado_por) REFERENCES usuarios(id) ON DELETE SET NULL
            )
        """)
        
        # Create donaciones table
        print("  → Creando tabla 'donaciones'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donaciones (
                id_donacion SERIAL PRIMARY KEY,
                id_usuario INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                monto DECIMAL(12, 2) NOT NULL,
                fecha_donacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE RESTRICT,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
            )
        """)
        
        # Create categorias_gasto table
        print("  → Creando tabla 'categorias_gasto'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_gasto (
                id_categoria SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                descripcion TEXT
            )
        """)
        
        # Create gastos table
        print("  → Creando tabla 'gastos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id_gasto SERIAL PRIMARY KEY,
                id_proyecto INTEGER NOT NULL,
                id_usuario INTEGER NOT NULL,
                categoria VARCHAR(100) NOT NULL,
                descripcion TEXT,
                monto DECIMAL(12, 2) NOT NULL,
                fecha_gasto DATE NOT NULL,
                archivo_nombre VARCHAR(255),
                archivo_path VARCHAR(500),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE RESTRICT
            )
        """)
        
        # Create objetivos table (project objectives)
        print("  → Creando tabla 'objetivos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objetivos (
                id_objetivo SERIAL PRIMARY KEY,
                id_proyecto INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                completado BOOLEAN DEFAULT FALSE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
            )
        """)
        
        # Create actividades table (project activities)
        print("  → Creando tabla 'actividades'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id_actividad SERIAL PRIMARY KEY,
                id_proyecto INTEGER NOT NULL,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT,
                fecha_inicio DATE,
                fecha_fin DATE,
                estado VARCHAR(50) DEFAULT 'pendiente',
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
            )
        """)
        
        # Create responsables table (project team members)
        print("  → Creando tabla 'responsables'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responsables (
                id_responsable SERIAL PRIMARY KEY,
                id_proyecto INTEGER NOT NULL,
                id_usuario INTEGER NOT NULL,
                rol_en_proyecto VARCHAR(100),
                fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE(id_proyecto, id_usuario)
            )
        """)
        
        # Create tareas table (task assignments)
        print("  → Creando tabla 'tareas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id SERIAL PRIMARY KEY,
                descripcion TEXT NOT NULL,
                estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_progreso', 'completada')),
                fecha_inicio DATE,
                fecha_fin DATE,
                usuario_id INTEGER,
                proyecto_id INTEGER NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                FOREIGN KEY (proyecto_id) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
            )
        """)
        
        # Add new columns to usuarios table for contact info and preferences
        print("  → Actualizando tabla 'usuarios' con campos adicionales...")
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='usuarios' AND column_name='telefono') THEN
                    ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='usuarios' AND column_name='direccion') THEN
                    ALTER TABLE usuarios ADD COLUMN direccion TEXT;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='usuarios' AND column_name='preferencia_email') THEN
                    ALTER TABLE usuarios ADD COLUMN preferencia_email BOOLEAN DEFAULT TRUE;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='usuarios' AND column_name='preferencia_sms') THEN
                    ALTER TABLE usuarios ADD COLUMN preferencia_sms BOOLEAN DEFAULT FALSE;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='usuarios' AND column_name='notas') THEN
                    ALTER TABLE usuarios ADD COLUMN notas TEXT;
                END IF;
            END $$;
        """)
        
        # Update proyectos table estado column to include new status values
        print("  → Verificando estados de proyectos...")
        cursor.execute("""
            DO $$
            BEGIN
                UPDATE proyectos SET estado = 'en_ejecucion' WHERE estado = 'activo';
            EXCEPTION WHEN OTHERS THEN
                NULL;
            END $$;
        """)
        
        # Insert default roles
        print("\n📝 Insertando roles por defecto...")
        cursor.execute("""
            INSERT INTO roles (id_rol, nombre_rol) VALUES
            (1, 'Donador'),
            (2, 'Administrador'),
            (3, 'Coordinador'),
            (4, 'Auditor'),
            (5, 'Desactivado')
            ON CONFLICT (id_rol) DO NOTHING
        """)
        
        # Insert default expense categories
        print("📝 Insertando categorías de gasto por defecto...")
        cursor.execute("""
            INSERT INTO categorias_gasto (nombre, descripcion) VALUES
            ('Material Educativo', 'Libros, cuadernos, útiles escolares'),
            ('Infraestructura', 'Construcción, reparaciones, mantenimiento'),
            ('Alimentación', 'Comida, bebidas, suministros de cocina'),
            ('Servicios', 'Electricidad, agua, internet, teléfono'),
            ('Personal', 'Salarios, honorarios profesionales'),
            ('Transporte', 'Combustible, pasajes, mantenimiento de vehículos'),
            ('Equipamiento', 'Mobiliario, equipos, herramientas'),
            ('Otros', 'Gastos misceláneos')
            ON CONFLICT (nombre) DO NOTHING
        """)
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nombre = 'admin'")
        admin_exists = cursor.fetchone()[0] > 0
        
        if not admin_exists:
            print("👤 Creando usuario administrador por defecto...")
            hashed_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO usuarios (nombre, correo, password, fullname, id_rol)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@gmail.com', hashed_password, 'Administrador', 2))
            print("✅ Usuario administrador creado:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   Email: admin@gmail.com")
        else:
            print("ℹ️  Usuario administrador ya existe, omitiendo creación...")
        
        # Commit changes
        conn.commit()
        print("\n✅ Base de datos inicializada correctamente!")
        print("\n📊 Resumen:")
        
        # Count tables
        cursor.execute("SELECT COUNT(*) FROM roles")
        print(f"   • Roles: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        print(f"   • Usuarios: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM proyectos")
        print(f"   • Proyectos: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM donaciones")
        print(f"   • Donaciones: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM gastos")
        print(f"   • Gastos: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM categorias_gasto")
        print(f"   • Categorías de gasto: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM objetivos")
        print(f"   • Objetivos: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM actividades")
        print(f"   • Actividades: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM responsables")
        print(f"   • Responsables: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM tareas")
        print(f"   • Tareas: {cursor.fetchone()[0]}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("  INICIALIZADOR DE BASE DE DATOS")
    print("  Sistema de Gestión de Donaciones")
    print("=" * 60)
    print()
    init_database()
    print()
    print("=" * 60)

# Overview

This is a Flask-based donation management platform that enables users to create, manage, and contribute to fundraising projects. The application supports role-based access control with distinct user types: donors (donadores), coordinators (coordinadores), and administrators (admins). Users can register, login, browse projects, make donations, and track fundraising progress. The platform uses PostgreSQL for data persistence and implements security features including CSRF protection and password hashing.

## Database Setup Required

**IMPORTANT**: This application requires a PostgreSQL database to function fully. To set up the database:

1. **Create Database**: 
   - Open the Replit Database tool in the left sidebar
   - Click "Create a database" to provision a PostgreSQL database
   - Replit will automatically set the required environment variables (PGHOST, PGUSER, PGPASSWORD, PGDATABASE, PGPORT)
   - **Note**: If you encounter a 403 error when creating the database, you may need to create it manually through the Replit UI Database panel

2. **Verify Database Connection**:
   - After creating the database, verify the environment variables are set:
   ```bash
   env | grep PG
   ```
   - You should see PGHOST, PGUSER, PGPASSWORD, PGDATABASE, and PGPORT

3. **Initialize Schema**: 
   - Run the initialization script to create tables and the default admin user:
   ```bash
   python scripts/init_db.py
   ```
   - The script will create six tables (roles, usuarios, proyectos, donaciones, gastos, categorias_gasto) and insert a default admin user

4. **Verify**: Check that all tables were created successfully by running the script output

**Default Admin Credentials** (created after running init_db.py): 
- Username: `admin`
- Password: `admin123`
- Email: `admin@gmail.com`

**Security Note**: The default password should be changed immediately after first login. In production, ensure you're using secure passwords and environment variables for all sensitive data.

# Recent Changes

## Coordinator Panel & Expense Validation Updates (December 2, 2025)
- **Fixed 'today' undefined error**: Added date import and `today=date.today()` to project detail template rendering
- **Expense validation improvements**:
  - Expenses now validate against collected funds (`monto_recaudado`) instead of project goal (`monto_objetivo`)
  - Expenses are blocked when project has no collected funds ($0 raised)
  - Updated expense listing template to show "Fondos Recaudados" with clear warning messages
  - Added `puede_registrar_gastos` flag to control expense creation button visibility
- **Coordinator panel enhancements**:
  - Added detailed project information below each project row in the panel
  - Displays objectives, activities, and tasks with completion counts (e.g., "2/5 completed")
  - Shows first 3 items of each category with visual status indicators
  - Color-coded status badges: green (completed), blue (in progress), yellow (pending)
  - Three-column grid layout for clean presentation

## Replit Environment Setup - Latest (December 2, 2025)
- Successfully configured Flask application for Replit environment
- **Python**: Installed Python 3.11 with all dependencies from requirements.txt
- **Database**: PostgreSQL database initialized with all tables and default admin user
- **Development Workflow**: Configured Flask Application workflow on port 5000 with webview output
- **Production Deployment**: Configured autoscale deployment with Gunicorn (3 workers, --bind=0.0.0.0:5000, --reuse-port)
- **Dependencies**: Cleaned up requirements.txt to remove duplicates
- **Git Configuration**: Added comprehensive .gitignore for Python/Flask projects
- **Application Status**: Running successfully at http://0.0.0.0:5000 with database connection verified

## Important Configuration Notes
- **Development**: Uses Flask development server (`python app.py`) for hot-reload debugging
- **Production**: Uses Gunicorn WSGI server with autoscale deployment target
- **Port Configuration**: Frontend on port 5000 (0.0.0.0 binding for Replit proxy compatibility)
- **Security**: SECRET_KEY uses fallback "dev-secret-key-change-in-production" for development; production deployment should set a secure SECRET_KEY environment variable
- **Database**: Requires PostgreSQL with environment variables (PGHOST, PGUSER, PGPASSWORD, PGDATABASE, PGPORT)

## Donor Profile & Project Management Features (December 2, 2025)
- **Donor Profile Management ("Mi Informacion")**:
  - New methods in ModelUser: get_profile() and update_profile()
  - Donors can update: fullname, email, phone, address, notes
  - Communication preferences: email and SMS notification toggles
  - New template: templates/donador/mi-informacion.html
  - Updated donor home navigation with link to profile

- **Project Status Management**:
  - Coordinators can update project status: en_planificacion, en_ejecucion, finalizado
  - Visual status indicator in project management panel
  - Status changes logged with proper authorization

- **Project Detail Management** (new controller: src/controllers/proyecto_detalle_controller.py):
  - **Objectives**: Create, toggle completion, delete objectives per project
  - **Activities**: Create with dates, update status (pendiente/en_progreso/completada), delete
  - **Team Members**: Add users with roles, remove team members
  - **Tasks**: Create with assignments, dates, status tracking, delete
  - New template: templates/coordinador/detalle-proyecto.html
  - 13 new routes in app.py for comprehensive project management
  - All handlers include verificar_permiso_proyecto() for proper authorization

- **Budget Alerts**: Verified ModelGasto.validar_presupuesto() provides alerts when expenses exceed available budget

## GitHub Import Setup (December 2, 2025)
- Successfully imported project from GitHub to Replit environment
- Installed Python 3.11 and all dependencies from requirements.txt
- Created database initialization script (`scripts/init_db.py`) with CASCADE constraints
- Added .gitignore for Python project and Replit artifacts
- Configured Flask Application workflow on port 5000 with webview output
- Set up production deployment with Gunicorn (3 workers, autoscale)
- Application running successfully with database connection verified
- **Important**: Database must be created before using the application (see Database Setup above)

## Project Archiving & Expense Management (December 2, 2025)
- Added project archiving feature for coordinators and administrators
  - New database columns: archivado (boolean), archivado_en (timestamp), archivado_por (user FK)
  - Archived projects are hidden from public view but visible to authorized users
  - Donations are blocked on archived projects
  - Archive/unarchive buttons in coordinator panel
- Implemented comprehensive expense management system
  - New gastos table with category, description, amount, date, and receipt file fields
  - File upload support for receipts (PDF, JPG, PNG up to 5MB)
  - Budget validation (expenses cannot exceed project objective)
  - CRUD operations for expenses with proper authorization
  - Created templates: gastos/listar.html, gastos/crear.html, gastos/editar.html
- Updated coordinator panel with project management options (edit, view donations, view expenses, archive)
- Created ver-donaciones.html template for viewing project donations

## Frontend Redesign (December 2, 2025)
- Created comprehensive CSS design system (`static/css/main.css`) with 900+ lines
- Implemented purple gradient color palette (#DA18FE, #BE45FF, #9945FF, #5C26FF, #3126FF, #726BFF)
- Added dark/light mode toggle with smooth CSS transitions
- Created JavaScript file (`static/js/main.js`) for theme toggle and subtle animations
- Redesigned all templates with modern card-based layout and glassmorphism effects
- Updated authentication templates (login, register) with new design
- Updated admin, donador, and coordinador panel templates
- Created missing templates (proyectos/listar, detalle, donar; coordinador/crear-proyecto)
- Fixed URL routing inconsistencies to match Flask route definitions in app.py

## Replit Environment Setup (December 2, 2025)
- Configured Flask application to run in Replit environment on port 5000 with host 0.0.0.0
- Updated config.py to use Replit database environment variables (PGHOST, PGUSER, PGPASSWORD, PGDATABASE, PGPORT)
- Added ProductionConfig class for production deployment with DEBUG=False
- Modified app.py to dynamically load configuration based on FLASK_ENV environment variable
- Fixed import errors in model files (changed to relative imports)
- Fixed SQL issues in ModelProyecto and ModelDonacion (column mismatches, typos)
- Added missing methods: get_by_user, get_donaciones, update
- Moved error handlers outside if __name__ block for proper Gunicorn support
- Created .gitignore for Python projects
- Initialized database schema with tables: roles, usuarios, proyectos, donaciones
- Configured Gunicorn deployment with autoscale on port 5000
- Fixed 404 error handler template path from '404.html' to 'error/404.html'
- Installed Python 3.11 and all required dependencies from requirements.txt
- Set up Flask Application workflow with webview output on port 5000
- Configured deployment with Gunicorn using --bind=0.0.0.0:5000 and --reuse-port flags

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

- **Template Engine**: Jinja2 templates with Bootstrap 5.3.8 for responsive UI
- **CSS Strategy**: Centralized design system in `static/css/main.css` with CSS custom properties for theming
- **Static Assets**: Centralized in `/static` directory for images, CSS, and JavaScript files
- **Design Pattern**: Template inheritance using a base template (`templates/base.html`) extended by role-specific views
- **Theme System**: Dark/light mode toggle with localStorage persistence and smooth CSS transitions
- **Color Palette**: Purple gradient (#DA18FE, #BE45FF, #9945FF, #5C26FF, #3126FF, #726BFF)
- **Animations**: Subtle fade-in, slide-up, and stagger effects via CSS and JavaScript

## Backend Architecture

- **Framework**: Flask web framework with modular controller structure
- **MVC Pattern**: 
  - Models: Entity classes (User, Proyecto, Donacion, Objetivo, Actividad, Responsable, Tarea, Gasto) with corresponding Model classes for database operations
  - Views: Jinja2 templates organized by role (admin, donador, coordinador)
  - Controllers: Separate controller modules per feature domain (auth, admin, donador, coordinador, proyecto, donacion, gasto, proyecto_detalle)
- **Authentication**: Flask-Login for session management with UserMixin integration
- **Authorization**: Custom role-based decorator (`@rol_required`) supporting multiple roles per route
- **Security**: Flask-WTF for CSRF protection, Werkzeug for password hashing
- **Configuration**: Environment-based config (development/production) with database credentials loaded from environment variables

## Database Architecture

- **Database**: PostgreSQL with psycopg2 driver
- **Connection Management**: Manual connection handling via `get_db()` function - connections opened per request and explicitly closed
- **Query Pattern**: Raw SQL queries with parameterized statements to prevent SQL injection
- **Cursor Factory**: RealDictCursor for dictionary-based row access
- **Schema**: 
  - `roles` table for role definitions
  - `usuarios` table with foreign key to roles
  - `proyectos` table for fundraising projects (includes archivado, archivado_en, archivado_por columns)
  - `donaciones` table linking users to projects with donation amounts
  - `gastos` table for expense tracking with receipt file uploads
  - `categorias_gasto` table for expense category definitions
- **Database Initialization**: Script-based schema creation (`scripts/init_db.py`)

## Authentication & Authorization

- **User Model**: Custom User class implementing Flask-Login's UserMixin
- **Password Security**: Werkzeug's `generate_password_hash()` and `check_password_hash()`
- **Session Management**: Flask-Login's `login_user()`, `logout_user()`, and `@login_required` decorator
- **Role System**: Integer-based roles (1=Donador, 2=Admin, 3=Coordinador, 5=Disabled)
- **Access Control**: Custom `@rol_required` decorator supporting multiple roles and flexible type matching (int/string)
- **Login Flow**: Form-based authentication with redirect based on user role

## Application Structure

- **Routing**: Centralized URL rule registration in `app.py`
- **Error Handling**: Custom 404 error page template
- **Flash Messages**: Bootstrap alert integration for user feedback
- **CSRF Protection**: Enabled globally via CSRFProtect with token validation on forms

# Despliegue en Vercel

## Requisitos Previos

1. **Cuenta en Vercel**: Crea una cuenta gratuita en [vercel.com](https://vercel.com)
2. **Repositorio Git**: Tu proyecto debe estar en GitHub, GitLab o Bitbucket
3. **Base de datos PostgreSQL externa**: Vercel es serverless, necesitas un servicio de base de datos externo

## Servicios de Base de Datos Recomendados

Como Vercel es serverless, necesitas una base de datos PostgreSQL externa. Opciones recomendadas:

- **Neon** (Recomendado - Plan gratuito disponible): [neon.tech](https://neon.tech)
- **Supabase** (Plan gratuito disponible): [supabase.com](https://supabase.com)
- **Railway** (Plan gratuito limitado): [railway.app](https://railway.app)
- **ElephantSQL** (Plan gratuito disponible): [elephantsql.com](https://elephantsql.com)

## Pasos para Desplegar en Vercel

### Paso 1: Preparar el Repositorio

1. Sube el contenido de la carpeta `donationzip/donation/` a tu repositorio Git
2. Asegurate de que los archivos `vercel.json` y `requirements.txt` esten en la raiz

### Paso 2: Configurar Base de Datos Externa

1. Crea una cuenta en Neon (u otro proveedor)
2. Crea una nueva base de datos PostgreSQL
3. Copia la URL de conexion (formato: `postgresql://user:password@host:port/database`)
4. Ejecuta el script de inicializacion conectandote a la base de datos:
   ```bash
   python scripts/init_db.py
   ```

### Paso 3: Desplegar en Vercel

**Opcion A: Desde la interfaz web (Recomendado)**

1. Ve a [vercel.com](https://vercel.com) e inicia sesion
2. Haz clic en **"Add New"** > **"Project"**
3. Importa tu repositorio de GitHub/GitLab/Bitbucket
4. En la configuracion del proyecto:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (o `donationzip/donation/` si no moviste los archivos)
   - **Build Command**: Dejar vacio
   - **Output Directory**: Dejar vacio

**Opcion B: Usando Vercel CLI**

```bash
npm i -g vercel
vercel login
cd donationzip/donation
vercel
vercel --prod
```

### Paso 4: Configurar Variables de Entorno

En el dashboard de Vercel:

1. Ve a tu proyecto > **Settings** > **Environment Variables**
2. Agrega las siguientes variables:

| Variable | Valor | Descripcion |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Entorno de produccion |
| `SECRET_KEY` | `[tu-clave-secreta-aleatoria]` | Clave para sesiones (genera una segura) |
| `PGHOST` | `[host-de-tu-db]` | Host de la base de datos |
| `PGUSER` | `[usuario-db]` | Usuario de la base de datos |
| `PGPASSWORD` | `[password-db]` | Contrasena de la base de datos |
| `PGDATABASE` | `[nombre-db]` | Nombre de la base de datos |
| `PGPORT` | `5432` | Puerto de PostgreSQL |

**Nota**: Algunos proveedores como Neon proporcionan `DATABASE_URL`. En ese caso, puedes modificar `config.py` para usar esa variable o extraer los valores individuales.

### Paso 5: Verificar Despliegue

1. Vercel te proporcionara una URL (ejemplo: `tu-proyecto.vercel.app`)
2. Visita la URL y verifica que la pagina de login aparezca
3. Intenta iniciar sesion con las credenciales del administrador

## Limitaciones de Vercel (Plan Gratuito)

- **Funciones serverless**: Tu app se ejecuta como funciones, no como servidor persistente
- **Timeout de 10 segundos**: Las solicitudes deben completarse en 10 segundos
- **Sin almacenamiento de archivos persistente**: Los archivos subidos (comprobantes de gastos) no persistiran
- **Ejecucion en frio**: Primera solicitud puede ser mas lenta

## Solucion para Subida de Archivos

Para manejar archivos en produccion, considera:

1. **Cloudinary** (imagenes y documentos): [cloudinary.com](https://cloudinary.com)
2. **AWS S3** (almacenamiento general): [aws.amazon.com/s3](https://aws.amazon.com/s3)
3. **Supabase Storage** (si ya usas Supabase): Incluido con el servicio

Modifica `src/utils/file_upload.py` para usar el servicio de almacenamiento elegido.

## Problemas Comunes

| Problema | Solucion |
|----------|----------|
| Error 502 Bad Gateway | Verifica que `requirements.txt` exista y tenga Flask |
| Error de conexion a DB | Verifica las variables de entorno PGHOST, PGUSER, etc. |
| psycopg2 error | Usa `psycopg2-binary` en lugar de `psycopg2` |
| Timeout error | Optimiza consultas de base de datos, considera paginacion |
| Error de importacion | Verifica que la estructura de carpetas sea correcta |

## Generar SECRET_KEY Seguro

```python
import secrets
print(secrets.token_hex(32))
```

Copia el resultado y usalo como valor de `SECRET_KEY` en Vercel.

## Notas Importantes para Base de Datos

### Conexion SSL (Requerido para la mayoria de proveedores)

Muchos proveedores de base de datos como Neon requieren conexion SSL. Si tienes errores de conexion, modifica `src/database.py`:

```python
connection = psycopg2.connect(
    host=CURRENT_CONFIG.PG_HOST,
    user=CURRENT_CONFIG.PG_USER,
    password=CURRENT_CONFIG.PG_PASSWORD,
    database=CURRENT_CONFIG.PG_DB,
    port=getattr(CURRENT_CONFIG, "PG_PORT", 5432),
    sslmode='require'  # Agregar esta linea
)
```


### DATABASE_URL

Si tu proveedor solo proporciona `DATABASE_URL`, puedes modificar `config.py`:

```python
import os
from urllib.parse import urlparse

class ProductionConfig(Config):
    DEBUG = False
    
    # Parsear DATABASE_URL si existe
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        parsed = urlparse(database_url)
        PG_HOST = parsed.hostname
        PG_USER = parsed.username
        PG_PASSWORD = parsed.password
        PG_DB = parsed.path[1:]  # Quitar el / inicial
        PG_PORT = parsed.port or 5432
    else:
        PG_HOST = os.environ.get("PGHOST")
        PG_USER = os.environ.get("PGUSER")
        PG_PASSWORD = os.environ.get("PGPASSWORD")
        PG_DB = os.environ.get("PGDATABASE")
        PG_PORT = int(os.environ.get("PGPORT", "5432"))
```

# External Dependencies

## Core Framework Dependencies

- **Flask**: Web application framework
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: CSRF protection and form handling
- **Werkzeug**: Password hashing utilities

## Database

- **PostgreSQL**: Primary relational database
- **psycopg2-binary**: PostgreSQL adapter for Python with binary distribution
- **SQLAlchemy**: Listed in requirements but not actively used in current codebase

## Data Processing & Visualization

- **Pandas**: Data manipulation (listed but not used in visible code)
- **Matplotlib**: Chart generation (listed but not used in visible code)

## Deployment

- **Gunicorn**: WSGI HTTP server for production deployment

## UI Framework

- **Bootstrap 5.3.8**: CSS framework loaded via CDN

## Configuration Dependencies

- Database connection parameters sourced from environment variables:
  - `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGPORT`
  - `FLASK_ENV` for environment selection
  - `SECRET_KEY` for session encryption
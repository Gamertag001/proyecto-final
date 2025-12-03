# Sistema de Gestión de Proyectos y Donaciones  
### Proyecto Final – Plataforma Multirol (Admin, Coordinador, Donador y Auditor)

---

## Descripción General

Este proyecto es un **sistema completo de gestión de proyectos, donaciones y gastos**, desarrollado con **Flask**, **PostgreSQL**, **Bootstrap**, **Jinja2** y un sistema de **roles personalizado** mediante decoradores.

La plataforma permite:

- Registrar y administrar proyectos.  
- Gestionar donaciones.  
- Controlar gastos asociados a cada proyecto.  
- Contar con roles que dividen las responsabilidades dentro del sistema.  
- Visualizar paneles según el rol del usuario.  
- Llevar auditoría, validaciones y control administrativo.

Es un proyecto ideal para organizaciones, fundaciones o equipos que necesiten transparencia y control del flujo de recursos.

---

##  Roles del Sistema

El sistema implementa **4 roles oficiales**, cada uno con un panel dedicado:

### 🔹 1. Administrador (Admin)
Responsable principal.  
Puede:
- Crear, editar y eliminar proyectos.  
- Registrar coordinadores.  
- Ver todos los donadores y auditores.  
- Revisar todas las transacciones.  
- Administrar usuarios y permisos.  

### 🔹 2. Coordinador
Encargado de ejecutar los proyectos.  
Puede:
- Ver proyectos asignados.  
- Registrar gastos.  
- Registrar avances del proyecto.  
- Ver donaciones recibidas para su proyecto.

### 🔹 3. Donador
Usuario que realiza aportes económicos.  
Puede:
- Consultar todos los proyectos disponibles.  
- Donar a uno o varios proyectos.  
- Ver el historial de sus donaciones.

### 🔹 4. Auditor
Rol especializado en verificación y transparencia.  
Puede:
- Revisar todos los gastos.  
- Ver ingresos y donaciones.  
- Revisar inconsistencias.  
- Generar informes internos.

---

## Arquitectura del Proyecto

###  Estructura general
proyecto-final/
│── app.py
│── database.py
│── decorators.py
│── requirements.txt
│── vercel.json
│── replit.md
│── static/
│ ├── css/
│ │ ├── styles.css
│ ├── js/
│── templates/
│ ├── base.html
│ ├── login.html
│ ├── register.html
│ ├── dashboard_admin.html
│ ├── dashboard_coordinator.html
│ ├── dashboard_donor.html
│ ├── dashboard_auditor.html
│ ├── proyectos.html
│ ├── donaciones.html
│ ├── gastos.html
│── scripts/
│ ├── init_db.py 


---

## Base de Datos

El sistema usa **PostgreSQL**.

### Tablas principales:

- **users**  
- **projects**  
- **donations**  
- **expenses**  
- **roles**

### Relaciones clave

- Un usuario puede tener 1 rol.  
- Un proyecto pertenece a un coordinador.  
- Una donación pertenece a un usuario y a un proyecto.  
- Un gasto pertenece a un proyecto.

---

## Backend – Flask

### Características:

- Sistema de login usando sesiones.  
- Decoradores para restringir rutas por rol.  
- Conexión persistente a PostgreSQL mediante `psycopg2`.  
- Uso de Jinja2 para renderizado dinámico.  
- Manejo de errores y validaciones.  
- Rutas separadas por módulos lógicos.

---

## Frontend – Bootstrap + CSS propio + js para animaciones

Incluye:

- Modo claro y modo oscuro.  
- Tablas estilizadas.  
- Tarjetas dinámicas de proyectos.  
- Formularios limpios.  
- Dashboard por rol.  
- Alertas visuales.

---

## Seguridad Implementada

- Protección de rutas por rol.  
- Hash de contraseñas.  
- Validación de formularios.  
- Manejo de sesiones seguro.  
- Prevención de accesos indebidos.

---

## Instalación y Ejecución

###  Clonar el repositorio

```bash
git clone https://github.com/Gamertag001/proyecto-final
cd proyecto-final

2️⃣ Instalar dependencias
pip install -r requirements.txt

3️⃣ Configurar variables de entorno

Crear .env:

DATABASE_URL=postgresql://user:password@localhost:5432/proyecto
FLASK_SECRET_KEY=clave_super_secreta

4️⃣ Inicializar la base de datos
python scripts/init_db.py

5️⃣ Ejecutar el servidor
python app.py


El proyecto correrá en:

http://localhost:5000

 Paneles del Sistema
Panel del Administrador

Estadísticas globales.

Gestión de proyectos y coordinadores.

Control total del sistema.

Panel del Coordinador

Gastos.

Avances.

Reportes del proyecto asignado.

Panel del Donador

Lista de proyectos.

Donaciones.

Historial personal.

Panel del Auditor

Vista completa de ingresos y egresos.

Validación de gastos.

Reportes internos.

Scripts Incluidos
scripts/init_db.py

Crea todas las tablas necesarias y deja la BD lista.

 Despliegue

 Vercel

El archivo vercel.json permite configurar el backend para despliegue sin servidor.

 Contribuciones

Puedes hacer fork, sugerir cambios o mejorar la documentación.

Licencia

Proyecto de uso académico sin restricciones.

Autor

Proyecto subido por Gamertag001.
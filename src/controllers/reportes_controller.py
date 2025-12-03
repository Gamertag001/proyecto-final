from flask import render_template
from flask_login import login_required, current_user
from decorators import rol_required
from src.database import get_db
from src.models.ModelUser import ModelUser
from src.models.ModelProyecto import ModelProyecto
from src.models.ModelDonacion import ModelDonacion

@login_required
@rol_required(2)
def reportes():
    """Panel de reportes para administrador"""
    db = get_db()
    try:
        # Obtener todos los usuarios
        all_users = ModelUser.get_all(db)
        
        # Contar usuarios por rol
        donadores = len([u for u in all_users if u.get('id_rol') == 1]) if all_users else 0
        coordinadores = len([u for u in all_users if u.get('id_rol') == 3]) if all_users else 0
        usuarios_activos = len([u for u in all_users if u.get('id_rol') != 5]) if all_users else 0
        
        # Obtener todos los proyectos
        proyectos = ModelProyecto.get_all(db)
        total_proyectos = len(proyectos) if proyectos else 0
        
        # Calcular estadísticas de proyectos
        total_meta = sum(p.monto_objetivo or 0 for p in proyectos) if proyectos else 0
        total_recaudado = sum(p.monto_recaudado or 0 for p in proyectos) if proyectos else 0
        porcentaje_total = round((total_recaudado / total_meta * 100), 2) if total_meta > 0 else 0
        
        # Obtener todas las donaciones
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM donaciones")
        total_donaciones = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(monto) FROM donaciones")
        result = cursor.fetchone()
        suma_donaciones = result[0] if result[0] is not None else 0
        
        # Obtener donación promedio
        donacion_promedio = round((suma_donaciones / total_donaciones), 2) if total_donaciones > 0 else 0
        
        # Obtener top 5 proyectos por recaudación
        top_proyectos = sorted(proyectos, key=lambda p: p.monto_recaudado or 0, reverse=True)[:5] if proyectos else []
        
        # Obtener detalles de donaciones por proyecto
        cursor.execute("""
            SELECT p.id_proyecto, p.nombre, COUNT(d.id_donacion) as total_donaciones, 
                   SUM(d.monto) as total_monto, p.monto_objetivo
            FROM proyectos p
            LEFT JOIN donaciones d ON p.id_proyecto = d.id_proyecto
            GROUP BY p.id_proyecto, p.nombre, p.monto_objetivo
            ORDER BY total_monto DESC NULLS LAST
        """)
        donaciones_por_proyecto = cursor.fetchall()
        
        cursor.close()
        
    finally:
        db.close()
    
    return render_template('admin/reportes.html',
                         donadores=donadores,
                         coordinadores=coordinadores,
                         usuarios_activos=usuarios_activos,
                         total_proyectos=total_proyectos,
                         total_meta=total_meta,
                         total_recaudado=total_recaudado,
                         porcentaje_total=porcentaje_total,
                         total_donaciones=total_donaciones,
                         suma_donaciones=suma_donaciones,
                         donacion_promedio=donacion_promedio,
                         top_proyectos=top_proyectos,
                         donaciones_por_proyecto=donaciones_por_proyecto)

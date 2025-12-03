from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decorators import rol_required
from src.database import get_db
from src.models.ModelProyecto import ModelProyecto
from src.models.ModelObjetivo import ModelObjetivo
from src.models.ModelActividad import ModelActividad
from src.models.ModelTarea import ModelTarea
from src.models.entities.proyecto import Proyecto
from src.models.entities.donacion import Donacion

@login_required
@rol_required(3, 2)
def panel_coordinador():
    '''Vista principal del coordinador o administrador.'''
    db = get_db()
    try:
        if int(getattr(current_user, "id_rol",0)) == 2:
            proyectos = ModelProyecto.get_all(db)
        else:
            proyectos = ModelProyecto.get_by_user(db, current_user.id)
        
        proyectos_detalles = {}
        for proyecto in proyectos:
            objetivos = ModelObjetivo.get_by_proyecto(db, proyecto.id_proyecto)
            actividades = ModelActividad.get_by_proyecto(db, proyecto.id_proyecto)
            tareas = ModelTarea.get_by_proyecto(db, proyecto.id_proyecto)
            
            objetivos_completados = len([o for o in objetivos if o.completado]) if objetivos else 0
            total_objetivos = len(objetivos) if objetivos else 0
            
            actividades_completadas = len([a for a in actividades if a.estado == 'completada']) if actividades else 0
            total_actividades = len(actividades) if actividades else 0
            
            tareas_completadas = len([t for t in tareas if t.estado == 'completada']) if tareas else 0
            total_tareas = len(tareas) if tareas else 0
            
            proyectos_detalles[proyecto.id_proyecto] = {
                'objetivos': objetivos[:3] if objetivos else [],
                'actividades': actividades[:3] if actividades else [],
                'tareas': tareas[:3] if tareas else [],
                'objetivos_completados': objetivos_completados,
                'total_objetivos': total_objetivos,
                'actividades_completadas': actividades_completadas,
                'total_actividades': total_actividades,
                'tareas_completadas': tareas_completadas,
                'total_tareas': total_tareas,
            }
    finally:
        db.close()
    return render_template('coordinador/panel-coordinador.html', proyectos=proyectos, proyectos_detalles=proyectos_detalles)

@login_required
@rol_required(3, 2)
def crear_proyecto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        monto_objetivo = request.form.get('monto_objetivo', '0').strip()

        if not nombre:
            flash('El nombre del proyecto es obligatorio', 'danger')
            return redirect(url_for('crear_proyecto'))
        
        try: 
            monto_objetivo = float(monto_objetivo or 0)
        except ValueError:
            flash('Monto objetivo invalido', 'danger')
            return redirect(url_for('crear_proyecto'))
        
        db = get_db()
        try:
            proyecto_entity = Proyecto(
                None, nombre, descripcion, monto_objetivo, 0.0, current_user.id, 'activo', None
            )
            success = ModelProyecto.create(db, proyecto_entity)
            if success:
                flash('Proyecto creado exitosamente', 'success')
                return redirect(url_for('panel_coordinador'))
            else:
                flash('Error al crear proyecto', 'danger')
                return redirect(url_for('crear_proyecto'))
        finally:
            db.close()
    
    return render_template('coordinador/crear-proyecto.html')

@login_required
@rol_required(3, 2)
def editar_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        if int(getattr(current_user, "id_rol",0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para editar este proyecto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if request.method == 'POST':
            proyecto.nombre = request.form.get('nombre', proyecto.nombre).strip()
            proyecto.descripcion = request.form.get('descripcion', proyecto.descripcion).strip()

            try:
                proyecto.monto_objetivo = float(request.form.get('monto_objetivo', proyecto.monto_objetivo).strip())
            except ValueError:
                flash('Monto objetivo invalido', 'danger')
                return redirect(url_for('editar_proyecto', id_proyecto=id_proyecto))
            
            success, message = ModelProyecto.update(db, proyecto)
            if success:
                flash('Proyecto actualizado exitosamente', 'success')
                return redirect(url_for('panel_coordinador'))
            else:
                flash(f'Error al actualizar proyecto: {message}', 'danger')
        
        return render_template('coordinador/crear-proyecto.html', proyecto=proyecto)
    finally:
        db.close()

@login_required
@rol_required(3, 2)
def ver_donaciones_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        if int(getattr(current_user, "id_rol",0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para ver las donaciones de este proyecto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        donaciones = ModelProyecto.get_donaciones(db, id_proyecto)
    finally:
        db.close()
    return render_template('coordinador/ver-donaciones.html', proyecto=proyecto, donaciones=donaciones)

@login_required
@rol_required(3, 2)
def archivar_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para archivar este proyecto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        success, error = ModelProyecto.archivar(db, id_proyecto, current_user.id)
        if success:
            flash('Proyecto archivado exitosamente. Ya no sera visible al publico.', 'success')
        else:
            flash(f'Error al archivar el proyecto: {error}', 'danger')
    finally:
        db.close()
    
    return redirect(url_for('panel_coordinador'))


@login_required
@rol_required(3, 2)
def desarchivar_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para desarchivar este proyecto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        success, error = ModelProyecto.desarchivar(db, id_proyecto)
        if success:
            flash('Proyecto desarchivado exitosamente. Ahora es visible al publico.', 'success')
        else:
            flash(f'Error al desarchivar el proyecto: {error}', 'danger')
    finally:
        db.close()
    
    return redirect(url_for('panel_coordinador'))


@login_required
@rol_required(3, 2)
def reportes_coordinador():
    """Reportes personalizados para coordinador"""
    db = get_db()
    try:
        if int(getattr(current_user, "id_rol", 0)) == 2:
            proyectos = ModelProyecto.get_all(db)
        else:
            proyectos = ModelProyecto.get_by_user(db, current_user.id)
        
        total_proyectos = len(proyectos) if proyectos else 0
        total_meta = sum(p.monto_objetivo or 0 for p in proyectos) if proyectos else 0
        total_recaudado = sum(p.monto_recaudado or 0 for p in proyectos) if proyectos else 0
        porcentaje_total = round((total_recaudado / total_meta * 100), 2) if total_meta > 0 else 0
        
        cursor = db.cursor()
        
        if int(getattr(current_user, "id_rol", 0)) == 2:
            cursor.execute("SELECT COUNT(*) FROM donaciones")
            total_donaciones = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(monto) FROM donaciones")
            result = cursor.fetchone()
            suma_donaciones = result[0] if result[0] is not None else 0
        else:
            project_ids = [p.id_proyecto for p in proyectos] if proyectos else []
            if project_ids:
                placeholders = ','.join(['%s'] * len(project_ids))
                cursor.execute(f"SELECT COUNT(*) FROM donaciones WHERE id_proyecto IN ({placeholders})", project_ids)
                total_donaciones = cursor.fetchone()[0]
                cursor.execute(f"SELECT SUM(monto) FROM donaciones WHERE id_proyecto IN ({placeholders})", project_ids)
                result = cursor.fetchone()
                suma_donaciones = result[0] if result[0] is not None else 0
            else:
                total_donaciones = 0
                suma_donaciones = 0
        
        top_proyectos = sorted(proyectos, key=lambda p: p.monto_recaudado or 0, reverse=True)[:5] if proyectos else []
        
        if int(getattr(current_user, "id_rol", 0)) == 2:
            cursor.execute("""
                SELECT p.id_proyecto, p.nombre, COUNT(d.id_donacion) as total_donaciones, 
                       SUM(d.monto) as total_monto, p.monto_objetivo
                FROM proyectos p
                LEFT JOIN donaciones d ON p.id_proyecto = d.id_proyecto
                GROUP BY p.id_proyecto, p.nombre, p.monto_objetivo
                ORDER BY total_monto DESC NULLS LAST
            """)
        else:
            project_ids = [p.id_proyecto for p in proyectos] if proyectos else []
            if project_ids:
                placeholders = ','.join(['%s'] * len(project_ids))
                cursor.execute(f"""
                    SELECT p.id_proyecto, p.nombre, COUNT(d.id_donacion) as total_donaciones, 
                           SUM(d.monto) as total_monto, p.monto_objetivo
                    FROM proyectos p
                    LEFT JOIN donaciones d ON p.id_proyecto = d.id_proyecto
                    WHERE p.id_proyecto IN ({placeholders})
                    GROUP BY p.id_proyecto, p.nombre, p.monto_objetivo
                    ORDER BY total_monto DESC NULLS LAST
                """, project_ids)
            else:
                cursor.execute("SELECT NULL LIMIT 0")
        
        donaciones_por_proyecto = cursor.fetchall()
        cursor.close()
        
    finally:
        db.close()
    
    return render_template('coordinador/reportes.html',
                         total_proyectos=total_proyectos,
                         total_meta=total_meta,
                         total_recaudado=total_recaudado,
                         porcentaje_total=porcentaje_total,
                         total_donaciones=total_donaciones,
                         suma_donaciones=suma_donaciones,
                         top_proyectos=top_proyectos,
                         donaciones_por_proyecto=donaciones_por_proyecto)

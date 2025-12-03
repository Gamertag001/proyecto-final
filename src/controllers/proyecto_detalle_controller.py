from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from decorators import rol_required
from src.database import get_db
from src.models.ModelProyecto import ModelProyecto
from src.models.ModelObjetivo import ModelObjetivo
from src.models.ModelActividad import ModelActividad
from src.models.ModelResponsable import ModelResponsable
from src.models.ModelTarea import ModelTarea
from src.models.entities.objetivo import Objetivo
from src.models.entities.actividad import Actividad
from src.models.entities.responsable import Responsable
from src.models.entities.tarea import Tarea
from datetime import date


def verificar_permiso_proyecto(proyecto, db):
    if not proyecto:
        return False, 'Proyecto no encontrado'
    if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
        return False, 'No tienes permiso para acceder a este proyecto'
    return True, None


@login_required
@rol_required(3, 2)
def detalle_gestion_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        objetivos = ModelObjetivo.get_by_proyecto(db, id_proyecto)
        actividades = ModelActividad.get_by_proyecto(db, id_proyecto)
        responsables = ModelResponsable.get_by_proyecto(db, id_proyecto)
        tareas = ModelTarea.get_by_proyecto(db, id_proyecto)
        usuarios_disponibles = ModelResponsable.get_usuarios_disponibles(db, id_proyecto)
        usuarios_proyecto = ModelTarea.get_usuarios_proyecto(db, id_proyecto)
        
    finally:
        db.close()
    
    return render_template('coordinador/detalle-proyecto.html',
                          proyecto=proyecto,
                          objetivos=objetivos,
                          actividades=actividades,
                          responsables=responsables,
                          tareas=tareas,
                          usuarios_disponibles=usuarios_disponibles,
                          usuarios_proyecto=usuarios_proyecto,
                          today=date.today())


@login_required
@rol_required(3, 2)
def actualizar_estado_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        nuevo_estado = request.form.get('estado', '').strip()
        estados_validos = ['en_planificacion', 'en_ejecucion', 'finalizado']
        
        if nuevo_estado not in estados_validos:
            flash('Estado no valido', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
        
        proyecto.estado = nuevo_estado
        success, error_msg = ModelProyecto.update(db, proyecto)
        
        if success:
            flash(f'Estado del proyecto actualizado a: {nuevo_estado.replace("_", " ").title()}', 'success')
        else:
            flash(f'Error al actualizar el estado: {error_msg}', 'danger')
            
    finally:
        db.close()
    
    return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))


@login_required
@rol_required(3, 2)
def crear_objetivo(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        descripcion = request.form.get('descripcion', '').strip()
        if not descripcion:
            flash('La descripcion del objetivo es obligatoria', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
        
        objetivo = Objetivo(id_proyecto=id_proyecto, descripcion=descripcion)
        success, result = ModelObjetivo.create(db, objetivo)
        
        if success:
            flash('Objetivo creado exitosamente', 'success')
        else:
            flash(f'Error al crear objetivo: {result}', 'danger')
            
    finally:
        db.close()
    
    return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))


@login_required
@rol_required(3, 2)
def toggle_objetivo(id_objetivo):
    db = get_db()
    try:
        objetivo = ModelObjetivo.get_by_id(db, id_objetivo)
        if not objetivo:
            flash('Objetivo no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, objetivo.id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        success, error_msg = ModelObjetivo.toggle_completado(db, id_objetivo)
        
        if success:
            flash('Estado del objetivo actualizado', 'success')
        else:
            flash(f'Error al actualizar objetivo: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=objetivo.id_proyecto))
            
    finally:
        db.close()


@login_required
@rol_required(3, 2)
def eliminar_objetivo(id_objetivo):
    db = get_db()
    try:
        objetivo = ModelObjetivo.get_by_id(db, id_objetivo)
        if not objetivo:
            flash('Objetivo no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, objetivo.id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        id_proyecto = objetivo.id_proyecto
        success, error_msg = ModelObjetivo.delete(db, id_objetivo)
        
        if success:
            flash('Objetivo eliminado', 'success')
        else:
            flash(f'Error al eliminar objetivo: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
            
    finally:
        db.close()


@login_required
@rol_required(3, 2)
def crear_actividad(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha_inicio = request.form.get('fecha_inicio') or None
        fecha_fin = request.form.get('fecha_fin') or None
        
        if not nombre:
            flash('El nombre de la actividad es obligatorio', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
        
        actividad = Actividad(
            id_proyecto=id_proyecto, 
            nombre=nombre, 
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='pendiente'
        )
        success, result = ModelActividad.create(db, actividad)
        
        if success:
            flash('Actividad creada exitosamente', 'success')
        else:
            flash(f'Error al crear actividad: {result}', 'danger')
            
    finally:
        db.close()
    
    return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))


@login_required
@rol_required(3, 2)
def actualizar_estado_actividad(id_actividad):
    db = get_db()
    try:
        actividad = ModelActividad.get_by_id(db, id_actividad)
        if not actividad:
            flash('Actividad no encontrada', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, actividad.id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        nuevo_estado = request.form.get('estado', '').strip()
        estados_validos = ['pendiente', 'en_progreso', 'completada']
        
        if nuevo_estado not in estados_validos:
            flash('Estado no valido', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=actividad.id_proyecto))
        
        success, error_msg = ModelActividad.update_estado(db, id_actividad, nuevo_estado)
        
        if success:
            flash('Estado de la actividad actualizado', 'success')
        else:
            flash(f'Error al actualizar actividad: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=actividad.id_proyecto))
            
    finally:
        db.close()


@login_required
@rol_required(3, 2)
def eliminar_actividad(id_actividad):
    db = get_db()
    try:
        actividad = ModelActividad.get_by_id(db, id_actividad)
        if not actividad:
            flash('Actividad no encontrada', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, actividad.id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        id_proyecto = actividad.id_proyecto
        success, error_msg = ModelActividad.delete(db, id_actividad)
        
        if success:
            flash('Actividad eliminada', 'success')
        else:
            flash(f'Error al eliminar actividad: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
            
    finally:
        db.close()


@login_required
@rol_required(3, 2)
def agregar_responsable(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        id_usuario = request.form.get('id_usuario')
        rol_en_proyecto = request.form.get('rol_en_proyecto', '').strip()
        
        if not id_usuario:
            flash('Debes seleccionar un usuario', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
        
        responsable = Responsable(
            id_proyecto=id_proyecto,
            id_usuario=int(id_usuario),
            rol_en_proyecto=rol_en_proyecto
        )
        success, result = ModelResponsable.create(db, responsable)
        
        if success:
            flash('Responsable agregado exitosamente', 'success')
        else:
            flash(f'Error al agregar responsable: {result}', 'danger')
            
    finally:
        db.close()
    
    return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))


@login_required
@rol_required(3, 2)
def eliminar_responsable(id_responsable):
    db = get_db()
    try:
        responsable = ModelResponsable.get_by_id(db, id_responsable)
        if not responsable:
            flash('Responsable no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, responsable.id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        id_proyecto = responsable.id_proyecto
        success, error_msg = ModelResponsable.delete(db, id_responsable)
        
        if success:
            flash('Responsable eliminado del proyecto', 'success')
        else:
            flash(f'Error al eliminar responsable: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
            
    finally:
        db.close()


@login_required
@rol_required(3, 2)
def crear_tarea(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        descripcion = request.form.get('descripcion', '').strip()
        usuario_id = request.form.get('usuario_id') or None
        fecha_inicio = request.form.get('fecha_inicio') or None
        fecha_fin = request.form.get('fecha_fin') or None
        
        if not descripcion:
            flash('La descripcion de la tarea es obligatoria', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
        
        tarea = Tarea(
            descripcion=descripcion,
            estado='pendiente',
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            usuario_id=int(usuario_id) if usuario_id else None,
            proyecto_id=id_proyecto
        )
        success, result = ModelTarea.create(db, tarea)
        
        if success:
            flash('Tarea creada exitosamente', 'success')
        else:
            flash(f'Error al crear tarea: {result}', 'danger')
            
    finally:
        db.close()
    
    return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))


@login_required
@rol_required(3, 2)
def actualizar_estado_tarea(id_tarea):
    db = get_db()
    try:
        tarea = ModelTarea.get_by_id(db, id_tarea)
        if not tarea:
            flash('Tarea no encontrada', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, tarea.proyecto_id)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        nuevo_estado = request.form.get('estado', '').strip()
        estados_validos = ['pendiente', 'en_progreso', 'completada']
        
        if nuevo_estado not in estados_validos:
            flash('Estado no valido', 'danger')
            return redirect(url_for('detalle_gestion_proyecto', id_proyecto=tarea.proyecto_id))
        
        success, error_msg = ModelTarea.update_estado(db, id_tarea, nuevo_estado)
        
        if success:
            flash('Estado de la tarea actualizado', 'success')
        else:
            flash(f'Error al actualizar tarea: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=tarea.proyecto_id))
            
    finally:
        db.close()


@login_required
@rol_required(3, 2)
def eliminar_tarea(id_tarea):
    db = get_db()
    try:
        tarea = ModelTarea.get_by_id(db, id_tarea)
        if not tarea:
            flash('Tarea no encontrada', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, tarea.proyecto_id)
        permitido, error = verificar_permiso_proyecto(proyecto, db)
        if not permitido:
            flash(error, 'danger')
            return redirect(url_for('panel_coordinador'))
        
        id_proyecto = tarea.proyecto_id
        success, error_msg = ModelTarea.delete(db, id_tarea)
        
        if success:
            flash('Tarea eliminada', 'success')
        else:
            flash(f'Error al eliminar tarea: {error_msg}', 'danger')
        
        return redirect(url_for('detalle_gestion_proyecto', id_proyecto=id_proyecto))
            
    finally:
        db.close()

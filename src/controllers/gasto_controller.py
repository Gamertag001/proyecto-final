from flask import render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from decorators import rol_required
from src.database import get_db
from src.models.ModelGasto import ModelGasto
from src.models.ModelProyecto import ModelProyecto
from src.models.entities.gasto import Gasto
from src.utils.file_upload import save_file, delete_file, validate_file
from decimal import Decimal
from datetime import datetime
import os


@login_required
@rol_required(3, 2)
def listar_gastos_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para ver los gastos de este proyecto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        gastos = ModelGasto.get_by_proyecto(db, id_proyecto)
        total_gastos = ModelGasto.get_total_gastos_proyecto(db, id_proyecto)
        monto_recaudado = proyecto.monto_recaudado or 0
        fondos_disponibles = monto_recaudado - total_gastos
        puede_registrar_gastos = monto_recaudado > 0
        
    finally:
        db.close()
    
    return render_template('gastos/listar.html', 
                          proyecto=proyecto, 
                          gastos=gastos,
                          total_gastos=total_gastos,
                          monto_recaudado=monto_recaudado,
                          fondos_disponibles=fondos_disponibles,
                          puede_registrar_gastos=puede_registrar_gastos)


@login_required
@rol_required(3, 2)
def crear_gasto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para agregar gastos a este proyecto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if proyecto.archivado:
            flash('No se pueden agregar gastos a un proyecto archivado', 'danger')
            return redirect(url_for('listar_gastos_proyecto', id_proyecto=id_proyecto))
        
        categorias = ModelGasto.get_categorias(db)
        
        if request.method == 'POST':
            categoria = request.form.get('categoria', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            monto_str = request.form.get('monto', '0').strip()
            fecha_gasto_str = request.form.get('fecha_gasto', '').strip()
            
            if not categoria:
                flash('La categoria es obligatoria', 'danger')
                return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
            
            if not descripcion:
                flash('La descripcion es obligatoria', 'danger')
                return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
            
            try:
                monto = Decimal(monto_str)
                if monto <= 0:
                    raise ValueError("El monto debe ser mayor a cero")
            except (ValueError, TypeError):
                flash('El monto debe ser un numero valido mayor a cero', 'danger')
                return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
            
            try:
                fecha_gasto = datetime.strptime(fecha_gasto_str, '%Y-%m-%d').date()
            except ValueError:
                flash('La fecha del gasto es invalida', 'danger')
                return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
            
            is_valid, error_msg = ModelGasto.validar_presupuesto(db, id_proyecto, monto)
            if not is_valid:
                flash(error_msg, 'danger')
                return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
            
            archivo_nombre = None
            archivo_path = None
            
            if 'comprobante' in request.files:
                file = request.files['comprobante']
                if file and file.filename != '':
                    success, error, nombre, path = save_file(file)
                    if not success:
                        flash(error, 'danger')
                        return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
                    archivo_nombre = nombre
                    archivo_path = path
            
            gasto = Gasto(
                id_gasto=None,
                id_proyecto=id_proyecto,
                categoria=categoria,
                descripcion=descripcion,
                monto=monto,
                fecha_gasto=fecha_gasto,
                archivo_nombre=archivo_nombre,
                archivo_path=archivo_path,
                id_usuario=current_user.id,
                creado_en=None
            )
            
            success, result = ModelGasto.create(db, gasto)
            if success:
                flash('Gasto registrado exitosamente', 'success')
                return redirect(url_for('listar_gastos_proyecto', id_proyecto=id_proyecto))
            else:
                if archivo_path:
                    delete_file(archivo_path)
                flash(f'Error al registrar el gasto: {result}', 'danger')
                return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)
        
    finally:
        db.close()
    
    return render_template('gastos/crear.html', proyecto=proyecto, categorias=categorias)


@login_required
@rol_required(3, 2)
def editar_gasto(id_gasto):
    db = get_db()
    try:
        gasto = ModelGasto.get_by_id(db, id_gasto)
        if not gasto:
            flash('Gasto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, gasto.id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para editar este gasto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if proyecto.archivado:
            flash('No se pueden editar gastos de un proyecto archivado', 'danger')
            return redirect(url_for('listar_gastos_proyecto', id_proyecto=gasto.id_proyecto))
        
        categorias = ModelGasto.get_categorias(db)
        
        if request.method == 'POST':
            categoria = request.form.get('categoria', gasto.categoria).strip()
            descripcion = request.form.get('descripcion', gasto.descripcion).strip()
            monto_str = request.form.get('monto', str(gasto.monto)).strip()
            fecha_gasto_str = request.form.get('fecha_gasto', '').strip()
            
            try:
                monto = Decimal(monto_str)
                if monto <= 0:
                    raise ValueError("El monto debe ser mayor a cero")
            except (ValueError, TypeError):
                flash('El monto debe ser un numero valido mayor a cero', 'danger')
                return render_template('gastos/editar.html', gasto=gasto, proyecto=proyecto, categorias=categorias)
            
            try:
                fecha_gasto = datetime.strptime(fecha_gasto_str, '%Y-%m-%d').date()
            except ValueError:
                flash('La fecha del gasto es invalida', 'danger')
                return render_template('gastos/editar.html', gasto=gasto, proyecto=proyecto, categorias=categorias)
            
            is_valid, error_msg = ModelGasto.validar_presupuesto(db, gasto.id_proyecto, monto, id_gasto)
            if not is_valid:
                flash(error_msg, 'danger')
                return render_template('gastos/editar.html', gasto=gasto, proyecto=proyecto, categorias=categorias)
            
            archivo_nombre = gasto.archivo_nombre
            archivo_path = gasto.archivo_path
            old_archivo_path = gasto.archivo_path
            
            if 'comprobante' in request.files:
                file = request.files['comprobante']
                if file and file.filename != '':
                    success, error, nombre, path = save_file(file)
                    if not success:
                        flash(error, 'danger')
                        return render_template('gastos/editar.html', gasto=gasto, proyecto=proyecto, categorias=categorias)
                    archivo_nombre = nombre
                    archivo_path = path
            
            gasto.categoria = categoria
            gasto.descripcion = descripcion
            gasto.monto = monto
            gasto.fecha_gasto = fecha_gasto
            gasto.archivo_nombre = archivo_nombre
            gasto.archivo_path = archivo_path
            
            success, error = ModelGasto.update(db, gasto)
            if success:
                if old_archivo_path and old_archivo_path != archivo_path:
                    delete_file(old_archivo_path)
                flash('Gasto actualizado exitosamente', 'success')
                return redirect(url_for('listar_gastos_proyecto', id_proyecto=gasto.id_proyecto))
            else:
                if archivo_path and archivo_path != old_archivo_path:
                    delete_file(archivo_path)
                flash(f'Error al actualizar el gasto: {error}', 'danger')
        
    finally:
        db.close()
    
    return render_template('gastos/editar.html', gasto=gasto, proyecto=proyecto, categorias=categorias)


@login_required
@rol_required(3, 2)
def eliminar_gasto(id_gasto):
    db = get_db()
    try:
        gasto = ModelGasto.get_by_id(db, id_gasto)
        if not gasto:
            flash('Gasto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, gasto.id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para eliminar este gasto', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if proyecto.archivado:
            flash('No se pueden eliminar gastos de un proyecto archivado', 'danger')
            return redirect(url_for('listar_gastos_proyecto', id_proyecto=gasto.id_proyecto))
        
        id_proyecto = gasto.id_proyecto
        success, error, archivo_path = ModelGasto.delete(db, id_gasto)
        
        if success:
            if archivo_path:
                delete_file(archivo_path)
            flash('Gasto eliminado exitosamente', 'success')
        else:
            flash(f'Error al eliminar el gasto: {error}', 'danger')
        
    finally:
        db.close()
    
    return redirect(url_for('listar_gastos_proyecto', id_proyecto=id_proyecto))


@login_required
@rol_required(3, 2)
def descargar_comprobante(id_gasto):
    db = get_db()
    try:
        gasto = ModelGasto.get_by_id(db, id_gasto)
        if not gasto:
            flash('Gasto no encontrado', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        proyecto = ModelProyecto.get_by_id(db, gasto.id_proyecto)
        if int(getattr(current_user, "id_rol", 0)) == 3 and proyecto.id_usuario != current_user.id:
            flash('No tienes permiso para ver este comprobante', 'danger')
            return redirect(url_for('panel_coordinador'))
        
        if not gasto.archivo_path:
            flash('Este gasto no tiene comprobante adjunto', 'warning')
            return redirect(url_for('listar_gastos_proyecto', id_proyecto=gasto.id_proyecto))
        
        file_path = os.path.join('static', gasto.archivo_path)
        if not os.path.exists(file_path):
            flash('El archivo del comprobante no fue encontrado', 'danger')
            return redirect(url_for('listar_gastos_proyecto', id_proyecto=gasto.id_proyecto))
        
    finally:
        db.close()
    
    return send_file(file_path, 
                    download_name=gasto.archivo_nombre or 'comprobante',
                    as_attachment=True)

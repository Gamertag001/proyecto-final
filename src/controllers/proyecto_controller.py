# src/controllers/proyecto_controller.py
from flask import render_template, request, redirect, url_for, flash
from src.database import get_db
from src.models.ModelProyecto import ModelProyecto
from src.models.ModelDonacion import ModelDonacion
from flask_login import login_required, current_user
from src.models.entities.donacion import Donacion

def listar_proyectos():
    db = get_db()
    try:
        proyectos = ModelProyecto.get_activos(db)
        
        donaciones_usuario = {}
        if current_user.is_authenticated and current_user.id_rol == 1:
            donaciones = ModelDonacion.get_by_user(db, current_user.id)
            for donacion in donaciones:
                if donacion.id_proyecto not in donaciones_usuario:
                    donaciones_usuario[donacion.id_proyecto] = 0
                donaciones_usuario[donacion.id_proyecto] += donacion.monto
    finally:
        db.close()
    
    return render_template('proyectos/listar.html', proyectos=proyectos, donaciones_usuario=donaciones_usuario)

def detalle_proyecto(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('listar_proyectos'))

        donaciones = ModelDonacion.get_by_project(db, id_proyecto)
    finally:
        db.close()

    return render_template('proyectos/detalle.html', proyecto=proyecto, donaciones=donaciones)

@login_required
def formulario_donacion(id_proyecto):
    db = get_db()
    try:
        proyecto = ModelProyecto.get_by_id(db, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('listar_proyectos'))
        
        if proyecto.archivado:
            flash('Este proyecto esta archivado y no acepta donaciones', 'warning')
            return redirect(url_for('listar_proyectos'))

        if request.method == 'POST':
            try:
                monto = float(request.form.get('monto', '0'))
            except ValueError:
                flash('Monto inválido', 'danger')
                return redirect(url_for('formulario_donacion', id_proyecto=id_proyecto))

            if monto <= 0:
                flash('El monto debe ser mayor que 0', 'danger')
                return redirect(url_for('formulario_donacion', id_proyecto=id_proyecto))

            # crear donación y actualizar proyecto
            donacion = Donacion(None, current_user.id, id_proyecto, monto, None)
            ok = ModelDonacion.create(db, donacion)
            if ok:
                # actualizar monto recaudado en proyecto
                ModelDonacion.sumar_al_proyecto(db, id_proyecto, monto)
                flash('Gracias por tu donación', 'success')
            else:
                flash('Error procesando la donación', 'danger')

            return redirect(url_for('detalle_proyecto', id_proyecto=id_proyecto))

    finally:
        db.close()

    return render_template('proyectos/donar.html', proyecto=proyecto)

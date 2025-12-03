# src/controllers/donacion_controller.py
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.database import get_db
from src.models.ModelDonacion import ModelDonacion
from src.models.entities.donacion import Donacion

@login_required
def historial_donaciones_usuario():
    db = get_db()
    try:
        donaciones = ModelDonacion.get_by_user(db, current_user.id)
        total_donado = sum(d.monto for d in donaciones) if donaciones else 0
    finally:
        db.close()
    return render_template('donaciones/historial.html', donaciones=donaciones, total_donado=total_donado)

# API minimal para crear donación (por ejemplo para fetch/ajax)
@login_required
def api_crear_donacion():
    data = request.get_json() or {}
    id_proyecto = data.get('id_proyecto')
    monto = data.get('monto')

    if not id_proyecto or not monto:
        return jsonify(success=False, message="Datos incompletos"), 400

    db = get_db()
    try:
        donacion = Donacion(None, current_user.id, id_proyecto, monto, None)
        ok = ModelDonacion.create(db, donacion)
        if not ok:
            return jsonify(success=False, message="Error al guardar donación"), 500

        ModelDonacion.sumar_al_proyecto(db, id_proyecto, monto)
    finally:
        db.close()

    return jsonify(success=True, message="Donación procesada")

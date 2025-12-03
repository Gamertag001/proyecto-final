from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from src.models.ModelUser import ModelUser
from src.database import get_db
from decorators import rol_required

# Vista de espera para usuarios desactivados
@login_required
@rol_required(5)
def disabled_page():
    """
    Vista para usuarios desactivados.
    - Requiere iniciar sesión.
    - Solo accesible para rol 5 (desactivado).
    """
    return render_template('disabled/disabled.html')
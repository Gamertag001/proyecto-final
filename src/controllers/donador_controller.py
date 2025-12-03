from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decorators import rol_required
from src.database import get_db
from src.models.ModelDonacion import ModelDonacion
from src.models.ModelUser import ModelUser

# Vista principal del donador (rol 1)
@login_required
@rol_required(1, 2)  # El rol 1 y 2 pueden entrar
def home():
    """
    Vista principal del donador o administrador.
    - Requiere iniciar sesión.
    - Solo accesible para roles 1 (donador) y 2 (admin).
    """
    db = get_db()
    try:
        # Obtener donaciones del usuario actual
        donaciones = ModelDonacion.get_by_user(db, current_user.id)
        
        # Calcular estadísticas
        total_donado = sum(d.monto for d in donaciones) if donaciones else 0
        numero_donaciones = len(donaciones) if donaciones else 0
        numero_proyectos = len(set(d.id_proyecto for d in donaciones)) if donaciones else 0
        
    finally:
        db.close()
    
    return render_template('donador/home.html', 
                         total_donado=total_donado,
                         numero_donaciones=numero_donaciones,
                         numero_proyectos=numero_proyectos)


@login_required
@rol_required(1, 2)
def mi_informacion():
    """
    Vista para que el donador pueda ver y actualizar su información de contacto
    y preferencias de comunicación.
    """
    db = get_db()
    try:
        perfil = ModelUser.get_profile(db, current_user.id)
        
        if request.method == 'POST':
            fullname = request.form.get('fullname', '').strip()
            correo = request.form.get('correo', '').strip()
            telefono = request.form.get('telefono', '').strip()
            direccion = request.form.get('direccion', '').strip()
            preferencia_email = request.form.get('preferencia_email') == 'on'
            preferencia_sms = request.form.get('preferencia_sms') == 'on'
            notas = request.form.get('notas', '').strip()
            
            if not fullname:
                flash('El nombre completo es obligatorio', 'danger')
                return render_template('donador/mi-informacion.html', perfil=perfil)
            
            if not correo:
                flash('El correo electrónico es obligatorio', 'danger')
                return render_template('donador/mi-informacion.html', perfil=perfil)
            
            success, error = ModelUser.update_profile(
                db, current_user.id, fullname, correo, telefono, direccion,
                preferencia_email, preferencia_sms, notas
            )
            
            if success:
                flash('Tu información ha sido actualizada exitosamente', 'success')
                perfil = ModelUser.get_profile(db, current_user.id)
            else:
                flash(f'Error al actualizar la información: {error}', 'danger')
        
    finally:
        db.close()
    
    return render_template('donador/mi-informacion.html', perfil=perfil)

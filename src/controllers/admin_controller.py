from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from decorators import rol_required
from src.database import get_db
from src.models.ModelUser import ModelUser
from src.models.ModelProyecto import ModelProyecto
from src.models.ModelDonacion import ModelDonacion

# Vista principal del panel admin
@login_required
@rol_required(2)
def panel():
    db = get_db()
    try:
        # Obtener estadísticas
        users_data = ModelUser.get_all(db)
        proyectos = ModelProyecto.get_all(db)
        
        # Contar usuarios activos (no desactivados, id_rol != 5)
        usuarios_registrados = len([u for u in users_data if u.get('id_rol') != 5]) if users_data else 0
        
        # Contar proyectos
        proyectos_activos = len(proyectos) if proyectos else 0
        
        # Calcular total recaudado
        total_recaudado = sum(p.monto_recaudado or 0 for p in proyectos) if proyectos else 0
    finally:
        db.close()
    
    return render_template('admin/panel.html', 
                         usuarios_registrados=usuarios_registrados,
                         proyectos_activos=proyectos_activos,
                         total_recaudado=total_recaudado)


@login_required
@rol_required(2)
def manage_user():
    db = get_db()
    users = ModelUser.get_all(db)
    db.close()
    return render_template('admin/vista-administrador-usuarios.html', users=users)


@login_required
@rol_required(2)
def edit_user(user_id):
    db = get_db()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        id_rol = request.form.get('id_rol', '').strip()

        if not username or not fullname or not email:
            db.close()
            flash('Nombre de usuario, nombre completo y email son obligatorios', 'danger')
            return redirect(url_for('edit_user', user_id=user_id))

        success, message = ModelUser.update(db, user_id, username=username, fullname=fullname, email=email, id_rol=id_rol)
        db.close()
        if success:
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('manage_user'))
        else:
            flash(f'Error al actualizar: {message}', 'danger')
            return redirect(url_for('edit_user', user_id=user_id))

    user = ModelUser.get_by_id(db, user_id)
    roles = ModelUser.get_roles(db)
    db.close()
    if user is None:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('manage_user'))
    return render_template('admin/editar-usuario.html', user=user, roles=roles)


@login_required
@rol_required(2)
def delete_user(user_id):
    db = get_db()
    success, message = ModelUser.delete(db, user_id)
    db.close()
    if success:
        flash('Usuario eliminado', 'success')
    else:
        flash(f'Error eliminando usuario: {message}', 'danger')
    return redirect(url_for('manage_user'))


@login_required
@rol_required(2)
def toggle_user_status(user_id):
    db = get_db()
    user = ModelUser.get_by_id(db, user_id)

    if not user:
        db.close()
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('manage_user'))

    # Evitar que el administrador se desactive a sí mismo
    if current_user.is_authenticated and current_user.id == user.id:
        db.close()
        flash('No puedes desactivar tu propia cuenta', 'danger')
        return redirect(url_for('manage_user'))

    # Obtener rol actual
    try:
        current_role = int(user.id_rol)
    except Exception:
        current_role = 1

    # 1 = activo, 5 = desactivado
    new_role = 1 if current_role == 5 else 5

    # Actualizar usuario manteniendo los valores actuales
    success, message = ModelUser.update(
        db,
        user_id,
        username=user.username,
        fullname=user.fullname,
        email=user.email,
        id_rol=new_role
    )

    db.close()

    if success:
        flash('Estado actualizado correctamente', 'success')
    else:
        flash(f'Error actualizando estado: {message}', 'danger')

    return redirect(url_for('manage_user'))

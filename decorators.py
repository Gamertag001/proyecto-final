from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def rol_required(*roles):
    """
    Decorador para restringir rutas a ciertos roles.
    Ejemplo:
        @rol_required(1)
        @rol_required(1, 2)
        @rol_required('admin')
        @rol_required(5)
    """
    # normalizar valores permitidos (acepta ints y strings)
    allowed = set()
    for r in roles:
        allowed.add(r)
        try:
            allowed.add(int(r))
        except Exception:
            pass
        allowed.add(str(r))

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión para acceder a esta página.")
                return redirect(url_for("login"))

            # detectar nombre de atributo posible en current_user
            candidate_attrs = ('id_rol', 'idRol', 'role', 'rol', 'id_role')
            user_role = None
            for a in candidate_attrs:
                if hasattr(current_user, a):
                    user_role = getattr(current_user, a)
                    break

            # comparar de forma tolerante a tipos (int/str)
            if user_role is None:
                flash("No tienes permiso para acceder a esta página.")
                return redirect(url_for("login"))

            if (user_role not in allowed) and (str(user_role) not in allowed):
                try:
                    if int(user_role) not in allowed:
                        flash("No tienes permiso para acceder a esta página.")
                        return redirect(url_for("login"))
                except Exception:
                    flash("No tienes permiso para acceder a esta página.")
                    return redirect(url_for("login"))

            return f(*args, **kwargs)

        return decorated_function

    return wrapper

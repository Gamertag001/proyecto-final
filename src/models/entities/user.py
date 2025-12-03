from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class User(UserMixin):
    # NOTA IMPORTANTE: El orden de los argumentos en __init__ debe ser exactamente
    # el mismo que en las llamadas de ModelUser.py (login, get_by_id).
    def __init__(self, id, username, password, email, id_rol, fullname="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.id_rol = id_rol
        self.fullname = fullname

    # La implementación de get_id es necesaria para Flask-Login
    def get_id(self):
        # Asegúrate de que el id sea una cadena para Flask-Login
        return str(self.id)

    @staticmethod
    def check_password(hashed_password, password):
        """Verifica si la contraseña ingresada coincide con el hash almacenado"""
        return check_password_hash(hashed_password, password)

    @staticmethod
    def generate_password(password):
        """Genera un hash para la contraseña"""
        return generate_password_hash(password)

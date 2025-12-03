from .entities.user import User
# Importamos el cursor de diccionario de psycopg2 para que las filas se lean como diccionarios
from psycopg2.extras import RealDictCursor 

class ModelUser():
    @classmethod
    def login(cls, db, user):
        cursor = None
        try:
            # CORRECCIÓN 1: Usar RealDictCursor en lugar de dictionary=True
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """ SELECT id, nombre, correo, password, fullname, id_rol FROM usuarios
                      WHERE nombre = %s """
            cursor.execute(sql, (user.username,))
            row = cursor.fetchone()
            if row:
                print("USER.OBJETO password:", repr(user.password))
                print("TIPO:", type(user.password))
                # 👇 PÉGALO AQUÍ
                print("PASS ingresado:", user.password)
                print("HASH en BD:", row['password'])
                print("COINCIDEN?", User.check_password(row['password'], user.password))
                # 👆
            
                # El resto del código de login (extracción de datos) funciona porque RealDictCursor
                # devuelve las filas como un diccionario.
                if User.check_password(row['password'], user.password):
                    logged_user = User(
                        row['id'],        # id
                        row['nombre'],    # username
                        row['password'],  # password (HASH)
                        row['correo'],    # email
                        row['id_rol'],    # rol
                        row['fullname']   # fullname
                    )
                    return logged_user
            
            return None
        except Exception as ex:
            # Aquí es útil imprimir el error en el log del servidor, no solo lanzarlo
            print(f"Error en login: {ex}") 
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_by_id(cls, db, id):
        cursor = None
        try:
            # CORRECCIÓN 2: Usar RealDictCursor
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """ SELECT id, nombre, correo, fullname, id_rol FROM usuarios
                      WHERE id = %s """
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            if row is not None:
                logged_user = User(
                    row['id'],
                    row['nombre'],
                    None, # Contraseña no es necesaria aquí
                    row['correo'],
                    row['id_rol'],
                    row['fullname'],
                )
                return logged_user
            return None
        except Exception as ex:
            print(f"Error en get_by_id: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def register(cls, db, user):
        cursor = None
        try:
            # CORRECCIÓN 3: Usar el cursor predeterminado para inserciones
            # En las inserciones no necesitamos RealDictCursor, un cursor normal es suficiente.
            cursor = db.cursor() 
            sql = """ INSERT INTO usuarios (nombre, correo, password, fullname, id_rol)
                      VALUES (%s, %s, %s, %s, %s) """
            
            # Asumo que esta función existe y usa una librería como Bcrypt
            hashed_password = User.generate_password(user.password) 
            
            # Ejecución de la inserción - usar el rol del objeto user (por defecto 1 = Donador)
            id_rol = user.id_rol if user.id_rol and user.id_rol in [1, 2, 3, 4] else 1
            cursor.execute(sql, (user.username, user.email, hashed_password, user.fullname, id_rol))
            
            # Confirmar la transacción
            db.commit()
            
            return True
        except Exception as ex:
            # Si hay un error (ej. nombre de usuario duplicado), forzamos un rollback
            db.rollback()
            print(f"Error en register: {ex}")
            # NO elevamos la excepción directamente, ya que Flask puede manejar el error
            # en el controlador. Devolvemos False si no se pudo registrar.
            return False 
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_all(cls, db):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT u.id, u.nombre, u.correo, u.fullname, u.id_rol,
                       COALESCE(r.nombre_rol, '') AS rol_nombre
                FROM usuarios u
                LEFT JOIN roles r ON u.id_rol = r.id_rol
                ORDER BY u.id
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows if rows is not None else []
        except Exception as ex:
            print(f"Error en get_all: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_roles(cls, db):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = "SELECT id_rol, nombre_rol FROM roles ORDER BY id_rol"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows if rows is not None else []
        except Exception as ex:
            print(f"Error en get_roles: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def update(cls, db, id, username=None, fullname=None, email=None, id_rol=None):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """ UPDATE usuarios
                      SET nombre = %s,
                          fullname = %s,
                          correo = %s,
                          id_rol = %s
                      WHERE id = %s """
            cursor.execute(sql, (username, fullname, email, id_rol, id))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Usuario no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error en update: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def delete(cls, db, id):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM usuarios WHERE id = %s"
            cursor.execute(sql, (id,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Usuario no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error en delete: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def toggle_status(cls, db, id):
        cursor = None
        try:
            cursor = db.cursor()
            # Primero obtenemos el rol actual
            sql_get = "SELECT id_rol FROM usuarios WHERE id = %s"
            cursor.execute(sql_get, (id,))
            row = cursor.fetchone()
            if row is None:
                return (False, "Usuario no encontrado")
            current_rol = row[0]
            # Alternamos el rol entre activo (1) y desactivado (5)
            new_rol = 5 if current_rol != 5 else 1
            sql_update = "UPDATE usuarios SET id_rol = %s WHERE id = %s"
            cursor.execute(sql_update, (new_rol, id))
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error en toggle_status: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_profile(cls, db, user_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT id, nombre, correo, fullname, id_rol, 
                       telefono, direccion, preferencia_email, preferencia_sms, notas
                FROM usuarios WHERE id = %s
            """
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return row
        except Exception as ex:
            print(f"Error en get_profile: {ex}")
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def update_profile(cls, db, user_id, fullname, correo, telefono, direccion, 
                       preferencia_email, preferencia_sms, notas):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE usuarios
                SET fullname = %s,
                    correo = %s,
                    telefono = %s,
                    direccion = %s,
                    preferencia_email = %s,
                    preferencia_sms = %s,
                    notas = %s
                WHERE id = %s
            """
            cursor.execute(sql, (fullname, correo, telefono, direccion, 
                                 preferencia_email, preferencia_sms, notas, user_id))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Usuario no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error en update_profile: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()

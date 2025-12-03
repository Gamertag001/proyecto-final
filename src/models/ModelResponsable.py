from psycopg2.extras import RealDictCursor
from .entities.responsable import Responsable

class ModelResponsable:
    @classmethod
    def get_by_proyecto(cls, db, proyecto_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT r.*, u.fullname as usuario_nombre, u.correo as usuario_correo
                FROM responsables r
                JOIN usuarios u ON r.id_usuario = u.id
                WHERE r.id_proyecto = %s
                ORDER BY r.fecha_asignacion ASC
            """
            cursor.execute(sql, (proyecto_id,))
            rows = cursor.fetchall()
            return [Responsable.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener responsables por proyecto: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_by_id(cls, db, responsable_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT r.*, u.fullname as usuario_nombre, u.correo as usuario_correo
                FROM responsables r
                JOIN usuarios u ON r.id_usuario = u.id
                WHERE r.id_responsable = %s
            """
            cursor.execute(sql, (responsable_id,))
            row = cursor.fetchone()
            return Responsable.from_row(row) if row else None
        except Exception as ex:
            print(f"Error al obtener responsable por ID: {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def create(cls, db, responsable):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                INSERT INTO responsables (id_proyecto, id_usuario, rol_en_proyecto)
                VALUES (%s, %s, %s)
                RETURNING id_responsable
            """
            cursor.execute(sql, (
                responsable.id_proyecto,
                responsable.id_usuario,
                responsable.rol_en_proyecto
            ))
            responsable_id = cursor.fetchone()[0]
            db.commit()
            return (True, responsable_id)
        except Exception as ex:
            db.rollback()
            if 'unique constraint' in str(ex).lower() or 'duplicate' in str(ex).lower():
                return (False, "Este usuario ya es responsable del proyecto")
            print(f"Error al crear responsable: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def update(cls, db, responsable):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE responsables
                SET rol_en_proyecto = %s
                WHERE id_responsable = %s
            """
            cursor.execute(sql, (
                responsable.rol_en_proyecto,
                responsable.id_responsable
            ))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Responsable no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar responsable: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def delete(cls, db, responsable_id):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM responsables WHERE id_responsable = %s"
            cursor.execute(sql, (responsable_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Responsable no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al eliminar responsable: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_usuarios_disponibles(cls, db, proyecto_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT u.id, u.fullname, u.correo
                FROM usuarios u
                WHERE u.id_rol IN (1, 2, 3)
                AND u.id NOT IN (
                    SELECT id_usuario FROM responsables WHERE id_proyecto = %s
                )
                ORDER BY u.fullname
            """
            cursor.execute(sql, (proyecto_id,))
            return cursor.fetchall()
        except Exception as ex:
            print(f"Error al obtener usuarios disponibles: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_all_usuarios(cls, db):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT id, fullname, correo
                FROM usuarios
                WHERE id_rol IN (1, 2, 3)
                ORDER BY fullname
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as ex:
            print(f"Error al obtener todos los usuarios: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()

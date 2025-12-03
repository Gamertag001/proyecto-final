from psycopg2.extras import RealDictCursor
from .entities.tarea import Tarea

class ModelTarea:
    @classmethod
    def get_by_proyecto(cls, db, proyecto_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT t.*, u.fullname as usuario_nombre 
                FROM tareas t
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                WHERE t.proyecto_id = %s
                ORDER BY t.fecha_fin ASC NULLS LAST, t.creado_en DESC
            """
            cursor.execute(sql, (proyecto_id,))
            rows = cursor.fetchall()
            return [Tarea.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener tareas por proyecto: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_by_usuario(cls, db, usuario_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT t.*, u.fullname as usuario_nombre, p.nombre as proyecto_nombre
                FROM tareas t
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                LEFT JOIN proyectos p ON t.proyecto_id = p.id_proyecto
                WHERE t.usuario_id = %s
                ORDER BY t.fecha_fin ASC NULLS LAST, t.creado_en DESC
            """
            cursor.execute(sql, (usuario_id,))
            rows = cursor.fetchall()
            return [Tarea.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener tareas por usuario: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_by_id(cls, db, tarea_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT t.*, u.fullname as usuario_nombre
                FROM tareas t
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                WHERE t.id = %s
            """
            cursor.execute(sql, (tarea_id,))
            row = cursor.fetchone()
            return Tarea.from_row(row) if row else None
        except Exception as ex:
            print(f"Error al obtener tarea por ID: {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def create(cls, db, tarea):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                INSERT INTO tareas (descripcion, estado, fecha_inicio, fecha_fin, usuario_id, proyecto_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            cursor.execute(sql, (
                tarea.descripcion,
                tarea.estado or 'pendiente',
                tarea.fecha_inicio,
                tarea.fecha_fin,
                tarea.usuario_id,
                tarea.proyecto_id
            ))
            tarea_id = cursor.fetchone()[0]
            db.commit()
            return (True, tarea_id)
        except Exception as ex:
            db.rollback()
            print(f"Error al crear tarea: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def update(cls, db, tarea):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE tareas
                SET descripcion = %s, estado = %s, fecha_inicio = %s, 
                    fecha_fin = %s, usuario_id = %s
                WHERE id = %s
            """
            cursor.execute(sql, (
                tarea.descripcion,
                tarea.estado,
                tarea.fecha_inicio,
                tarea.fecha_fin,
                tarea.usuario_id,
                tarea.id
            ))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Tarea no encontrada")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar tarea: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def update_estado(cls, db, tarea_id, nuevo_estado):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "UPDATE tareas SET estado = %s WHERE id = %s"
            cursor.execute(sql, (nuevo_estado, tarea_id))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Tarea no encontrada")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar estado de tarea: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def delete(cls, db, tarea_id):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM tareas WHERE id = %s"
            cursor.execute(sql, (tarea_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Tarea no encontrada")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al eliminar tarea: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_usuarios_proyecto(cls, db, proyecto_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT DISTINCT u.id, u.fullname, u.correo
                FROM usuarios u
                LEFT JOIN responsables r ON u.id = r.id_usuario AND r.id_proyecto = %s
                LEFT JOIN proyectos p ON p.id_usuario = u.id AND p.id_proyecto = %s
                WHERE r.id_responsable IS NOT NULL OR p.id_proyecto IS NOT NULL
                ORDER BY u.fullname
            """
            cursor.execute(sql, (proyecto_id, proyecto_id))
            return cursor.fetchall()
        except Exception as ex:
            print(f"Error al obtener usuarios del proyecto: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()

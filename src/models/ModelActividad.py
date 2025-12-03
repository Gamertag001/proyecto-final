from psycopg2.extras import RealDictCursor
from .entities.actividad import Actividad

class ModelActividad:
    @classmethod
    def get_by_proyecto(cls, db, proyecto_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT * FROM actividades 
                WHERE id_proyecto = %s
                ORDER BY fecha_inicio ASC NULLS LAST, id_actividad ASC
            """
            cursor.execute(sql, (proyecto_id,))
            rows = cursor.fetchall()
            return [Actividad.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener actividades por proyecto: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_by_id(cls, db, actividad_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = "SELECT * FROM actividades WHERE id_actividad = %s"
            cursor.execute(sql, (actividad_id,))
            row = cursor.fetchone()
            return Actividad.from_row(row) if row else None
        except Exception as ex:
            print(f"Error al obtener actividad por ID: {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def create(cls, db, actividad):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                INSERT INTO actividades (id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_actividad
            """
            cursor.execute(sql, (
                actividad.id_proyecto,
                actividad.nombre,
                actividad.descripcion,
                actividad.fecha_inicio,
                actividad.fecha_fin,
                actividad.estado or 'pendiente'
            ))
            actividad_id = cursor.fetchone()[0]
            db.commit()
            return (True, actividad_id)
        except Exception as ex:
            db.rollback()
            print(f"Error al crear actividad: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def update(cls, db, actividad):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE actividades
                SET nombre = %s, descripcion = %s, fecha_inicio = %s, 
                    fecha_fin = %s, estado = %s
                WHERE id_actividad = %s
            """
            cursor.execute(sql, (
                actividad.nombre,
                actividad.descripcion,
                actividad.fecha_inicio,
                actividad.fecha_fin,
                actividad.estado,
                actividad.id_actividad
            ))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Actividad no encontrada")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar actividad: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def update_estado(cls, db, actividad_id, nuevo_estado):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "UPDATE actividades SET estado = %s WHERE id_actividad = %s"
            cursor.execute(sql, (nuevo_estado, actividad_id))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Actividad no encontrada")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar estado de actividad: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def delete(cls, db, actividad_id):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM actividades WHERE id_actividad = %s"
            cursor.execute(sql, (actividad_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Actividad no encontrada")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al eliminar actividad: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()

from psycopg2.extras import RealDictCursor
from .entities.objetivo import Objetivo

class ModelObjetivo:
    @classmethod
    def get_by_proyecto(cls, db, proyecto_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT * FROM objetivos 
                WHERE id_proyecto = %s
                ORDER BY fecha_creacion ASC
            """
            cursor.execute(sql, (proyecto_id,))
            rows = cursor.fetchall()
            return [Objetivo.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener objetivos por proyecto: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_by_id(cls, db, objetivo_id):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = "SELECT * FROM objetivos WHERE id_objetivo = %s"
            cursor.execute(sql, (objetivo_id,))
            row = cursor.fetchone()
            return Objetivo.from_row(row) if row else None
        except Exception as ex:
            print(f"Error al obtener objetivo por ID: {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def create(cls, db, objetivo):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                INSERT INTO objetivos (id_proyecto, descripcion, completado)
                VALUES (%s, %s, %s)
                RETURNING id_objetivo
            """
            cursor.execute(sql, (
                objetivo.id_proyecto,
                objetivo.descripcion,
                objetivo.completado or False
            ))
            objetivo_id = cursor.fetchone()[0]
            db.commit()
            return (True, objetivo_id)
        except Exception as ex:
            db.rollback()
            print(f"Error al crear objetivo: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def update(cls, db, objetivo):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE objetivos
                SET descripcion = %s, completado = %s
                WHERE id_objetivo = %s
            """
            cursor.execute(sql, (
                objetivo.descripcion,
                objetivo.completado,
                objetivo.id_objetivo
            ))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Objetivo no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar objetivo: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def toggle_completado(cls, db, objetivo_id):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE objetivos 
                SET completado = NOT completado
                WHERE id_objetivo = %s
            """
            cursor.execute(sql, (objetivo_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Objetivo no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al cambiar estado de objetivo: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def delete(cls, db, objetivo_id):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM objetivos WHERE id_objetivo = %s"
            cursor.execute(sql, (objetivo_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Objetivo no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al eliminar objetivo: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()

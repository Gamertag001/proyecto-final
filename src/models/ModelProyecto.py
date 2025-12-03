from psycopg2.extras import RealDictCursor
from .entities.proyecto import Proyecto

class ModelProyecto:
    @classmethod
    def get_all(cls, db, incluir_archivados=True):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            if incluir_archivados:
                sql = """SELECT id_proyecto, nombre, descripcion, monto_objetivo, monto_recaudado, 
                         estado, fecha_creacion, archivado, archivado_en, archivado_por 
                         FROM proyectos ORDER BY fecha_creacion DESC"""
            else:
                sql = """SELECT id_proyecto, nombre, descripcion, monto_objetivo, monto_recaudado, 
                         estado, fecha_creacion, archivado, archivado_en, archivado_por 
                         FROM proyectos WHERE archivado = FALSE ORDER BY fecha_creacion DESC"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [Proyecto.from_row(row) for row in rows] if rows is not None else []
        except Exception as ex:
            print(f"Error al obtener proyectos: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()
    
    @classmethod
    def get_activos(cls, db):
        return cls.get_all(db, incluir_archivados=False)

    @classmethod
    def get_by_id(cls, db, id_proyecto):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """SELECT id_proyecto, nombre, descripcion, monto_objetivo, monto_recaudado, 
                     estado, fecha_creacion, archivado, archivado_en, archivado_por, id_usuario 
                     FROM proyectos WHERE id_proyecto = %s"""
            cursor.execute(sql, (id_proyecto,))
            row = cursor.fetchone()
            if row is not None:
                return Proyecto.from_row(row)
            else:
                return None
        except Exception as ex:
            print(f"Error al obtener proyecto por ID: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()
    @classmethod
    def create(cls, db, proyecto: Proyecto):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """ INSERT INTO proyectos (nombre, descripcion, monto_objetivo, monto_recaudado, id_usuario, estado)
                      VALUES (%s, %s, %s, %s, %s, %s) """
            cursor.execute(sql, (proyecto.nombre, 
                                 proyecto.descripcion, 
                                 proyecto.monto_objetivo,
                                 proyecto.monto_recaudado, 
                                 proyecto.id_usuario, 
                                 proyecto.estado))
            db.commit()
            return True
        except Exception as ex:
            db.rollback()
            print(f"Error al crear proyecto: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()
        
    @classmethod
    def update(cls, db, proyecto: Proyecto):
        # Actualizar un proyecto existente
        cursor = None
        try:
            cursor = db.cursor()
            sql = """ UPDATE proyectos
                      SET nombre = %s,
                          descripcion = %s,
                          monto_objetivo = %s,
                          monto_recaudado = %s,
                          estado = %s
                      WHERE id_proyecto = %s """
            cursor.execute(sql, (proyecto.nombre, 
                                 proyecto.descripcion, 
                                 proyecto.monto_objetivo,
                                 proyecto.monto_recaudado, 
                                 proyecto.estado,
                                 proyecto.id_proyecto))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Proyecto no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar proyecto: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def delete(cls, db, id_proyecto):
        # Eliminar un proyecto por su ID
        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM proyectos WHERE id_proyecto = %s"
            cursor.execute(sql, (id_proyecto,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Proyecto no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al eliminar proyecto: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_by_user(cls, db, id_usuario, incluir_archivados=True):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            if incluir_archivados:
                sql = """SELECT id_proyecto, nombre, descripcion, monto_objetivo, monto_recaudado, 
                         estado, fecha_creacion, id_usuario, archivado, archivado_en, archivado_por 
                         FROM proyectos WHERE id_usuario = %s ORDER BY fecha_creacion DESC"""
            else:
                sql = """SELECT id_proyecto, nombre, descripcion, monto_objetivo, monto_recaudado, 
                         estado, fecha_creacion, id_usuario, archivado, archivado_en, archivado_por 
                         FROM proyectos WHERE id_usuario = %s AND archivado = FALSE 
                         ORDER BY fecha_creacion DESC"""
            cursor.execute(sql, (id_usuario,))
            rows = cursor.fetchall()
            return [Proyecto.from_row(row) for row in rows] if rows is not None else []
        except Exception as ex:
            print(f"Error al obtener proyectos por usuario: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_donaciones(cls, db, id_proyecto):
        from .ModelDonacion import ModelDonacion
        return ModelDonacion.get_by_project(db, id_proyecto)
    
    @classmethod
    def archivar(cls, db, id_proyecto, id_usuario):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """UPDATE proyectos 
                     SET archivado = TRUE, archivado_en = NOW(), archivado_por = %s 
                     WHERE id_proyecto = %s"""
            cursor.execute(sql, (id_usuario, id_proyecto))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Proyecto no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al archivar proyecto: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()
    
    @classmethod
    def desarchivar(cls, db, id_proyecto):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """UPDATE proyectos 
                     SET archivado = FALSE, archivado_en = NULL, archivado_por = NULL 
                     WHERE id_proyecto = %s"""
            cursor.execute(sql, (id_proyecto,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Proyecto no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al desarchivar proyecto: {ex}")
            return (False, str(ex))
        finally:
            if cursor is not None:
                cursor.close()
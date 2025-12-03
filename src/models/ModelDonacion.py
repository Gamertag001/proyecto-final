from psycopg2.extras import RealDictCursor
from .entities.donacion import Donacion

class ModelDonacion:
    @classmethod
    def get_all(cls, db):
        # Obtener todas las donaciones de la base de datos
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql ="""
            SELECT d.id_donacion, d.id_usuario, d.id_proyecto, d.monto, d.fecha_donacion,
                   u.nombre AS nombre_usuario,
                   p.nombre AS nombre_proyecto
                   FROM donaciones d
                   INNER JOIN usuarios u ON d.id_usuario = u.id
                   INNER JOIN proyectos p ON d.id_proyecto = p.id_proyecto
                   ORDER BY d.fecha_donacion DESC"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [Donacion.from_row(row) for row in rows] if rows is not None else []
        
        except Exception as ex:
            print(f"Error al obtener donaciones: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()    
    @classmethod
    def get_by_project(cls, db, id_proyecto):
        # Obtener donaciones por ID de proyecto
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
            SELECT d.id_donacion, d.id_usuario, d.id_proyecto,
            d.monto, d.fecha_donacion,
            u.nombre AS nombre_usuario
            FROM donaciones d
            INNER JOIN usuarios u ON d.id_usuario = u.id
            WHERE d.id_proyecto = %s
            ORDER BY d.fecha_donacion DESC
            """
            cursor.execute(sql, (id_proyecto,))
            rows = cursor.fetchall()
            return [Donacion.from_row(row) for row in rows] if rows is not None else []
        except Exception as ex:
            print(f"Error al obtener donaciones por proyecto: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def create(cls, db, donacion: Donacion):
        # Crear una nueva donación
        cursor = None
        try:
            # Validar que el monto sea positivo
            if not isinstance(donacion.monto, (int, float)) or donacion.monto <= 0:
                raise ValueError("El monto debe ser un número positivo")
            
            cursor = db.cursor()
            sql = """ INSERT INTO donaciones (id_usuario, id_proyecto, monto)
                      VALUES (%s, %s, %s) """
            cursor.execute(sql, (donacion.id_usuario,
                                 donacion.id_proyecto,
                                 donacion.monto))
            db.commit()
            return True
        except Exception as ex:
            db.rollback()
            print(f"Error al crear donacion: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()
    @classmethod
    def get_total_by_proyect(cls, db, id_proyecto):
        # Obtener el total donado para un proyecto específico
        cursor = None
        try:
            cursor = db.cursor()
            # Suma todas las donaciones que se encuentran para el proyecto dado
            sql = "SELECT COALESCE(SUM(monto), 0) AS total_donado FROM donaciones WHERE id_proyecto = %s"
            # Ejecutar la consulta
            cursor.execute(sql, (id_proyecto,))
            total = cursor.fetchone()[0]
            return total
        except Exception as ex:
            print(f"Error al obtener total donado por proyecto: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_by_user(cls, db, id_usuario):
        # Obtener donaciones por ID de usuario
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
            SELECT d.id_donacion, d.id_usuario, d.id_proyecto,
            d.monto, d.fecha_donacion,
            p.nombre AS nombre_proyecto
            FROM donaciones d
            INNER JOIN proyectos p ON d.id_proyecto = p.id_proyecto
            WHERE d.id_usuario = %s
            ORDER BY d.fecha_donacion DESC
            """
            cursor.execute(sql, (id_usuario,))
            rows = cursor.fetchall()
            return [Donacion.from_row(row) for row in rows] if rows is not None else []
        except Exception as ex:
            print(f"Error al obtener donaciones por usuario: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def sumar_al_proyecto(cls, db, id_proyecto, monto):
        '''
        Aumenta el monto recaudado de un proyecto en especifico
        Se usa cuando una donacion es creada
        '''
        cursor = None
        try:
            # Validar que el monto sea positivo
            if not isinstance(monto, (int, float)) or monto <= 0:
                raise ValueError("El monto debe ser un número positivo")
            
            cursor = db.cursor()
            sql = """
            UPDATE proyectos 
            SET monto_recaudado = monto_recaudado + %s 
            WHERE id_proyecto = %s
            """
            cursor.execute(sql, (monto, id_proyecto))
            db.commit()

        except Exception as ex:
            db.rollback()
            print(f"Error al sumar al proyecto: {ex}")
            raise Exception(ex)
        finally:
            if cursor is not None:
                cursor.close()
    
from psycopg2.extras import RealDictCursor
from .entities.gasto import Gasto
from decimal import Decimal


class ModelGasto:
    @classmethod
    def get_all(cls, db):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT g.*, p.nombre as nombre_proyecto, u.nombre as nombre_usuario
                FROM gastos g
                JOIN proyectos p ON g.id_proyecto = p.id_proyecto
                JOIN usuarios u ON g.id_usuario = u.id
                ORDER BY g.creado_en DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [Gasto.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener gastos: {ex}")
            raise Exception(ex)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_by_id(cls, db, id_gasto):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT g.*, p.nombre as nombre_proyecto, u.nombre as nombre_usuario
                FROM gastos g
                JOIN proyectos p ON g.id_proyecto = p.id_proyecto
                JOIN usuarios u ON g.id_usuario = u.id
                WHERE g.id_gasto = %s
            """
            cursor.execute(sql, (id_gasto,))
            row = cursor.fetchone()
            return Gasto.from_row(row) if row else None
        except Exception as ex:
            print(f"Error al obtener gasto por ID: {ex}")
            raise Exception(ex)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_by_proyecto(cls, db, id_proyecto):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = """
                SELECT g.*, p.nombre as nombre_proyecto, u.nombre as nombre_usuario
                FROM gastos g
                JOIN proyectos p ON g.id_proyecto = p.id_proyecto
                JOIN usuarios u ON g.id_usuario = u.id
                WHERE g.id_proyecto = %s
                ORDER BY g.fecha_gasto DESC
            """
            cursor.execute(sql, (id_proyecto,))
            rows = cursor.fetchall()
            return [Gasto.from_row(row) for row in rows] if rows else []
        except Exception as ex:
            print(f"Error al obtener gastos por proyecto: {ex}")
            raise Exception(ex)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_total_gastos_proyecto(cls, db, id_proyecto):
        cursor = None
        try:
            cursor = db.cursor()
            sql = "SELECT COALESCE(SUM(monto), 0) FROM gastos WHERE id_proyecto = %s"
            cursor.execute(sql, (id_proyecto,))
            result = cursor.fetchone()
            return Decimal(result[0]) if result else Decimal(0)
        except Exception as ex:
            print(f"Error al obtener total de gastos: {ex}")
            raise Exception(ex)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def create(cls, db, gasto: Gasto):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                INSERT INTO gastos (id_proyecto, categoria, descripcion, monto, 
                                   fecha_gasto, archivo_nombre, archivo_path, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_gasto
            """
            cursor.execute(sql, (
                gasto.id_proyecto,
                gasto.categoria,
                gasto.descripcion,
                gasto.monto,
                gasto.fecha_gasto,
                gasto.archivo_nombre,
                gasto.archivo_path,
                gasto.id_usuario
            ))
            result = cursor.fetchone()
            db.commit()
            return (True, result[0] if result else None)
        except Exception as ex:
            db.rollback()
            print(f"Error al crear gasto: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def update(cls, db, gasto: Gasto):
        cursor = None
        try:
            cursor = db.cursor()
            sql = """
                UPDATE gastos
                SET categoria = %s,
                    descripcion = %s,
                    monto = %s,
                    fecha_gasto = %s,
                    archivo_nombre = %s,
                    archivo_path = %s
                WHERE id_gasto = %s
            """
            cursor.execute(sql, (
                gasto.categoria,
                gasto.descripcion,
                gasto.monto,
                gasto.fecha_gasto,
                gasto.archivo_nombre,
                gasto.archivo_path,
                gasto.id_gasto
            ))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Gasto no encontrado")
            db.commit()
            return (True, None)
        except Exception as ex:
            db.rollback()
            print(f"Error al actualizar gasto: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def delete(cls, db, id_gasto):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT archivo_path FROM gastos WHERE id_gasto = %s", (id_gasto,))
            row = cursor.fetchone()
            archivo_path = row.get('archivo_path') if row else None
            
            cursor.execute("DELETE FROM gastos WHERE id_gasto = %s", (id_gasto,))
            if cursor.rowcount == 0:
                db.rollback()
                return (False, "Gasto no encontrado", None)
            db.commit()
            return (True, None, archivo_path)
        except Exception as ex:
            db.rollback()
            print(f"Error al eliminar gasto: {ex}")
            return (False, str(ex), None)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_categorias(cls, db):
        cursor = None
        try:
            cursor = db.cursor(cursor_factory=RealDictCursor)
            sql = "SELECT * FROM categorias_gasto ORDER BY nombre"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows if rows else []
        except Exception as ex:
            print(f"Error al obtener categorias: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def validar_presupuesto(cls, db, id_proyecto, monto_nuevo, id_gasto_excluir=None):
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute(
                "SELECT monto_objetivo, monto_recaudado FROM proyectos WHERE id_proyecto = %s",
                (id_proyecto,)
            )
            result = cursor.fetchone()
            if not result:
                return (False, "Proyecto no encontrado")
            
            monto_recaudado = Decimal(result[1]) if result[1] else Decimal(0)
            
            if monto_recaudado <= 0:
                return (False, "No se pueden registrar gastos. El proyecto no tiene fondos recaudados. Las donaciones deben recibirse primero antes de poder gastar.")
            
            if id_gasto_excluir:
                sql = """
                    SELECT COALESCE(SUM(monto), 0) FROM gastos 
                    WHERE id_proyecto = %s AND id_gasto != %s
                """
                cursor.execute(sql, (id_proyecto, id_gasto_excluir))
            else:
                sql = "SELECT COALESCE(SUM(monto), 0) FROM gastos WHERE id_proyecto = %s"
                cursor.execute(sql, (id_proyecto,))
            
            result = cursor.fetchone()
            total_gastos_actual = Decimal(result[0]) if result else Decimal(0)
            
            nuevo_total = total_gastos_actual + Decimal(monto_nuevo)
            
            if nuevo_total > monto_recaudado:
                disponible = monto_recaudado - total_gastos_actual
                return (False, f"El monto excede los fondos recaudados disponibles. Fondos disponibles: ${disponible:.2f}")
            
            return (True, None)
        except Exception as ex:
            print(f"Error al validar presupuesto: {ex}")
            return (False, str(ex))
        finally:
            if cursor:
                cursor.close()

from src.database import get_db
from flask_login import current_user


def log_action(accion, usuario_id=None):
    """
    Registra una acción en la tabla de auditoría.
    
    Args:
        accion: Descripción de la acción realizada
        usuario_id: ID del usuario que realizó la acción (opcional, usa current_user si no se proporciona)
    """
    db = None
    cursor = None
    try:
        if usuario_id is None and current_user and current_user.is_authenticated:
            usuario_id = current_user.id
        
        db = get_db()
        if db is None:
            return False
            
        cursor = db.cursor()
        sql = """
            INSERT INTO auditoria (usuario_id, accion)
            VALUES (%s, %s)
        """
        cursor.execute(sql, (usuario_id, accion))
        db.commit()
        return True
    except Exception as ex:
        print(f"Error al registrar auditoría: {ex}")
        if db:
            db.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_audit_logs(limit=100, usuario_id=None, fecha_desde=None, fecha_hasta=None):
    """
    Obtiene los registros de auditoría.
    
    Args:
        limit: Número máximo de registros a obtener
        usuario_id: Filtrar por usuario específico
        fecha_desde: Filtrar desde esta fecha
        fecha_hasta: Filtrar hasta esta fecha
    """
    db = None
    cursor = None
    try:
        from psycopg2.extras import RealDictCursor
        db = get_db()
        if db is None:
            return []
            
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT a.id, a.usuario_id, a.accion, a.fecha,
                   COALESCE(u.nombre, 'Sistema') as usuario_nombre,
                   COALESCE(u.fullname, 'Sistema') as usuario_fullname
            FROM auditoria a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if usuario_id:
            sql += " AND a.usuario_id = %s"
            params.append(usuario_id)
        
        if fecha_desde:
            sql += " AND a.fecha >= %s"
            params.append(fecha_desde)
        
        if fecha_hasta:
            sql += " AND a.fecha <= %s"
            params.append(fecha_hasta)
        
        sql += " ORDER BY a.fecha DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows if rows else []
    except Exception as ex:
        print(f"Error al obtener registros de auditoría: {ex}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

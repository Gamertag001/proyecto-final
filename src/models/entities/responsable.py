class Responsable:
    def __init__(self, id_responsable=None, id_proyecto=None, id_usuario=None, 
                 rol_en_proyecto=None, fecha_asignacion=None, 
                 usuario_nombre=None, usuario_correo=None):
        self.id_responsable = id_responsable
        self.id_proyecto = id_proyecto
        self.id_usuario = id_usuario
        self.rol_en_proyecto = rol_en_proyecto
        self.fecha_asignacion = fecha_asignacion
        self.usuario_nombre = usuario_nombre
        self.usuario_correo = usuario_correo
    
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id_responsable=row.get('id_responsable'),
            id_proyecto=row.get('id_proyecto'),
            id_usuario=row.get('id_usuario'),
            rol_en_proyecto=row.get('rol_en_proyecto'),
            fecha_asignacion=row.get('fecha_asignacion'),
            usuario_nombre=row.get('usuario_nombre') or row.get('fullname'),
            usuario_correo=row.get('usuario_correo') or row.get('correo')
        )
    
    def to_dict(self):
        return {
            'id_responsable': self.id_responsable,
            'id_proyecto': self.id_proyecto,
            'id_usuario': self.id_usuario,
            'rol_en_proyecto': self.rol_en_proyecto,
            'fecha_asignacion': str(self.fecha_asignacion) if self.fecha_asignacion else None,
            'usuario_nombre': self.usuario_nombre,
            'usuario_correo': self.usuario_correo
        }

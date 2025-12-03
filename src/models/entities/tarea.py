class Tarea:
    def __init__(self, id=None, descripcion=None, estado='pendiente', 
                 fecha_inicio=None, fecha_fin=None, usuario_id=None, 
                 proyecto_id=None, creado_en=None, usuario_nombre=None):
        self.id = id
        self.descripcion = descripcion
        self.estado = estado
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.usuario_id = usuario_id
        self.proyecto_id = proyecto_id
        self.creado_en = creado_en
        self.usuario_nombre = usuario_nombre
    
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row.get('id'),
            descripcion=row.get('descripcion'),
            estado=row.get('estado', 'pendiente'),
            fecha_inicio=row.get('fecha_inicio'),
            fecha_fin=row.get('fecha_fin'),
            usuario_id=row.get('usuario_id'),
            proyecto_id=row.get('proyecto_id'),
            creado_en=row.get('creado_en'),
            usuario_nombre=row.get('usuario_nombre')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha_inicio': str(self.fecha_inicio) if self.fecha_inicio else None,
            'fecha_fin': str(self.fecha_fin) if self.fecha_fin else None,
            'usuario_id': self.usuario_id,
            'proyecto_id': self.proyecto_id,
            'creado_en': str(self.creado_en) if self.creado_en else None,
            'usuario_nombre': self.usuario_nombre
        }
    
    @property
    def estado_display(self):
        estados = {
            'pendiente': 'Pendiente',
            'en_progreso': 'En Progreso',
            'completada': 'Completada'
        }
        return estados.get(self.estado, self.estado)
    
    @property
    def estado_color(self):
        colores = {
            'pendiente': 'warning',
            'en_progreso': 'info',
            'completada': 'success'
        }
        return colores.get(self.estado, 'secondary')

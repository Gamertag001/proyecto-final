class Actividad:
    def __init__(self, id_actividad=None, id_proyecto=None, nombre=None, 
                 descripcion=None, fecha_inicio=None, fecha_fin=None, 
                 estado='pendiente'):
        self.id_actividad = id_actividad
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
    
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id_actividad=row.get('id_actividad'),
            id_proyecto=row.get('id_proyecto'),
            nombre=row.get('nombre'),
            descripcion=row.get('descripcion'),
            fecha_inicio=row.get('fecha_inicio'),
            fecha_fin=row.get('fecha_fin'),
            estado=row.get('estado', 'pendiente')
        )
    
    def to_dict(self):
        return {
            'id_actividad': self.id_actividad,
            'id_proyecto': self.id_proyecto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_inicio': str(self.fecha_inicio) if self.fecha_inicio else None,
            'fecha_fin': str(self.fecha_fin) if self.fecha_fin else None,
            'estado': self.estado
        }
    
    @property
    def estado_display(self):
        estados = {
            'pendiente': 'Pendiente',
            'en_progreso': 'En Progreso',
            'completada': 'Completada'
        }
        return estados.get(self.estado, self.estado)

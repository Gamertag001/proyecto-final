class Objetivo:
    def __init__(self, id_objetivo=None, id_proyecto=None, descripcion=None, 
                 completado=False, fecha_creacion=None):
        self.id_objetivo = id_objetivo
        self.id_proyecto = id_proyecto
        self.descripcion = descripcion
        self.completado = completado
        self.fecha_creacion = fecha_creacion
    
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id_objetivo=row.get('id_objetivo'),
            id_proyecto=row.get('id_proyecto'),
            descripcion=row.get('descripcion'),
            completado=row.get('completado', False),
            fecha_creacion=row.get('fecha_creacion')
        )
    
    def to_dict(self):
        return {
            'id_objetivo': self.id_objetivo,
            'id_proyecto': self.id_proyecto,
            'descripcion': self.descripcion,
            'completado': self.completado,
            'fecha_creacion': str(self.fecha_creacion) if self.fecha_creacion else None
        }

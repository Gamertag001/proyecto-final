class Proyecto:
    def __init__(self, id_proyecto, nombre, descripcion, monto_objetivo, monto_recaudado, 
                 id_usuario, estado, fecha_creacion, archivado=False, archivado_en=None, 
                 archivado_por=None):
        self.id_proyecto = id_proyecto
        self.nombre = nombre    
        self.descripcion = descripcion
        self.monto_objetivo = monto_objetivo
        self.monto_recaudado = monto_recaudado
        self.id_usuario = id_usuario
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.archivado = archivado
        self.archivado_en = archivado_en
        self.archivado_por = archivado_por
    
    @classmethod
    def from_row(cls, row):
        return cls(
            row.get('id_proyecto'),
            row.get('nombre'),
            row.get('descripcion'),
            row.get('monto_objetivo'),
            row.get('monto_recaudado'),
            row.get('id_usuario'),
            row.get('estado'),
            row.get('fecha_creacion'),
            row.get('archivado', False),
            row.get('archivado_en'),
            row.get('archivado_por')
        )
    
    def esta_archivado(self):
        return self.archivado == True
    
    def porcentaje_recaudado(self):
        if not self.monto_objetivo or self.monto_objetivo == 0:
            return 0
        return round((self.monto_recaudado or 0) / self.monto_objetivo * 100, 2)

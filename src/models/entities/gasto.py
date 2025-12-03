class Gasto:
    def __init__(self, id_gasto, id_proyecto, categoria, descripcion, monto, 
                 fecha_gasto, archivo_nombre, archivo_path, id_usuario, creado_en,
                 nombre_proyecto=None, nombre_usuario=None):
        self.id_gasto = id_gasto
        self.id_proyecto = id_proyecto
        self.categoria = categoria
        self.descripcion = descripcion
        self.monto = monto
        self.fecha_gasto = fecha_gasto
        self.archivo_nombre = archivo_nombre
        self.archivo_path = archivo_path
        self.id_usuario = id_usuario
        self.creado_en = creado_en
        self.nombre_proyecto = nombre_proyecto
        self.nombre_usuario = nombre_usuario
    
    @classmethod
    def from_row(cls, row):
        return cls(
            row.get('id_gasto'),
            row.get('id_proyecto'),
            row.get('categoria'),
            row.get('descripcion'),
            row.get('monto'),
            row.get('fecha_gasto'),
            row.get('archivo_nombre'),
            row.get('archivo_path'),
            row.get('id_usuario'),
            row.get('creado_en'),
            row.get('nombre_proyecto'),
            row.get('nombre_usuario')
        )
    
    def tiene_archivo(self):
        return self.archivo_path is not None and self.archivo_path != ''
    
    def extension_archivo(self):
        if not self.archivo_nombre:
            return None
        return self.archivo_nombre.rsplit('.', 1)[-1].lower() if '.' in self.archivo_nombre else None

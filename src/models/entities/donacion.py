class Donacion:
    def __init__(self, id_donacion, id_usuario, id_proyecto, monto, fecha_donacion  ):
        self.id_donacion = id_donacion
        self.id_usuario = id_usuario
        self.id_proyecto = id_proyecto
        self.monto = monto
        self.fecha_donacion = fecha_donacion
    @classmethod
    def from_row(cls, row):
        "permite crear una instancia de Donacion a partir de una fila de la base de datos"
        return cls(
            row.get('id_donacion'),
            row.get('id_usuario'),
            row.get('id_proyecto'),
            row.get('monto'),
            row.get('fecha_donacion')
        )
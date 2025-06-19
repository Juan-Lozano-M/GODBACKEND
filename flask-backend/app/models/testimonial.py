from app import db

class Testimonio(db.Model):
    __tablename__ = 'testimonios'

    id_tes = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usu_tes = db.Column(db.Integer, db.ForeignKey('usuarios.id_usu'), nullable=True)
    contenido_tes = db.Column(db.Text, nullable=False)
    fecha_publicacion_tes = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    estado_tes = db.Column(db.Enum('aprobado', 'anulado', 'en espera'), nullable=False, default='en espera')
    titulo_tes = db.Column(db.String(100), nullable=False)
    cargo_tes = db.Column(db.String(100), nullable=True)

    # Relación inversa al usuario
    usuario = db.relationship('User', backref=db.backref('testimonios', lazy=True))

    def to_dict(self):
        nombre_usuario = "Usuario desconocido"
        try:
            if self.usuario and hasattr(self.usuario, 'nombre_usu'):
                nombre_usuario = self.usuario.nombre_usu
            elif self.titulo_tes:
                nombre_usuario = self.titulo_tes
        except:
            if self.titulo_tes:
                nombre_usuario = self.titulo_tes

        return {
            "id_tes": self.id_tes,
            "nombre_usuario": nombre_usuario,
            "cargo_tes": self.cargo_tes if self.cargo_tes else "",
            "titulo_tes": self.titulo_tes if self.titulo_tes else "",
            "contenido_tes": self.contenido_tes if self.contenido_tes else "",
            "fecha_publicacion_tes": self.fecha_publicacion_tes.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_publicacion_tes else None,
            "estado_tes": self.estado_tes if self.estado_tes else "en espera"
        }
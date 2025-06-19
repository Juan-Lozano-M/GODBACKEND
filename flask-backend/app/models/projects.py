from app import db

class Proyecto(db.Model):
    __tablename__ = 'proyectos'

    id_proyecto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo_proyecto = db.Column(db.String(255), nullable=False)
    categoria_proyecto = db.Column(db.String(100))
    estado_proyecto = db.Column(db.Enum('En Progreso', 'Finalizado', 'Planeado'), default='Planeado')
    anio_proyecto = db.Column(db.Integer, nullable=False)
    participantes_proyecto = db.Column(db.Integer)
    descripcion_proyecto = db.Column(db.Text)
    metodologiauno_proyecto = db.Column(db.Text)
    metodologiados_proyecto = db.Column(db.Text)
    areas_proyecto = db.Column(db.Text)

    imagenurl_proyecto = db.Column(db.String(255))  # Campo nuevo para URL de la imagen

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usu'), nullable=False)
    usuario = db.relationship('User', backref=db.backref('proyectos', lazy=True))

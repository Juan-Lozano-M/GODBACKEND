from app import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = 'usuarios'

    id_usu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usu = db.Column(db.String(255), nullable=False)
    correo_usu = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash_usu = db.Column(db.String(255), nullable=True)
    fecha_registro_usu = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    intereses = db.Column(db.String(255), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    institucion = db.Column(db.String(255), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    public_id = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(10), default='User')
    
    # Relación con noticias (un usuario puede crear muchas noticias)
    noticias_creadas = db.relationship('News', backref='autor', lazy=True)

    def __init__(self, nombre_usu, correo_usu, contrasena_hash_usu=None, google_id=None, firebase_uid=None):
        self.nombre_usu = nombre_usu
        self.correo_usu = correo_usu
        if contrasena_hash_usu:
            self.contrasena_hash_usu = generate_password_hash(contrasena_hash_usu)
        self.google_id = google_id
        self.firebase_uid = firebase_uid

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_usu,
            'nombre': self.nombre_usu,
            'correo': self.correo_usu,
            'role': self.role,
            'fecha_registro': self.fecha_registro_usu.isoformat() if self.fecha_registro_usu else None,
            'intereses': self.intereses,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'institucion': self.institucion,
            'profile_image': self.profile_image
        }

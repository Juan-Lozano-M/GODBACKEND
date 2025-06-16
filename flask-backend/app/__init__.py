from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/gameofdreams'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS with credentials support
    CORS(app, 
         origins=["http://localhost:5173"],
         supports_credentials=True,
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:5173"],
                 "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             },
             r"/auth/*": {
                 "origins": ["http://localhost:5173"],
                 "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         })

    app.config.from_object(Config)
    Config.init_cloudinary()

    # Initialize Firebase
    cred = credentials.Certificate('Firebase/clave-firebase.json') 
    firebase_admin.initialize_app(cred)

    # Test root route
    @app.route('/')
    def index():
        return "¡Bienvenido a la API!"

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    from app.routes.cloudinary_routes import cloudinary_bp
    app.register_blueprint(cloudinary_bp, url_prefix='/api/cloudinary')

    from app.routes.news_routes import news_bp
    app.register_blueprint(news_bp)
    
    from app.routes.chatbot_routes import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')


    from app.routes.testimonial_routes import testimonial_bp
    app.register_blueprint(testimonial_bp)

    from app.routes.stats_routes import stats_bp
    app.register_blueprint(stats_bp)
    

    return app
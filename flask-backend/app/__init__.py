from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
from flask_migrate import Migrate
import json
import os
from firebase_admin import credentials

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Configure CORS with credentials support
    CORS(app, 
         origins=[
             "http://localhost:5173", 
             "http://127.0.0.1:5173",
             "https://proyecto-god.netlify.app"
         ],
         supports_credentials=True,
         methods=["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
         allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
         resources={
             r"/api/*": {
                 "origins": [
                     "http://localhost:5173", 
                     "http://127.0.0.1:5173",
                     "https://proyecto-god.netlify.app"
                 ],
                 "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
                 "supports_credentials": True
             },
             r"/auth/*": {
                 "origins": [
                     "http://localhost:5173", 
                     "http://127.0.0.1:5173",
                     "https://proyecto-god.netlify.app"
                 ],
                 "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
                 "supports_credentials": True             }
         })

    Config.init_cloudinary()

    # Initialize Firebase
    firebase_json = os.environ["FIREBASE_CREDENTIALS_JSON"]
    cred_dict = json.loads(firebase_json)
    cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
    cred = credentials.Certificate(cred_dict)
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
    
    from app.routes.projects_routes import projects_bp
    app.register_blueprint(projects_bp)
    
    from app.routes.chatbot_routes import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')

    from app.routes.testimonial_routes import testimonial_bp
    app.register_blueprint(testimonial_bp)

    from app.routes.stats_routes import stats_bp
    app.register_blueprint(stats_bp)

    from app.routes.visit_routes import visit_routes
    app.register_blueprint(visit_routes)
    
    from app.routes.contact_routes import contact_bp
    app.register_blueprint(contact_bp, url_prefix='/api')

    return app
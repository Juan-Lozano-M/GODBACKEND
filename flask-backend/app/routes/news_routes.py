# Importación de Blueprint de Flask para crear rutas modulares
from flask import Blueprint
# Importación de los controladores para manejar noticias
from app.controllers.news_controller import (
    create_news, 
    upload_news_image, 
    get_all_news,
    get_all_news_admin,
    get_news_by_slug,
    get_news_by_id,
    search_news,
    update_news # <-- Importa la función que implementaremos
)

# Creación del Blueprint para las rutas de noticias
news_bp = Blueprint('news', __name__)

# Rutas para el CRUD de noticias
news_bp.route('/api/news', methods=['POST'])(create_news)                    # Crear noticia
news_bp.route('/api/news/upload-image', methods=['POST'])(upload_news_image) # Subir imagen
news_bp.route('/api/news/get-news', methods=['GET'])(get_all_news)          # Obtener todas las noticias
news_bp.route('/api/news/get-all-admin', methods=['GET'])(get_all_news_admin) # Obtener todas las noticias sin filtro de estado
news_bp.route('/api/news/search', methods=['GET'])(search_news)             # Buscar noticias
news_bp.route('/api/news/id/<int:news_id>', methods=['GET'])(get_news_by_id) # Obtener por ID
news_bp.route('/api/news/<slug>', methods=['GET'])(get_news_by_slug)        # Obtener por slug
news_bp.route('/api/news/update-news/<int:news_id>', methods=['PATCH', 'OPTIONS'])(update_news) # Actualizar noticia

# IMPORTANTE: La ruta del slug debe ir al final para evitar conflictos
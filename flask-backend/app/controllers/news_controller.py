from flask import Blueprint, request, jsonify, session
from app.services.cloudinary_service import CloudinaryService
from app.models.news import News
from app.models.user import User
from app import db
from firebase_admin import auth
import re  # ← Esta importación faltaba




def create_news():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verificar token de Firebase
        try:
            decoded_token = auth.verify_id_token(token, clock_skew_seconds=5)
            email = decoded_token.get('email')
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Buscar usuario por email
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        if user.role != 'Admin':
            return jsonify({'status': 'error', 'message': 'Only administrators can create news'}), 403
        
        # Resto del código igual...
        required_fields = ['title', 'category', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        new_news = News(
            titulo_noticia=data['title'],
            categoria_noticia=data['category'],
            contenido_noticia=data['content'],
            autor_id=user.id_usu,
            descripcion_noticia=data.get('description'),
            imagen_url_noticia=data.get('image'),
            public_id_noticia=data.get('public_id')
        )
        
        new_news.validate_title()
        new_news.validate_content()
        
        db.session.add(new_news)
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'News created successfully',
            'news': new_news.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500



def upload_news_image():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        file = request.files['file']
        result = CloudinaryService.upload_image(file, 'news_images')

        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'url': result['url'],
                'public_id': result['public_id']
            })
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500



def get_all_news():
    try:
        # Solo noticias publicadas
        news_list = News.query.filter_by(es_publicada=True).order_by(News.fecha_creacion.desc()).all()
        news_data = [n.to_dict() for n in news_list]

        return jsonify({'status': 'success', 'news': news_data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_news_by_slug(slug):
    """
    Obtiene una noticia específica por su slug
    El slug debe tener el formato: titulo-de-la-noticia-123 (donde 123 es el ID)
    """
    try:
        # Validar formato del slug
        if not slug or len(slug.strip()) == 0:
            return jsonify({'status': 'error', 'message': 'Slug is required'}), 400
        
        # Extraer el ID del slug (último número después del último guión)
        id_match = re.search(r'-(\d+)$', slug)
        
        if not id_match:
            return jsonify({
                'status': 'error', 
                'message': 'Invalid slug format. Expected format: title-with-hyphens-123'
            }), 400
        
        news_id = int(id_match.group(1))
        
        # Buscar la noticia por ID y que esté publicada
        news = News.query.filter_by(id_noticia=news_id, es_publicada=True).first()
        
        if not news:
            return jsonify({'status': 'error', 'message': 'News not found'}), 404
        
        # Verificar que el slug coincida exactamente con el generado
        expected_slug = news.generate_slug()
        if expected_slug != slug:
            return jsonify({
                'status': 'error', 
                'message': 'Slug mismatch. Use the correct slug format.',
                'correct_slug': expected_slug
            }), 400
        
        return jsonify({
            'status': 'success', 
            'news': news.to_dict()
        }), 200
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': 'Invalid news ID in slug'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Internal server error: {str(e)}'}), 500


def get_news_by_id(news_id):
    """
    Función alternativa para obtener noticia por ID directamente
    (Por si necesitas una ruta más simple)
    """
    try:
        news_id = int(news_id)
        news = News.query.filter_by(id_noticia=news_id, es_publicada=True).first()
        
        if not news:
            return jsonify({'status': 'error', 'message': 'News not found'}), 404
        
        return jsonify({
            'status': 'success', 
            'news': news.to_dict()
        }), 200
        
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid news ID'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def search_news():
    """
    Buscar noticias por título, categoría o contenido
    """
    try:
        query_param = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Construir la consulta base
        query = News.query.filter_by(es_publicada=True)
        
        # Filtrar por búsqueda de texto
        if query_param:
            search = f"%{query_param}%"
            query = query.filter(
                db.or_(
                    News.titulo_noticia.ilike(search),
                    News.descripcion_noticia.ilike(search),
                    News.contenido_noticia.ilike(search)
                )
            )
        
        # Filtrar por categoría
        if category:
            query = query.filter(News.categoria_noticia.ilike(f"%{category}%"))
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(News.fecha_creacion.desc())
        
        # Paginación
        paginated_news = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'news': [news.to_dict() for news in paginated_news.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_news.total,
                'pages': paginated_news.pages,
                'has_next': paginated_news.has_next,
                'has_prev': paginated_news.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
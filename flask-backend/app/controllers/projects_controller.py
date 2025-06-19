from flask import request, jsonify
from app.models.projects import Proyecto
from app.models.user import User
from app import db
from firebase_admin import auth
import json


def create_project():
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
            return jsonify({'status': 'error', 'message': 'Only administrators can create projects'}), 403
        
        # Validar campos requeridos
        required_fields = ['title', 'category', 'year']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        # Mapear estados del frontend al backend
        status_mapping = {
            'activo': 'En Progreso',
            'completado': 'Finalizado'
        }
        
        estado = status_mapping.get(data.get('status', 'activo'), 'En Progreso')
        
        # Convertir areas (array) a string JSON para almacenar en la BD
        areas_json = json.dumps(data.get('areas', [])) if data.get('areas') else None
        
        new_project = Proyecto(
            titulo_proyecto=data['title'],
            categoria_proyecto=data['category'],
            estado_proyecto=estado,
            anio_proyecto=int(data['year']),
            participantes_proyecto=int(data.get('participants', 0)) if data.get('participants') else None,
            descripcion_proyecto=data.get('description', ''),
            metodologiauno_proyecto=data.get('methodology1', ''),
            metodologiados_proyecto=data.get('methodology2', ''),
            areas_proyecto=areas_json,
            imagenurl_proyecto=data.get('image'),
            id_usuario=user.id_usu
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project created successfully',
            'project_id': new_project.id_proyecto
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


def get_all_projects():
    try:
        projects = Proyecto.query.all()
        
        projects_list = []
        for project in projects:
            # Parsear areas de JSON string a lista
            areas = json.loads(project.areas_proyecto) if project.areas_proyecto else []
            
            # Convertir guiones bajos a espacios en las áreas
            areas_formatted = [area.replace('_', ' ').title() for area in areas]
            
            # Mapear estados del backend al frontend
            status_mapping = {
                'En Progreso': 'activo',
                'Finalizado': 'completado',
                'Planeado': 'planeado'
            }
            
            # Convertir guiones bajos a espacios en la categoría
            category_formatted = project.categoria_proyecto.replace('_', ' ').title() if project.categoria_proyecto else ''
            
            project_data = {
                'id': project.id_proyecto,
                'title': project.titulo_proyecto,
                'category': category_formatted,
                'status': status_mapping.get(project.estado_proyecto, 'activo'),
                'year': project.anio_proyecto,
                'participants': project.participantes_proyecto,
                'description': project.descripcion_proyecto,
                'methodology1': project.metodologiauno_proyecto,
                'methodology2': project.metodologiados_proyecto,
                'areas': areas_formatted,
                'image': project.imagenurl_proyecto,
                'author': {
                    'id': project.usuario.id_usu,
                    'name': project.usuario.nombre_usu,
                    'email': project.usuario.correo_usu
                } if project.usuario else None
            }
            projects_list.append(project_data)
        
        return jsonify({
            'status': 'success',
            'projects': projects_list
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def get_project_by_id(project_id):
    try:
        project = Proyecto.query.get(project_id)
        
        if not project:
            return jsonify({'status': 'error', 'message': 'Project not found'}), 404
        
        # Parsear areas de JSON string a lista
        areas = json.loads(project.areas_proyecto) if project.areas_proyecto else []
        
        # Convertir guiones bajos a espacios en las áreas
        areas_formatted = [area.replace('_', ' ').title() for area in areas]
        
        # Mapear estados del backend al frontend
        status_mapping = {
            'En Progreso': 'activo',
            'Finalizado': 'completado',
            'Planeado': 'planeado'
        }
        
        # Convertir guiones bajos a espacios en la categoría
        category_formatted = project.categoria_proyecto.replace('_', ' ').title() if project.categoria_proyecto else ''
        
        project_data = {
            'id': project.id_proyecto,
            'title': project.titulo_proyecto,
            'category': category_formatted,
            'status': status_mapping.get(project.estado_proyecto, 'activo'),
            'year': project.anio_proyecto,
            'participants': project.participantes_proyecto,
            'description': project.descripcion_proyecto,
            'methodology1': project.metodologiauno_proyecto,
            'methodology2': project.metodologiados_proyecto,
            'areas': areas_formatted,
            'image': project.imagenurl_proyecto,
            'author': {
                'id': project.usuario.id_usu,
                'name': project.usuario.nombre_usu,
                'email': project.usuario.correo_usu
            } if project.usuario else None
        }
        
        return jsonify({
            'status': 'success',
            'project': project_data
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def update_project(project_id):
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
            return jsonify({'status': 'error', 'message': 'Only administrators can update projects'}), 403
        
        # Buscar el proyecto
        project = Proyecto.query.get(project_id)
        if not project:
            return jsonify({'status': 'error', 'message': 'Project not found'}), 404
        
        # Mapear estados del frontend al backend
        status_mapping = {
            'activo': 'En Progreso',
            'completado': 'Finalizado'
        }
        
        # Actualizar campos si están presentes
        if 'title' in data:
            project.titulo_proyecto = data['title']
        if 'category' in data:
            project.categoria_proyecto = data['category']
        if 'status' in data:
            project.estado_proyecto = status_mapping.get(data['status'], 'En Progreso')
        if 'year' in data:
            project.anio_proyecto = int(data['year'])
        if 'participants' in data:
            project.participantes_proyecto = int(data['participants']) if data['participants'] else None
        if 'description' in data:
            project.descripcion_proyecto = data['description']
        if 'methodology1' in data:
            project.metodologiauno_proyecto = data['methodology1']
        if 'methodology2' in data:
            project.metodologiados_proyecto = data['methodology2']
        if 'areas' in data:
            project.areas_proyecto = json.dumps(data['areas']) if data['areas'] else None
        if 'image' in data:
            project.imagenurl_proyecto = data['image']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


def delete_project(project_id):
    try:
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
            return jsonify({'status': 'error', 'message': 'Only administrators can delete projects'}), 403
        
        # Buscar el proyecto
        project = Proyecto.query.get(project_id)
        if not project:
            return jsonify({'status': 'error', 'message': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


def search_projects():
    try:
        # Obtener parámetros de búsqueda
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        year = request.args.get('year', '').strip()
        
        # Construir la consulta base
        projects_query = Proyecto.query
        
        # Filtrar por texto en título o descripción
        if query:
            projects_query = projects_query.filter(
                (Proyecto.titulo_proyecto.ilike(f'%{query}%')) |
                (Proyecto.descripcion_proyecto.ilike(f'%{query}%'))
            )
        
        # Filtrar por categoría
        if category:
            projects_query = projects_query.filter(Proyecto.categoria_proyecto == category)
        
        # Filtrar por estado
        if status:
            status_mapping = {
                'activo': 'En Progreso',
                'completado': 'Finalizado'
            }
            backend_status = status_mapping.get(status)
            if backend_status:
                projects_query = projects_query.filter(Proyecto.estado_proyecto == backend_status)
          # Filtrar por año
        if year:
            try:
                year_int = int(year)
                projects_query = projects_query.filter(Proyecto.anio_proyecto == year_int)
            except ValueError:
                pass  # Ignorar años inválidos
        
        projects = projects_query.all()
        
        projects_list = []
        for project in projects:
            # Parsear areas de JSON string a lista
            areas = json.loads(project.areas_proyecto) if project.areas_proyecto else []
            
            # Convertir guiones bajos a espacios en las áreas
            areas_formatted = [area.replace('_', ' ').title() for area in areas]
            
            # Mapear estados del backend al frontend
            status_mapping = {
                'En Progreso': 'activo',
                'Finalizado': 'completado',
                'Planeado': 'planeado'
            }
            
            # Convertir guiones bajos a espacios en la categoría
            category_formatted = project.categoria_proyecto.replace('_', ' ').title() if project.categoria_proyecto else ''
            
            project_data = {
                'id': project.id_proyecto,
                'title': project.titulo_proyecto,
                'category': category_formatted,
                'status': status_mapping.get(project.estado_proyecto, 'activo'),
                'year': project.anio_proyecto,
                'participants': project.participantes_proyecto,
                'description': project.descripcion_proyecto,
                'methodology1': project.metodologiauno_proyecto,
                'methodology2': project.metodologiados_proyecto,
                'areas': areas_formatted,
                'image': project.imagenurl_proyecto,
                'author': {
                    'id': project.usuario.id_usu,
                    'name': project.usuario.nombre_usu,
                    'email': project.usuario.correo_usu
                } if project.usuario else None
            }
            projects_list.append(project_data)
        
        return jsonify({
            'status': 'success',
            'projects': projects_list,
            'total': len(projects_list)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Importaciones necesarias
import json
from flask import jsonify, request
from app import db
from app.models.testimonial import Testimonio
from firebase_admin import auth
from flask_cors import cross_origin
from datetime import datetime
from sqlalchemy import text


@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def get_testimonials_with_user():
    """
    Obtiene testimonios aprobados con información del usuario
    """
    try:
        print("=== DEBUGGING get_testimonials_with_user ===")
        
        query = text("""
            SELECT 
                t.id_tes,
                t.titulo_tes,
                t.contenido_tes,
                t.cargo_tes,
                t.estado_tes,
                t.fecha_publicacion_tes,
                t.id_usu_tes,
                u.nombre_usu,
                u.profile_image
            FROM testimonios t
            INNER JOIN usuarios u ON t.id_usu_tes = u.id_usu
            ORDER BY t.fecha_publicacion_tes DESC
        """)
        result = db.session.execute(query)
        testimonios = []
        
        for row in result:
            row_dict = row._asdict() if hasattr(row, '_asdict') else dict(row)
            print(f"Processing testimonial ID: {row_dict['id_tes']}")
            print(f"Profile image URL: {row_dict.get('profile_image', 'None')}")
            
            testimonial_data = {
                'id_tes': row_dict['id_tes'],
                'titulo_tes': row_dict['titulo_tes'],
                'contenido_tes': row_dict['contenido_tes'],
                'cargo_tes': row_dict['cargo_tes'],
                'estado_tes': row_dict['estado_tes'],
                'fecha_publicacion_tes': row_dict['fecha_publicacion_tes'].isoformat() if row_dict['fecha_publicacion_tes'] else None,
                'nombre_usuario': row_dict['nombre_usu'],
                'profile_image': row_dict['profile_image']
            }
            testimonios.append(testimonial_data)
            
        print(f"Returning {len(testimonios)} testimonials")
        return jsonify(testimonios), 200
        
    except Exception as e:
        print(f"Error al obtener testimonios con usuario: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def get_testimonials():
    """
    Obtiene todos los testimonios de la base de datos con información del usuario
    """
    try:
        print("=== DEBUGGING get_testimonials ===")
        
        # Usar la consulta SQL directa para obtener los datos del usuario
        query = text("""
            SELECT 
                t.id_tes,
                t.titulo_tes,
                t.contenido_tes,
                t.cargo_tes,
                t.estado_tes,
                t.fecha_publicacion_tes,
                t.id_usu_tes,
                u.nombre_usu,
                u.profile_image
            FROM testimonios t
            LEFT JOIN usuarios u ON t.id_usu_tes = u.id_usu
            ORDER BY t.fecha_publicacion_tes DESC
        """)
        
        result = db.session.execute(query)
        testimonials = []
        
        for row in result:
            # Convertir la fila a diccionario
            row_dict = row._asdict() if hasattr(row, '_asdict') else dict(row)
            print(f"Processing testimonial ID: {row_dict['id_tes']}")
            print(f"User profile_image: {row_dict.get('profile_image', 'None')}")
            
            testimonial_data = {
                'id_tes': row_dict['id_tes'],
                'nombre_usuario': row_dict['nombre_usu'] if row_dict['nombre_usu'] else (row_dict['titulo_tes'] if row_dict['titulo_tes'] else "Usuario desconocido"),
                'cargo_tes': row_dict['cargo_tes'] if row_dict['cargo_tes'] else "",
                'estado_tes': row_dict['estado_tes'] if row_dict['estado_tes'] else "en espera",
                'titulo_tes': row_dict['titulo_tes'] if row_dict['titulo_tes'] else "",
                'contenido_tes': row_dict['contenido_tes'] if row_dict['contenido_tes'] else "",
                'fecha_publicacion_tes': row_dict['fecha_publicacion_tes'].isoformat() if row_dict['fecha_publicacion_tes'] else None,
                'profile_image': row_dict['profile_image']
            }
            
            testimonials.append(testimonial_data)
        
        print(f"Returning {len(testimonials)} testimonials with profile images")
        return jsonify(testimonials), 200

    except Exception as e:
        print(f"Error in get_testimonials: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


def get_testimonial_stats():
    """
    Obtiene estadísticas de testimonios (aprobados, rechazados, en espera)
    """
    try:
        print("=== DEBUGGING get_testimonial_stats ===")
        
        # Contar testimonios por estado
        aprobados = Testimonio.query.filter_by(estado_tes='aprobado').count()
        rechazados = Testimonio.query.filter_by(estado_tes='anulado').count()
        en_espera = Testimonio.query.filter_by(estado_tes='en espera').count()
        total = Testimonio.query.count()
        
        print(f"Stats - Aprobados: {aprobados}, Rechazados: {rechazados}, En espera: {en_espera}, Total: {total}")
        
        # Calcular porcentajes si hay testimonios
        porcentaje_aprobacion = 0
        porcentaje_rechazo = 0
        
        if total > 0:
            porcentaje_aprobacion = round((aprobados / total) * 100, 2)
            porcentaje_rechazo = round((rechazados / total) * 100, 2)
        
        stats_data = {
            'testimonios_aprobados': aprobados,
            'testimonios_rechazados': rechazados,
            'testimonios_en_espera': en_espera,
            'total_testimonios': total,
            'porcentaje_aprobacion': porcentaje_aprobacion,
            'porcentaje_rechazo': porcentaje_rechazo
        }
        
        print(f"Returning stats: {stats_data}")
        return jsonify(stats_data), 200

    except Exception as e:
        print(f"Error in get_testimonial_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    
    
def cambiar_estado_testimonio(testimonio_id):
    """
    Función mejorada para cambiar el estado de un testimonio
    """
    try:
        print(f"=== DEBUGGING cambiar_estado_testimonio ===")
        print(f"Testimonio ID: {testimonio_id}")
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
            
        nuevo_estado = data.get('estado')
        print(f"Nuevo estado: {nuevo_estado}")
        
        estados_validos = ['aprobado', 'anulado', 'en espera']
        if nuevo_estado not in estados_validos:
            return jsonify({'error': f'Estado no válido. Debe ser uno de: {estados_validos}'}), 400
        
        testimonio = Testimonio.query.get(testimonio_id)
        if not testimonio:
            return jsonify({'error': 'Testimonio no encontrado'}), 404
        
        estado_anterior = testimonio.estado_tes
        testimonio.estado_tes = nuevo_estado
        db.session.commit()
        
        print(f"Estado cambiado de '{estado_anterior}' a '{nuevo_estado}'")
        
        return jsonify({
            'message': 'Estado actualizado correctamente',
            'testimonio': testimonio.to_dict(),
            'estado_anterior': estado_anterior,
            'estado_nuevo': nuevo_estado
        }), 200
        
    except Exception as e:
        print(f"Error in cambiar_estado_testimonio: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def get_testimonials_by_status():
    """
    Obtiene testimonios filtrados por estado con información del usuario
    """
    try:
        print("=== DEBUGGING get_testimonials_by_status ===")
        
        status = request.args.get('status', '').lower()
        print(f"Filtering testimonials by status: '{status}'")
        
        # Construir la consulta SQL con JOIN
        base_query = """
            SELECT 
                t.id_tes,
                t.titulo_tes,
                t.contenido_tes,
                t.cargo_tes,
                t.estado_tes,
                t.fecha_publicacion_tes,
                t.id_usu_tes,
                u.nombre_usu,
                u.profile_image
            FROM testimonios t
            LEFT JOIN usuarios u ON t.id_usu_tes = u.id_usu
        """
        
        # Aplicar filtro si se proporciona un estado válido
        valid_statuses = ['aprobado', 'anulado', 'en espera']
        if status and status in valid_statuses:
            query = base_query + f" WHERE t.estado_tes = '{status}'"
            print(f"Applied filter for status: {status}")
        else:
            query = base_query
        
        query += " ORDER BY t.fecha_publicacion_tes DESC"
        
        # Usar sqlalchemy.text para consultas SQL crudas
        from sqlalchemy import text
        result = db.session.execute(text(query))
        testimonials = []
        
        for row in result:
            row_dict = row._asdict() if hasattr(row, '_asdict') else dict(row)
            print(f"Processing testimonial ID: {row_dict['id_tes']}")
            
            testimonial_data = {
                'id_tes': row_dict['id_tes'],
                'nombre_usuario': row_dict['nombre_usu'] if row_dict['nombre_usu'] else (row_dict['titulo_tes'] if row_dict['titulo_tes'] else "Usuario desconocido"),
                'cargo_tes': row_dict['cargo_tes'] if row_dict['cargo_tes'] else "",
                'estado_tes': row_dict['estado_tes'] if row_dict['estado_tes'] else "en espera",
                'titulo_tes': row_dict['titulo_tes'] if row_dict['titulo_tes'] else "",
                'contenido_tes': row_dict['contenido_tes'] if row_dict['contenido_tes'] else "",
                'fecha_publicacion_tes': row_dict['fecha_publicacion_tes'].isoformat() if row_dict['fecha_publicacion_tes'] else None,
                'profile_image': row_dict['profile_image']
            }
            testimonials.append(testimonial_data)
        
        print(f"Returning {len(testimonials)} testimonials with profile images")
        return jsonify(testimonials), 200

    except Exception as e:
        print(f"Error in get_testimonials_by_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def update_testimonial_status():
    """
    Actualiza el estado de un testimonio específico
    Requiere autenticación de administrador
    """
    try:
        print("=== DEBUGGING update_testimonial_status ===")
        
        # Verificación del token de autenticación
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("No authorization header found")
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        # Decodificación del token
        token = auth_header.split(' ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            email = decoded_token.get('email')
            print(f"Token verified for email: {email}")
        except Exception as token_error:
            print(f"Token verification failed: {str(token_error)}")
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

        # Obtener datos de la solicitud
        data = request.get_json()
        print(f"Request data received: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
        testimonial_id = data.get('testimonial_id')
        new_status = data.get('status')
        
        print(f"Updating testimonial {testimonial_id} to status: {new_status}")

        if not testimonial_id or not new_status:
            print("Missing testimonial_id or status in request")
            return jsonify({'status': 'error', 'message': 'Testimonial ID and status are required'}), 400

        # Validar que el estado sea válido
        valid_statuses = ['aprobado', 'anulado', 'en espera']
        if new_status not in valid_statuses:
            print(f"Invalid status provided: {new_status}")
            return jsonify({'status': 'error', 'message': 'Invalid status. Must be: aprobado, anulado, or en espera'}), 400

        # Búsqueda del testimonio
        testimonial = Testimonio.query.filter_by(id_tes=testimonial_id).first()
        if not testimonial:
            print(f"Testimonial not found with ID: {testimonial_id}")
            return jsonify({'status': 'error', 'message': 'Testimonial not found'}), 404

        # Actualizar el estado
        old_status = testimonial.estado_tes
        testimonial.estado_tes = new_status
        print(f"Updating testimonial status from '{old_status}' to '{new_status}'")

        # Guardar cambios
        db.session.commit()
        print("Testimonial status updated successfully in database")

        # Obtener nombre del usuario si existe la relación
        nombre_usuario = "Usuario desconocido"
        try:
            if testimonial.usuario and hasattr(testimonial.usuario, 'nombre_usu'):
                nombre_usuario = testimonial.usuario.nombre_usu
            else:
                if testimonial.titulo_tes:
                    nombre_usuario = testimonial.titulo_tes
        except:
            if testimonial.titulo_tes:
                nombre_usuario = testimonial.titulo_tes

        return jsonify({
            'status': 'success',
            'message': 'Estado del testimonio actualizado correctamente',
            'testimonial': {
                'id_tes': testimonial.id_tes,
                'nombre_usuario': nombre_usuario,
                'estado_tes': testimonial.estado_tes,
                'titulo_tes': testimonial.titulo_tes
            }
        })

    except Exception as e:
        print(f"Error in update_testimonial_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def get_testimonial_by_id():
    """
    Obtiene un testimonio específico por su ID con información del usuario
    """
    try:
        print("=== DEBUGGING get_testimonial_by_id ===")
        
        testimonial_id = request.args.get('id')
        print(f"Looking for testimonial with ID: {testimonial_id}")
        
        if not testimonial_id:
            return jsonify({'status': 'error', 'message': 'Testimonial ID is required'}), 400

        # Usar consulta SQL con JOIN
        query = """
            SELECT 
                t.id_tes,
                t.titulo_tes,
                t.contenido_tes,
                t.cargo_tes,
                t.estado_tes,
                t.fecha_publicacion_tes,
                t.id_usu_tes,
                u.nombre_usu,
                u.profile_image
            FROM testimonios t
            LEFT JOIN usuarios u ON t.id_usu_tes = u.id_usu
            WHERE t.id_tes = :testimonial_id
        """
        
        result = db.session.execute(query, {'testimonial_id': testimonial_id})
        row = result.fetchone()
        
        if not row:
            print(f"Testimonial not found with ID: {testimonial_id}")
            return jsonify({'status': 'error', 'message': 'Testimonial not found'}), 404

        row_dict = row._asdict() if hasattr(row, '_asdict') else dict(row)
        
        testimonial_data = {
            'id_tes': row_dict['id_tes'],
            'nombre_usuario': row_dict['nombre_usu'] if row_dict['nombre_usu'] else (row_dict['titulo_tes'] if row_dict['titulo_tes'] else "Usuario desconocido"),
            'cargo_tes': row_dict['cargo_tes'] if row_dict['cargo_tes'] else "",
            'estado_tes': row_dict['estado_tes'] if row_dict['estado_tes'] else "en espera",
            'titulo_tes': row_dict['titulo_tes'] if row_dict['titulo_tes'] else "",
            'contenido_tes': row_dict['contenido_tes'] if row_dict['contenido_tes'] else "",
            'fecha_publicacion_tes': row_dict['fecha_publicacion_tes'].isoformat() if row_dict['fecha_publicacion_tes'] else None,
            'profile_image': row_dict['profile_image']
        }
        
        print(f"Found testimonial with profile_image: {row_dict['profile_image']}")
        return jsonify(testimonial_data), 200

    except Exception as e:
        print(f"Error in get_testimonial_by_id: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def create_testimonial():
    """
    Crea un nuevo testimonio con estado 'en espera' por defecto
    Requiere autenticación del usuario
    """
    try:
        print("=== DEBUGGING create_testimonial ===")
        
        # Verificación del token de autenticación
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("No authorization header found")
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        # Decodificación del token
        token = auth_header.split(' ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            email = decoded_token.get('email')
            print(f"Token verified for email: {email}")
        except Exception as token_error:
            print(f"Token verification failed: {str(token_error)}")
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

        # Buscar el usuario en la base de datos
        from app.models.user import User
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            print(f"User not found for email: {email}")
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Obtener datos del testimonio
        data = request.get_json()
        print(f"Datos recibidos para nuevo testimonio: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validar campos requeridos
        titulo = data.get('titulo_tes')
        contenido = data.get('contenido_tes')
        cargo = data.get('cargo_tes', '')  # Campo opcional
        
        print(f"Titulo: {titulo}, Contenido: {contenido}, Cargo: {cargo}")
        
        if not titulo or not contenido:
            print("Missing required fields")
            return jsonify({'status': 'error', 'message': 'Título y contenido son campos obligatorios'}), 400
        
        # Crear nuevo testimonio con el ID del usuario autenticado
        nuevo_testimonio = Testimonio(
            titulo_tes=titulo,
            contenido_tes=contenido,
            cargo_tes=cargo,
            estado_tes='en espera',
            id_usu_tes=user.id_usu  # Asignar el ID del usuario autenticado
        )
        
        print(f"Creating testimonial for user ID: {user.id_usu}")
        
        db.session.add(nuevo_testimonio)
        db.session.commit()
        
        print(f"Testimonio creado con ID: {nuevo_testimonio.id_tes}")
        
        return jsonify({
            'status': 'success', 
            'message': 'Testimonio enviado correctamente',
            'testimonio': {
                'id_tes': nuevo_testimonio.id_tes,
                'titulo_tes': nuevo_testimonio.titulo_tes,
                'contenido_tes': nuevo_testimonio.contenido_tes,
                'cargo_tes': nuevo_testimonio.cargo_tes,
                'estado_tes': nuevo_testimonio.estado_tes,
                'id_usu_tes': nuevo_testimonio.id_usu_tes,
                'nombre_usuario': user.nombre_usu
            }
        }), 201
        
    except Exception as e:
        print(f"Error al crear testimonio: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500


# 🗑️ FUNCIÓN PARA ELIMINAR TESTIMONIO PERMANENTEMENTE
@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def delete_testimonial(testimonio_id):
    """
    Elimina permanentemente un testimonio de la base de datos
    Solo permite eliminar testimonios en estado 'anulado'
    """
    try:
        print(f"=== ELIMINANDO TESTIMONIO ID: {testimonio_id} ===")
        
        # Buscar el testimonio
        testimonio = Testimonio.query.get(testimonio_id)
        
        if not testimonio:
            return jsonify({
                'status': 'error',
                'message': 'Testimonio no encontrado'
            }), 404
        
        # Verificar que esté en estado anulado (opcional, para mayor seguridad)
        if testimonio.estado_tes != 'anulado':
            return jsonify({
                'status': 'error',
                'message': 'Solo se pueden eliminar testimonios en estado anulado'
            }), 400
        
        # Eliminar el testimonio
        db.session.delete(testimonio)
        db.session.commit()
        
        print(f"Testimonio {testimonio_id} eliminado exitosamente")
        
        return jsonify({
            'status': 'success',
            'message': 'Testimonio eliminado permanentemente'
        }), 200
        
    except Exception as e:
        print(f"Error al eliminar testimonio: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


# 📅 FUNCIÓN PARA OBTENER TESTIMONIOS ANULADOS ANTIGUOS
@cross_origin(origins=["http://localhost:5173", "https://proyecto-god.netlify.app"])
def get_testimonials_anulados_antiguos():
    """
    Obtiene testimonios anulados que tienen más de X días de antigüedad
    """
    try:
        # Obtener parámetro de días (por defecto 30)
        dias = request.args.get('dias', 30, type=int)
        
        print(f"=== OBTENIENDO TESTIMONIOS ANULADOS ANTIGUOS ({dias} días) ===")
        
        # Query para obtener testimonios anulados antiguos
        query = text("""
            SELECT 
                t.id_tes,
                t.titulo_tes,
                t.contenido_tes,
                t.cargo_tes,
                t.fecha_publicacion_tes,
                u.nombre_usu,
                DATEDIFF(CURDATE(), t.fecha_publicacion_tes) as dias_antiguedad
            FROM testimonios t
            INNER JOIN usuarios u ON t.id_usu_tes = u.id_usu
            WHERE t.estado_tes = 'anulado'
            AND DATEDIFF(CURDATE(), t.fecha_publicacion_tes) >= :dias
            ORDER BY t.fecha_publicacion_tes ASC
        """)
        
        result = db.session.execute(query, {'dias': dias})
        testimonios_antiguos = []
        
        for row in result:
            row_dict = row._asdict() if hasattr(row, '_asdict') else dict(row)
            
            testimonio_data = {
                'id': row_dict['id_tes'],
                'titulo': row_dict['titulo_tes'],
                'contenido': row_dict['contenido_tes'],
                'cargo': row_dict['cargo_tes'],
                'fecha_publicacion': row_dict['fecha_publicacion_tes'].isoformat() if row_dict['fecha_publicacion_tes'] else None,
                'nombre_usuario': row_dict['nombre_usu'],
                'dias_antiguedad': row_dict['dias_antiguedad']
            }
            testimonios_antiguos.append(testimonio_data)
        
        print(f"Encontrados {len(testimonios_antiguos)} testimonios anulados antiguos")
        
        return jsonify(testimonios_antiguos), 200
        
    except Exception as e:
        print(f"Error al obtener testimonios antiguos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500
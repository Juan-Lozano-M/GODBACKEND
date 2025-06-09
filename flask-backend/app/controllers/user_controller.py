# Importaciones necesarias
import json  # Para manejar conversiones JSON
from flask import jsonify, request  # Para manejar solicitudes HTTP y respuestas JSON
from app import db  # Instancia de la base de datos
from app.models.user import User  # Modelo de usuario
from firebase_admin import auth  # Para autenticación con Firebase
from app.services.cloudinary_service import CloudinaryService  # Servicio para manejar imágenes en Cloudinary
from flask_cors import cross_origin


def get_user_profile():
    try:
        print("=== DEBUGGING get_user_profile ===")
        
        # Verificación del token de autenticación
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        # Decodificación del token y obtención del email
        token = auth_header.split(' ')[1]
        
        try:
            # Verificar el token con tolerancia de tiempo
            decoded_token = auth.verify_id_token(token, check_revoked=False)
            email = decoded_token.get('email')
            print(f"Token verified successfully for email: {email}")
            
        except auth.InvalidIdTokenError as token_error:
            print(f"Invalid token error: {str(token_error)}")
            
            # Si es un error de tiempo, intentar con un pequeño delay
            if "used too early" in str(token_error).lower():
                print("Token timing issue detected, retrying after small delay...")
                import time
                time.sleep(1)  # Esperar 1 segundo
                try:
                    decoded_token = auth.verify_id_token(token, check_revoked=False)
                    email = decoded_token.get('email')
                    print(f"Token verified successfully after retry for email: {email}")
                except Exception as retry_error:
                    print(f"Token verification failed after retry: {str(retry_error)}")
                    return jsonify({'status': 'error', 'message': 'Token verification failed'}), 401
            else:
                return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
                
        except Exception as firebase_error:
            print(f"Firebase token verification error: {str(firebase_error)}")
            return jsonify({'status': 'error', 'message': 'Token verification failed'}), 401

        # Búsqueda del usuario en la base de datos
        try:
            user = User.query.filter_by(correo_usu=email).first()
            if not user:
                print(f"User not found for email: {email}")
                return jsonify({'status': 'error', 'message': 'User not found'}), 404
                
        except Exception as db_error:
            print(f"Database query error: {str(db_error)}")
            return jsonify({'status': 'error', 'message': 'Database error'}), 500

        # Conversión de intereses de JSON string a lista Python
        try:
            intereses_list = json.loads(user.intereses) if user.intereses else []
        except Exception as json_error:
            print(f"JSON parsing error for intereses: {str(json_error)}")
            intereses_list = []  # Fallback a lista vacía

        # Retorno de la información del usuario
        return jsonify({
            'status': 'success',
            'user': {
                'nombre_usu': user.nombre_usu,
                'correo_usu': user.correo_usu,
                'intereses': intereses_list,
                'fecha_nacimiento': user.fecha_nacimiento.isoformat() if user.fecha_nacimiento else None,
                'institucion': user.institucion,
                'profile_image': user.profile_image
            }
        })

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def update_user_interests():

    try:
        # Verificación de autenticación
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        # Decodificación del token
        token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get('email')

        # Obtención de nuevos intereses desde la solicitud
        data = request.get_json()
        interests = data.get('interests', [])

        # Búsqueda y actualización del usuario
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Conversión de lista a JSON string y actualización
        user.intereses = json.dumps(interests)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Interests updated successfully'
        })

    except Exception as e:
        print(f"Error in update_user_interests: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def update_user_profile():
    try:
        # Verification code remains the same
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get('email')

        # Get data from request
        data = request.get_json()
        
        # Find user
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Update user fields based on what was sent
        if 'nombre_usu' in data:
            user.nombre_usu = data['nombre_usu']
        if 'profile_image' in data:
            user.profile_image = data['profile_image']
            if 'public_id' in data:
                user.public_id = data['public_id']
        
        # Agregar soporte para fecha de nacimiento
        if 'fecha_nacimiento' in data:
            from datetime import datetime
            try:
                fecha_obj = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
                user.fecha_nacimiento = fecha_obj
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Save changes
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': {
                'nombre_usu': user.nombre_usu,
                'correo_usu': user.correo_usu,
                'profile_image': user.profile_image,
                'public_id': user.public_id,
                'fecha_nacimiento': user.fecha_nacimiento.isoformat() if user.fecha_nacimiento else None
            }
        })

    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@cross_origin(origins="http://localhost:5173")
def update_user_email():
    try:
        # Verify Firebase token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(token)
        old_email = decoded_token.get('email')

        # Get the new email from the request body
        data = request.get_json()
        new_email = data.get('new_email')

        if not new_email:
            return jsonify({'status': 'error', 'message': 'No new email provided'}), 400

        # Find user with the old email
        user = User.query.filter_by(correo_usu=old_email.lower()).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Update the email
        user.correo_usu = new_email.lower()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Correo actualizado en base de datos',
            'user': {
                'nombre_usu': user.nombre_usu,
                'correo_usu': user.correo_usu
            }
        })

    except Exception as e:
        print(f"Error in update_user_email: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def update_user_birthdate():
    """
    Actualiza la fecha de nacimiento del usuario en la base de datos
    """
    try:
        # Verificación del token de autenticación
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        # Decodificación del token
        token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get('email')

        # Obtención de la nueva fecha de nacimiento desde la solicitud
        data = request.get_json()
        fecha_nacimiento = data.get('fecha_nacimiento')

        if not fecha_nacimiento:
            return jsonify({'status': 'error', 'message': 'No birthdate provided'}), 400

        # Búsqueda del usuario
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Convertir string a objeto Date
        from datetime import datetime
        try:
            # Asumiendo que la fecha viene en formato YYYY-MM-DD
            fecha_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            user.fecha_nacimiento = fecha_obj
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Guardar cambios
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Fecha de nacimiento actualizada correctamente',
            'user': {
                'nombre_usu': user.nombre_usu,
                'correo_usu': user.correo_usu,
                'fecha_nacimiento': user.fecha_nacimiento.isoformat() if user.fecha_nacimiento else None
            }
        })

    except Exception as e:
        print(f"Error in update_user_birthdate: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
        
def update_user_institution():
    """
    Actualiza la institución educativa del usuario en la base de datos
    """
    try:
        print("=== DEBUGGING update_user_institution ===")
        
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

        # Obtención de la nueva institución desde la solicitud
        data = request.get_json()
        print(f"Request data received: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
        institucion = data.get('institution')
        print(f"Institution to update: {institucion}")

        if not institucion:
            print("No institution field in request")
            return jsonify({'status': 'error', 'message': 'No institution provided'}), 400

        # Búsqueda del usuario
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            print(f"User not found for email: {email}")
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Actualizar la institución
        old_institution = user.institucion
        user.institucion = institucion
        print(f"Updating institution from '{old_institution}' to '{institucion}'")

        # Guardar cambios
        db.session.commit()
        print("Institution updated successfully in database")

        return jsonify({
            'status': 'success',
            'message': 'Institución actualizada correctamente',
            'user': {
                'nombre_usu': user.nombre_usu,
                'correo_usu': user.correo_usu,
                'institucion': user.institucion
            }
        })

    except Exception as e:
        print(f"Error in update_user_institution: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
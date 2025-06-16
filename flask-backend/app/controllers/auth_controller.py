# Importaciones necesarias
import re  # Para validación de expresiones regulares
from flask import request, jsonify  # Para manejar solicitudes HTTP y respuestas JSON
from app.models.user import User  # Modelo de usuario de la base de datos
from app import db  # Instancia de la base de datos
from werkzeug.security import generate_password_hash, check_password_hash  # Para encriptación de contraseñas
import firebase_admin  # SDK de Firebase
from firebase_admin import auth  # Para autenticación con Firebase
from firebase_admin.auth import ActionCodeSettings  # Para configurar enlaces de restablecimiento de contraseña
from sqlalchemy import text  # Para consultas SQL personalizadas
 # Assuming you have an Admin model

# Función para validar el formato del correo electrónico
def es_correo_valido(correo):
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(patron, correo)

# Función para verificar tokens de Firebase con tolerancia de tiempo
def verificar_token_firebase(token):
    try:
        # Añade tolerancia de 5 segundos para diferencias de reloj
        return auth.verify_id_token(token, clock_skew_seconds=5)
    except Exception as e:
        print(f"Error verificando token: {str(e)}")
        return None

# Función para manejar solicitudes de restablecimiento de contraseña
def request_password_reset():
    try:
        data = request.get_json()  # Obtiene datos JSON de la solicitud
        email = data.get('email')

        # Validaciones del correo electrónico
        if not email:
            return jsonify({'status': 'error', 'message': 'Correo electrónico requerido'}), 400
            
        if not es_correo_valido(email):
            return jsonify({'status': 'error', 'message': 'Formato de correo inválido'}), 400
            
        # Verifica si el usuario existe en la base de datos local
        user = User.query.filter_by(correo_usu=email.lower()).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'No existe una cuenta con este correo'}), 404

        # Verifica si el usuario existe en Firebase
        try:
            firebase_user = auth.get_user_by_email(email)
        except firebase_admin.auth.UserNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'Usuario no encontrado en Firebase'
            }), 404
        except Exception as firebase_error:
            print(f"Firebase user check error: {str(firebase_error)}")
            return jsonify({
                'status': 'error',
                'message': 'Error al verificar usuario en Firebase'
            }), 500
            
        # Genera el enlace de restablecimiento de contraseña
        try:
            # Configura las opciones para el enlace de restablecimiento
            action_code_settings = ActionCodeSettings(
                url='http://localhost:5173/login/recoverpassword',
                handle_code_in_app=True
            )
            
            # Genera el enlace de restablecimiento
            reset_link = auth.generate_password_reset_link(
                email, 
                action_code_settings=action_code_settings
            )
            
            return jsonify({
                'status': 'success',
                'message': 'Se ha enviado un enlace para restablecer la contraseña a tu correo',
                'resetLink': reset_link
            })
        except Exception as firebase_error:
            print(f"Firebase reset error: {str(firebase_error)}")
            # Manejo de error por exceso de intentos
            if "RESET_PASSWORD_EXCEED_LIMIT" in str(firebase_error):
                return jsonify({
                    'status': 'error', 
                    'message': 'Has excedido el límite de intentos de restablecimiento de contraseña. Por favor, espera unos minutos antes de intentar nuevamente.'
                }), 429
            return jsonify({
                'status': 'error', 
                'message': 'Error al generar enlace de recuperación'
            }), 500
            
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error al procesar la solicitud'}), 500

# Función para registrar nuevos usuarios
def register_user():
    try:
        data = request.get_json()
        print("Received data:", data)

        # Manejo de registro con token de Firebase
        if 'token' in data:
            token = data.get('token')
            decoded_token = verificar_token_firebase(token)
            if not decoded_token:
                print("Invalid Firebase token")
                return jsonify({'status': 'error', 'message': 'Token de Firebase inválido'}), 401

            # Extrae información del usuario
            email = data.get('correo_usu')
            name = data.get('nombre_usu')
            firebase_uid = data.get('firebase_uid')

            # Manejo de contraseña
            contrasena = data.get('contrasena_hash_usu')
            password_hash = generate_password_hash(contrasena) if contrasena else None

            try:
                # Busca si el usuario ya existe
                existing_user = User.query.filter_by(correo_usu=email.lower()).first()
                
                if existing_user:
                    # Actualiza usuario existente
                    existing_user.firebase_uid = firebase_uid
                    existing_user.nombre_usu = name
                    existing_user.google_id = firebase_uid
                    if contrasena:
                        existing_user.contrasena_hash_usu = password_hash
                    db.session.commit()
                    
                    user_response = existing_user
                else:
                    # Crea nuevo usuario
                    new_user = User(
                        nombre_usu=name,
                        correo_usu=email.lower(),
                        contrasena_hash_usu=password_hash,
                        firebase_uid=firebase_uid,
                        google_id=firebase_uid if not contrasena else None
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    
                    user_response = new_user

                return jsonify({
                    'status': 'success',
                    'message': 'Usuario registrado exitosamente',
                    'user': {
                        'nombre': user_response.nombre_usu,
                        'correo': user_response.correo_usu,
                        'firebase_uid': user_response.firebase_uid,
                        'role': user_response.role  # Include role in registration response
                    }
                })

            except Exception as e:
                db.session.rollback()
                print(f"MySQL Error: {str(e)}")
                return jsonify({'status': 'error', 'message': f'Error en la base de datos: {str(e)}'}), 500

    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Función para iniciar sesión de usuarios
def login_user():
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token no proporcionado'}), 401

        decoded_token = verificar_token_firebase(token)
        if not decoded_token:
            return jsonify({'status': 'error', 'message': 'Token inválido'}), 401

        email = decoded_token.get('email')
        user = User.query.filter_by(correo_usu=email.lower()).first()

        if user:
            # Debug: Print user information
            print(f"User found: {user.nombre_usu}, Email: {user.correo_usu}, Role: {user.role}")
            
            return jsonify({
                'status': 'success',
                'message': 'Inicio de sesión exitoso',
                'user': {
                    'nombre': user.nombre_usu,
                    'correo': user.correo_usu,
                    'firebase_uid': user.firebase_uid,
                    'role': user.role or 'User',
                    'profile_image': user.profile_image or "", # Para imagen de perfil en el primer inicio de sesión 
                }
            })
        else:
            print(f"User not found for email: {email}")
            return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404

    except Exception as e:
        print(f"Error en el inicio de sesión: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error en el inicio de sesión: {str(e)}'}), 500


def send_verification_email():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'status': 'error', 'message': 'Email is required'}), 400

        # Use ActionCodeSettings to specify the URL to redirect to after verification
        action_code_settings = ActionCodeSettings(
            url='http://localhost:5173/verify-email',  # Your frontend URL
            handle_code_in_app=True
        )

        # Generate the email verification link
        verification_link = auth.generate_email_verification_link(email, action_code_settings)

        # Send the verification link to the user's email
        # (You can use a service like SendGrid, Mailgun, etc.)

        return jsonify({'status': 'success', 'message': 'Verification email sent'})
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error sending verification email'}), 500


def update_email():
    try:
        data = request.get_json()
        uid = data.get('firebase_uid')
        new_email = data.get('new_email')

        if not uid or not new_email:
            return jsonify({'status': 'error', 'message': 'Firebase UID and new email are required'}), 400

        # Find the user by Firebase UID
        user = User.query.filter_by(firebase_uid=uid).first()

        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Update the user's email
        user.correo_usu = new_email.lower()
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Email updated successfully'})
    except Exception as e:
        print(f"Error updating email: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error updating email'}), 500
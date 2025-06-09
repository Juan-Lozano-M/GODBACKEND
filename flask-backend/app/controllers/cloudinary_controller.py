from flask import request, jsonify
from app.services.cloudinary_service import CloudinaryService
from firebase_admin import auth
from app.models.user import User 
from app import db 

def upload_file():
    try:
        # Verifica autenticación
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token.get('uid')

        # Obtiene usuario desde la base de datos
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Verifica si hay archivo en la petición
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        file = request.files['file']
        if not file:
            return jsonify({'status': 'error', 'message': 'Empty file'}), 400

        # Elimina imagen anterior si existe
        if user.public_id:
            CloudinaryService.delete_image(user.public_id)

        # Sube nueva imagen
        folder = request.form.get('folder', 'uploads')
        result = CloudinaryService.upload_image(file, folder)

        if result['status'] == 'success':
            # Guarda la nueva URL y public_id en la base de datos
            user.profile_image = result['url']
            user.public_id = result['public_id']
            db.session.commit()

            return jsonify({
                'status': 'success',
                'url': result['url'],
                'public_id': result['public_id']
            })

        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500

    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def delete_file():
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(token)

        # Get public_id from request
        data = request.get_json()
        public_id = data.get('public_id')

        if not public_id:
            return jsonify({'status': 'error', 'message': 'No public_id provided'}), 400

        # Delete using service
        result = CloudinaryService.delete_image(public_id)

        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': 'File deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 500

    except Exception as e:
        print(f"Error in delete_file: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
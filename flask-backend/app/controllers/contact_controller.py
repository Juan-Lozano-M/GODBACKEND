from flask import request, jsonify, current_app
from flask_mail import Message
from app import mail
import logging

def send_contact_email():
    """
    Controlador para enviar correos de contacto
    """
    try:
        # Obtener datos del formulario
        data = request.get_json()
        
        # Validar que se recibieron datos
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Campos requeridos básicos
        required_fields = ['rol', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Validar email
        email = data.get('email')
        if '@' not in email:
            return jsonify({'error': 'El email no es válido'}), 400
          # Construir el contenido del mensaje según el rol
        rol = data.get('rol')
        
        # Obtener el nombre según el rol
        nombre_contacto = ""
        if rol == "Estudiante":
            nombre_contacto = data.get('nombre', 'Usuario')
        elif rol == "Maestro":
            nombre_contacto = data.get('nombre', 'Usuario')
        elif rol == "Padre":
            nombre_contacto = data.get('nombrePadre', 'Usuario')
        
        subject = f"El {rol.lower()} {nombre_contacto} desea comunicarse con Game of Dreams"
        
        # Crear el cuerpo del mensaje
        message_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #A4FF00; text-align: center;">📞 Nuevo Contacto - Game of Dreams</h2>
                
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">
                        🎯 El {rol.lower()} <strong>{nombre_contacto}</strong> desea comunicarse con la empresa
                    </h3>
                </div>
                
                <div style="background-color: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h3 style="color: #A4FF00; border-bottom: 2px solid #A4FF00; padding-bottom: 10px;">
                        📋 Información de contacto:
                    </h3>"""
        
        # Agregar campos específicos según el rol
        if rol == "Estudiante":
            message_body += f"""
            <p><strong>Nombre:</strong> {data.get('nombre', 'No proporcionado')}</p>
            <p><strong>Institución:</strong> {data.get('institucion', 'No proporcionado')}</p>
            <p><strong>Grado:</strong> {data.get('grado', 'No proporcionado')}</p>
            <p><strong>Teléfono:</strong> {data.get('telefono', 'No proporcionado')}</p>
            <p><strong>Email:</strong> {email}</p>
            """
        elif rol == "Maestro":
            message_body += f"""
            <p><strong>Nombre:</strong> {data.get('nombre', 'No proporcionado')}</p>
            <p><strong>Institución:</strong> {data.get('institucion', 'No proporcionado')}</p>
            <p><strong>Materia:</strong> {data.get('materia', 'No proporcionado')}</p>
            <p><strong>Teléfono:</strong> {data.get('telefono', 'No proporcionado')}</p>
            <p><strong>Email:</strong> {email}</p>
            """
        elif rol == "Padre":
            message_body += f"""
            <p><strong>Nombre del padre/madre:</strong> {data.get('nombrePadre', 'No proporcionado')}</p>
            <p><strong>Nombre del estudiante:</strong> {data.get('nombreEstudiante', 'No proporcionado')}</p>
            <p><strong>Institución del hijo/a:</strong> {data.get('institucion', 'No proporcionado')}</p>
            <p><strong>Teléfono:</strong> {data.get('telefono', 'No proporcionado')}</p>
            <p><strong>Email:</strong> {email}</p>
            """
        
        # Agregar mensaje adicional si existe
        if data.get('mensaje'):
            message_body += f"""
            <h3>Mensaje adicional:</h3>
            <p>{data.get('mensaje')}</p>
            """
        
        message_body += """
            <hr>
            <p><small>Este mensaje fue enviado desde el formulario de contacto de Game of Dreams</small></p>
        </body>
        </html>
        """
        
        # Crear el mensaje de correo
        msg = Message(
            subject=subject,
            recipients=[current_app.config['ADMIN_EMAIL']],
            html=message_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Enviar el correo
        mail.send(msg)
        
        # Logging para debugging
        current_app.logger.info(f"Correo enviado exitosamente para {rol}: {email}")
        
        return jsonify({
            'message': 'Correo enviado exitosamente',
            'status': 'success'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor al enviar el correo',
            'details': str(e)
        }), 500

def send_custom_contact_email():
    """
    Controlador para enviar correos de contacto personalizados con mensaje libre
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Campos requeridos para contacto personalizado
        required_fields = ['nombre', 'email', 'mensaje']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        nombre = data.get('nombre')
        email = data.get('email')
        mensaje = data.get('mensaje')
        asunto = data.get('asunto', 'Mensaje de contacto')
        
        # Validar email
        if '@' not in email:
            return jsonify({'error': 'El email no es válido'}), 400
        
        subject = f"Contacto desde Game of Dreams - {asunto}"
        
        message_body = f"""
        <html>
        <body>
            <h2>Nuevo mensaje de contacto</h2>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Asunto:</strong> {asunto}</p>
            <h3>Mensaje:</h3>
            <p>{mensaje}</p>
            <hr>
            <p><small>Este mensaje fue enviado desde el formulario de contacto de Game of Dreams</small></p>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[current_app.config['ADMIN_EMAIL']],
            html=message_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        
        current_app.logger.info(f"Correo personalizado enviado desde: {email}")
        
        return jsonify({
            'message': 'Mensaje enviado exitosamente',
            'status': 'success'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo personalizado: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor al enviar el mensaje',
            'details': str(e)
        }), 500

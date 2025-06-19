# Sistema de Formulario de Contacto con Flask-Mail

Este README explica cómo configurar y usar el sistema completo de formulario de contacto que envía correos electrónicos usando Flask-Mail.

## 📋 Características

- **Formulario interactivo por roles**: Estudiante, Maestro, Padre
- **Formulario de contacto simple**: Para mensajes generales
- **Envío de correos automático**: Usando Flask-Mail con Gmail
- **Variables de entorno**: Para proteger credenciales sensibles
- **Validación en frontend y backend**
- **Estados de carga y manejo de errores**

## 🚀 Configuración del Backend

### 1. Instalar dependencias

```bash
cd GODPROYECTO-BACKEND/flask-backend
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en `GODPROYECTO-BACKEND/flask-backend/` basado en `.env.example`:

```env
# Configuración de Flask-Mail para Gmail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com
ADMIN_EMAIL=admin@tudominio.com
```

### 3. Configurar Gmail para Flask-Mail

#### Opción 1: Contraseña de aplicación (Recomendado)
1. Ve a tu cuenta de Google → Seguridad
2. Activa la verificación en 2 pasos
3. Ve a "Contraseñas de aplicaciones"
4. Genera una nueva contraseña para "Correo"
5. Usa esta contraseña en `MAIL_PASSWORD`

#### Opción 2: Permitir aplicaciones menos seguras (No recomendado)
1. Ve a tu cuenta de Google → Seguridad
2. Activa "Acceso de aplicaciones menos seguras"
3. Usa tu contraseña normal en `MAIL_PASSWORD`

### 4. Iniciar el servidor

```bash
python app.py
```

## 🎨 Configuración del Frontend

### 1. Instalar dependencias (si es necesario)

```bash
cd GODPROYECTO
npm install axios
```

### 2. Usar los componentes

#### Formulario por roles (ya integrado):
```jsx
import SeccionContactob from './components/contacto/SeccionContactob';

function App() {
  return (
    <div>
      <SeccionContactob />
    </div>
  );
}
```

#### Formulario simple:
```jsx
import FormularioContactoSimple from './components/contacto/FormularioContactoSimple';

function ContactPage() {
  return (
    <div>
      <FormularioContactoSimple />
    </div>
  );
}
```

## 📡 Endpoints de la API

### POST /api/contact/form
Envía formulario de contacto por roles (Estudiante, Maestro, Padre)

**Body:**
```json
{
  "rol": "Estudiante",
  "nombre": "Juan Pérez",
  "institucion": "Colegio San José",
  "grado": "10°",
  "telefono": "555-1234",
  "email": "juan@email.com"
}
```

### POST /api/contact/message
Envía mensaje de contacto personalizado

**Body:**
```json
{
  "nombre": "Ana García",
  "email": "ana@email.com",
  "asunto": "Consulta sobre el proyecto",
  "mensaje": "Hola, me interesa saber más sobre..."
}
```

### GET /api/contact/test
Prueba la conexión del módulo de contacto

## 🔧 Estructura de archivos creados/modificados

### Backend:
```
flask-backend/
├── .env.example                          # Plantilla de variables de entorno
├── requirements.txt                      # Flask-Mail agregado
├── config.py                            # Configuración de Flask-Mail
├── app/__init__.py                       # Flask-Mail inicializado
├── app/controllers/contact_controller.py # Lógica de envío de correos
└── app/routes/contact_routes.py         # Rutas de contacto
```

### Frontend:
```
src/
├── services/contactService.js           # Servicio para API calls
├── components/contacto/
│   ├── SeccionContactob.jsx            # Formulario por roles (modificado)
│   └── FormularioContactoSimple.jsx   # Formulario simple (nuevo)
```

## 🧪 Pruebas

### 1. Probar la conexión
```bash
curl http://localhost:5000/api/contact/test
```

### 2. Probar envío de formulario
```bash
curl -X POST http://localhost:5000/api/contact/form \
  -H "Content-Type: application/json" \
  -d '{
    "rol": "Estudiante",
    "nombre": "Test User",
    "email": "test@email.com",
    "telefono": "555-1234",
    "institucion": "Test School",
    "grado": "10°"
  }'
```

## 🚨 Solución de problemas

### Error: "Import flask_mail could not be resolved"
```bash
pip install Flask-Mail==0.9.1
```

### Error: "Authentication failed"
- Verifica que uses una contraseña de aplicación de Gmail
- Verifica que las variables de entorno estén correctas
- Asegúrate de que el archivo `.env` esté en la raíz del backend

### Error: "Connection refused"
- Verifica que el backend esté corriendo en puerto 5000
- Verifica la configuración de axios en `axiosConfig.js`

### Correos no llegan
- Revisa la carpeta de spam
- Verifica que `ADMIN_EMAIL` esté configurado correctamente
- Revisa los logs del servidor Flask

## 📧 Formato de correos enviados

Los correos incluyen:
- **Asunto**: "Nuevo contacto desde el formulario - [Rol]"
- **Remitente**: Tu email configurado en `MAIL_DEFAULT_SENDER`
- **Destinatario**: Email configurado en `ADMIN_EMAIL`
- **Contenido HTML**: Información organizada del formulario

## 🔐 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Validación en frontend y backend
- ✅ Sanitización de datos
- ✅ CORS configurado correctamente
- ✅ Contraseñas de aplicación para Gmail

## 📚 Recursos adicionales

- [Documentación Flask-Mail](https://flask-mail.readthedocs.io/)
- [Contraseñas de aplicación Gmail](https://support.google.com/accounts/answer/185833)
- [Configuración SMTP Gmail](https://support.google.com/mail/answer/7126229)

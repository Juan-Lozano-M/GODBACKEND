from flask import request, jsonify
import requests
import os
import re
from datetime import datetime

# Configuración de OpenRouter para usar DeepSeek
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Patrones para detectar saludos simples
SIMPLE_GREETINGS = [
    r'^(hola|hello|hi|hey|buenas|buenos días|buenas tardes|buenas noches)$',
    r'^(hola|hello|hi|hey)\s*[!.]*$',
    r'^(qué tal|cómo estás|cómo está|how are you)[\s!.]*$',
    r'^(saludos|saludo)[\s!.]*$'
]

# Respuestas rápidas para saludos
QUICK_RESPONSES = [
    "¡Hola! Soy Michael, tu asistente virtual especializado en orientación profesional. ¿En qué puedo ayudarte hoy? 😊",
    "¡Hola! Me llamo Michael y estoy aquí para ayudarte con tu orientación profesional y académica. ¿Qué te gustaría saber? 🎯",
    "¡Buenas! Soy Michael, especialista en carreras universitarias y orientación laboral. ¿Cómo puedo ayudarte? 🚀"
]

def is_simple_greeting(message):
    """Detecta si el mensaje es un saludo simple"""
    message_clean = message.lower().strip()
    for pattern in SIMPLE_GREETINGS:
        if re.match(pattern, message_clean):
            return True
    return False

def get_quick_response():
    """Retorna una respuesta rápida para saludos simples"""
    import random
    return random.choice(QUICK_RESPONSES)

def clean_markdown_formatting(text):
    """Elimina formato markdown como ** y otros símbolos de formato"""
    # Eliminar ** para bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Eliminar * para italic
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Eliminar __ para bold
    text = re.sub(r'__(.*?)__', r'\1', text)
    # Eliminar _ para italic
    text = re.sub(r'_(.*?)_', r'\1', text)
    return text

def send_message():
    """Maneja los mensajes del chatbot con DeepSeek a través de OpenRouter"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Mensaje requerido'
            }), 400

        if not OPENROUTER_API_KEY:
            return jsonify({
                'status': 'error',
                'message': 'API key de OpenRouter no configurada'
            }), 500
        
        # Verificar si es un saludo simple para respuesta rápida
        if is_simple_greeting(user_message):
            return jsonify({
                'status': 'success',
                'message': get_quick_response(),
                'timestamp': datetime.now().isoformat()
            })
        
        # Preparar el contexto para DeepSeek con instrucciones mejoradas
        messages = [
            {
                "role": "system",
                "content": """Eres Michael, un asistente virtual especializado en orientación profesional y carreras universitarias. 
                Tu objetivo es ayudar a estudiantes y profesionales jóvenes con orientación profesional y académica.
                
                INSTRUCCIONES CRÍTICAS:
                - Responde de forma CONCISA y DIRECTA (máximo 200 palabras por respuesta)
                - NO uses formato markdown como ** o __ para negrita
                - Usa emojis moderadamente para hacer las respuestas más amigables
                - Para preguntas complejas, da respuestas útiles pero breves
                - Enfócate en información práctica y accionable
                - Mantén un tono amigable pero profesional
                
                ESPECIALIDADES:
                - Carreras universitarias y orientación académica
                - Tendencias laborales y oportunidades profesionales
                - Caminos educativos y especializaciones
                - Habilidades necesarias para diferentes profesiones
                - Información del mercado laboral (especialmente Colombia/Latinoamérica)
                
                ESTILO DE RESPUESTA:
                - Directo y útil
                - Sin formato markdown pesado
                - Máximo 200 palabras
                - Incluir datos concretos cuando sea posible
                - Hacer preguntas de seguimiento breves si es necesario"""
            }
        ]
        
        # Agregar historial de conversación (últimos 8 mensajes para contexto)
        for msg in conversation_history[-8:]:
            if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                messages.append({
                    "role": msg.get('role'),
                    "content": msg.get('content')
                })
        
        # Agregar mensaje actual del usuario
        messages.append({
            "role": "user",
            "content": user_message
        })
          # Llamada a OpenRouter API para usar DeepSeek
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',  # Tu dominio
            'X-Title': 'Game of Dreams Chatbot'  # Nombre de tu app
        }
        
        payload = {
            'model': 'deepseek/deepseek-chat',  # Modelo de DeepSeek en OpenRouter
            'messages': messages,
            'max_tokens': 400,  # Reducido para respuestas más concisas
            'temperature': 0.6,  # Reducido para respuestas más directas
            'top_p': 0.8,  # Reducido para mejor calidad
            'stream': False        }
        
        print(f"Enviando request a OpenRouter API: {payload}")  # Debug log
        
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            openrouter_response = response.json()
            bot_message = openrouter_response['choices'][0]['message']['content']
            
            # Limpiar formato markdown de la respuesta
            bot_message_clean = clean_markdown_formatting(bot_message)
            
            return jsonify({
                'status': 'success',
                'message': bot_message_clean,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"OpenRouter API Error: {response.status_code} - {response.text}")
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar la solicitud con OpenRouter'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Tiempo de espera agotado. Por favor, intenta de nuevo.'
        }), 408
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error de conexión con el servicio de AI'
        }), 503
    except Exception as e:
        print(f"Error general: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno del servidor'
        }), 500

def get_predefined_responses():
    """Obtiene respuestas predefinidas para preguntas comunes"""
    try:
        responses = {
            "Top profesiones": """🚀 TOP PROFESIONES EN DEMANDA 2024:

🔥 TECNOLOGÍA:
• Desarrollador de IA/ML - Crecimiento del 40% anual
• Especialista en Ciberseguridad - 3.5M puestos sin cubrir globalmente
• Desarrollador Full Stack - Salario promedio: $25-45M COP/año
• Científico de Datos - Demanda creciente en todas las industrias

💚 SOSTENIBILIDAD:
• Ingeniero en Energías Renovables - Sector en expansión
• Consultor Ambiental - Regulaciones cada vez más estrictas
• Especialista en Economía Circular - Nuevas oportunidades

🏥 SALUD:
• Enfermería Especializada - Déficit de 13M profesionales mundial
• Terapia Física - Población envejeciente = mayor demanda
• Salud Mental - 43% incremento post-pandemia

¿Te interesa profundizar en alguna área específica? 🤔""",

            "¿Cómo saber qué estudiar?": """🎯 GUÍA PARA DESCUBRIR TU CARRERA IDEAL:

1️⃣ AUTOCONOCIMIENTO:
• ¿Qué actividades te emocionan más?
• ¿En qué materias destacas naturalmente?
• ¿Prefieres trabajar con personas, datos o cosas?
• ¿Te gusta resolver problemas o crear cosas nuevas?

2️⃣ EXPLORACIÓN PRÁCTICA:
• Test vocacionales (16personalities, O*NET Interest Profiler)
• Shadowing profesional - Acompaña a profesionistas un día
• Cursos online gratuitos (Coursera, edX, Khan Academy)
• Voluntariado en áreas de interés

3️⃣ INVESTIGACIÓN DE MERCADO:
• Salarios promedio en tu región
• Proyecciones de crecimiento laboral
• Testimonios de profesionales
• Universidades con mejor reputación

4️⃣ PRUEBA Y VALIDA:
• Proyectos personales relacionados
• Prácticas profesionales tempranas
• Networking con profesionales del área

💡 TIP: No busques la "pasión perfecta", muchas veces el interés se desarrolla con la experiencia.

¿Hay algún área que ya te llama la atención? 🌟""",

            "Trabajos con demanda?": """📈 SECTORES CON MAYOR DEMANDA LABORAL:

💻 TECNOLOGÍA (Crecimiento: 25-40% anual)
• Desarrollo de Software
• Inteligencia Artificial
• Ciberseguridad
• Cloud Computing
• DevOps Engineering

🏥 SALUD Y BIENESTAR
• Enfermería (déficit de 6M profesionales)
• Fisioterapia (+18% proyectado)
• Psicología y Salud Mental (+13%)
• Tecnología Médica (+7%)

🌱 SOSTENIBILIDAD Y AMBIENTE
• Energías Renovables (+52% en 5 años)
• Ingeniería Ambiental
• Gestión de Residuos
• Agricultura Sostenible

📊 ANÁLISIS Y DATOS
• Científicos de Datos (+35%)
• Business Intelligence
• Marketing Digital
• Investigación de Mercados

🎓 EDUCACIÓN Y CAPACITACIÓN
• E-learning (+21%)
• Capacitación Corporativa
• Diseño Instruccional
• EdTech

💰 RANGO SALARIAL PROMEDIO (COL):
• Tecnología: $30-60M COP/año
• Salud: $25-50M COP/año
• Sostenibilidad: $20-40M COP/año

¿Qué sector te interesa más? 🎯""",

            "¿Qué hago si no me gusta nada?": """💭 ES COMPLETAMENTE NORMAL SENTIRSE PERDIDO/A:

🔍 ESTRATEGIAS PARA ENCONTRAR TU CAMINO:

1️⃣ CAMBIA LA PERSPECTIVA:
• No busques "tu pasión", busca problemas que quieras resolver
• Pregúntate: ¿Qué injusticias del mundo te molestan?
• ¿Qué te resulta fácil pero a otros les cuesta?

2️⃣ EXPLORA SIN PRESIÓN:
• Regla de los 30 días: Dedica 30 min/día a algo nuevo
• Visita ferias universitarias y profesionales
• Ve documentales sobre diferentes profesiones
• Habla con familiares sobre sus trabajos

3️⃣ ENFÓCATE EN HABILIDADES:
• ¿Eres bueno/a comunicándote?
• ¿Te gusta organizar y planificar?
• ¿Prefieres trabajar con las manos?
• ¿Se te facilitan los números?

4️⃣ CONSIDERA CARRERAS HÍBRIDAS:
• Bioingeniería (biología + ingeniería)
• Psicología Deportiva (psicología + deporte)
• Marketing Digital (marketing + tecnología)
• Periodismo de Datos (comunicación + análisis)

5️⃣ BUSCA APOYO:
• Orientación vocacional profesional
• Mentores en diferentes áreas
• Grupos de estudiantes universitarios
• Plataformas como LinkedIn para networking

💡 RECUERDA:
• El 80% de profesionales exitosos cambiaron de carrera al menos una vez
• Tu primer trabajo no define tu vida entera
• Es mejor empezar con algo que te parezca "interesante" que no empezar

¿Hay algo que siempre te haya resultado fácil o natural? 🌱"""
        }
        
        return jsonify({
            'status': 'success',
            'responses': responses
        })
        
    except Exception as e:
        print(f"Error getting predefined responses: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al obtener respuestas predefinidas'
        }), 500
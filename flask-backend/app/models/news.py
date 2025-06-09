from app import db
from datetime import datetime
import re
import unicodedata
import json

class News(db.Model):
    __tablename__ = 'noticias'
    
    id_noticia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo_noticia = db.Column(db.String(255), nullable=False)
    categoria_noticia = db.Column(db.String(100), nullable=False)
    descripcion_noticia = db.Column(db.Text, nullable=True)
    contenido_noticia = db.Column(db.Text, nullable=False)
    imagen_url_noticia = db.Column(db.String(500), nullable=True)
    public_id_noticia = db.Column(db.String(255), nullable=True)
    es_publicada = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    fecha_actualizacion = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Clave foránea para relacionar con el usuario (administrador)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usu'), nullable=False)
    
    def __init__(self, titulo_noticia, categoria_noticia, contenido_noticia, autor_id, 
                 descripcion_noticia=None, imagen_url_noticia=None, public_id_noticia=None):
        self.titulo_noticia = titulo_noticia
        self.categoria_noticia = self._validate_category(categoria_noticia)
        self.contenido_noticia = contenido_noticia
        self.autor_id = autor_id
        self.descripcion_noticia = descripcion_noticia
        self.imagen_url_noticia = imagen_url_noticia
        self.public_id_noticia = public_id_noticia
    
    def _validate_category(self, categoria):
        """Valida que la categoría sea válida"""
        valid_categories = ['deportes', 'tecnologia', 'politica', 'entretenimiento', 'salud', 'economia', 'educacion']
        if categoria.lower() not in valid_categories:
            raise ValueError(f"Categoría inválida. Debe ser una de: {', '.join(valid_categories)}")
        return categoria.lower()
    
    def parse_lexical_content(self, content):
        """
        Convierte contenido de Lexical Editor a texto plano preservando las listas
        """
        try:
            if not content:
                return ""
            
            # Intentar parsear como JSON
            try:
                data = json.loads(content) if isinstance(content, str) else content
            except (json.JSONDecodeError, TypeError):
                return content
            
            # Verificar si tiene la estructura de Lexical
            if not isinstance(data, dict) or 'root' not in data:
                return content
            
            def extract_text_from_node(node, depth=0):
                text_parts = []
                
                if isinstance(node, dict):
                    node_type = node.get('type', '')
                    
                    # Si es un nodo de texto
                    if node_type == 'text' and 'text' in node:
                        text_parts.append(node['text'])
                    
                    # Si es un párrafo
                    elif node_type == 'paragraph':
                        if 'children' in node and isinstance(node['children'], list):
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth)
                                if child_text:
                                    text_parts.append(child_text)
                        
                        if text_parts:
                            return ' '.join(text_parts) + '\n\n'
                    
                    # Si es una lista
                    elif node_type == 'list':
                        if 'children' in node and isinstance(node['children'], list):
                            for i, child in enumerate(node['children']):
                                child_text = extract_text_from_node(child, depth, 
                                                                  list_type=node.get('listType', 'bullet'),
                                                                  item_index=i+1)
                                if child_text:
                                    text_parts.append(child_text)
                        
                        return ''.join(text_parts) + '\n'
                    
                    # Si es un item de lista
                    elif node_type == 'listitem':
                        list_type = kwargs.get('list_type', 'bullet')
                        item_index = kwargs.get('item_index', 1)
                        
                        if 'children' in node and isinstance(node['children'], list):
                            item_content = []
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth + 1)
                                if child_text:
                                    item_content.append(child_text.strip())
                            
                            if item_content:
                                content_text = ' '.join(item_content).strip()
                                
                                if list_type == 'number':
                                    prefix = f"{item_index}. "
                                else:
                                    prefix = "• "
                                
                                indent = "  " * depth
                                return f"{indent}{prefix}{content_text}\n"
                    
                    # Si es un encabezado
                    elif node_type.startswith('heading'):
                        if 'children' in node and isinstance(node['children'], list):
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth)
                                if child_text:
                                    text_parts.append(child_text)
                        
                        if text_parts:
                            header_text = ' '.join(text_parts)
                            return f"\n{header_text}\n\n"
                    
                    # Para otros tipos de nodos, procesar hijos
                    else:
                        if 'children' in node and isinstance(node['children'], list):
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth)
                                if child_text:
                                    text_parts.append(child_text)
                
                return ''.join(text_parts)
            
            # Función auxiliar para manejar parámetros kwargs
            def extract_text_from_node(node, depth=0, **kwargs):
                text_parts = []
                
                if isinstance(node, dict):
                    node_type = node.get('type', '')
                    
                    # Si es un nodo de texto
                    if node_type == 'text' and 'text' in node:
                        text_parts.append(node['text'])
                    
                    # Si es un párrafo
                    elif node_type == 'paragraph':
                        if 'children' in node and isinstance(node['children'], list):
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth)
                                if child_text:
                                    text_parts.append(child_text)
                        
                        if text_parts:
                            return ' '.join(text_parts) + '\n\n'
                    
                    # Si es una lista
                    elif node_type == 'list':
                        if 'children' in node and isinstance(node['children'], list):
                            for i, child in enumerate(node['children']):
                                child_text = extract_text_from_node(child, depth, 
                                                                  list_type=node.get('listType', 'bullet'),
                                                                  item_index=i+1)
                                if child_text:
                                    text_parts.append(child_text)
                        
                        return ''.join(text_parts) + '\n'
                    
                    # Si es un item de lista
                    elif node_type == 'listitem':
                        list_type = kwargs.get('list_type', 'bullet')
                        item_index = kwargs.get('item_index', 1)
                        
                        if 'children' in node and isinstance(node['children'], list):
                            item_content = []
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth + 1)
                                if child_text:
                                    item_content.append(child_text.strip())
                            
                            if item_content:
                                content_text = ' '.join(item_content).strip()
                                
                                if list_type == 'number':
                                    prefix = f"{item_index}. "
                                else:
                                    prefix = "• "
                                
                                indent = "  " * depth
                                return f"{indent}{prefix}{content_text}\n"
                    
                    # Para otros tipos de nodos, procesar hijos
                    else:
                        if 'children' in node and isinstance(node['children'], list):
                            for child in node['children']:
                                child_text = extract_text_from_node(child, depth)
                                if child_text:
                                    text_parts.append(child_text)
                
                return ''.join(text_parts)
            
            # Extraer texto desde la raíz
            extracted_text = extract_text_from_node(data['root'])
            
            # Limpieza básica
            cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', extracted_text.strip())
            
            return cleaned_text if cleaned_text else "Contenido no disponible"
            
        except Exception as e:
            print(f"Error parsing Lexical content: {str(e)}")
            return content if isinstance(content, str) else "Error al procesar contenido"
    
    def get_plain_content(self):
        """Obtiene el contenido como texto plano con formato de listas"""
        return self.parse_lexical_content(self.contenido_noticia)
    
    def get_html_content(self):
        """Obtiene el contenido como HTML"""
        return self.parse_lexical_to_html(self.contenido_noticia)
    
    def parse_lexical_to_html(self, content):
        """
        Convierte contenido de Lexical Editor a HTML con soporte para listas
        """
        try:
            if not content:
                return ""
            
            try:
                data = json.loads(content) if isinstance(content, str) else content
            except (json.JSONDecodeError, TypeError):
                return f"<p>{content}</p>"
            
            if not isinstance(data, dict) or 'root' not in data:
                return f"<p>{content}</p>"
            
            def extract_html_from_node(node):
                if isinstance(node, dict):
                    node_type = node.get('type', '')
                    
                    # Nodo de texto
                    if node_type == 'text' and 'text' in node:
                        text = node['text']
                        
                        # Aplicar formato si existe
                        format_value = node.get('format', 0)
                        if format_value & 1:  # Bold
                            text = f"<strong>{text}</strong>"
                        if format_value & 2:  # Italic
                            text = f"<em>{text}</em>"
                        
                        return text
                    
                    # Párrafo
                    elif node_type == 'paragraph':
                        children_html = ""
                        if 'children' in node and isinstance(node['children'], list):
                            children_html = ''.join(extract_html_from_node(child) for child in node['children'])
                        return f"<p>{children_html}</p>"
                    
                    # Encabezados
                    elif node_type.startswith('heading'):
                        level = node.get('tag', 'h2')
                        children_html = ""
                        if 'children' in node and isinstance(node['children'], list):
                            children_html = ''.join(extract_html_from_node(child) for child in node['children'])
                        return f"<{level}>{children_html}</{level}>"
                    
                    # Lista
                    elif node_type == 'list':
                        list_type = node.get('listType', 'bullet')
                        list_tag = 'ol' if list_type == 'number' else 'ul'
                        
                        children_html = ""
                        if 'children' in node and isinstance(node['children'], list):
                            children_html = ''.join(extract_html_from_node(child) for child in node['children'])
                        
                        return f"<{list_tag}>{children_html}</{list_tag}>"
                    
                    # Item de lista
                    elif node_type == 'listitem':
                        children_html = ""
                        if 'children' in node and isinstance(node['children'], list):
                            children_html = ''.join(extract_html_from_node(child) for child in node['children'])
                        return f"<li>{children_html}</li>"
                    
                    # Nodo root u otros contenedores
                    else:
                        if 'children' in node and isinstance(node['children'], list):
                            return ''.join(extract_html_from_node(child) for child in node['children'])
                
                return ""
            
            html_content = extract_html_from_node(data['root'])
            return html_content if html_content else "<p>Contenido no disponible</p>"
            
        except Exception as e:
            print(f"Error parsing Lexical content to HTML: {str(e)}")
            return f"<p>{content if isinstance(content, str) else 'Error al procesar contenido'}</p>"
    
    def generate_slug(self):
        """Genera un slug basado en el título de la noticia"""
        if not self.titulo_noticia:
            return str(self.id_noticia) if self.id_noticia else 'noticia'
        
        # Convertir a minúsculas
        slug = self.titulo_noticia.lower()
        
        # Normalizar caracteres Unicode (quitar acentos)
        slug = unicodedata.normalize('NFKD', slug)
        slug = slug.encode('ascii', 'ignore').decode('ascii')
        
        # Reemplazar espacios y caracteres especiales con guiones
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        
        # Quitar guiones al inicio y final
        slug = slug.strip('-')
        
        # Limitar longitud y agregar ID para unicidad
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')
        
        # Agregar ID para garantizar unicidad
        return f"{slug}-{self.id_noticia}" if self.id_noticia else slug
    
    def validate_title(self):
        """Valida el título"""
        if not self.titulo_noticia or len(self.titulo_noticia.strip()) == 0:
            raise ValueError("El título no puede estar vacío")
        if len(self.titulo_noticia) > 255:
            raise ValueError("El título no puede exceder 255 caracteres")
        return True
    
    def validate_content(self):
        """Valida el contenido"""
        if not self.contenido_noticia or len(self.contenido_noticia.strip()) == 0:
            raise ValueError("El contenido no puede estar vacío")
        return True
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_noticia,
            'id_noticia': self.id_noticia,
            # Nombres para el frontend
            'title': self.titulo_noticia,
            'category': self.categoria_noticia,
            'description': self.descripcion_noticia,
            'image': self.imagen_url_noticia,
            'slug': self.generate_slug(),
            'date': self.fecha_creacion.strftime('%d de %B de %Y') if self.fecha_creacion else None,
            'author': self.autor.nombre_usu if self.autor else 'Autor desconocido',
            # Nombres originales del backend
            'titulo': self.titulo_noticia,
            'categoria': self.categoria_noticia,
            'descripcion': self.descripcion_noticia,
            'contenido': self.get_plain_content(),  # ← Texto plano con formato de listas
            'contenido_html': self.get_html_content(),  # ← HTML con formato de listas
            'contenido_raw': self.contenido_noticia,  # ← Contenido original
            'imagen_url': self.imagen_url_noticia,
            'public_id': self.public_id_noticia,
            'es_publicada': self.es_publicada,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'autor': {
                'id': self.autor.id_usu,
                'nombre': self.autor.nombre_usu,
                'correo': self.autor.correo_usu
            } if self.autor else None
        }
    
    def __repr__(self):
        return f'<News {self.id_noticia}: {self.titulo_noticia} - Autor: {self.autor.nombre_usu if self.autor else "Sin autor"}>'
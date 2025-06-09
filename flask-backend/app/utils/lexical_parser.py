import json
import re

def parse_lexical_content_with_lists(content):
    """
    Convierte contenido de Lexical Editor a texto plano preservando las listas
    
    Args:
        content (str): String JSON del contenido de Lexical
        
    Returns:
        str: Texto plano extraído del contenido con formato de listas
    """
    try:
        # Si el contenido ya es un string normal, devolverlo tal como está
        if not content:
            return ""
        
        # Intentar parsear como JSON
        try:
            data = json.loads(content) if isinstance(content, str) else content
        except (json.JSONDecodeError, TypeError):
            # Si no es JSON válido, asumir que es texto plano
            return content
        
        # Verificar si tiene la estructura de Lexical
        if not isinstance(data, dict) or 'root' not in data:
            return content
        
        # Contador para listas numeradas
        ordered_list_counters = []
        
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
                    list_type = node.get('listType', 'bullet')
                    
                    # Inicializar contador para listas numeradas
                    if list_type == 'number':
                        if len(ordered_list_counters) <= depth:
                            ordered_list_counters.extend([0] * (depth + 1 - len(ordered_list_counters)))
                        ordered_list_counters[depth] = 0
                    
                    if 'children' in node and isinstance(node['children'], list):
                        for child in node['children']:
                            child_text = extract_text_from_node(child, depth)
                            if child_text:
                                text_parts.append(child_text)
                    
                    return ''.join(text_parts) + '\n'
                
                # Si es un item de lista
                elif node_type == 'listitem':
                    # Encontrar el tipo de lista padre
                    list_type = 'bullet'  # Por defecto
                    
                    if 'children' in node and isinstance(node['children'], list):
                        item_content = []
                        for child in node['children']:
                            child_text = extract_text_from_node(child, depth + 1)
                            if child_text:
                                item_content.append(child_text.strip())
                        
                        if item_content:
                            content_text = ' '.join(item_content).strip()
                            
                            # Detectar si es lista numerada por el contexto
                            # (esto es una aproximación, idealmente deberías tener acceso al nodo padre)
                            if any(char.isdigit() for char in content_text[:10]):
                                # Es probable que sea numerada
                                if len(ordered_list_counters) <= depth:
                                    ordered_list_counters.extend([0] * (depth + 1 - len(ordered_list_counters)))
                                ordered_list_counters[depth] += 1
                                prefix = f"{ordered_list_counters[depth]}. "
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
                        level = node.get('tag', 'h2')
                        header_text = ' '.join(text_parts)
                        
                        # Formatear según el nivel
                        if level == 'h1':
                            return f"\n{'=' * len(header_text)}\n{header_text}\n{'=' * len(header_text)}\n\n"
                        elif level == 'h2':
                            return f"\n{header_text}\n{'-' * len(header_text)}\n\n"
                        else:
                            return f"\n{header_text}\n\n"
                
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
        
        # Limpiar texto: remover espacios extra pero preservar estructura de listas
        lines = extracted_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.rstrip()
            if stripped_line or (cleaned_lines and not cleaned_lines[-1].strip()):
                cleaned_lines.append(stripped_line)
        
        # Remover líneas vacías múltiples al final
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        return cleaned_text if cleaned_text else "Contenido no disponible"
        
    except Exception as e:
        print(f"Error parsing Lexical content with lists: {str(e)}")
        return content if isinstance(content, str) else "Error al procesar contenido"


def parse_lexical_to_html_enhanced(content):
    """
    Convierte contenido de Lexical Editor a HTML con soporte completo para listas
    
    Args:
        content (str): String JSON del contenido de Lexical
        
    Returns:
        str: HTML extraído del contenido
    """
    try:
        if not content:
            return ""
        
        # Intentar parsear como JSON
        try:
            data = json.loads(content) if isinstance(content, str) else content
        except (json.JSONDecodeError, TypeError):
            return f"<p>{content}</p>"
        
        # Verificar si tiene la estructura de Lexical
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
                    if format_value & 4:  # Underline
                        text = f"<u>{text}</u>"
                    if format_value & 8:  # Strikethrough
                        text = f"<s>{text}</s>"
                    
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
                
                # Cita en bloque
                elif node_type == 'quote':
                    children_html = ""
                    if 'children' in node and isinstance(node['children'], list):
                        children_html = ''.join(extract_html_from_node(child) for child in node['children'])
                    return f"<blockquote>{children_html}</blockquote>"
                
                # Código
                elif node_type == 'code':
                    children_html = ""
                    if 'children' in node and isinstance(node['children'], list):
                        children_html = ''.join(extract_html_from_node(child) for child in node['children'])
                    return f"<pre><code>{children_html}</code></pre>"
                
                # Nodo root u otros contenedores
                else:
                    if 'children' in node and isinstance(node['children'], list):
                        return ''.join(extract_html_from_node(child) for child in node['children'])
            
            return ""
        
        # Extraer HTML desde la raíz
        html_content = extract_html_from_node(data['root'])
        
        return html_content if html_content else "<p>Contenido no disponible</p>"
        
    except Exception as e:
        print(f"Error parsing Lexical content to HTML: {str(e)}")
        return f"<p>{content if isinstance(content, str) else 'Error al procesar contenido'}</p>"
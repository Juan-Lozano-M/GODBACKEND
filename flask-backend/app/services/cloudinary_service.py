import cloudinary
import cloudinary.uploader
from werkzeug.datastructures import FileStorage

class CloudinaryService:
    @staticmethod
    def upload_image(file: FileStorage, folder: str = "uploads"):
        try:            # Configurar transformaciones según el tipo de contenido
            if folder == "news_images" or "news" in folder.lower():
                # Para noticias: dimensiones más grandes y formato panorámico
                transformation = [
                    {'width': 1200, 'height': 800, 'crop': 'fill'},
                    {'quality': 'auto:good'}
                ]
            else:
                # Para perfiles y otros: dimensiones cuadradas
                transformation = [
                    {'width': 400, 'height': 400, 'crop': 'fill'},
                    {'quality': 'auto'}
                ]
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder=folder,
                allowed_formats=['jpg', 'png', 'jpeg'],
                transformation=transformation
            )
            return {
                'status': 'success',
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id']
            }
        except Exception as e:
            print(f"Error uploading to Cloudinary: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to upload image'
            }

    @staticmethod
    def delete_image(public_id: str):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            print(f"Error deleting from Cloudinary: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to delete image'
            }
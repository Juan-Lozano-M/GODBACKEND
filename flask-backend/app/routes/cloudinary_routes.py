from flask import Blueprint
from app.controllers.cloudinary_controller import upload_file, delete_file

cloudinary_bp = Blueprint('cloudinary_bp', __name__)

cloudinary_bp.route('/upload', methods=['POST'])(upload_file)
cloudinary_bp.route('/delete', methods=['DELETE'])(delete_file)

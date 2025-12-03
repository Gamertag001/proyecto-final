import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024
UPLOAD_FOLDER = 'static/uploads/recibos'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None


def generate_unique_filename(original_filename):
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:12]
    if ext:
        return f"{unique_id}.{ext}"
    return unique_id


def validate_file(file):
    if not file or file.filename == '':
        return (False, "No se ha seleccionado ningun archivo")
    
    if not allowed_file(file.filename):
        return (False, f"Tipo de archivo no permitido. Solo se aceptan: {', '.join(ALLOWED_EXTENSIONS)}")
    
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return (False, f"El archivo excede el tamano maximo permitido de {max_mb:.0f} MB")
    
    return (True, None)


def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file):
    ensure_upload_folder()
    
    is_valid, error_message = validate_file(file)
    if not is_valid:
        return (False, error_message, None, None)
    
    original_filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(original_filename)
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(file_path)
        relative_path = f"uploads/recibos/{unique_filename}"
        return (True, None, original_filename, relative_path)
    except Exception as ex:
        return (False, f"Error al guardar el archivo: {str(ex)}", None, None)


def delete_file(relative_path):
    if not relative_path:
        return True
    
    full_path = os.path.join('static', relative_path)
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
        return True
    except Exception as ex:
        print(f"Error al eliminar archivo: {ex}")
        return False


def get_file_url(relative_path):
    if not relative_path:
        return None
    return f"/static/{relative_path}"

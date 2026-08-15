import os
import secrets
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Checks if the uploaded file has an allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(form_picture, folder='profile_pics'):
    """
    Saves an uploaded profile picture to app/static/uploads/profile_pics/
    Resizes image using Pillow to 300x300 for optimized performance.
    Returns saved relative filename.
    """
    if not form_picture or not hasattr(form_picture, 'filename') or not form_picture.filename:
        return 'default.jpg'

    random_hex = secrets.token_hex(8)
    sec_fn = secure_filename(form_picture.filename)
    if not sec_fn:
        return 'default.jpg'

    _, f_ext = os.path.splitext(sec_fn)
    f_ext = f_ext.lower()
    if f_ext.lstrip('.') not in ALLOWED_EXTENSIONS:
        f_ext = '.jpg'

    
    picture_fn = random_hex + f_ext
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', folder)
    os.makedirs(upload_dir, exist_ok=True)
    picture_path = os.path.join(upload_dir, picture_fn)

    # Resize image to thumbnail size
    output_size = (300, 300)
    try:
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    except Exception:
        form_picture.save(picture_path)

    return picture_fn

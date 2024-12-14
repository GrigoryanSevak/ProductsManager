import hashlib
from io import BytesIO
from PIL import Image


def get_image_size(files_path):
    try:
        with open(files_path, 'rb') as f:
            image_data = f.read()
            image = Image.open(BytesIO(image_data))
            return {'width': image.size[0], 'height': image.size[1], 'size': len(image_data)}
    except:
        return {'width': None, 'height': None, 'size': None}


def hash_file(files_path, hash_algo='sha256'):
    hash_func = hashlib.new(hash_algo)
    
    try:
        with open(files_path, 'rb') as file:
            while chunk := file.read(8192):
                    hash_func.update(chunk)
        
        return hash_func.hexdigest()[:40]
    except:
        return ''
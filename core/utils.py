from random import choice
import string
from uuid import uuid4
import os.path


def generate_random_string(
        size=10, chars=string.ascii_letters + string.digits + '-_'):
    return ''.join([choice(chars) for i in range(size)])


def get_image_upload_path(instance, filename):
    app_name = instance.__class__._meta.app_label
    file_extention = filename.split('.')[-1]
    new_file_name = f'{uuid4()}.{file_extention}'
    file_path = os.path.join(app_name, new_file_name)
    return file_path


def get_ckeditor_image_upload_path(filename):
    file_extention = filename.split('.')[-1]
    new_file_name = f'{uuid4()}.{file_extention}'
    file_path = os.path.join('ckeditor', new_file_name)
    return file_path

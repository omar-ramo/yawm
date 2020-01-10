import os
from uuid import uuid4

from django.conf import settings
from django.core.files import File


def assign_default_image_to_profile(profile):
    default_image_path = os.path.join(
        settings.BASE_DIR, 'static', 'img', 'default_person_image.png')
    profile.image.save(
        f'{uuid4()}.png',
        File(open(default_image_path, 'rb')),
        save=False)
    return profile

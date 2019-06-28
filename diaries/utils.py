import os
import re
from urllib.parse import unquote

from django.conf import settings


def delete_ckeditor_rich_text_images(html_content):
	'''Find the sources of images in the provided html content. and delete
	   the actual image.
	'''
	image_regex = r'{}'.format(settings.CKEDITOR_UPLOAD_PATH)
	image_regex += r'[a-zA-Z0-9@\.\+-_%]+/[0-9]{4}/[0-9]{2}/[0-9]{2}/'
	image_regex += r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\.[a-zA-Z]{2,5}'
	
	images_occurences = re.findall(image_regex, html_content)

	for img_upload_path in images_occurences:

		img_upload_path = unquote(img_upload_path)
		img_full_path = os.path.join(settings.MEDIA_ROOT, img_upload_path)
		
		# CKEDITOR automatically generate thumbnails for images
		img_name = '.'.join(img_full_path.split('.')[:-1])
		img_ext = img_full_path.split('.')[-1]
		img_thumb_full_path = '{}_thumb.{}'.format(img_name, img_ext)


		os.unlink(img_full_path)
		os.unlink(img_thumb_full_path)



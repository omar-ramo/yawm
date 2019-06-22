# Yawm
It's just like a blog application. but here it's intended as a place where users can write there diaries. some of it's functionalities are: likes,comments, drafts, following system, notification(not in real time for now)...

### What i used:

-  **Django**: backend
-  **django-ckeditor**: Diray content editor.
-  **django-crispy-forms**: To render forms
-  **django-notification-hq**: To manage notifications
-  **bleach**: To clean and linkfy diary content
-  ...

for production:

-  **python-decouple**: To store sensative data as environement variables.
-  **dj-database-url**: Instead of DB_USER, DB_HOST... use DATABASE_URL
-  **django-storages + dropbox**: Where i store media files.

Well, there is much more to go.

### To run it locally:
`python manage migrate --settings=yawm.settings.dev`
`python manage runserver --settings=yawm.settings.dev`

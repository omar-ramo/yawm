"""yawm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.decorators.cache import never_cache
import notifications.urls
from ckeditor_uploader import views as ckeditor_uploader_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'inbox/notifications/',
        include(
            notifications.urls,
            namespace='notifications')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('auth/', include('allauth.urls')),

    path('ckeditor/', include([
        path(
            'upload/',
            login_required(ckeditor_uploader_views.upload),
            name='ckeditor_upload'
        ),
        path(
            'browse/',
            login_required(never_cache(ckeditor_uploader_views.browse)),
            name='ckeditor_browse'
        ),
    ])),
    path('', include('diaries.urls', namespace='diaries')),

]

if settings.DEBUG is True:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

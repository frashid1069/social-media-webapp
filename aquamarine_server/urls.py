"""
URL configuration for aquamarine_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView 
from django.conf import settings
from django.conf.urls.static import static

# From https://drf-spectacular.readthedocs.io/en/latest/readme.html#installation 
# From https://www.youtube.com/watch?v=jc8v_DpAbEk 
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("service.urls")),
    path('schema/', SpectacularAPIView.as_view(), name='schema'), 
    path('swagger/', SpectacularSwaggerView.as_view(), name='swagger'), 
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Check if the application is running in development mode (DEBUG = True)
if settings.DEBUG:
    # Add URL patterns to serve media files from MEDIA_ROOT when the URL starts with MEDIA_URL.
    # This configuration is only for development purposes.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Explanation:
    # - `static()` generates a URL pattern to map URLs starting with MEDIA_URL to files stored in MEDIA_ROOT.
    # - This allows Django's development server to serve media files like images, videos, or documents
    #   from the local file system without needing an external web server like Apache or Nginx.

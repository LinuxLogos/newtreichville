"""
URL configuration for new_treichville_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include # Make sure include is imported
from django.conf import settings # Add this import
from django.conf.urls.static import static # Add this import
from django.views.generic import TemplateView # Add this import

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),

    # Frontend Pages - served by Django for development convenience
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("menu/", TemplateView.as_view(template_name="menu.html"), name="menu"),
    path("events/", TemplateView.as_view(template_name="events.html"), name="events"),
    path("reservation/", TemplateView.as_view(template_name="reservation.html"), name="reservation"),
    path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # It's also common to serve static files from the main static directory this way in dev
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # However, Django's runserver handles STATIC_URL automatically if APP_DIRS=True or through finders.
    # Our frontend/static files are not yet part of Django's static file collection system.

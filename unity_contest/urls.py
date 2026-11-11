"""
URL configuration for unity_contest project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import views as core_views

urlpatterns = [
    path(f"{settings.ADMIN_PATH}login/", core_views.admin_login_redirect),
    path(settings.ADMIN_PATH, admin.site.urls),
    path("", include("core.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

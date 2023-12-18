from django.contrib import admin
from django.urls import include, path

from config.settings import ADMIN_URL

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path("", include("secretariat.urls")),
]

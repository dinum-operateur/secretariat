from django.urls import path

from secretariat import views

urlpatterns = [
    path("", views.view_index, name="index"),
    path("accessibilite/", views.view_accessibilite, name="accessibilite"),
]

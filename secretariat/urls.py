from django.urls import include, path

from secretariat import views

urlpatterns = [
    path("", views.view_index, name="index"),
    path("accessibilite/", views.view_accessibilite, name="accessibilite"),
    path("compte/", include("django.contrib.auth.urls")),
]

# see https://docs.djangoproject.com/en/4.2/topics/auth/default/#using-the-views
# compte/login/ [name='login']
# compte/logout/ [name='logout']
# compte/password_change/ [name='password_change']
# compte/password_change/done/ [name='password_change_done']
# compte/password_reset/ [name='password_reset']
# compte/password_reset/done/ [name='password_reset_done']
# compte/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# compte/reset/done/ [name='password_reset_complete']

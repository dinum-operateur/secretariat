from django.contrib.auth import logout
from django.shortcuts import redirect, render


def view_index(request):
    return render(request, "secretariat/accueil.html")


def view_accessibilite(request):
    return render(request, "secretariat/accessibilite.html")


def logout_view(request):
    logout(request)
    return redirect("index")

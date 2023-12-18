from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render


def view_index(request):
    return render(request, "secretariat/accueil.html")


def view_accessibilite(request):
    return render(request, "secretariat/accessibilite.html")


def view_logout(request):
    logout(request)
    messages.success(
        request,
        "Vous avez bien été déconnecté.e.",
    )
    return redirect("index")

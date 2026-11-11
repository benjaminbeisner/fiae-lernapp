from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("anmelden/", auth_views.LoginView.as_view(template_name="accounts/anmelden.html"), name="login"),
    path("abmelden/", auth_views.LogoutView.as_view(), name="logout"),
    path("einstellungen/", views.profil, name="profil"),
    path("registrieren/", views.registrieren, name="registrieren"),
    path("passwort/", auth_views.PasswordChangeView.as_view(template_name="accounts/passwort.html", success_url="/"), name="password_change"),
]

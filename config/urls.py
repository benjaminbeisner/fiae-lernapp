from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "FIAE-Lernapp Verwaltung"
admin.site.site_title = "FIAE-Lernapp"

urlpatterns = [
    path("verwaltung/", admin.site.urls),
    path("konto/", include("accounts.urls")),
    path("", include("lernen.urls")),
]

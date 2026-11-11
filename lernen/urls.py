from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("einstufung/", views.einstufung_start, name="einstufung_start"),
    path("heute/", views.taeglich_start, name="taeglich_start"),
    path("thema/<slug:slug>/", views.thema_detail, name="thema_detail"),
    path("thema/<slug:slug>/ueben/", views.thema_start, name="thema_start"),
    path("lektion/<int:pk>/", views.lektion_start, name="lektion_start"),
    path("lernen/", views.sitzung, name="sitzung"),
    path("lernen/ende/", views.sitzung_ende, name="sitzung_ende"),
    path("pruefung/", views.simulation_start, name="simulation_start"),
    path("pruefung/<int:pk>/", views.simulation, name="simulation"),
    path("pruefung/<int:pk>/ergebnis/", views.simulation_ergebnis, name="simulation_ergebnis"),
    path("rangliste/", views.rangliste, name="rangliste"),
    path("abzeichen/", views.abzeichen, name="abzeichen"),
]

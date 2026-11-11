from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("einstufung/", views.einstufung_start, name="einstufung_start"),
    path("heute/", views.taeglich_start, name="taeglich_start"),
    path("thema/<slug:slug>/", views.thema_start, name="thema_start"),
    path("lernen/", views.sitzung, name="sitzung"),
    path("lernen/ende/", views.sitzung_ende, name="sitzung_ende"),
]

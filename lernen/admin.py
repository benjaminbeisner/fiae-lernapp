from django.contrib import admin

from .models import Antwort, Frage, Karte, PdfPruefung, Thema, Versuch


class AntwortInline(admin.TabularInline):
    model = Antwort
    extra = 0


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    list_display = ("name", "pruefung", "gewicht", "reihenfolge")
    list_filter = ("pruefung",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Frage)
class FrageAdmin(admin.ModelAdmin):
    list_display = ("schluessel", "thema", "typ", "schwierigkeit", "einstufung", "aktiv")
    list_filter = ("thema__pruefung", "thema", "typ", "einstufung", "aktiv")
    search_fields = ("schluessel", "text")
    inlines = [AntwortInline]


@admin.register(Karte)
class KarteAdmin(admin.ModelAdmin):
    list_display = ("user", "frage", "box", "faellig_am", "richtig_anzahl", "falsch_anzahl")
    list_filter = ("box",)


@admin.register(Versuch)
class VersuchAdmin(admin.ModelAdmin):
    list_display = ("user", "frage", "quelle", "richtig", "zeitpunkt")
    list_filter = ("quelle", "richtig")


@admin.register(PdfPruefung)
class PdfPruefungAdmin(admin.ModelAdmin):
    list_display = ("user", "nummer", "erstellt", "gesamt", "note")
    list_filter = ("erstellt",)

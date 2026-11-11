from django.contrib import admin

from .models import InviteCode, Profil


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "notiz", "nutzungen", "max_nutzungen", "gueltig_bis", "aktiv", "erstellt_am")
    list_filter = ("aktiv",)
    search_fields = ("code", "notiz")
    readonly_fields = ("nutzungen", "erstellt_von", "erstellt_am")

    def save_model(self, request, obj, form, change):
        if not obj.erstellt_von_id:
            obj.erstellt_von = request.user
        super().save_model(request, obj, form, change)


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("user", "eingeladen_mit", "tagesziel_minuten")

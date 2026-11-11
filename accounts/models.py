import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def _neuer_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # ohne verwechselbare Zeichen
    return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(2))


class InviteCode(models.Model):
    code = models.CharField("Code", max_length=20, unique=True, default=_neuer_code)
    notiz = models.CharField("Notiz (z. B. für wen)", max_length=100, blank=True)
    max_nutzungen = models.PositiveIntegerField("Max. Nutzungen", default=1)
    nutzungen = models.PositiveIntegerField("Bisher genutzt", default=0)
    gueltig_bis = models.DateTimeField("Gültig bis", null=True, blank=True)
    aktiv = models.BooleanField("Aktiv", default=True)
    erstellt_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Einladungscode"
        verbose_name_plural = "Einladungscodes"
        ordering = ["-erstellt_am"]

    def __str__(self) -> str:
        return f"{self.code} ({self.nutzungen}/{self.max_nutzungen})"

    def ist_gueltig(self) -> bool:
        if not self.aktiv or self.nutzungen >= self.max_nutzungen:
            return False
        return self.gueltig_bis is None or self.gueltig_bis > timezone.now()


class Profil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil")
    eingeladen_mit = models.ForeignKey(InviteCode, null=True, blank=True, on_delete=models.SET_NULL)
    tagesziel_minuten = models.PositiveIntegerField("Tagesziel (Minuten)", default=20)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profile"

    def __str__(self) -> str:
        return f"Profil von {self.user}"

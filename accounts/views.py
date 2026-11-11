from django.contrib.auth import login
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render

from .forms import RegistrierungsForm
from .models import InviteCode, Profil


def registrieren(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrierungsForm(request.POST or None, initial={"einladungscode": request.GET.get("code", "")})
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # Code sperren und erneut prüfen, damit er nicht doppelt verbraucht wird
            invite = InviteCode.objects.select_for_update().get(pk=form.invite.pk)
            if not invite.ist_gueltig():
                form.add_error("einladungscode", "Dieser Einladungscode ist gerade verbraucht worden.")
                return render(request, "accounts/registrieren.html", {"form": form})
            user = form.save()
            InviteCode.objects.filter(pk=invite.pk).update(nutzungen=F("nutzungen") + 1)
            Profil.objects.create(user=user, eingeladen_mit=invite)
        login(request, user)
        return redirect("einstufung_start")
    return render(request, "accounts/registrieren.html", {"form": form})

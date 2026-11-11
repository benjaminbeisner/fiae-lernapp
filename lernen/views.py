import random
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import logik
from .models import Frage, Karte, Thema, Versuch

SITZUNG = "lernsitzung"
TITEL = {
    Versuch.Quelle.EINSTUFUNG: "Einstufungstest",
    Versuch.Quelle.TAEGLICH: "Tägliches Lernen",
    Versuch.Quelle.THEMA: "Themen-Training",
}


def _starte(request, art: str, ids: list[int], titel: str | None = None):
    if not ids:
        messages.info(request, "Gerade gibt es dafür keine Fragen. Schau später wieder vorbei.")
        return redirect("dashboard")
    request.session[SITZUNG] = {
        "art": art, "titel": titel or TITEL[art], "ids": ids, "pos": 0,
        "richtig": 0, "beantwortet": None, "ergebnisse": [],
    }
    return redirect("sitzung")


@login_required
def dashboard(request):
    user = request.user
    heute = timezone.localdate()
    hat_einstufung = Versuch.objects.filter(user=user, quelle=Versuch.Quelle.EINSTUFUNG).exists()
    context = {
        "hat_einstufung": hat_einstufung,
        "faellig": Karte.objects.filter(user=user, faellig_am__lte=heute, frage__aktiv=True).count(),
        "heute_beantwortet": Versuch.objects.filter(user=user, zeitpunkt__date=heute).count(),
        "serie": logik.lernserie(user),
        "themen": logik.themen_statistik(user),
        "pruefung_ap1": date.fromisoformat(settings.AP1_DATUM),
        "laufende_sitzung": request.session.get(SITZUNG),
    }
    context["tage_bis_ap1"] = (context["pruefung_ap1"] - heute).days
    return render(request, "lernen/dashboard.html", context)


@login_required
def einstufung_start(request):
    if request.method == "POST":
        return _starte(request, Versuch.Quelle.EINSTUFUNG, logik.einstufung_fragen())
    anzahl = Frage.objects.filter(aktiv=True, einstufung=True, thema__pruefung="AP1").count()
    return render(request, "lernen/einstufung_start.html", {"anzahl": anzahl})


@login_required
@require_POST
def taeglich_start(request):
    return _starte(request, Versuch.Quelle.TAEGLICH, logik.tagesfragen(request.user))


@login_required
@require_POST
def thema_start(request, slug):
    thema = get_object_or_404(Thema, slug=slug)
    return _starte(request, Versuch.Quelle.THEMA, logik.themen_training(thema), f"Training: {thema.name}")


@login_required
def sitzung(request):
    s = request.session.get(SITZUNG)
    if not s:
        return redirect("dashboard")
    if s["pos"] >= len(s["ids"]):
        return redirect("sitzung_ende")

    frage = get_object_or_404(Frage.objects.select_related("thema"), id=s["ids"][s["pos"]])

    if request.method == "POST":
        aktion = request.POST.get("aktion")
        if aktion == "antworten" and s["beantwortet"] is None:
            richtig, eingabe = logik.pruefe_antwort(frage, request.POST)
            logik.karte_aktualisieren(request.user, frage, richtig, s["art"], eingabe)
            s["beantwortet"] = {"richtig": richtig, "eingabe": eingabe}
            s["richtig"] += int(richtig)
            s["ergebnisse"].append({"thema": frage.thema.name, "richtig": richtig})
        elif aktion == "weiter" and s["beantwortet"] is not None:
            s["pos"] += 1
            s["beantwortet"] = None
        elif aktion == "abbrechen":
            s["ids"] = s["ids"][: s["pos"] + (1 if s["beantwortet"] is not None else 0)]
            s["pos"] = len(s["ids"])
        request.session[SITZUNG] = s
        return redirect("sitzung")

    antworten = list(frage.antworten.all())
    if frage.typ != Frage.Typ.ZAHL and not s["beantwortet"]:
        random.Random(f"{request.user.id}-{frage.id}-{s['pos']}").shuffle(antworten)
    gewaehlt = set()
    if s["beantwortet"] and frage.typ != Frage.Typ.ZAHL:
        gewaehlt = {int(x) for x in s["beantwortet"]["eingabe"].split(",") if x}
    return render(request, "lernen/frage.html", {
        "s": s, "frage": frage, "antworten": antworten, "gewaehlt": gewaehlt,
        "nummer": s["pos"] + 1, "gesamt": len(s["ids"]),
        "fortschritt": round(100 * s["pos"] / len(s["ids"])),
    })


@login_required
def sitzung_ende(request):
    s = request.session.get(SITZUNG)
    if not s:
        return redirect("dashboard")
    pro_thema: dict[str, list[int]] = {}
    for e in s["ergebnisse"]:
        z = pro_thema.setdefault(e["thema"], [0, 0])
        z[0] += int(e["richtig"])
        z[1] += 1
    themen = sorted(
        ({"name": k, "richtig": v[0], "gesamt": v[1], "quote": round(100 * v[0] / v[1])} for k, v in pro_thema.items()),
        key=lambda x: x["quote"],
    )
    beantwortet = len(s["ergebnisse"])
    context = {
        "s": s, "themen": themen, "beantwortet": beantwortet,
        "quote": round(100 * s["richtig"] / beantwortet) if beantwortet else 0,
    }
    if request.method == "POST":
        del request.session[SITZUNG]
        return redirect("dashboard")
    return render(request, "lernen/ende.html", context)

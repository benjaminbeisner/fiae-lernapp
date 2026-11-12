import random
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from accounts.models import Profil

from . import belohnung, logik
from .models import Abzeichen, Frage, Karte, Lektion, LektionGelesen, Lernzeit, PdfPruefung, Simulation, Thema, Versuch

SITZUNG = "lernsitzung"
MAX_SEK_FRAGE = 180
MAX_SEK_LEKTION = 300
SIM_FRAGEN = 40
SIM_MINUTEN = 60


def _profil(user) -> Profil:
    return Profil.objects.get_or_create(user=user)[0]


def _neue_abzeichen_melden(request):
    for a in belohnung.abzeichen_pruefen(request.user):
        messages.success(request, f"{a.symbol} Neues Abzeichen: {a.name}! {a.beschreibung}.")


def _starte(request, art: str, items: list[dict], titel: str):
    if not items:
        messages.info(request, "Gerade gibt es dafür keine passenden Inhalte. Schau später wieder vorbei.")
        return redirect("dashboard")
    request.session[SITZUNG] = {
        "art": art, "titel": titel, "items": items, "pos": 0, "richtig": 0,
        "beantwortet": None, "ergebnisse": [], "gezeigt": None, "lektionen": 0,
    }
    return redirect("sitzung")


def _sekunden_seit(iso, maximum):
    t = parse_datetime(iso) if iso else None
    if not t:
        return 0
    return int(min(max((timezone.now() - t).total_seconds(), 0), maximum))


@login_required
def dashboard(request):
    user = request.user
    heute = timezone.localdate()
    profil = _profil(user)
    level, xp_im_level, xp_level = belohnung.level_aus_xp(profil.xp)
    minuten = belohnung.minuten_heute(user)
    ziel = profil.tagesziel_minuten or 20
    themen = logik.themen_statistik(user)
    for z in themen:
        z["niveau"] = logik.niveau(user, z["thema"])
    pruefung = date.fromisoformat(settings.AP1_DATUM)
    context = {
        "profil": profil,
        "hat_einstufung": Versuch.objects.filter(user=user, quelle=Versuch.Quelle.EINSTUFUNG).exists(),
        "faellig": Karte.objects.filter(user=user, faellig_am__lte=heute, frage__aktiv=True).count(),
        "serie": logik.lernserie(user),
        "themen": themen,
        "tage_bis_ap1": (pruefung - heute).days,
        "laufende_sitzung": request.session.get(SITZUNG),
        "level": level, "xp_im_level": xp_im_level, "xp_level": xp_level,
        "xp_prozent": round(100 * xp_im_level / xp_level),
        "minuten": minuten, "ziel": ziel, "ziel_prozent": min(100, round(100 * minuten / ziel)),
        "letzte_abzeichen": [belohnung.ABZEICHEN_NACH_SCHLUESSEL[a] for a in
                              Abzeichen.objects.filter(user=user).order_by("-erhalten_am").values_list("schluessel", flat=True)[:4]
                              if a in belohnung.ABZEICHEN_NACH_SCHLUESSEL],
        "offene_simulation": Simulation.objects.filter(user=user, abgegeben__isnull=True, frist__gt=timezone.now()).first(),
    }
    return render(request, "lernen/dashboard.html", context)


@login_required
def einstufung_start(request):
    if request.method == "POST":
        return _starte(request, Versuch.Quelle.EINSTUFUNG, logik.einstufung_fragen(), "Einstufungstest")
    anzahl = Frage.objects.filter(aktiv=True, einstufung=True, thema__pruefung="AP1").count()
    return render(request, "lernen/einstufung_start.html", {"anzahl": anzahl})


@login_required
@require_POST
def taeglich_start(request):
    items, titel = logik.tagesnugget(request.user)
    return _starte(request, Versuch.Quelle.TAEGLICH, items, titel)


@login_required
@require_POST
def thema_start(request, slug):
    thema = get_object_or_404(Thema, slug=slug)
    return _starte(request, Versuch.Quelle.THEMA, logik.themen_training(request.user, thema), f"Training: {thema.name}")


@login_required
@require_POST
def lektion_start(request, pk):
    lektion = get_object_or_404(Lektion, pk=pk, aktiv=True)
    return _starte(request, Versuch.Quelle.THEMA, logik.lektion_items(request.user, lektion), f"Lernnugget: {lektion.titel}")


@login_required
@require_POST
def wiederholung_start(request):
    return _starte(request, Versuch.Quelle.WIEDERHOLUNG, logik.wiederholung(request.user), "Wiederholung")


@login_required
def thema_detail(request, slug):
    thema = get_object_or_404(Thema, slug=slug)
    gelesen = set(LektionGelesen.objects.filter(user=request.user).values_list("lektion_id", flat=True))
    lektionen = []
    for l in thema.lektionen.filter(aktiv=True):
        fest, gesamt = logik.lektion_fortschritt(request.user, l)
        lektionen.append({"l": l, "gelesen": l.id in gelesen, "fragen": gesamt, "fest": fest,
                          "prozent": round(100 * fest / gesamt) if gesamt else 0})
    stat = next((z for z in logik.themen_statistik(request.user) if z["thema"].id == thema.id), None)
    return render(request, "lernen/thema.html", {
        "thema": thema, "lektionen": lektionen, "stat": stat, "niveau": logik.niveau(request.user, thema)})


@login_required
def sitzung(request):
    s = request.session.get(SITZUNG)
    if not s or "items" not in s:
        request.session.pop(SITZUNG, None)
        return redirect("dashboard")
    if s["pos"] >= len(s["items"]):
        return redirect("sitzung_ende")
    item = s["items"][s["pos"]]

    if item["t"] == "lektion":
        lektion = get_object_or_404(Lektion.objects.select_related("thema"), id=item["id"])
        if request.method == "POST":
            if request.POST.get("aktion") == "abbrechen":
                s["items"] = s["items"][: s["pos"]]
            else:
                dauer = _sekunden_seit(s.get("gezeigt"), MAX_SEK_LEKTION)
                _, neu = LektionGelesen.objects.get_or_create(user=request.user, lektion=lektion)
                if neu:
                    belohnung.xp_gutschreiben(request.user, belohnung.XP_LEKTION)
                belohnung.lernzeit_buchen(request.user, dauer)
                s["lektionen"] += 1
                s["pos"] += 1
            s["gezeigt"] = None
            request.session[SITZUNG] = s
            return redirect("sitzung")
        if not s.get("gezeigt"):
            s["gezeigt"] = timezone.now().isoformat()
            request.session[SITZUNG] = s
        return render(request, "lernen/lektion.html", _fortschritt(s) | {"s": s, "lektion": lektion})

    frage = get_object_or_404(Frage.objects.select_related("thema", "lektion"), id=item["id"])

    if request.method == "POST":
        aktion = request.POST.get("aktion")
        if aktion == "antworten" and s["beantwortet"] is None:
            richtig, eingabe = logik.pruefe_antwort(frage, request.POST)
            dauer = _sekunden_seit(s.get("gezeigt"), MAX_SEK_FRAGE)
            logik.karte_aktualisieren(request.user, frage, richtig, s["art"], eingabe, dauer)
            s["beantwortet"] = {"richtig": richtig, "eingabe": eingabe}
            s["richtig"] += int(richtig)
            s["ergebnisse"].append({"thema": frage.thema.name, "richtig": richtig})
        elif aktion == "weiter" and s["beantwortet"] is not None:
            s["pos"] += 1
            s["beantwortet"] = None
            s["gezeigt"] = None
        elif aktion == "abbrechen":
            s["items"] = s["items"][: s["pos"] + (1 if s["beantwortet"] is not None else 0)]
            s["pos"] = len(s["items"])
        request.session[SITZUNG] = s
        return redirect("sitzung")

    if not s.get("gezeigt") and s["beantwortet"] is None:
        s["gezeigt"] = timezone.now().isoformat()
        request.session[SITZUNG] = s
    antworten = list(frage.antworten.all())
    if frage.typ != Frage.Typ.ZAHL:
        random.Random(f"{request.user.id}-{frage.id}-{s['pos']}").shuffle(antworten)
    gewaehlt = set()
    if s["beantwortet"] and frage.typ != Frage.Typ.ZAHL:
        gewaehlt = {int(x) for x in s["beantwortet"]["eingabe"].split(",") if x}
    return render(request, "lernen/frage.html", _fortschritt(s) | {
        "s": s, "frage": frage, "antworten": antworten, "gewaehlt": gewaehlt})


def _fortschritt(s):
    return {"nummer": s["pos"] + 1, "gesamt": len(s["items"]), "fortschritt": round(100 * s["pos"] / max(len(s["items"]), 1))}


@login_required
def sitzung_ende(request):
    s = request.session.get(SITZUNG)
    if not s:
        return redirect("dashboard")
    if request.method == "POST":
        del request.session[SITZUNG]
        return redirect("dashboard")
    if not s.get("abzeichen_geprueft"):
        _neue_abzeichen_melden(request)
        s["abzeichen_geprueft"] = True
        request.session[SITZUNG] = s
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
    return render(request, "lernen/ende.html", {
        "s": s, "themen": themen, "beantwortet": beantwortet,
        "quote": round(100 * s["richtig"] / beantwortet) if beantwortet else 0,
        "xp": s["richtig"] * belohnung.XP_RICHTIG + (beantwortet - s["richtig"]) * belohnung.XP_FALSCH + s.get("lektionen", 0) * belohnung.XP_LEKTION,
        "minuten": belohnung.minuten_heute(request.user), "ziel": _profil(request.user).tagesziel_minuten,
    })


# ---------- Prüfungssimulation ----------

@login_required
def simulation_start(request):
    offen = Simulation.objects.filter(user=request.user, abgegeben__isnull=True, frist__gt=timezone.now()).first()
    if request.method == "POST":
        if offen:
            return redirect("simulation", pk=offen.pk)
        ids = logik.simulation_fragen(SIM_FRAGEN)
        if not ids:
            messages.info(request, "Es gibt noch keine Fragen für die Simulation.")
            return redirect("dashboard")
        sim = Simulation.objects.create(user=request.user, fragen_ids=ids,
                                        frist=timezone.now() + timedelta(minutes=SIM_MINUTEN))
        return redirect("simulation", pk=sim.pk)
    bisher = Simulation.objects.filter(user=request.user, abgegeben__isnull=False)[:10]
    return render(request, "lernen/simulation_start.html", {
        "offen": offen, "bisher": bisher, "anzahl": SIM_FRAGEN, "minuten": SIM_MINUTEN,
        "pdf_bisher": PdfPruefung.objects.filter(user=request.user)[:10]})


@login_required
def simulation(request, pk):
    sim = get_object_or_404(Simulation, pk=pk, user=request.user)
    if sim.abgegeben:
        return redirect("simulation_ergebnis", pk=sim.pk)
    fragen = {f.id: f for f in Frage.objects.filter(id__in=sim.fragen_ids).select_related("thema").prefetch_related("antworten")}
    liste = [fragen[i] for i in sim.fragen_ids if i in fragen]

    if request.method == "POST":
        aktion = request.POST.get("aktion", "speichern")
        antworten = {}
        for f in liste:
            if f.typ == Frage.Typ.ZAHL:
                antworten[str(f.id)] = request.POST.get(f"f{f.id}-zahl", "").strip()[:50]
            else:
                antworten[str(f.id)] = [x for x in request.POST.getlist(f"f{f.id}") if x.isdigit()]
        sim.antworten = antworten
        if aktion == "abgeben" or timezone.now() > sim.frist:
            _simulation_auswerten(request, sim, liste)
            return redirect("simulation_ergebnis", pk=sim.pk)
        sim.save(update_fields=["antworten"])
        messages.info(request, "Zwischenstand gespeichert.")
        return redirect("simulation", pk=sim.pk)

    for f in liste:
        f.gemischt = list(f.antworten.all())
        random.Random(f"sim{sim.pk}-{f.id}").shuffle(f.gemischt)
        a = sim.antworten.get(str(f.id))
        f.gewaehlt = {int(x) for x in a} if isinstance(a, list) else set()
        f.zahl_wert = a if isinstance(a, str) else ""
        f.p = logik.punkte_fuer(f)
    return render(request, "lernen/simulation.html", {
        "sim": sim, "fragen": liste, "rest_sek": max(0, int((sim.frist - timezone.now()).total_seconds()))})


class _Daten(dict):
    """Minimaler Ersatz für request.POST, damit pruefe_antwort wiederverwendet werden kann."""

    def getlist(self, key):
        v = self.get(key, [])
        return v if isinstance(v, list) else [v]


def _simulation_auswerten(request, sim, liste):
    erreicht = gesamt = 0
    for f in liste:
        a = sim.antworten.get(str(f.id))
        p = logik.punkte_fuer(f)
        gesamt += p
        if a in (None, "", []):
            richtig, eingabe = False, ""
        elif f.typ == Frage.Typ.ZAHL:
            richtig, eingabe = logik.pruefe_antwort(f, _Daten(zahl=a))
        else:
            richtig, eingabe = logik.pruefe_antwort(f, _Daten(antwort=a))
        erreicht += p if richtig else 0
        logik.karte_aktualisieren(request.user, f, richtig, Versuch.Quelle.PRUEFUNG, eingabe)
    sim.punkte = round(100 * erreicht / gesamt, 1) if gesamt else 0
    sim.punkte_max = 100
    sim.abgegeben = timezone.now()
    sim.save()
    sekunden = int(min((sim.abgegeben - sim.start).total_seconds(), SIM_MINUTEN * 60))
    belohnung.lernzeit_buchen(request.user, sekunden)
    belohnung.xp_gutschreiben(request.user, belohnung.XP_SIMULATION)
    _neue_abzeichen_melden(request)


@login_required
def simulation_ergebnis(request, pk):
    sim = get_object_or_404(Simulation, pk=pk, user=request.user, abgegeben__isnull=False)
    fragen = {f.id: f for f in Frage.objects.filter(id__in=sim.fragen_ids).select_related("thema").prefetch_related("antworten")}
    zeilen, pro_thema = [], {}
    for i in sim.fragen_ids:
        f = fragen.get(i)
        if not f:
            continue
        a = sim.antworten.get(str(i))
        if f.typ == Frage.Typ.ZAHL:
            richtig = bool(a) and logik.pruefe_antwort(f, _Daten(zahl=a))[0]
            gewaehlt = set()
        else:
            gewaehlt = {int(x) for x in a} if isinstance(a, list) else set()
            richtig = bool(gewaehlt) and logik.pruefe_antwort(f, _Daten(antwort=[str(x) for x in gewaehlt]))[0]
        zeilen.append({"f": f, "richtig": richtig, "gewaehlt": gewaehlt, "eingabe": a if isinstance(a, str) else "",
                       "p": logik.punkte_fuer(f)})
        t = pro_thema.setdefault(f.thema.name, [0, 0])
        t[0] += richtig
        t[1] += 1
    themen = sorted(({"name": k, "richtig": v[0], "gesamt": v[1], "quote": round(100 * v[0] / v[1])} for k, v in pro_thema.items()),
                    key=lambda x: x["quote"])
    return render(request, "lernen/simulation_ergebnis.html", {"sim": sim, "zeilen": zeilen, "themen": themen})


# ---------- Rangliste, Abzeichen, Profil ----------

@login_required
def rangliste(request):
    zeitraum = request.GET.get("zeitraum", "woche")
    heute = timezone.localdate()
    if zeitraum == "heute":
        ab, titel = heute, "Heute"
    elif zeitraum == "monat":
        ab, titel = heute.replace(day=1), "Dieser Monat"
    else:
        zeitraum, ab, titel = "woche", belohnung.wochenbeginn(heute), "Diese Woche"
    summen = (Lernzeit.objects.filter(datum__gte=ab, user__is_active=True).exclude(user__profil__in_rangliste=False)
              .values("user", "user__first_name", "user__username", "user__profil__anzeigename")
              .annotate(s=Sum("sekunden")).order_by("-s"))
    zeilen = []
    for platz, z in enumerate(summen, start=1):
        zeilen.append({
            "platz": platz,
            "name": z["user__profil__anzeigename"] or z["user__first_name"] or z["user__username"],
            "minuten": z["s"] // 60,
            "ich": z["user"] == request.user.id,
        })
    maximum = max((z["minuten"] for z in zeilen), default=0) or 1
    for z in zeilen:
        z["balken"] = round(100 * z["minuten"] / maximum)
    return render(request, "lernen/rangliste.html", {
        "zeilen": zeilen, "zeitraum": zeitraum, "titel": titel, "sichtbar": _profil(request.user).in_rangliste})


@login_required
def abzeichen(request):
    erhalten = dict(Abzeichen.objects.filter(user=request.user).values_list("schluessel", "erhalten_am"))
    liste = [{"a": a, "am": erhalten.get(a.schluessel)} for a in belohnung.ABZEICHEN]
    profil = _profil(request.user)
    level, xp_im_level, xp_level = belohnung.level_aus_xp(profil.xp)
    themen = [{"key": k, "name": n, "ab": lv, "frei": level >= lv} for k, n, lv in belohnung.FARBTHEMEN]
    return render(request, "lernen/abzeichen.html", {
        "liste": liste, "anzahl": len(erhalten), "level": level, "profil": profil, "farbthemen": themen,
        "xp_im_level": xp_im_level, "xp_level": xp_level})


# ---------- Übungsprüfung als PDF ----------

@login_required
@require_POST
def pdf_pruefung_neu(request):
    benutzt = set(PdfPruefung.objects.values_list("seed", flat=True))
    rng = random.SystemRandom()
    seed = rng.randint(1, 999_999)
    while seed in benutzt:
        seed = rng.randint(1, 999_999)
    pp = PdfPruefung.objects.create(user=request.user, seed=seed)
    return redirect("pdf_pruefung", pk=pp.pk)


@login_required
def pdf_pruefung(request, pk):
    pp = get_object_or_404(PdfPruefung, pk=pk, user=request.user)
    if request.method == "POST":
        try:
            werte = [int(request.POST.get(f"a{i}", "")) for i in range(1, 5)]
        except ValueError:
            werte = None
        if not werte or any(not 0 <= w <= 25 for w in werte):
            messages.error(request, "Bitte für jede Aufgabe eine ganze Zahl von 0 bis 25 eintragen.")
        else:
            erstes_mal = pp.punkte is None
            pp.punkte, pp.bewertet_am = werte, timezone.now()
            pp.save()
            if erstes_mal:
                belohnung.xp_gutschreiben(request.user, belohnung.XP_SIMULATION)
            messages.success(request, f"Gespeichert: {pp.gesamt} von 100 Punkten, Note {pp.note}.")
            return redirect("pdf_pruefung", pk=pp.pk)
    return render(request, "lernen/pdf_pruefung.html", {"pp": pp, "aufgaben": range(1, 5)})


@login_required
def pdf_pruefung_datei(request, pk, art):
    from django.http import HttpResponse

    from .pruefung import pdf, zusammenstellen

    if art not in ("aufgaben", "loesung"):
        from django.http import Http404
        raise Http404
    pp = get_object_or_404(PdfPruefung, pk=pk, user=request.user)
    daten = zusammenstellen.pruefung(pp.seed)
    inhalt = pdf.aufgaben_pdf(daten) if art == "aufgaben" else pdf.loesung_pdf(daten)
    name = f"Uebungspruefung_AP1_{pp.nummer}{'_Loesung' if art == 'loesung' else ''}.pdf"
    antwort = HttpResponse(inhalt, content_type="application/pdf")
    antwort["Content-Disposition"] = f'attachment; filename="{name}"'
    return antwort

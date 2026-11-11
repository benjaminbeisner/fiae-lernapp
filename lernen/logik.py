"""Lernlogik: Antworten prüfen, Lernsitzungen zusammenstellen, Statistik."""

import random
import re
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone

from .models import Frage, Karte, Thema, Versuch


def zahl_lesen(text: str) -> Decimal:
    """Liest Zahlen in deutscher oder englischer Schreibweise: 1.234,5 / 1234.5 / 1 234"""
    s = text.strip().replace(" ", "").replace("\u00a0", "").replace("€", "").replace("%", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    return Decimal(s)


def pruefe_antwort(frage: Frage, daten) -> tuple[bool, str]:
    """Gibt (richtig, eingabe als Text) zurück. `daten` ist request.POST."""
    if frage.typ == Frage.Typ.ZAHL:
        roh = daten.get("zahl") or ""
        try:
            wert = zahl_lesen(roh)
        except (InvalidOperation, ValueError):
            return False, roh[:200]
        return abs(wert - frage.loesung_zahl) <= frage.toleranz, roh.strip()[:200]

    gewaehlt = {int(x) for x in daten.getlist("antwort") if x.isdigit()}
    richtige = set(frage.antworten.filter(richtig=True).values_list("id", flat=True))
    return gewaehlt == richtige, ",".join(str(i) for i in sorted(gewaehlt))


def karte_aktualisieren(user, frage: Frage, richtig: bool, quelle: str, eingabe: str = "") -> Karte:
    karte, _ = Karte.objects.get_or_create(user=user, frage=frage)
    karte.bewerten(richtig)
    karte.save()
    Versuch.objects.create(user=user, frage=frage, quelle=quelle, richtig=richtig, eingabe=eingabe)
    return karte


def einstufung_fragen() -> list[int]:
    """Alle Einstufungsfragen, nach Themen gruppiert, innerhalb des Themas gemischt."""
    ids = []
    for thema in Thema.objects.filter(pruefung="AP1"):
        teil = list(thema.fragen.filter(aktiv=True, einstufung=True).values_list("id", flat=True))
        random.shuffle(teil)
        ids.extend(teil)
    return ids


def themen_quoten(user, pruefung: str = "AP1") -> dict[int, float]:
    """Wie dringend jedes Thema geübt werden sollte: Prüfungsgewicht x Schwäche."""
    seit = timezone.now() - timedelta(days=60)
    stat = (
        Versuch.objects.filter(user=user, zeitpunkt__gte=seit, frage__thema__pruefung=pruefung)
        .values("frage__thema")
        .annotate(n=Count("id"), r=Count("id", filter=Q(richtig=True)))
    )
    quote = {s["frage__thema"]: s["r"] / s["n"] for s in stat if s["n"]}
    ergebnis = {}
    for thema in Thema.objects.filter(pruefung=pruefung):
        schwaeche = 1.0 - quote.get(thema.id, 0.5)  # unbekannt = mittel
        ergebnis[thema.id] = thema.gewicht * (0.3 + schwaeche)
    return ergebnis


def tagesfragen(user, pruefung: str = "AP1") -> list[int]:
    """Fällige Wiederholungen zuerst, danach neue Fragen nach Gewicht und Schwäche."""
    heute = timezone.localdate()
    faellig = list(
        Karte.objects.filter(user=user, faellig_am__lte=heute, frage__aktiv=True, frage__thema__pruefung=pruefung)
        .order_by("faellig_am", "box")
        .values_list("frage_id", flat=True)[: settings.DAILY_REVIEW_LIMIT]
    )
    bekannt = Karte.objects.filter(user=user).values_list("frage_id", flat=True)
    neu_pool = defaultdict(list)
    for fid, tid in Frage.objects.filter(aktiv=True, thema__pruefung=pruefung).exclude(id__in=bekannt).values_list("id", "thema_id"):
        neu_pool[tid].append(fid)
    for liste in neu_pool.values():
        random.shuffle(liste)

    quoten = themen_quoten(user, pruefung)
    neu = []
    while len(neu) < settings.DAILY_NEW_QUESTIONS and any(neu_pool.values()):
        themen = [t for t, l in neu_pool.items() if l]
        gewichte = [quoten.get(t, 1.0) for t in themen]
        t = random.choices(themen, weights=gewichte, k=1)[0]
        neu.append(neu_pool[t].pop())

    ids = faellig + neu
    random.shuffle(ids)
    return ids


def themen_training(thema: Thema, anzahl: int = 10) -> list[int]:
    ids = list(thema.fragen.filter(aktiv=True).values_list("id", flat=True))
    random.shuffle(ids)
    return ids[:anzahl]


def themen_statistik(user, pruefung: str = "AP1") -> list[dict]:
    """Pro Thema: Trefferquote (alle Versuche) und gefestigte Fragen (Box >= 4)."""
    versuche = {
        s["frage__thema"]: s
        for s in Versuch.objects.filter(user=user, frage__thema__pruefung=pruefung)
        .values("frage__thema")
        .annotate(n=Count("id"), r=Count("id", filter=Q(richtig=True)))
    }
    gefestigt = dict(
        Karte.objects.filter(user=user, box__gte=4, frage__thema__pruefung=pruefung)
        .values("frage__thema").annotate(n=Count("id")).values_list("frage__thema", "n")
    )
    zeilen = []
    for thema in Thema.objects.filter(pruefung=pruefung).annotate(anzahl=Count("fragen", filter=Q(fragen__aktiv=True))):
        v = versuche.get(thema.id)
        quote = round(100 * v["r"] / v["n"]) if v and v["n"] else None
        zeilen.append({
            "thema": thema,
            "versuche": v["n"] if v else 0,
            "quote": quote,
            "gefestigt": gefestigt.get(thema.id, 0),
            "anzahl": thema.anzahl,
            "fortschritt": round(100 * gefestigt.get(thema.id, 0) / thema.anzahl) if thema.anzahl else 0,
        })
    return zeilen


def lernserie(user) -> int:
    """Wie viele Tage in Folge (bis heute oder gestern) gelernt wurde."""
    tage = set(
        timezone.localtime(z).date()
        for z in Versuch.objects.filter(user=user, zeitpunkt__gte=timezone.now() - timedelta(days=400)).values_list("zeitpunkt", flat=True)
    )
    tag = timezone.localdate()
    if tag not in tage:
        tag -= timedelta(days=1)
    serie = 0
    while tag in tage:
        serie += 1
        tag -= timedelta(days=1)
    return serie

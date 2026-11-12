"""Lernlogik: Antworten prüfen, Lernsitzungen zusammenstellen, Statistik."""

import random
import re
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone

from .models import Frage, Karte, Lektion, LektionGelesen, Thema, Versuch


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


def karte_aktualisieren(user, frage: Frage, richtig: bool, quelle: str, eingabe: str = "", dauer: int = 0) -> Karte:
    from .belohnung import XP_FALSCH, XP_RICHTIG, lernzeit_buchen, xp_gutschreiben

    karte, _ = Karte.objects.get_or_create(user=user, frage=frage)
    karte.bewerten(richtig)
    karte.save()
    Versuch.objects.create(user=user, frage=frage, quelle=quelle, richtig=richtig, eingabe=eingabe, dauer_sek=dauer)
    xp_gutschreiben(user, XP_RICHTIG if richtig else XP_FALSCH)
    lernzeit_buchen(user, dauer)
    return karte


def einstufung_fragen() -> list[dict]:
    """Alle Einstufungsfragen, nach Themen gruppiert, innerhalb des Themas gemischt."""
    ids = []
    for thema in Thema.objects.filter(pruefung="AP1"):
        teil = list(thema.fragen.filter(aktiv=True, einstufung=True).values_list("id", flat=True))
        random.shuffle(teil)
        ids.extend(teil)
    return [{"t": "frage", "id": i} for i in ids]


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


def niveau(user, thema) -> int:
    """Wissensstand in einem Thema: 1 = Grundlagen, 2 = Aufbau, 3 = Prüfungsniveau."""
    letzte = list(
        Versuch.objects.filter(user=user, frage__thema=thema).order_by("-zeitpunkt").values_list("richtig", flat=True)[:20]
    )
    if len(letzte) < 4:
        return 1
    quote = sum(letzte) / len(letzte)
    return 1 if quote < 0.6 else 2 if quote < 0.85 else 3


def _passend_zum_niveau(fragen: list[Frage], stufe: int, anzahl: int, gesperrt=None) -> list[Frage]:
    """Zieht Fragen gewichtet (gleiche Schwierigkeit wie das Niveau bevorzugt).
    Von Varianten derselben Aufgabenvorlage (gruppe) kommt nur eine."""
    gesperrt = set(gesperrt or ())
    pool = [f for f in fragen if not f.gruppe or f.gruppe not in gesperrt]
    auswahl = []
    while pool and len(auswahl) < anzahl:
        gewichte = [3.0 if f.schwierigkeit == stufe else 1.0 if abs(f.schwierigkeit - stufe) == 1 else 0.3 for f in pool]
        f = random.choices(pool, weights=gewichte, k=1)[0]
        auswahl.append(f)
        if f.gruppe:
            gesperrt.add(f.gruppe)
            pool = [x for x in pool if x.gruppe != f.gruppe]
        else:
            pool.remove(f)
    return auswahl


def lektion_fortschritt(user, lektion) -> tuple[int, int]:
    """(gefestigte Fragen, Fragen gesamt) einer Lektion."""
    gesamt = lektion.fragen.filter(aktiv=True).count()
    fest = Karte.objects.filter(user=user, frage__lektion=lektion, frage__aktiv=True, box__gte=4).count()
    return fest, gesamt


def naechste_lektion(user, thema) -> Lektion | None:
    """Erst ungelesene Abschnitte passend zum Niveau, danach den am wenigsten gefestigten."""
    gelesen = set(LektionGelesen.objects.filter(user=user).values_list("lektion_id", flat=True))
    stufe = niveau(user, thema)
    alle = list(thema.lektionen.filter(aktiv=True).order_by("stufe", "reihenfolge"))
    offen = [l for l in alle if l.id not in gelesen]
    for l in offen:
        if l.stufe <= stufe + 1:
            return l
    if offen:
        return offen[0]
    if not alle:
        return None

    def quote(l):
        fest, gesamt = lektion_fortschritt(user, l)
        return fest / gesamt if gesamt else 1
    return min(alle, key=lambda l: (quote(l), random.random()))


def lektion_fragen(user, lektion, anzahl: int = 8) -> list[int]:
    """Fragen genau zu diesem Abschnitt: zuerst neue, dann fällige, dann am wenigsten gefestigte."""
    fragen = list(lektion.fragen.filter(aktiv=True))
    karten = {k.frage_id: k for k in Karte.objects.filter(user=user, frage__in=fragen)}
    stufe = niveau(user, lektion.thema)
    heute = timezone.localdate()
    neu = [f for f in fragen if f.id not in karten]
    faellig = [f for f in fragen if f.id in karten and karten[f.id].faellig_am <= heute]
    rest = sorted((f for f in fragen if f.id in karten and karten[f.id].faellig_am > heute),
                  key=lambda f: (karten[f.id].box, karten[f.id].faellig_am))
    auswahl = _passend_zum_niveau(neu, stufe, anzahl)
    gruppen = {f.gruppe for f in auswahl if f.gruppe}
    if len(auswahl) < anzahl:
        auswahl += _passend_zum_niveau(faellig, stufe, anzahl - len(auswahl), gruppen)
        gruppen |= {f.gruppe for f in auswahl if f.gruppe}
    for f in rest:
        if len(auswahl) >= anzahl:
            break
        if f not in auswahl and (not f.gruppe or f.gruppe not in gruppen):
            auswahl.append(f)
            if f.gruppe:
                gruppen.add(f.gruppe)
    random.shuffle(auswahl)
    return [f.id for f in auswahl]


def tagesnugget(user, pruefung: str = "AP1") -> tuple[list[dict], str]:
    """Das tägliche Lernnugget: ein Abschnitt im dringendsten Thema wird erklärt,
    danach kommen ausschließlich Fragen zu genau diesem Abschnitt."""
    quoten = themen_quoten(user, pruefung)
    themen = list(Thema.objects.filter(pruefung=pruefung, id__in=quoten))
    random.shuffle(themen)
    themen.sort(key=lambda t: -quoten[t.id] * random.uniform(0.7, 1.3))
    for thema in themen:
        lektion = naechste_lektion(user, thema)
        if lektion and lektion.fragen.filter(aktiv=True).exists():
            return lektion_items(user, lektion), f"Lernnugget: {lektion.titel}"
    return [], "Lernnugget"


def lektion_items(user, lektion, anzahl: int = 8) -> list[dict]:
    return [{"t": "lektion", "id": lektion.id}] + [{"t": "frage", "id": i} for i in lektion_fragen(user, lektion, anzahl)]


def wiederholung(user, anzahl: int = 20, pruefung: str = "AP1") -> list[dict]:
    """Fällige Karten (verteilte Wiederholung), eine Variante pro Aufgabenvorlage."""
    heute = timezone.localdate()
    karten = (Karte.objects.filter(user=user, faellig_am__lte=heute, frage__aktiv=True, frage__thema__pruefung=pruefung)
              .select_related("frage").order_by("faellig_am", "box"))
    ids, gruppen = [], set()
    for k in karten:
        if len(ids) >= anzahl:
            break
        g = k.frage.gruppe
        if g and g in gruppen:
            continue
        gruppen.add(g)
        ids.append(k.frage_id)
    random.shuffle(ids)
    return [{"t": "frage", "id": i} for i in ids]


def tagesfragen(user, pruefung: str = "AP1") -> list[int]:
    """Nur die Frage-IDs des Tagesnuggets (für Tests und einfache Aufrufe)."""
    return [i["id"] for i in tagesnugget(user, pruefung)[0] if i["t"] == "frage"]


def themen_training(user, thema: Thema, anzahl: int = 10) -> list[dict]:
    """Gemischte Fragen aus dem ganzen Thema, passend zum Niveau, ohne doppelte Vorlagen."""
    fragen = _passend_zum_niveau(list(thema.fragen.filter(aktiv=True)), niveau(user, thema), anzahl)
    return [{"t": "frage", "id": f.id} for f in fragen]


def simulation_fragen(anzahl: int = 40, pruefung: str = "AP1") -> list[int]:
    """Fragen für die Prüfungssimulation, verteilt nach Prüfungsgewicht der Themen."""
    themen = list(Thema.objects.filter(pruefung=pruefung))
    summe = sum(t.gewicht for t in themen) or 1
    ids = []
    for t in themen:
        n = max(1, round(anzahl * t.gewicht / summe))
        pool = list(t.fragen.filter(aktiv=True))
        # gemischte Schwierigkeit, eher anspruchsvoll, keine zwei Varianten derselben Vorlage
        ids += [f.id for f in _passend_zum_niveau(pool, 2, n)]
    random.shuffle(ids)
    return ids[:anzahl]


def punkte_fuer(frage: Frage) -> int:
    return frage.punkte or {1: 2, 2: 3, 3: 4}.get(frage.schwierigkeit, 3)


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

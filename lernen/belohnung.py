"""Erfahrungspunkte, Level, freischaltbare Farbthemen und Abzeichen."""

from dataclasses import dataclass
from datetime import timedelta
from typing import Callable

from django.db.models import Sum
from django.utils import timezone

XP_RICHTIG = 10
XP_FALSCH = 3
XP_LEKTION = 15
XP_SIMULATION = 50


def level_aus_xp(xp: int) -> tuple[int, int, int]:
    """(Level, XP im aktuellen Level, XP bis zum nächsten Level). Level n+1 braucht n*100 XP mehr."""
    level, schwelle = 1, 0
    while xp >= schwelle + level * 100:
        schwelle += level * 100
        level += 1
    return level, xp - schwelle, level * 100


# Farbthemen, die mit dem Level freigeschaltet werden
FARBTHEMEN = [
    ("standard", "Standard", 1),
    ("ozean", "Ozean", 2),
    ("wald", "Wald", 3),
    ("sonnenuntergang", "Sonnenuntergang", 5),
    ("terminal", "Terminal", 7),
    ("galaxie", "Galaxie", 10),
]


def xp_gutschreiben(user, menge: int) -> None:
    from accounts.models import Profil
    profil, _ = Profil.objects.get_or_create(user=user)
    profil.xp += menge
    profil.save(update_fields=["xp"])


def lernzeit_buchen(user, sekunden: int) -> None:
    from .models import Lernzeit
    if sekunden <= 0:
        return
    eintrag, _ = Lernzeit.objects.get_or_create(user=user, datum=timezone.localdate())
    eintrag.sekunden += sekunden
    eintrag.save(update_fields=["sekunden"])


def minuten_heute(user) -> int:
    from .models import Lernzeit
    e = Lernzeit.objects.filter(user=user, datum=timezone.localdate()).first()
    return (e.sekunden // 60) if e else 0


def wochenbeginn(tag=None):
    tag = tag or timezone.localdate()
    return tag - timedelta(days=tag.weekday())


@dataclass
class AbzeichenDef:
    schluessel: str
    symbol: str
    name: str
    beschreibung: str
    pruefen: Callable[[dict], bool]


def _statistik(user) -> dict:
    from accounts.models import Profil
    from .logik import lernserie, themen_statistik
    from .models import LektionGelesen, Lernzeit, Simulation, Versuch

    versuche = Versuch.objects.filter(user=user)
    profil = Profil.objects.filter(user=user).first()
    sims = Simulation.objects.filter(user=user, abgegeben__isnull=False)
    stunden = [timezone.localtime(z).hour for z in versuche.order_by("-zeitpunkt").values_list("zeitpunkt", flat=True)[:200]]
    themen = themen_statistik(user)
    return {
        "versuche": versuche.count(),
        "richtig": versuche.filter(richtig=True).count(),
        "einstufung": versuche.filter(quelle="einstufung").exists(),
        "serie": lernserie(user),
        "lektionen": LektionGelesen.objects.filter(user=user).count(),
        "sim_beste": max((s.prozent or 0 for s in sims), default=None),
        "frueh": any(h < 8 for h in stunden),
        "spaet": any(h >= 22 for h in stunden),
        "woche_min": (Lernzeit.objects.filter(user=user, datum__gte=wochenbeginn()).aggregate(s=Sum("sekunden"))["s"] or 0) // 60,
        "heute_min": minuten_heute(user),
        "tagesziel": profil.tagesziel_minuten if profil else 20,
        "thema_gefestigt": any(t["anzahl"] and t["fortschritt"] >= 80 for t in themen),
        "alle_themen_geuebt": all(t["versuche"] > 0 for t in themen if t["anzahl"]),
    }


ABZEICHEN = [
    AbzeichenDef("start", "🚀", "Losgelegt", "Die erste Frage beantwortet", lambda s: s["versuche"] >= 1),
    AbzeichenDef("einstufung", "🧭", "Standort bestimmt", "Den Einstufungstest gemacht", lambda s: s["einstufung"]),
    AbzeichenDef("tagesziel", "🎯", "Ziel erreicht", "Das Tagesziel an einem Tag geschafft", lambda s: s["heute_min"] >= s["tagesziel"]),
    AbzeichenDef("serie3", "🔥", "Warmgelaufen", "3 Tage in Folge gelernt", lambda s: s["serie"] >= 3),
    AbzeichenDef("serie7", "🔥", "Eine Woche dran", "7 Tage in Folge gelernt", lambda s: s["serie"] >= 7),
    AbzeichenDef("serie30", "🏆", "Eiserne Disziplin", "30 Tage in Folge gelernt", lambda s: s["serie"] >= 30),
    AbzeichenDef("fragen100", "💯", "Hundert", "100 Fragen beantwortet", lambda s: s["versuche"] >= 100),
    AbzeichenDef("fragen500", "📚", "Vielleser", "500 Fragen beantwortet", lambda s: s["versuche"] >= 500),
    AbzeichenDef("fragen1000", "🧠", "Wissensspeicher", "1.000 Fragen beantwortet", lambda s: s["versuche"] >= 1000),
    AbzeichenDef("lektionen10", "📖", "Wissbegierig", "10 Lernnuggets gelesen", lambda s: s["lektionen"] >= 10),
    AbzeichenDef("allrounder", "🌐", "Allrounder", "In jedem Thema mindestens eine Frage geübt", lambda s: s["alle_themen_geuebt"]),
    AbzeichenDef("meister", "🥇", "Themenprofi", "80 % eines Themas gefestigt", lambda s: s["thema_gefestigt"]),
    AbzeichenDef("woche60", "⏱️", "Fleißige Woche", "60 Minuten in einer Woche gelernt", lambda s: s["woche_min"] >= 60),
    AbzeichenDef("woche180", "⚡", "Turbo-Woche", "3 Stunden in einer Woche gelernt", lambda s: s["woche_min"] >= 180),
    AbzeichenDef("bestanden", "✅", "Bestanden", "Eine Prüfungssimulation mit mindestens 50 %", lambda s: (s["sim_beste"] or 0) >= 50),
    AbzeichenDef("note2", "🌟", "Gut vorbereitet", "Eine Prüfungssimulation mit mindestens 81 % (Note 2)", lambda s: (s["sim_beste"] or 0) >= 81),
    AbzeichenDef("note1", "👑", "Sehr gut", "Eine Prüfungssimulation mit mindestens 92 % (Note 1)", lambda s: (s["sim_beste"] or 0) >= 92),
    AbzeichenDef("frueh", "🌅", "Frühaufsteher", "Vor 8 Uhr gelernt", lambda s: s["frueh"]),
    AbzeichenDef("eule", "🦉", "Nachteule", "Nach 22 Uhr gelernt", lambda s: s["spaet"]),
]
ABZEICHEN_NACH_SCHLUESSEL = {a.schluessel: a for a in ABZEICHEN}


def abzeichen_pruefen(user) -> list[AbzeichenDef]:
    """Vergibt neu erreichte Abzeichen und gibt sie zurück."""
    from .models import Abzeichen
    vorhanden = set(Abzeichen.objects.filter(user=user).values_list("schluessel", flat=True))
    offen = [a for a in ABZEICHEN if a.schluessel not in vorhanden]
    if not offen:
        return []
    stat = _statistik(user)
    neu = [a for a in offen if a.pruefen(stat)]
    Abzeichen.objects.bulk_create([Abzeichen(user=user, schluessel=a.schluessel) for a in neu], ignore_conflicts=True)
    return neu

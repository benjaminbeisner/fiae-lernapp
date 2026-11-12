"""Bausteine für Prüfungsteilaufgaben.

Ein Baustein liefert ein dict:
  {"thema": str, "intro": str (optional), "teile": [Teil, ...]}
Teil:
  {"text": str, "punkte": int, "antwort": Antwortform, "loesung": str, "code": str (optional), "daten": Tabelle (optional)}
Antwortformen:
  ("zeilen", n)                 freie Textantwort mit n Zeilen
  ("rechnen", n)                Rechenkästchen mit n Zeilen + Ergebnisfeld
  ("felder", [label, ...])      beschriftete Einzelfelder
  ("tabelle", kopf, zeilen)     Tabelle; None in einer Zelle = Eingabefeld
  ("code", n)                   Codefeld (Courier) mit n Zeilen
Textauszeichnung: **fett**, `code`.
"""
from decimal import ROUND_HALF_UP, Decimal


def T(text, punkte, antwort, loesung, code="", daten=None):
    return {"text": text, "punkte": punkte, "antwort": antwort, "loesung": loesung, "code": code, "daten": daten}


def Z(n):
    return ("zeilen", n)


def R(n=6):
    return ("rechnen", n)


def F(*labels):
    return ("felder", list(labels))


def TAB(kopf, zeilen):
    return ("tabelle", kopf, zeilen)


def CODE(n):
    return ("code", n)


def zahl(x, stellen=2):
    d = Decimal(str(x)).quantize(Decimal(1) / (10 ** stellen), rounding=ROUND_HALF_UP)
    t = f"{d:,.{stellen}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if "," in t:
        t = t.rstrip("0").rstrip(",")
    return t


def eur(x):
    d = Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"

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


def T(text, punkte, antwort, loesung, code="", daten=None, erwartet=None):
    return {"text": text, "punkte": punkte, "antwort": antwort, "loesung": loesung, "code": code, "daten": daten, "erwartet": erwartet}


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


# ---------- Erwartete Antworten (automatische Korrektur) ----------
# Ein Teil kann `erwartet` haben: eine Liste mit einem Eintrag je automatisch prüfbarem Eingabefeld
# (Felder bei "felder", leere Zellen bei "tabelle" zeilenweise, das Ergebnisfeld bei "rechnen", das Codefeld bei SQL).
# None bedeutet: dieses Feld wird selbst bewertet.

def N(wert, tol=0.0, rel=0.0):
    """Zahl; tol absolut, rel relativ (0.005 = 0,5 %)."""
    return ("zahl", float(wert), float(tol), float(rel))


def W(*varianten):
    """Text, der (normalisiert) genau einer Variante entsprechen muss."""
    return ("wort", list(varianten))


def K(*stichworte):
    """Text, der mindestens eines der Stichworte enthält."""
    return ("stichwort", list(stichworte))


def IP(adresse, *weitere):
    return ("wort", [adresse, *weitere])


def ZAHLEN(*werte):
    """Alle Zahlen in der Antwort in genau dieser Reihenfolge."""
    return ("zahlen", [float(w) for w in werte])


def PFAD(*knoten):
    return ("pfad", "".join(knoten))


def SQL(tabellen_sql, erwartet_sql, geordnet=False, pruef_sql=None):
    """SQL-Antwort: wird auf einer Kopie der Beispieltabelle ausgeführt und mit der Musterlösung verglichen.
    pruef_sql: bei UPDATE/DELETE wird danach diese Abfrage verglichen."""
    return ("sql", tabellen_sql, erwartet_sql, geordnet, pruef_sql)

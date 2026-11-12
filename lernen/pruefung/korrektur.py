"""Online-Bearbeitung und Korrektur der Übungsprüfung.

Jede Teilaufgabe hat Eingaben (Schlüssel t{aufgabe}_{teil}_{k}). Eingaben mit erwarteter Antwort werden automatisch
geprüft, alles andere bewertet die Person selbst anhand der Musterlösung (geführte Selbstkorrektur).

Bewertungsmodi:
  "zellen": Felder/Tabellen – jede Zelle zählt gleich viel (automatisch oder per Häkchen „richtig“).
  "ganz":   Freitext, Rechnung, Code – richtig erkanntes Ergebnis = volle Punkte, sonst Punkte selbst wählen.
"""
import re
import sqlite3
import unicodedata

MAX_LAENGE = 4000


# ---------- Normalisieren ----------

def norm(s) -> str:
    s = unicodedata.normalize("NFC", str(s or "")).lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"), ("–", "-"), ("—", "-"), ("→", "-")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    return s.rstrip(".").strip()


_ZAHL = re.compile(r"-?\d[\d.,]*")


def _zahl_aus(tok: str):
    tok = tok.rstrip(".,")
    if not tok or tok == "-":
        return None
    if "," in tok and "." in tok:
        if tok.rfind(",") > tok.rfind("."):
            tok = tok.replace(".", "").replace(",", ".")
        else:
            tok = tok.replace(",", "")
    elif "," in tok:
        tok = tok.replace(",", ".") if tok.count(",") == 1 else tok.replace(",", "")
    elif tok.count(".") > 1 or re.fullmatch(r"-?\d{1,3}(\.\d{3})+", tok):
        tok = tok.replace(".", "")
    try:
        return float(tok)
    except ValueError:
        return None


def zahlen(text) -> list:
    """Alle Zahlen in einem Text, deutsch oder englisch geschrieben ("1.234,5", "1234.5", "1,5")."""
    t = str(text or "").replace("−", "-").replace(" ", " ")
    t = re.sub(r"(?<=\d) (?=\d{3}\b)", "", t)  # 1 234 → 1234
    werte = [_zahl_aus(m.group()) for m in _ZAHL.finditer(t)]
    return [w for w in werte if w is not None]


def _gleich(x, wert, tol=0.0, rel=0.0):
    return abs(x - wert) <= max(tol, rel * abs(wert), 0.005) + 1e-9


# ---------- SQL ----------

_SQL_VERBOTEN = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA}


def _db(tabellen_sql):
    db = sqlite3.connect(":memory:")
    db.executescript(tabellen_sql)
    db.set_authorizer(lambda aktion, *_: sqlite3.SQLITE_DENY if aktion in _SQL_VERBOTEN else sqlite3.SQLITE_OK)
    zaehler = [0]

    def abbruch():
        zaehler[0] += 1
        return 1 if zaehler[0] > 2000 else 0  # sehr großzügig für 6 Zeilen, verhindert Endlosabfragen
    db.set_progress_handler(abbruch, 1000)
    return db


def _zeilen(rows, geordnet):
    def wert(v):
        return round(v, 2) if isinstance(v, float) else (float(v) if isinstance(v, int) else norm(v))
    r = [tuple(wert(v) for v in row) for row in rows]
    return r if geordnet else sorted(r, key=repr)


def sql_ausfuehren(tabellen_sql, anweisung, pruef_sql=None):
    """Führt eine einzelne Anweisung auf einer frischen Kopie aus. Liefert (zeilen, fehler)."""
    a = (anweisung or "").strip().rstrip(";").strip()
    if not a:
        return None, "leer"
    if ";" in a.replace("';'", ""):
        return None, "Bitte nur eine Anweisung."
    if len(a) > MAX_LAENGE:
        return None, "zu lang"
    db = _db(tabellen_sql)
    try:
        cur = db.execute(a)
        rows = cur.fetchmany(500) if cur.description else []
        if pruef_sql:
            db.set_authorizer(None)
            rows = db.execute(pruef_sql).fetchall()
        return rows, None
    except sqlite3.Error as e:
        return None, str(e)
    finally:
        db.close()


# ---------- Einzelne Antwort prüfen ----------

def pruefen(erwartet, antwort) -> bool:
    if erwartet is None:
        return None
    art = erwartet[0]
    text = str(antwort or "")
    if not text.strip():
        return False
    if art == "zahl":
        z = zahlen(text)
        return bool(z) and (_gleich(z[0], *erwartet[1:]) or _gleich(z[-1], *erwartet[1:]))
    if art == "zahlen":
        z = zahlen(text)
        return len(z) == len(erwartet[1]) and all(_gleich(a, b) for a, b in zip(z, erwartet[1]))
    if art == "wort":
        a = norm(text).replace(" ", "")
        return any(a == norm(v).replace(" ", "") for v in erwartet[1])
    if art == "stichwort":
        a = norm(text)
        return any(norm(s) in a for s in erwartet[1])
    if art == "pfad":
        return "".join(re.findall(r"[A-Za-z0-9]+", text)).upper() == erwartet[1].upper()
    if art == "sql":
        _, tabellen, soll_sql, geordnet, pruef = erwartet
        ist, fehler = sql_ausfuehren(tabellen, text, pruef)
        if fehler:
            return False
        soll, _ = sql_ausfuehren(tabellen, soll_sql, pruef)
        return _zeilen(ist, geordnet or bool(pruef)) == _zeilen(soll, geordnet or bool(pruef))
    raise ValueError(f"unbekannte Prüfart {art}")


# ---------- Aufbau der Prüfung ----------

def eingaben(teil, tkey):
    """Liste der Eingaben einer Teilaufgabe: dicts mit key, art (text/zeile/code), label, erwartet."""
    form = teil["antwort"]
    erw = list(teil.get("erwartet") or [])
    art = form[0]
    if art == "zeilen":
        return [{"key": f"{tkey}_0", "art": "text", "zeilen": form[1], "label": "", "erwartet": None}]
    if art == "rechnen":
        return [{"key": f"{tkey}_0", "art": "text", "zeilen": max(3, form[1]), "label": "Rechenweg", "erwartet": None, "rechenweg": True},
                {"key": f"{tkey}_1", "art": "zeile", "label": "Ergebnis", "erwartet": erw[0] if erw else None}]
    if art == "felder":
        return [{"key": f"{tkey}_{i}", "art": "zeile", "label": l, "erwartet": erw[i] if i < len(erw) else None}
                for i, l in enumerate(form[1])]
    if art == "tabelle":
        out, n = [], 0
        for r, zeile in enumerate(form[2]):
            for s, zelle in enumerate(zeile):
                if zelle is None:
                    out.append({"key": f"{tkey}_{n}", "art": "zelle", "zeile": r, "spalte": s, "label": form[1][s],
                                "erwartet": erw[n] if n < len(erw) else None})
                    n += 1
        return out
    if art == "code":
        return [{"key": f"{tkey}_0", "art": "code", "zeilen": form[1], "label": "", "erwartet": erw[0] if erw else None}]
    raise ValueError(art)


def modus(teil):
    return "zellen" if teil["antwort"][0] in ("felder", "tabelle") else "ganz"


def struktur(p):
    """Aufgaben → Bausteine → Teile mit Label, Schlüssel und Eingaben (für Formular und Korrektur)."""
    aufgaben = []
    for a_nr, a in enumerate(p["aufgaben"], 1):
        bl, teil_nr = [], 0
        for b_nr, b in enumerate(a["bausteine"]):
            mehrere = len(b["teile"]) > 1
            haupt = "abcdefghijklmnop"[b_nr]
            teile = []
            for j, t in enumerate(b["teile"]):
                tkey = f"t{a_nr}_{teil_nr}"
                teil_nr += 1
                art = t["antwort"][0]
                teile.append({"key": tkey, "label": f"{haupt}{'abcdefgh'[j]})" if mehrere else f"{haupt})", "teil": t,
                              "art": art, "modus": modus(t), "eingaben": eingaben(t, tkey)})
            bl.append({"intro": b.get("intro", ""), "teile": teile})
        aufgaben.append({"nr": a_nr, "punkte": a["punkte"], "bausteine": bl})
    return aufgaben


def alle_teile(p):
    for a in struktur(p):
        for b in a["bausteine"]:
            for t in b["teile"]:
                yield a["nr"], t


def gueltige_schluessel(p):
    return {e["key"] for _, t in alle_teile(p) for e in t["eingaben"]}


# ---------- Bewertung ----------

def halbe(x):
    """Auf halbe Punkte runden (kaufmännisch)."""
    return int(x * 2 + 0.5 + 1e-9) / 2


def automatisch(p, antworten):
    """{eingabe_key: True/False/None} – None = selbst bewerten."""
    return {e["key"]: pruefen(e["erwartet"], antworten.get(e["key"], "")) for _, t in alle_teile(p) for e in t["eingaben"]}


def punkte_teil(t, auto, selbst):
    """Punkte einer Teilaufgabe aus automatischer Prüfung und Selbstbewertung.
    selbst: {eingabe_key: True} für als richtig markierte Zellen, {teil_key: Punkte} für ganze Teile."""
    max_p = t["teil"]["punkte"]
    if t["modus"] == "zellen":
        ein = t["eingaben"]
        ok = sum(1 for e in ein if auto.get(e["key"]) or bool(selbst.get(e["key"])))
        return halbe(max_p * ok / len(ein))
    pruefbar = [e for e in t["eingaben"] if e["erwartet"] is not None]
    if pruefbar and all(auto.get(e["key"]) for e in pruefbar):
        return float(max_p)
    try:
        w = float(selbst.get(t["key"], 0) or 0)
    except (TypeError, ValueError):
        w = 0.0
    return min(max(halbe(w), 0.0), float(max_p))


def bewerten(p, antworten, selbst, auto=None):
    """Liefert (punkte_je_aufgabe [4 Werte], punkte_je_teil {teil_key: Punkte}, auto)."""
    auto = automatisch(p, antworten) if auto is None else auto
    je_aufgabe = [0.0] * len(p["aufgaben"])
    je_teil = {}
    for nr, t in alle_teile(p):
        pt = punkte_teil(t, auto, selbst)
        je_teil[t["key"]] = pt
        je_aufgabe[nr - 1] += pt
    return [halbe(x) for x in je_aufgabe], je_teil, auto


def braucht_selbst(t, auto):
    """Muss die Person diesen Teil (oder Zellen davon) selbst bewerten?"""
    if t["modus"] == "zellen":
        return any(not auto.get(e["key"]) for e in t["eingaben"])
    pruefbar = [e for e in t["eingaben"] if e["erwartet"] is not None]
    return not (pruefbar and all(auto.get(e["key"]) for e in pruefbar))

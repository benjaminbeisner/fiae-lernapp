"""Erzeugt fragen/ap1/gen/*.json.  Aufruf: python -m lernen.generator"""
import json
from decimal import Decimal
from pathlib import Path

from . import datenbanken, einheiten, hardware, kommunikation, netzwerk, programmierung, projekt, sicherheit, uml, wirtschaft

BASIS = Path(__file__).resolve().parents[2] / "fragen" / "ap1"
MODULE = [("01_sicherheit", sicherheit), ("02_wirtschaft", wirtschaft), ("03_netzwerk", netzwerk), ("04_hardware", hardware),
          ("05_programmierung", programmierung), ("06_datenbanken", datenbanken), ("07_projektmanagement", projekt),
          ("08_kommunikation", kommunikation), ("09_uml", uml), ("10_einheiten", einheiten)]


def lektionen():
    keys = set()
    for p in BASIS.glob("*.json"):
        keys |= {l["schluessel"] for l in json.loads(p.read_text(encoding="utf-8")).get("lektionen", [])}
    return keys


def pruefen(f, lek):
    assert f["lektion"] in lek, f
    assert len(f["schluessel"]) <= 50 and len(f["gruppe"]) <= 60, f["schluessel"]
    if f["typ"] == "zahl":
        d = Decimal(str(f["loesung"]))
        assert abs(d) < Decimal("1e10") and d == round(d, 4), (f["schluessel"], d)
        if isinstance(f["loesung"], float) and f["loesung"].is_integer():
            f["loesung"] = int(f["loesung"])
    else:
        texte = [a["text"] for a in f["antworten"]]
        assert len(texte) == len(set(texte)) and len(texte) >= 2, f["schluessel"]
        assert all(len(t) <= 300 for t in texte), f["schluessel"]
        assert any(a["richtig"] for a in f["antworten"]), f["schluessel"]


MARKE = "\n\n**Vertiefung**\n\n"


def vertiefungen_eintragen():
    """Hängt die Vertiefungsabschnitte an die Lektionen der Grunddateien an (idempotent)."""
    from .vertiefung import V
    for p in sorted(BASIS.glob("[0-9]*.json")):
        daten = json.loads(p.read_text(encoding="utf-8"))
        geaendert = False
        for l in daten.get("lektionen", []):
            if l["schluessel"] in V:
                neu = l["inhalt"].split(MARKE)[0] + MARKE + V[l["schluessel"]].strip()
                if neu != l["inhalt"]:
                    l["inhalt"], geaendert = neu, True
        if geaendert:
            p.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    vertiefungen_eintragen()
    lek = lektionen()
    ziel = BASIS / "gen"
    ziel.mkdir(exist_ok=True)
    gesamt = 0
    gesehen = set()
    for name, modul in MODULE:
        fragen = []
        for f in modul.erzeugen():
            pruefen(f, lek)
            kennung = (f["text"], tuple(sorted(a["text"] for a in f.get("antworten", []))))
            if kennung in gesehen:   # identische Variante (z. B. gleiche Zufallszahlen) überspringen
                continue
            gesehen.add(kennung)
            fragen.append(f)
        (ziel / f"{name}_aufgaben.json").write_text(json.dumps({"fragen": fragen}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{name}: {len(fragen)} Fragen")
        gesamt += len(fragen)
    print("Erzeugt:", gesamt)


if __name__ == "__main__":
    main()

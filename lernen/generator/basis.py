import random
from decimal import ROUND_HALF_UP, Decimal


def zahl(x, stellen: int = 2) -> str:
    """Deutsche Schreibweise: 1.234,56 (ohne überflüssige Nachkommastellen)."""
    d = Decimal(str(x)).quantize(Decimal(1) / (10 ** stellen), rounding=ROUND_HALF_UP) if stellen else Decimal(round(x))
    text = f"{d:,.{stellen}f}" if stellen else f"{int(d):,}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    if "," in text:
        text = text.rstrip("0").rstrip(",")
    return text


def runden(x, stellen=2) -> float:
    return float(Decimal(str(x)).quantize(Decimal(1) / (10 ** stellen), rounding=ROUND_HALF_UP))


class Sammler:
    """Sammelt erzeugte Fragen einer Datei."""

    def __init__(self):
        self.fragen = []
        self._schluessel = set()

    def _neu(self, gruppe, nr, thema, lektion, text, erkl, s):
        key = f"G-{gruppe}-{nr:03d}"
        assert key not in self._schluessel, key
        self._schluessel.add(key)
        return {"schluessel": key, "thema": thema, "lektion": lektion, "gruppe": gruppe, "text": text,
                "erklaerung": erkl, "schwierigkeit": s, "einstufung": False}

    def zahl(self, gruppe, nr, thema, lektion, text, loesung, erkl, einheit="", tol=0, s=2):
        d = self._neu(gruppe, nr, thema, lektion, text, erkl, s)
        d.update(typ="zahl", loesung=loesung, toleranz=tol, einheit=einheit)
        self.fragen.append(d)

    def wahl(self, gruppe, nr, thema, lektion, text, richtig, falsch, erkl, s=2, rng=None):
        """Eine richtige Antwort, bis zu drei falsche (Duplikate werden entfernt)."""
        richtig = str(richtig)
        falsche = []
        for f in falsch:
            f = str(f)
            if f != richtig and f not in falsche:
                falsche.append(f)
        assert len(falsche) >= 2, (gruppe, nr, richtig, falsch)
        d = self._neu(gruppe, nr, thema, lektion, text, erkl, s)
        d.update(typ="einfach", antworten=[{"text": richtig, "richtig": True}] +
                 [{"text": f, "richtig": False} for f in falsche[:3]])
        self.fragen.append(d)

    def mehrfach(self, gruppe, nr, thema, lektion, text, richtige, falsche, erkl, s=2, einzeln=True):
        """Bei Faktenlisten (einzeln=True) bekommt jede Zeile eine eigene Gruppe."""
        assert richtige and falsche
        if einzeln:
            gruppe, nr = f"{gruppe}{nr:02d}", 1
        d = self._neu(gruppe, nr, thema, lektion, text, erkl, s)
        d.update(typ="mehrfach" if len(richtige) > 1 else "einfach",
                 antworten=[{"text": r, "richtig": True} for r in richtige] + [{"text": f, "richtig": False} for f in falsche])
        self.fragen.append(d)


def rng_fuer(name: str) -> random.Random:
    return random.Random(f"fiae-{name}")


def zuordnung(s: "Sammler", kuerzel, thema, lektion, paare, hin, rueck=None, schwierigkeit=1, rng=None):
    """Fragen aus einer Faktentabelle.

    paare: Liste von (a, b) oder (a, b, erklaerung). `hin` enthält {a} und fragt nach b,
    `rueck` enthält {b} und fragt nach a (nur wenn b in der Tabelle eindeutig ist).
    Falsche Antworten stammen aus derselben Tabelle. Beide Richtungen teilen sich eine Gruppe.
    """
    rng = rng or rng_fuer(kuerzel)
    alle_b = list(dict.fromkeys(p[1] for p in paare))
    alle_a = list(dict.fromkeys(p[0] for p in paare))
    for i, p in enumerate(paare, 1):
        a, b = p[0], p[1]
        erkl = p[2] if len(p) > 2 else f"{str(a).rstrip('.?!:')} → **{b}**."
        gruppe = f"{kuerzel}{i:02d}"
        andere_b = [x for x in alle_b if x != b]
        rng.shuffle(andere_b)
        s.wahl(gruppe, 1, thema, lektion, hin.format(a=a, b=b), b, andere_b[:3], erkl, s=schwierigkeit)
        if rueck and sum(1 for q in paare if q[1] == b) == 1:
            andere_a = [x for x in alle_a if x != a]
            rng.shuffle(andere_a)
            s.wahl(gruppe, 2, thema, lektion, rueck.format(a=a, b=b), a, andere_a[:3], erkl, s=schwierigkeit)


def aussagen(s: "Sammler", kuerzel, thema, lektion, frage, richtige, falsche, n=8, k_richtig=(1, 3), anzahl=4,
             erkl="", schwierigkeit=2, rng=None):
    """Mehrfachauswahl: aus Listen richtiger und falscher Aussagen werden n Varianten gemischt."""
    rng = rng or rng_fuer(kuerzel)
    for i in range(1, n + 1):
        kr = rng.randint(*k_richtig)
        kr = min(kr, len(richtige), anzahl - 1)
        r = rng.sample(richtige, kr)
        f = rng.sample(falsche, min(anzahl - kr, len(falsche)))
        s.mehrfach(kuerzel, i, thema, lektion, frage, r, f, erkl or "Richtig sind: " + "; ".join(r) + ".",
                   s=schwierigkeit, einzeln=False)

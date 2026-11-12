"""Stellt aus den Bausteinen eine Übungsprüfung im Aufbau der AP1 zusammen (4 Aufgaben à 25 Punkte)."""
import itertools
import random

from . import slot_arbeitsplatz, slot_netzwerk, slot_sicherheit, slot_software
from .szenarien import IT_FIRMEN, KUNDEN

SLOTS = [slot_arbeitsplatz, slot_netzwerk, slot_sicherheit, slot_software]
# Themen, die in der jeweiligen Aufgabe mindestens einmal vorkommen (Gewichtung wie in den echten Prüfungen)
PFLICHT = [{"wirtschaft"}, {"projektmanagement"}, {"kommunikation"}, {"programmierung"}]
PUNKTE_JE_AUFGABE = 25


def punkte(baustein):
    return sum(t["punkte"] for t in baustein["teile"])


def _auswahl(rng, bausteine, pflicht=frozenset()):
    """Wählt 2–5 Bausteine, die zusammen genau 25 Punkte ergeben (zufällig, aber reproduzierbar)."""
    for groessen in ((3, 4), (2, 5)):
        kombis = [c for n in groessen for c in itertools.combinations(range(len(bausteine)), n)
                  if sum(punkte(bausteine[i]) for i in c) == PUNKTE_JE_AUFGABE
                  and (not pflicht or any(bausteine[i]["thema"] in pflicht for i in c))]
        if kombis:
            break
    if not kombis:
        raise ValueError("Keine passende Kombination")
    return [bausteine[i] for i in rng.choice(kombis)]


def pruefung(seed: int) -> dict:
    rng = random.Random(f"ap1-{seed}")
    kunde = rng.choice(KUNDEN)
    it = rng.choice(IT_FIRMEN)
    aufgaben = []
    for slot, pflicht in zip(SLOTS, PFLICHT):
        fabriken = list(slot.BAUSTEINE)
        rng.shuffle(fabriken)
        bausteine = [f(rng, kunde) for f in fabriken]
        gewaehlt = _auswahl(rng, bausteine, pflicht)
        aufgaben.append({"punkte": PUNKTE_JE_AUFGABE, "bausteine": gewaehlt})
    situation = (f"Sie sind Auszubildende bzw. Auszubildender der **{it}**. Das Unternehmen bietet IT-Dienstleistungen von der Beratung über die Beschaffung "
                 f"bis zur Einrichtung und Betreuung von IT-Systemen an. Ein neuer Kunde ist die **{kunde['name']}**, {kunde['art']}. "
                 f"Ihr Team ist für {kunde['projekt']} zuständig.")
    return {"seed": seed, "nummer": f"{seed:06d}", "kunde": kunde, "it_firma": it, "situation": situation, "aufgaben": aufgaben}

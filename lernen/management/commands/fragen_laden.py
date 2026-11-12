"""Lädt Themen und Fragen aus JSON-Dateien im Ordner fragen/ (idempotent).

Aufruf: python manage.py fragen_laden            (alle Dateien in fragen/)
        python manage.py fragen_laden fragen/ap1.json
"""

import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lernen.models import Antwort, Frage, Lektion, Thema


class Command(BaseCommand):
    help = "Lädt Fragen aus JSON-Dateien und aktualisiert vorhandene anhand ihres Schlüssels."

    def add_arguments(self, parser):
        parser.add_argument("dateien", nargs="*")

    @transaction.atomic
    def handle(self, *args, dateien, **opts):
        pfade = [Path(d) for d in dateien] or sorted((Path(settings.BASE_DIR) / "fragen").rglob("*.json"))
        if not pfade:
            raise CommandError("Keine Fragendateien gefunden.")
        alle_dateien = not dateien
        vorhanden = set()
        laut = opts.get("verbosity", 1) > 0
        for pfad in pfade:
            daten = json.loads(pfad.read_text(encoding="utf-8"))
            vorhanden |= {f["schluessel"] for f in daten.get("fragen", [])}
            for t in daten.get("themen", []):
                Thema.objects.update_or_create(slug=t["slug"], defaults={
                    "name": t["name"], "gewicht": t.get("gewicht", 5),
                    "pruefung": t.get("pruefung", "AP1"), "reihenfolge": t.get("reihenfolge", 0)})
            for l in daten.get("lektionen", []):
                Lektion.objects.update_or_create(schluessel=l["schluessel"], defaults={
                    "thema": Thema.objects.get(slug=l["thema"]), "titel": l["titel"], "inhalt": l["inhalt"],
                    "merksatz": l.get("merksatz", ""), "bild": l.get("bild", ""), "stufe": l.get("stufe", 1),
                    "reihenfolge": l.get("reihenfolge", 0), "aktiv": l.get("aktiv", True)})
            neu = geaendert = 0
            for f in daten.get("fragen", []):
                try:
                    thema = Thema.objects.get(slug=f["thema"])
                except Thema.DoesNotExist:
                    raise CommandError(f"{pfad}: Thema '{f['thema']}' von Frage {f['schluessel']} fehlt.")
                werte = {
                    "thema": thema, "typ": f["typ"], "text": f["text"], "erklaerung": f.get("erklaerung", ""),
                    "schwierigkeit": f.get("schwierigkeit", 2), "einstufung": f.get("einstufung", False),
                    "loesung_zahl": Decimal(str(f["loesung"])) if f["typ"] == "zahl" else None,
                    "toleranz": Decimal(str(f.get("toleranz", 0))), "einheit": f.get("einheit", ""), "aktiv": f.get("aktiv", True),
                    "bild": f.get("bild", ""), "punkte": f.get("punkte", 0), "gruppe": f.get("gruppe", ""),
                    "lektion": Lektion.objects.get(schluessel=f["lektion"]) if f.get("lektion") else None,
                }
                frage, erstellt = Frage.objects.update_or_create(schluessel=f["schluessel"], defaults=werte)
                neu += erstellt
                soll = [(a["text"], a["richtig"]) for a in f.get("antworten", [])]
                ist = list(frage.antworten.order_by("reihenfolge", "id").values_list("text", "richtig"))
                if soll != ist:
                    frage.antworten.all().delete()
                    Antwort.objects.bulk_create([Antwort(frage=frage, text=t, richtig=r, reihenfolge=i) for i, (t, r) in enumerate(soll)])
                    geaendert += not erstellt
                if f["typ"] != "zahl" and not any(r for _, r in soll):
                    raise CommandError(f"Frage {f['schluessel']} hat keine richtige Antwort.")
            if laut:
                self.stdout.write(self.style.SUCCESS(
                    f"{pfad.name}: {len(daten.get('lektionen', []))} Lektionen, {len(daten.get('fragen', []))} Fragen "
                    f"({neu} neu, {geaendert} mit geänderten Antworten)"))
        if alle_dateien:
            # Fragen, die aus den Dateien verschwunden sind, nicht löschen (Lernstand bleibt), nur deaktivieren
            weg = Frage.objects.filter(aktiv=True).exclude(schluessel__in=vorhanden).update(aktiv=False)
            if weg and laut:
                self.stdout.write(f"{weg} nicht mehr vorhandene Fragen deaktiviert.")

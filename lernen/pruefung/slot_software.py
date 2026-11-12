"""Aufgabenbereich: Programmierung, Datenbanken und UML."""
import sqlite3

from ..generator.datenbanken import KAT_VON
from .bausteine_basis import CODE, F, R, T, TAB, Z, eur, zahl


def schreibtischtest(rng, k):
    werte = rng.sample(range(2, 40), 5)
    g = rng.randint(10, 30)
    code = (f"zahlen = {werte}\nsumme = 0\nanzahl = 0\nfür i von 0 bis 4\n    wenn zahlen[i] > {g} dann\n        summe = summe + zahlen[i]\n"
            f"        anzahl = anzahl + 1\n    ende wenn\nende für\nausgabe(summe, anzahl)")
    zeilen, s, a, loes = [], 0, 0, []
    for i, w in enumerate(werte):
        if w > g:
            s += w
            a += 1
        zeilen.append([str(i), None, None, None])
        loes.append(f"i={i}: {w}, summe {s}, anzahl {a}")
    return {"thema": "programmierung", "intro": "Gegeben ist folgender Pseudocode (Arrays beginnen bei Index 0):",
            "teile": [T("Führen Sie einen Schreibtischtest durch. Tragen Sie nach jedem Schleifendurchlauf die Werte ein.", 5,
                        TAB(["i", "zahlen[i]", "summe", "anzahl"], zeilen), "; ".join(loes) + ". Je Zeile 1 Punkt.", code=code),
                      T("Nennen Sie die Ausgabe des Programms.", 1, F("Ausgabe:"), f"{s}, {a}")]}


def algorithmus_schreiben(rng, k):
    art = rng.choice([("den größten Wert eines Arrays `preise` zu ermitteln", "max = preise[0]\nfür i von 1 bis länge(preise) - 1\n    wenn preise[i] > max dann\n        max = preise[i]\n    ende wenn\nende für\nausgabe(max)"),
                      ("den Durchschnitt aller Werte eines Arrays `messwerte` zu berechnen", "summe = 0\nfür i von 0 bis länge(messwerte) - 1\n    summe = summe + messwerte[i]\nende für\nausgabe(summe / länge(messwerte))"),
                      ("zu zählen, wie viele Artikel im Array `bestand` den Wert 0 haben", "anzahl = 0\nfür i von 0 bis länge(bestand) - 1\n    wenn bestand[i] == 0 dann\n        anzahl = anzahl + 1\n    ende wenn\nende für\nausgabe(anzahl)")])
    return {"thema": "programmierung", "teile": [
        T(f"Schreiben Sie einen Algorithmus in Pseudocode, um {art[0]}.", 6, ("code", 10),
          "Musterlösung (andere korrekte Lösungen zulässig):\n```\n" + art[1] + "\n```\nBewertung: Initialisierung 1 P., Schleife 2 P., Bedingung/Berechnung 2 P., Ausgabe 1 P."),
    ]}


def code_fehler(rng, k):
    return {"thema": "programmierung", "intro": "Der folgende Pseudocode soll die Summe der Zahlen von 1 bis n berechnen. Für n = 4 gibt er jedoch 6 statt 10 aus.",
            "teile": [T("Erläutern Sie den Fehler, nennen Sie die Fehlerart und korrigieren Sie die betroffene Zeile.", 4, Z(4),
                        "Die Schleife läuft nur bis n − 1 (Off-by-one). Logischer Fehler (Programm läuft, Ergebnis falsch). Korrektur: `solange i <= n` (statt `i < n`).",
                        code="summe = 0\ni = 1\nsolange i < n\n    summe = summe + i\n    i = i + 1\nende solange\nausgabe(summe)")]}


def _artikel(rng):
    namen = rng.sample(list(KAT_VON), 6)
    z = [(i, n, KAT_VON[n], rng.choice([9.9, 19.99, 25.0, 49.0, 79.9, 129.0]), rng.choice([0, 5, 12, 20, 35])) for i, n in enumerate(namen, 1)]
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE artikel (artikel_id INT, bezeichnung TEXT, kategorie TEXT, preis REAL, bestand INT)")
    db.executemany("INSERT INTO artikel VALUES (?,?,?,?,?)", z)
    tab = TAB(["artikel_id", "bezeichnung", "kategorie", "preis", "bestand"], [[str(a), b, c, zahl(d), str(e)] for a, b, c, d, e in z])
    return db, z, tab


def sql_schreiben(rng, k):
    db, z, tab = _artikel(rng)
    kat = rng.choice(sorted({r[2] for r in z}))
    return {"thema": "datenbanken", "intro": "Gegeben ist die Tabelle `artikel` des Warenwirtschaftssystems:",
            "teile": [
                T(f"Schreiben Sie eine SQL-Abfrage, die Bezeichnung und Preis aller Artikel der Kategorie **{kat}** absteigend nach Preis ausgibt.", 3, ("code", 4),
                  f"`SELECT bezeichnung, preis FROM artikel WHERE kategorie = '{kat}' ORDER BY preis DESC;`", daten=tab),
                T("Schreiben Sie eine SQL-Abfrage, die je Kategorie die Anzahl der Artikel und den Gesamtbestand ausgibt.", 3, ("code", 4),
                  "`SELECT kategorie, COUNT(*), SUM(bestand) FROM artikel GROUP BY kategorie;`"),
                T("Schreiben Sie eine SQL-Anweisung, die den Preis aller Artikel ohne Bestand um 10 % senkt.", 2, ("code", 3),
                  "`UPDATE artikel SET preis = preis * 0.9 WHERE bestand = 0;`"),
            ]}


def sql_ergebnis(rng, k):
    db, z, tab = _artikel(rng)
    g = rng.choice([20, 30, 50])
    q1 = f"SELECT COUNT(*) FROM artikel WHERE preis > {g} AND bestand > 0;"
    q2 = "SELECT MAX(preis) FROM artikel;"
    q3 = "SELECT SUM(preis * bestand) FROM artikel WHERE kategorie = 'Peripherie';"
    w = [db.execute(q).fetchone()[0] or 0 for q in (q1, q2, q3)]
    return {"thema": "datenbanken", "intro": "Gegeben ist die Tabelle `artikel`:",
            "teile": [T("Geben Sie das Ergebnis der Abfragen an.", 4, TAB(["Abfrage", "Ergebnis"], [[q1, None], [q2, None], [q3, None]]),
                        f"{w[0]}; {zahl(w[1])}; {zahl(w[2])} (NULL, falls keine Peripherie vorhanden, zählt als 0).", daten=tab)]}


def erm(rng, k):
    sz = rng.choice([("Kunde", "Bestellung", "Artikel", "Ein Kunde kann mehrere Bestellungen aufgeben, jede Bestellung gehört zu genau einem Kunden. Eine Bestellung enthält mehrere Artikel, ein Artikel kann in vielen Bestellungen vorkommen."),
                     ("Mitarbeiter", "Abteilung", "Projekt", "Jeder Mitarbeiter gehört zu genau einer Abteilung, eine Abteilung hat mehrere Mitarbeiter. Mitarbeiter arbeiten in mehreren Projekten, ein Projekt hat mehrere Mitarbeiter.")])
    a, b, c, text = sz
    if a == "Kunde":
        loes = "Kunde–Bestellung 1:n; Bestellung–Artikel m:n. Tabellen: kunde(kunde_id PK, …), bestellung(bestell_id PK, kunde_id FK, datum), artikel(artikel_id PK, …), bestellposition(bestell_id FK, artikel_id FK, menge; PK aus beiden)."
    else:
        loes = "Abteilung–Mitarbeiter 1:n; Mitarbeiter–Projekt m:n. Tabellen: abteilung(abt_id PK, …), mitarbeiter(ma_id PK, abt_id FK, …), projekt(projekt_id PK, …), mitarbeit(ma_id FK, projekt_id FK, stunden; PK aus beiden)."
    return {"thema": "datenbanken", "intro": text,
            "teile": [T("Nennen Sie die Kardinalitäten der beiden Beziehungen.", 2, F(f"{a} – {b}:" if a == "Kunde" else f"{b} – {a}:", f"{b} – {c}:" if a == "Kunde" else f"{a} – {c}:"),
                        loes.split(" Tabellen")[0]),
                      T("Überführen Sie das Modell in Tabellen. Kennzeichnen Sie Primär- (PK) und Fremdschlüssel (FK).", 5, Z(6), loes)]}


def normalisierung(rng, k):
    return {"thema": "datenbanken", "intro": "Eine Tabelle enthält: rechnung(rechnungs_nr, datum, kunden_nr, kunden_name, kunden_ort, artikel_liste).",
            "teile": [T("Nennen Sie zwei Verstöße gegen die Normalformen und die betroffene Normalform.", 4, Z(4),
                        "artikel_liste enthält mehrere Werte → Verstoß gegen 1NF. kunden_name/kunden_ort hängen von kunden_nr ab (transitive Abhängigkeit) → Verstoß gegen 3NF."),
                      T("Nennen Sie eine Anomalie, die dadurch entstehen kann.", 1, Z(2), "z. B. Änderungsanomalie: Kundenort muss in vielen Rechnungen geändert werden; Löschanomalie; Einfügeanomalie.")]}


def uml_klasse(rng, k):
    kl = rng.choice([("Fahrzeug", "Kennzeichen (Text), Kilometerstand (ganze Zahl)", "fahren(strecke) erhöht den Kilometerstand", "- kennzeichen: String\n- kilometerstand: int\n+ fahren(strecke: int): void\n+ getKilometerstand(): int"),
                     ("Konto", "IBAN (Text), Saldo (Kommazahl)", "einzahlen(betrag) erhöht den Saldo", "- iban: String\n- saldo: double\n+ einzahlen(betrag: double): void\n+ getSaldo(): double"),
                     ("Termin", "Datum (Datum), Beschreibung (Text)", "verschieben(neuesDatum) ändert das Datum", "- datum: Date\n- beschreibung: String\n+ verschieben(neuesDatum: Date): void\n+ getDatum(): Date")])
    return {"thema": "uml", "teile": [
        T(f"Erstellen Sie das UML-Klassendiagramm der Klasse **{kl[0]}** mit den privaten Attributen {kl[1]}, der öffentlichen Methode {kl[2]} und einem Getter für das zweite Attribut.", 4, ("code", 7),
          f"```\n{kl[0]}\n----------\n{kl[3]}\n```\nKlassenname 0,5 P., Attribute mit Sichtbarkeit und Typ 1,5 P., Methoden 2 P."),
        T("Erläutern Sie das Prinzip der Kapselung.", 1, Z(2), "Attribute sind privat und nur über öffentliche Methoden (Getter/Setter) zugänglich."),
    ]}


def uml_beziehungen(rng, k):
    b = rng.sample([("Eine Rechnung besteht aus Rechnungspositionen, die mit ihr gelöscht werden.", "Komposition"),
                    ("Ein Team hat Mitarbeiter, die auch ohne das Team existieren.", "Aggregation"),
                    ("Ein Lkw ist ein Fahrzeug.", "Vererbung"), ("Ein Kunde gibt Bestellungen auf.", "Assoziation"),
                    ("Die Klasse PdfExport implementiert das Interface Export.", "Realisierung")], 4)
    return {"thema": "uml", "teile": [
        T("Nennen Sie die passende Beziehungsart im Klassendiagramm.", 4, TAB(["Sachverhalt", "Beziehung"], [[x, None] for x, _ in b]), "; ".join(f"{x} → {y}" for x, y in b) + ".")]}


def aktivitaet(rng, k):
    return {"thema": "uml", "teile": [
        T("Der Ablauf „Ticket bearbeiten“ soll als Aktivitätsdiagramm dargestellt werden. Nennen Sie vier Elemente des Aktivitätsdiagramms und ihre Bedeutung.", 4, Z(5),
          "Startknoten (gefüllter Kreis), Aktion (abgerundetes Rechteck), Verzweigung (Raute mit [Bedingungen]), Endknoten (Kreis mit Ring), Gabelung/Vereinigung (Balken), Swimlanes."),
    ]}


def compiler(rng, k):
    return {"thema": "programmierung", "teile": [
        T("Erläutern Sie den Unterschied zwischen Compiler und Interpreter und nennen Sie je eine Programmiersprache als Beispiel.", 4, Z(5),
          "Compiler übersetzt den gesamten Quellcode vorab in Maschinencode (z. B. C, C++, Go); schnell, plattformabhängig. Interpreter führt den Code zur Laufzeit Anweisung für Anweisung aus (z. B. Python, PHP); flexibel, langsamer."),
    ]}


def datentypen(rng, k):
    d = rng.sample([("Postleitzahl 01067", "String"), ("Anzahl Mitarbeitende", "Integer"), ("Nettopreis", "Float/Decimal"),
                    ("Newsletter abonniert ja/nein", "Boolean"), ("Geburtsdatum", "Date"), ("Telefonnummer", "String")], 4)
    return {"thema": "programmierung", "teile": [
        T("Ordnen Sie den Werten einen geeigneten Datentyp zu.", 2, TAB(["Wert", "Datentyp"], [[a, None] for a, _ in d]), "; ".join(f"{a}: {b}" for a, b in d) + ". Je 0,5 Punkte."),
    ]}


BAUSTEINE = [schreibtischtest, algorithmus_schreiben, code_fehler, sql_schreiben, sql_ergebnis, erm, normalisierung, uml_klasse,
             uml_beziehungen, aktivitaet, compiler, datentypen]

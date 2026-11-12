import sqlite3

from .basis import Sammler, aussagen, rng_fuer, runden, zahl, zuordnung

T = "datenbanken"
KAT_VON = {"Maus": "Peripherie", "Tastatur": "Peripherie", "Monitor": "Peripherie", "Headset": "Peripherie", "Webcam": "Peripherie",
           "Drucker": "Peripherie", "Router": "Netzwerk", "Switch": "Netzwerk", "Patchkabel": "Netzwerk", "Access Point": "Netzwerk",
           "SSD": "Speicher", "USB-Stick": "Speicher", "Festplatte": "Speicher", "Speicherkarte": "Speicher",
           "Dock": "Zubehör", "Toner": "Zubehör", "Hub": "Zubehör", "Lüfter": "Zubehör", "Netzteil": "Zubehör"}
NAMEN = list(KAT_VON)
KAT = ["Peripherie", "Netzwerk", "Speicher", "Zubehör"]
ORTE = ["Berlin", "Hamburg", "Köln", "Leipzig", "Mainz", "Dresden"]
KUNDEN = ["Meyer", "Schulz", "Yilmaz", "Becker", "Nowak", "Wagner", "Kaya", "Hoffmann"]


def md(spalten, zeilen):
    kopf = "| " + " | ".join(spalten) + " |\n|" + "---|" * len(spalten) + "\n"
    return kopf + "\n".join("| " + " | ".join(f"{v:.2f}".replace(".", ",") if isinstance(v, float) else str(v) for v in z) + " |" for z in zeilen)


def artikel(rng, n=None):
    n = n or rng.randint(6, 8)
    zeilen = []
    for i, name in enumerate(rng.sample(NAMEN, n), 1):
        zeilen.append((i, name, KAT_VON[name], float(rng.choice([4.99, 9.90, 12.50, 19.99, 25.00, 39.90, 49.00, 79.90, 129.00, 199.00]) ),
                       rng.choice([0, 3, 5, 8, 12, 20, 35, 50])))
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE artikel (id INTEGER PRIMARY KEY, name TEXT, kategorie TEXT, preis REAL, bestand INTEGER)")
    db.executemany("INSERT INTO artikel VALUES (?,?,?,?,?)", zeilen)
    return db, zeilen


def erzeugen():
    s = Sammler()
    rng = rng_fuer("datenbanken")
    sp = ["id", "name", "kategorie", "preis", "bestand"]

    # ---------- DB-L4: SELECT, WHERE, ORDER BY ----------
    for i in range(1, 26):
        db, z = artikel(rng)
        g = rng.choice([10, 20, 30, 50])
        k = rng.choice(KAT)
        q = rng.choice([f"SELECT COUNT(*) FROM artikel WHERE preis > {g};",
                        f"SELECT COUNT(*) FROM artikel WHERE kategorie = '{k}';",
                        f"SELECT COUNT(*) FROM artikel WHERE bestand = 0 OR preis < {g};",
                        f"SELECT COUNT(*) FROM artikel WHERE kategorie = '{k}' AND bestand > 5;",
                        f"SELECT COUNT(*) FROM artikel WHERE preis BETWEEN 10 AND {g + 40};",
                        "SELECT COUNT(*) FROM artikel WHERE name LIKE '%e%';",
                        f"SELECT COUNT(*) FROM artikel WHERE kategorie IN ('{k}', 'Zubehör');"])
        w = db.execute(q).fetchone()[0]
        s.zahl("DB-COUNTWHERE", i, T, "DB-L4", f"Tabelle `artikel`:\n\n{md(sp, z)}\n\nWelches Ergebnis liefert die Abfrage?\n\n```\n{q}\n```",
               w, "Zeilen, die die WHERE-Bedingung erfüllen, werden gezählt. BETWEEN schließt beide Grenzen ein, LIKE '%e%' = enthält ein e (in SQLite und MySQL standardmäßig ohne Unterscheidung von Groß-/Kleinschreibung).", s=2)
    for i in range(1, 21):
        db, z = artikel(rng)
        richtung = rng.choice(["ASC", "DESC"])
        spalte = rng.choice(["preis", "bestand", "name"])
        off = rng.choice([0, 0, 1, 2])
        q = f"SELECT name FROM artikel ORDER BY {spalte} {richtung}, id LIMIT 1" + (f" OFFSET {off}" if off else "") + ";"
        w = db.execute(q).fetchone()[0]
        andere = [r[1] for r in z if r[1] != w]
        rng.shuffle(andere)
        s.wahl("DB-ORDER", i, T, "DB-L4", f"Tabelle `artikel`:\n\n{md(sp, z)}\n\nWelchen Namen liefert die Abfrage?\n\n```\n{q}\n```", w, andere[:3],
               f"ORDER BY {spalte} {richtung} sortiert {'aufsteigend' if richtung == 'ASC' else 'absteigend'}; LIMIT 1 nimmt die erste Zeile"
               + (f", OFFSET {off} überspringt vorher {off} Zeile(n)." if off else "."), s=2)
    klauseln = [("SELECT", "legt fest, welche Spalten ausgegeben werden"), ("FROM", "nennt die Tabelle(n), aus denen gelesen wird"),
                ("WHERE", "filtert einzelne Zeilen vor der Gruppierung"), ("ORDER BY", "sortiert das Ergebnis"), ("GROUP BY", "fasst Zeilen mit gleichen Werten zu Gruppen zusammen"),
                ("HAVING", "filtert Gruppen nach der Aggregation"), ("DISTINCT", "entfernt doppelte Ergebniszeilen"), ("LIMIT", "begrenzt die Anzahl der Ergebniszeilen"),
                ("LIKE", "vergleicht Text mit Mustern (% und _)"), ("IS NULL", "prüft auf fehlende Werte"), ("INNER JOIN", "verknüpft Zeilen zweier Tabellen, die zusammenpassen"),
                ("LEFT JOIN", "liefert alle Zeilen der linken Tabelle, auch ohne Partner rechts")]
    zuordnung(s, "DB-KLAUSEL", T, "DB-L4", klauseln, "Was bewirkt **{a}** in einer SQL-Abfrage?", "Welches SQL-Schlüsselwort {b}?", rng=rng)
    dml = [("INSERT INTO", "fügt neue Datensätze ein"), ("UPDATE … SET", "ändert vorhandene Datensätze"), ("DELETE FROM", "löscht Datensätze"),
           ("CREATE TABLE", "legt eine neue Tabelle an"), ("ALTER TABLE", "ändert die Struktur einer Tabelle"), ("DROP TABLE", "löscht eine Tabelle samt Inhalt"),
           ("GRANT", "vergibt Rechte an Benutzer"), ("REVOKE", "entzieht Benutzern Rechte")]
    zuordnung(s, "DB-DML", T, "DB-L4", dml, "Was bewirkt der SQL-Befehl **{a}**?", "Welcher SQL-Befehl {b}?", rng=rng)
    gruppen = [("SELECT, INSERT, UPDATE, DELETE", "DML (Data Manipulation Language)"), ("CREATE, ALTER, DROP", "DDL (Data Definition Language)"),
               ("GRANT, REVOKE", "DCL (Data Control Language)"), ("COMMIT, ROLLBACK", "TCL (Transaction Control Language)")]
    zuordnung(s, "DB-SQLGRP", T, "DB-L4", gruppen, "Zu welcher SQL-Sprachgruppe gehören **{a}**?", None, schwierigkeit=2, rng=rng)
    for i in range(1, 13):
        db, z = artikel(rng)
        ziel = rng.choice(z)
        neu = ziel[4] + rng.choice([5, 10, -2])
        q = rng.choice([f"UPDATE artikel SET bestand = bestand + 10 WHERE kategorie = '{ziel[2]}';",
                        f"DELETE FROM artikel WHERE preis < {ziel[3]};",
                        f"UPDATE artikel SET preis = preis * 2 WHERE id = {ziel[0]};"])
        db.execute(q)
        if q.startswith("DELETE"):
            frage, w = "Wie viele Zeilen enthält die Tabelle danach?", db.execute("SELECT COUNT(*) FROM artikel").fetchone()[0]
        elif "bestand" in q:
            frage, w = "Wie hoch ist danach die Summe aller Bestände?", db.execute("SELECT SUM(bestand) FROM artikel").fetchone()[0]
        else:
            frage, w = f"Welchen Preis hat Artikel {ziel[0]} danach?", runden(db.execute(f"SELECT preis FROM artikel WHERE id={ziel[0]}").fetchone()[0])
        s.zahl("DB-AENDERN", i, T, "DB-L4", f"Tabelle `artikel`:\n\n{md(sp, z)}\n\nEs wird ausgeführt:\n\n```\n{q}\n```\n\n{frage}", w,
               "UPDATE ändert und DELETE löscht nur die Zeilen, auf die die WHERE-Bedingung zutrifft. Ohne WHERE wären alle Zeilen betroffen!", tol=0.01, s=2)

    # ---------- DB-L5: Aggregieren, Gruppieren, JOIN ----------
    for i in range(1, 21):
        db, z = artikel(rng)
        k = rng.choice(KAT)
        q = rng.choice(["SELECT SUM(bestand) FROM artikel;", "SELECT MAX(preis) FROM artikel;", "SELECT MIN(preis) FROM artikel WHERE bestand > 0;",
                        "SELECT ROUND(AVG(preis), 2) FROM artikel;", f"SELECT SUM(preis * bestand) FROM artikel WHERE kategorie = '{k}';",
                        "SELECT COUNT(DISTINCT kategorie) FROM artikel;"])
        w = db.execute(q).fetchone()[0]
        if w is None:
            w = 0
        s.zahl("DB-AGG", i, T, "DB-L5", f"Tabelle `artikel`:\n\n{md(sp, z)}\n\nWelches Ergebnis liefert die Abfrage? (ggf. auf 2 Nachkommastellen; NULL = 0)\n\n```\n{q}\n```",
               runden(w), "Aggregatfunktionen: COUNT zählt, SUM summiert, AVG bildet den Durchschnitt, MIN/MAX liefern den kleinsten/größten Wert.", tol=0.01, s=2)
    for i in range(1, 16):
        db, z = artikel(rng, 8)
        k = rng.choice(sorted({r[2] for r in z}))
        art = rng.choice(["count", "sum", "having"])
        if art == "having":
            n = rng.choice([1, 2])
            q = f"SELECT kategorie, COUNT(*) FROM artikel GROUP BY kategorie HAVING COUNT(*) > {n};"
            w = len(db.execute(q).fetchall())
            frage = "Wie viele Zeilen hat das Ergebnis?"
        else:
            q = f"SELECT kategorie, {'COUNT(*)' if art == 'count' else 'SUM(bestand)'} FROM artikel GROUP BY kategorie;"
            w = dict(db.execute(q).fetchall())[k]
            frage = f"Welcher Wert steht im Ergebnis in der Zeile **{k}**?"
        s.zahl("DB-GROUP", i, T, "DB-L5", f"Tabelle `artikel`:\n\n{md(sp, z)}\n\n```\n{q}\n```\n\n{frage}", w,
               "GROUP BY bildet je Kategorie eine Gruppe; die Aggregatfunktion wird pro Gruppe berechnet. HAVING filtert danach ganze Gruppen.", s=3)
    for i in range(1, 16):
        kunden = [(j, n, rng.choice(ORTE)) for j, n in enumerate(rng.sample(KUNDEN, 4), 1)]
        best = [(100 + j, rng.randint(1, 5), rng.choice([50, 80, 120, 200, 350])) for j in range(1, rng.randint(5, 7))]
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE kunde (kunde_id INTEGER PRIMARY KEY, name TEXT, ort TEXT)")
        db.execute("CREATE TABLE bestellung (best_id INTEGER PRIMARY KEY, kunde_id INTEGER, betrag REAL)")
        db.executemany("INSERT INTO kunde VALUES (?,?,?)", kunden)
        db.executemany("INSERT INTO bestellung VALUES (?,?,?)", best)
        ziel = rng.choice(kunden)
        art = rng.choice(["summe", "anzahl", "ohne", "left"])
        if art == "summe":
            q = f"SELECT SUM(b.betrag)\nFROM kunde k\nINNER JOIN bestellung b ON k.kunde_id = b.kunde_id\nWHERE k.name = '{ziel[1]}';"
        elif art == "anzahl":
            q = f"SELECT COUNT(*)\nFROM kunde k\nINNER JOIN bestellung b ON k.kunde_id = b.kunde_id\nWHERE k.ort = '{ziel[2]}';"
        elif art == "ohne":
            q = "SELECT COUNT(*)\nFROM kunde k\nLEFT JOIN bestellung b ON k.kunde_id = b.kunde_id\nWHERE b.best_id IS NULL;"
        else:
            q = "SELECT COUNT(*)\nFROM kunde k\nLEFT JOIN bestellung b ON k.kunde_id = b.kunde_id;"
        w = db.execute(q).fetchone()[0] or 0
        txt = (f"Tabelle `kunde`:\n\n{md(['kunde_id', 'name', 'ort'], kunden)}\n\nTabelle `bestellung`:\n\n{md(['best_id', 'kunde_id', 'betrag'], [(a, b, float(c)) for a, b, c in best])}"
               f"\n\nWelches Ergebnis liefert die Abfrage? (NULL = 0)\n\n```\n{q}\n```")
        s.zahl("DB-JOIN", i, T, "DB-L5", txt, runden(w),
               "INNER JOIN liefert nur Kunden mit Bestellungen. LEFT JOIN liefert alle Kunden, Kunden ohne Bestellung einmal mit NULL-Werten.", tol=0.01, s=3)
    joins = [("INNER JOIN", "nur Datensätze mit passendem Partner in beiden Tabellen"), ("LEFT JOIN", "alle Datensätze der linken Tabelle, rechts ggf. NULL"),
             ("RIGHT JOIN", "alle Datensätze der rechten Tabelle, links ggf. NULL"), ("CROSS JOIN", "jede Zeile mit jeder Zeile (kartesisches Produkt)")]
    zuordnung(s, "DB-JOINART", T, "DB-L5", joins, "Was liefert ein **{a}**?", "Welcher Join liefert {b}?", schwierigkeit=2, rng=rng)
    for i in range(1, 9):
        a, b = rng.randint(3, 20), rng.randint(2, 15)
        s.zahl("DB-KREUZ", i, T, "DB-L5", f"Tabelle A hat **{a} Zeilen**, Tabelle B **{b} Zeilen**. Wie viele Zeilen liefert `SELECT * FROM A, B;` (ohne WHERE)?",
               a * b, f"Ohne Join-Bedingung entsteht das kartesische Produkt: {a} × {b} = {a*b}.", s=2)

    # ---------- DB-L1: Schlüssel ----------
    schl = [("Primärschlüssel", "identifiziert jeden Datensatz einer Tabelle eindeutig"), ("Fremdschlüssel", "verweist auf den Primärschlüssel einer anderen Tabelle"),
            ("zusammengesetzter Schlüssel", "Primärschlüssel aus mehreren Attributen"), ("Surrogatschlüssel", "künstlicher Schlüssel ohne fachliche Bedeutung, z. B. fortlaufende ID"),
            ("Schlüsselkandidat", "Attribut(kombination), die eindeutig wäre und als Primärschlüssel infrage kommt"),
            ("referentielle Integrität", "jeder Fremdschlüsselwert muss als Primärschlüssel existieren"), ("Attribut", "eine Spalte bzw. Eigenschaft einer Entität"),
            ("Tupel / Datensatz", "eine Zeile einer Tabelle"), ("NOT NULL", "Spalte darf keinen leeren Wert enthalten"), ("UNIQUE", "Werte der Spalte dürfen sich nicht wiederholen")]
    zuordnung(s, "DB-SCHL", T, "DB-L1", schl, "Was bedeutet **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)
    pk = [("Tabelle Mitarbeiter (Vorname, Nachname, Personalnummer, Abteilung)", "Personalnummer"),
          ("Tabelle Artikel (Bezeichnung, Artikelnummer, Preis, Farbe)", "Artikelnummer"),
          ("Tabelle Fahrzeug (Marke, Kennzeichen, Farbe, Baujahr)", "Kennzeichen"),
          ("Tabelle Kunde (Name, Ort, Kundennummer, Telefon)", "Kundennummer"),
          ("Tabelle Rechnung (Datum, Rechnungsnummer, Betrag, Kunde)", "Rechnungsnummer"),
          ("Tabelle Raum (Gebäude, Raumnummer, Plätze) – Raumnummern wiederholen sich je Gebäude", "Gebäude + Raumnummer"),
          ("Tabelle Bestellposition (Bestellnummer, Positionsnummer, Artikel, Menge)", "Bestellnummer + Positionsnummer")]
    for i, (t, a) in enumerate(pk, 1):
        attrs = [x.strip() for x in t.split("(")[1].split(")")[0].split(",")]
        falsch = [x for x in attrs if x not in a]
        s.wahl("DB-PKWAHL", i, T, "DB-L1", f"Welches Attribut eignet sich als Primärschlüssel? {t}", a, falsch + ["Name"],
               "Ein Primärschlüssel muss eindeutig und stabil sein; Namen, Farben oder Orte wiederholen sich.", s=1)
    datentypen = [("INT", "ganze Zahlen"), ("DECIMAL(10,2)", "Geldbeträge mit genau zwei Nachkommastellen"), ("VARCHAR(50)", "Text mit variabler Länge bis 50 Zeichen"),
                  ("CHAR(5)", "Text mit fester Länge, z. B. Postleitzahl"), ("DATE", "Kalenderdatum"), ("BOOLEAN", "Wahrheitswert"), ("DATETIME / TIMESTAMP", "Datum mit Uhrzeit"),
                  ("TEXT", "lange Texte ohne feste Obergrenze")]
    zuordnung(s, "DB-DTYP", T, "DB-L1", datentypen, "Wofür eignet sich der SQL-Datentyp **{a}**?", "Welcher SQL-Datentyp passt für {b}?", rng=rng)

    # ---------- DB-L2: ERM, Kardinalitäten ----------
    kard = [("Person – Personalausweis (gültig)", "1:1"), ("Kunde – Bestellung", "1:n"), ("Student – Kurs", "m:n"), ("Abteilung – Mitarbeiter (Stammabteilung)", "1:n"),
            ("Artikel – Lieferant (mehrere Lieferanten je Artikel)", "m:n"), ("Land – Hauptstadt", "1:1"), ("Mutter – leibliches Kind", "1:n"),
            ("Autor – Buch (Bücher können mehrere Autoren haben)", "m:n"), ("Mitarbeiter – Firmenparkplatz (fest zugewiesen)", "1:1"),
            ("Rechnung – Rechnungsposition", "1:n"), ("Projekt – Mitarbeiter (in mehreren Projekten)", "m:n"), ("Fahrzeug – Kennzeichen (aktuell)", "1:1")]
    for i, (a, b) in enumerate(kard, 1):
        s.mehrfach("DB-KARD", i, T, "DB-L2", f"Welche Kardinalität besteht zwischen **{a}**?", [b], [x for x in ["1:1", "1:n", "m:n"] if x != b],
                   "Frage in beide Richtungen: Wie viele B gehören zu einem A, wie viele A zu einem B?", s=2)
    erm = [("Rechteck", "Entität (Entitätstyp)"), ("Raute", "Beziehung"), ("Ellipse/Oval", "Attribut"), ("unterstrichenes Attribut", "Primärschlüssel"),
           ("doppelte Ellipse", "mehrwertiges Attribut"), ("gestrichelte Ellipse", "abgeleitetes Attribut")]
    zuordnung(s, "DB-ERMSYM", T, "DB-L2", erm, "Was stellt im ER-Diagramm (Chen-Notation) ein(e) **{a}** dar?", "Wie wird ein(e) **{b}** in der Chen-Notation dargestellt?", rng=rng)
    for i, (rel, n) in enumerate([("eine m:n-Beziehung zwischen Student und Kurs", 3), ("eine 1:n-Beziehung zwischen Kunde und Bestellung", 2),
                                  ("eine 1:1-Beziehung zwischen Mitarbeiter und Dienstwagen", 1), ("zwei m:n-Beziehungen: Artikel–Lieferant und Artikel–Lager", 5),
                                  ("eine m:n-Beziehung zwischen Projekt und Mitarbeiter mit dem Attribut Stunden", 3)], 1):
        s.zahl("DB-TABANZ", i, T, "DB-L2", f"Wie viele Tabellen entstehen mindestens bei der Umsetzung ins relationale Modell für {rel}?", n,
               "1:1 kann in eine Tabelle zusammengefasst werden, 1:n braucht 2 Tabellen (Fremdschlüssel auf der n-Seite), m:n braucht eine zusätzliche Zwischentabelle.", s=2)

    # ---------- DB-L3: Normalisierung ----------
    nf = [("Jedes Attribut enthält nur atomare Werte, keine Wiederholungsgruppen", "1. Normalform"),
          ("Jedes Nicht-Schlüsselattribut hängt vom ganzen Primärschlüssel ab", "2. Normalform"),
          ("Kein Nicht-Schlüsselattribut hängt transitiv vom Primärschlüssel ab", "3. Normalform")]
    zuordnung(s, "DB-NF", T, "DB-L3", nf, "Welche Normalform fordert: {a}?", "Was fordert die **{b}**?", rng=rng)
    verstoss = [("Spalte Telefon enthält „0301234, 0171555“", "1. Normalform"), ("Spalte Adresse enthält „Hauptstr. 5, 10115 Berlin“ in einem Feld", "1. Normalform"),
                ("Tabelle Bestellposition(BestNr, ArtNr, Menge, Artikelbezeichnung) – Bezeichnung hängt nur von ArtNr ab", "2. Normalform"),
                ("Tabelle Prüfung(MatrNr, KursNr, Note, Kursname) – Kursname hängt nur von KursNr ab", "2. Normalform"),
                ("Tabelle Mitarbeiter(PersNr, Name, AbtNr, Abteilungsname) – Abteilungsname hängt von AbtNr ab", "3. Normalform"),
                ("Tabelle Kunde(KdNr, Name, PLZ, Ort) – Ort hängt von der PLZ ab", "3. Normalform"),
                ("Spalten Kurs1, Kurs2, Kurs3 in einer Tabelle", "1. Normalform")]
    for i, (a, b) in enumerate(verstoss, 1):
        s.mehrfach("DB-NFVERST", i, T, "DB-L3", f"Gegen welche Normalform wird verstoßen? {a}", [b], [x for x in ["1. Normalform", "2. Normalform", "3. Normalform"] if x != b],
                   "1NF: atomare Werte. 2NF: keine Abhängigkeit von nur einem Teil eines zusammengesetzten Schlüssels. 3NF: keine transitiven Abhängigkeiten.", s=3)
    anom = [("Einfügeanomalie", "ein neuer Sachverhalt kann nicht gespeichert werden, ohne andere (fehlende) Daten einzutragen"),
            ("Änderungsanomalie", "eine Information muss an vielen Stellen geändert werden, sonst entstehen Widersprüche"),
            ("Löschanomalie", "beim Löschen eines Datensatzes gehen ungewollt andere Informationen verloren"),
            ("Redundanz", "dieselbe Information ist mehrfach gespeichert")]
    zuordnung(s, "DB-ANOM", T, "DB-L3", anom, "Was beschreibt eine **{a}**?", "Wie heißt es, wenn {b}?", rng=rng)
    aussagen(s, "DB-NFAUSS", T, "DB-L3", "Welche Aussagen zur Normalisierung treffen zu?",
             ["Normalisierung reduziert Redundanzen.", "Die 3NF setzt die 2NF voraus.", "Normalisierung hilft, Anomalien zu vermeiden.",
              "Durch Normalisierung entstehen oft mehr Tabellen."],
             ["Normalisierung macht Abfragen immer schneller.", "Die 2NF ist nur bei einspaltigen Primärschlüsseln verletzbar.",
              "In der 1NF sind Listen in einem Feld erlaubt.", "Normalisierung erhöht die Redundanz."], n=8, k_richtig=(1, 3), rng=rng)
    return s.fragen

from .basis import Sammler, aussagen, rng_fuer, zuordnung

T = "uml"


def erzeugen():
    s = Sammler()
    rng = rng_fuer("uml")

    # ---------- UML-L1: Klassendiagramm ----------
    sicht = [("+", "public – überall sichtbar"), ("-", "private – nur innerhalb der Klasse"), ("#", "protected – Klasse und Unterklassen"), ("~", "package – innerhalb des Pakets")]
    zuordnung(s, "UML-SICHT", T, "UML-L1", sicht, "Welche Sichtbarkeit bedeutet das Zeichen `{a}` im Klassendiagramm?", "Welches Zeichen steht für **{b}**?", rng=rng)
    begriffe = [("Klasse", "Bauplan mit Attributen und Methoden"), ("Objekt", "konkrete Instanz einer Klasse"), ("Attribut", "Eigenschaft einer Klasse"),
                ("Methode / Operation", "Verhalten bzw. Funktion einer Klasse"), ("Konstruktor", "Methode, die beim Erzeugen eines Objekts aufgerufen wird"),
                ("Kapselung", "Attribute sind privat und nur über Methoden zugänglich"), ("Getter / Setter", "Methoden zum Lesen bzw. Ändern privater Attribute"),
                ("statisches Attribut (unterstrichen)", "gehört zur Klasse, nicht zu einem einzelnen Objekt"), ("abstrakte Klasse (kursiv)", "kann nicht direkt instanziiert werden"),
                ("Interface", "legt Methoden fest, die implementierende Klassen bereitstellen müssen"), ("Polymorphie", "gleicher Methodenaufruf führt je nach Objekttyp zu unterschiedlichem Verhalten"),
                ("Überschreiben", "Unterklasse ersetzt eine geerbte Methode durch eine eigene Implementierung")]
    zuordnung(s, "UML-BEGR", T, "UML-L1", begriffe, "Was bedeutet **{a}** in der Objektorientierung?", "Welcher Begriff passt: {b}?", rng=rng)
    klassen = [("Kunde", ["- kundenNr: int", "- name: String", "+ getName(): String", "+ setName(n: String): void"]),
               ("Konto", ["- iban: String", "- saldo: double", "+ einzahlen(betrag: double): void", "+ getSaldo(): double"]),
               ("Artikel", ["- artNr: int", "- preis: double", "# bestand: int", "+ berechneBrutto(): double"]),
               ("Fahrzeug", ["- kennzeichen: String", "- km: int", "+ fahren(strecke: int): void", "~ pruefen(): boolean"])]
    nr = 0
    for name, zeilen in klassen:
        attrs = [z for z in zeilen if "(" not in z]
        meth = [z for z in zeilen if "(" in z]
        bild = f"Klasse **{name}**:\n\n```\n{name}\n" + "-" * 30 + "\n" + "\n".join(attrs) + "\n" + "-" * 30 + "\n" + "\n".join(meth) + "\n```\n\n"
        nr += 1
        s.zahl("UML-KLATTR", nr, T, "UML-L1", bild + "Wie viele Attribute hat die Klasse?", len(attrs), "Attribute stehen im mittleren Feld, Methoden im unteren.", s=1)
        s.zahl("UML-KLMETH", nr, T, "UML-L1", bild + "Wie viele Methoden hat die Klasse?", len(meth), "Methoden erkennt man an den Klammern ().", s=1)
        priv = [z.split(":")[0][2:] for z in zeilen if z.startswith("-")]
        nicht = [z.split("(")[0][2:] if "(" in z else z.split(":")[0][2:] for z in zeilen if not z.startswith("-")]
        s.mehrfach("UML-KLPRIV", nr, T, "UML-L1", bild + "Welche Elemente sind **private**?", priv, nicht, "Private Elemente sind mit - gekennzeichnet.", s=1)
        m = meth[-1]
        rueck = m.split("):")[1].strip()
        s.wahl("UML-KLRUECK", nr, T, "UML-L1", bild + f"Welchen Rückgabetyp hat `{m[2:].split('(')[0]}`?", rueck,
               [x for x in ["void", "int", "double", "String", "boolean"] if x != rueck], "Der Rückgabetyp steht nach der Parameterklammer hinter dem Doppelpunkt; void = keine Rückgabe.", s=1)

    # ---------- UML-L2: Beziehungen ----------
    bez = [("Vererbung (Generalisierung)", "durchgezogene Linie mit leerem Dreieck zur Oberklasse"),
           ("Assoziation", "einfache durchgezogene Linie, ggf. mit Pfeil für die Navigationsrichtung"),
           ("Aggregation", "Linie mit leerer Raute am Ganzen"), ("Komposition", "Linie mit gefüllter Raute am Ganzen"),
           ("Realisierung (Interface)", "gestrichelte Linie mit leerem Dreieck zum Interface"), ("Abhängigkeit", "gestrichelte Linie mit offenem Pfeil")]
    zuordnung(s, "UML-BEZSYM", T, "UML-L2", bez, "Wie wird eine **{a}** im Klassendiagramm dargestellt?", "Welche Beziehung zeigt: {b}?", rng=rng)
    bsp = [("Ein Auto ist ein Fahrzeug.", "Vererbung (Generalisierung)"), ("Ein Gebäude besteht aus Räumen; ohne Gebäude gibt es die Räume nicht.", "Komposition"),
           ("Eine Fußballmannschaft hat Spieler; Spieler existieren auch ohne die Mannschaft.", "Aggregation"),
           ("Ein Kunde gibt Bestellungen auf.", "Assoziation"), ("Ein Hund ist ein Tier.", "Vererbung (Generalisierung)"),
           ("Eine Rechnung besteht aus Rechnungspositionen, die mit ihr gelöscht werden.", "Komposition"),
           ("Ein Warenkorb enthält Artikel, die es auch unabhängig gibt.", "Aggregation"), ("Ein Lehrer unterrichtet Schüler.", "Assoziation"),
           ("Die Klasse PdfExport implementiert das Interface Exportierbar.", "Realisierung (Interface)"),
           ("Ein Buch besteht aus Kapiteln, die ohne das Buch nicht existieren.", "Komposition"),
           ("Ein Girokonto ist ein Konto.", "Vererbung (Generalisierung)"), ("Eine Abteilung hat Mitarbeiter, die die Abteilung wechseln können.", "Aggregation")]
    zuordnung(s, "UML-BEZBSP", T, "UML-L2", bsp, "Welche Beziehung passt? {a}", None, schwierigkeit=2, rng=rng)
    mult = [("1", "genau eins"), ("0..1", "keins oder eins"), ("*", "beliebig viele (auch keins)"), ("0..*", "beliebig viele (auch keins)"),
            ("1..*", "mindestens eins"), ("2..5", "zwei bis fünf")]
    for i, (a, b) in enumerate(mult, 1):
        andere = list(dict.fromkeys(x for _, x in mult if x != b))
        rng.shuffle(andere)
        s.wahl("UML-MULT", i, T, "UML-L2", f"Was bedeutet die Multiplizität `{a}` an einer Assoziation?", b, andere[:3], f"{a} = {b}.", s=1)
    multbsp = [("Ein Kunde hat beliebig viele Bestellungen, jede Bestellung gehört zu genau einem Kunden. Welche Multiplizität steht an der Seite Bestellung?", "*"),
               ("… und welche an der Seite Kunde?", None),
               ("Ein Mitarbeiter hat höchstens einen Dienstwagen. Multiplizität an der Seite Dienstwagen?", "0..1"),
               ("Jede Bestellung enthält mindestens eine Position. Multiplizität an der Seite Position?", "1..*"),
               ("Ein Auto hat genau vier Räder. Multiplizität an der Seite Rad?", "4")]
    for i, (a, b) in enumerate([m for m in multbsp if m[1]], 1):
        s.wahl("UML-MULTBSP", i, T, "UML-L2", a, b, [x for x in ["1", "0..1", "*", "1..*", "4"] if x != b][:3],
               "Multiplizitäten werden an das Ende geschrieben, dessen Anzahl sie beschreiben.", s=2)

    # ---------- UML-L3: Use Case, Aktivität, weitere Diagramme ----------
    uc = [("Akteur (Strichmännchen)", "Person oder System außerhalb, das mit dem System interagiert"), ("Anwendungsfall (Ellipse)", "Funktion, die das System für einen Akteur erbringt"),
          ("Systemgrenze (Rechteck)", "trennt das System von seiner Umgebung"), ("«include»", "der Anwendungsfall wird immer mit ausgeführt"),
          ("«extend»", "der Anwendungsfall wird nur unter einer Bedingung ergänzt")]
    zuordnung(s, "UML-UC", T, "UML-L3", uc, "Was bedeutet im Use-Case-Diagramm: **{a}**?", "Welches Element im Use-Case-Diagramm: {b}?", rng=rng)
    akt = [("gefüllter Kreis", "Startknoten"), ("gefüllter Kreis mit Ring", "Endknoten (Aktivität endet)"), ("Rechteck mit abgerundeten Ecken", "Aktion"),
           ("Raute", "Verzweigung oder Zusammenführung"), ("dicker Balken", "Gabelung/Vereinigung paralleler Abläufe"), ("Kreis mit Kreuz", "Ablaufende (nur dieser Fluss endet)"),
           ("Schwimmbahn (Swimlane)", "ordnet Aktionen einem Verantwortlichen zu"), ("[Bedingung] an einer Kante", "Guard – der Weg wird nur genommen, wenn die Bedingung gilt")]
    zuordnung(s, "UML-AKT", T, "UML-L3", akt, "Was stellt im Aktivitätsdiagramm ein(e) **{a}** dar?", "Wie wird im Aktivitätsdiagramm ein(e) **{b}** dargestellt?", rng=rng)
    dia = [("Klassendiagramm", "statische Struktur: Klassen, Attribute, Methoden, Beziehungen"), ("Use-Case-Diagramm", "was das System aus Sicht der Akteure leistet"),
           ("Aktivitätsdiagramm", "Ablauf eines Prozesses mit Verzweigungen und Parallelität"), ("Sequenzdiagramm", "zeitliche Abfolge von Nachrichten zwischen Objekten"),
           ("Zustandsdiagramm", "Zustände eines Objekts und die Übergänge zwischen ihnen"), ("Komponentendiagramm", "Aufbau aus Softwarekomponenten und Schnittstellen"),
           ("Verteilungsdiagramm", "Verteilung von Software auf Hardware-Knoten"), ("Objektdiagramm", "Momentaufnahme konkreter Objekte mit Attributwerten")]
    zuordnung(s, "UML-DIA", T, "UML-L3", dia, "Was zeigt ein **{a}**?", "Welches UML-Diagramm zeigt: {b}?", rng=rng)
    art = [("Klassendiagramm", "Strukturdiagramm"), ("Komponentendiagramm", "Strukturdiagramm"), ("Objektdiagramm", "Strukturdiagramm"), ("Verteilungsdiagramm", "Strukturdiagramm"),
           ("Use-Case-Diagramm", "Verhaltensdiagramm"), ("Aktivitätsdiagramm", "Verhaltensdiagramm"), ("Sequenzdiagramm", "Verhaltensdiagramm"), ("Zustandsdiagramm", "Verhaltensdiagramm")]
    for i, (a, b) in enumerate(art, 1):
        s.mehrfach("UML-ART", i, T, "UML-L3", f"Ist das **{a}** ein Struktur- oder ein Verhaltensdiagramm?", [b],
                   ["Verhaltensdiagramm" if b == "Strukturdiagramm" else "Strukturdiagramm", "Kein UML-Diagramm"],
                   "Strukturdiagramme zeigen den Aufbau, Verhaltensdiagramme Abläufe und Interaktionen.", s=1)
    seq = [("Lebenslinie", "gestrichelte senkrechte Linie unter einem Objekt"), ("synchrone Nachricht", "durchgezogener Pfeil mit gefüllter Spitze, Sender wartet"),
           ("asynchrone Nachricht", "Pfeil mit offener Spitze, Sender wartet nicht"), ("Antwortnachricht", "gestrichelter Pfeil zurück zum Aufrufer"),
           ("Aktivierungsbalken", "schmales Rechteck auf der Lebenslinie, solange das Objekt aktiv ist"), ("alt-Fragment", "Alternative: je nach Bedingung ein Zweig")]
    zuordnung(s, "UML-SEQ", T, "UML-L3", seq, "Sequenzdiagramm: Wie wird ein(e) **{a}** dargestellt bzw. was bedeutet es?", "Was ist im Sequenzdiagramm: {b}?", rng=rng)
    return s.fragen

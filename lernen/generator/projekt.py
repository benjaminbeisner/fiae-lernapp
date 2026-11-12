from .basis import Sammler, aussagen, rng_fuer, zuordnung

T = "projektmanagement"


def netzplan(rng, n):
    namen = "ABCDEFGH"[:n]
    vor = {namen[0]: []}
    for k in range(1, n):
        moegl = list(namen[:k])
        anz = 1 if k < 2 else rng.choice([1, 1, 2])
        vor[namen[k]] = sorted(rng.sample(moegl[-3:], min(anz, len(moegl[-3:]))))
    # alle ohne Nachfolger außer dem letzten an den letzten hängen
    nach = {x: [y for y in namen if x in vor[y]] for x in namen}
    letzter = namen[-1]
    for x in namen[:-1]:
        if not nach[x] and x not in vor[letzter]:
            vor[letzter] = sorted(vor[letzter] + [x])
    nach = {x: [y for y in namen if x in vor[y]] for x in namen}
    dauer = {x: rng.randint(1, 8) for x in namen}
    faz, fez = {}, {}
    for x in namen:
        faz[x] = max((fez[v] for v in vor[x]), default=0)
        fez[x] = faz[x] + dauer[x]
    ende = fez[letzter]
    saz, sez = {}, {}
    for x in reversed(namen):
        sez[x] = min((saz[y] for y in nach[x]), default=ende)
        saz[x] = sez[x] - dauer[x]
    gp = {x: saz[x] - faz[x] for x in namen}
    fp = {x: (min((faz[y] for y in nach[x]), default=ende) - fez[x]) for x in namen}
    return namen, vor, dauer, faz, fez, saz, sez, gp, fp, ende


def wege(namen, vor):
    nach = {x: [y for y in namen if x in vor[y]] for x in namen}
    res = []

    def geh(x, pfad):
        if not nach[x]:
            res.append(pfad)
        for y in nach[x]:
            geh(y, pfad + [y])
    for s in [x for x in namen if not vor[x]]:
        geh(s, [s])
    return res


def erzeugen():
    s = Sammler()
    rng = rng_fuer("projekt")

    # ---------- PM-L3: Netzplan ----------
    nr = 0
    for runde in range(96):
        n = rng.choice([5, 6, 6, 7])
        namen, vor, dauer, faz, fez, saz, sez, gp, fp, ende = netzplan(rng, n)
        tab = "| Vorgang | Dauer (Tage) | Vorgänger |\n|---|---|---|\n" + "\n".join(
            f"| {x} | {dauer[x]} | {', '.join(vor[x]) or '–'} |" for x in namen)
        art = ["dauer", "faz", "saz", "gp", "fp", "krit"][runde % 6]
        x = rng.choice(namen[1:-1])
        nr += 1
        kopf = f"Gegeben ist folgende Vorgangsliste (Start bei Tag 0):\n\n{tab}\n\n"
        erkl_basis = "Vorwärtsrechnung: FAZ = größtes FEZ der Vorgänger, FEZ = FAZ + Dauer. Rückwärtsrechnung: SEZ = kleinstes SAZ der Nachfolger, SAZ = SEZ − Dauer. "
        werte = "; ".join(f"{y}: FAZ {faz[y]}, FEZ {fez[y]}, SAZ {saz[y]}, SEZ {sez[y]}, GP {gp[y]}" for y in namen)
        if art == "dauer":
            s.zahl("PM-NPDAUER", nr, T, "PM-L3", kopf + "Wie viele Tage dauert das Projekt mindestens?", ende, erkl_basis + werte + ".", einheit="Tage", s=3)
        elif art == "faz":
            s.zahl("PM-NPFAZ", nr, T, "PM-L3", kopf + f"Wie lautet der **frühestmögliche Anfangszeitpunkt (FAZ)** von Vorgang **{x}**?", faz[x], erkl_basis + werte + ".", s=2)
        elif art == "saz":
            s.zahl("PM-NPSAZ", nr, T, "PM-L3", kopf + f"Wie lautet der **spätestmögliche Anfangszeitpunkt (SAZ)** von Vorgang **{x}**?", saz[x], erkl_basis + werte + ".", s=3)
        elif art == "gp":
            s.zahl("PM-NPGP", nr, T, "PM-L3", kopf + f"Wie groß ist der **Gesamtpuffer** von Vorgang **{x}** in Tagen?", gp[x],
                   "Gesamtpuffer = SAZ − FAZ (bzw. SEZ − FEZ). " + werte + ".", einheit="Tage", s=3)
        elif art == "fp":
            s.zahl("PM-NPFP", nr, T, "PM-L3", kopf + f"Wie groß ist der **freie Puffer** von Vorgang **{x}** in Tagen?", fp[x],
                   f"Freier Puffer = kleinstes FAZ der Nachfolger − eigenes FEZ. Für {x}: FEZ {fez[x]}, freier Puffer {fp[x]}. " + werte + ".", einheit="Tage", s=3)
        else:
            alle = wege(namen, vor)
            krit = [w for w in alle if all(gp[y] == 0 for y in w)]
            if not krit or len(alle) < 3:
                continue
            r = " → ".join(krit[0])
            falsch = [" → ".join(w) for w in alle if w not in krit]
            if len(falsch) < 2:
                continue
            s.wahl("PM-NPKRIT", nr, T, "PM-L3", kopf + "Welcher Weg ist der **kritische Pfad**?", r, falsch,
                   "Der kritische Pfad besteht aus Vorgängen mit Gesamtpuffer 0 und ist der längste Weg. " + werte + ".", s=3)
    np_begr = [("FAZ", "frühester Anfangszeitpunkt"), ("FEZ", "frühester Endzeitpunkt"), ("SAZ", "spätester Anfangszeitpunkt"), ("SEZ", "spätester Endzeitpunkt"),
               ("GP (Gesamtpuffer)", "Zeit, um die ein Vorgang verschoben werden kann, ohne das Projektende zu gefährden"),
               ("FP (freier Puffer)", "Zeit, um die ein Vorgang verschoben werden kann, ohne den nächsten Vorgang zu verschieben"),
               ("kritischer Pfad", "Folge von Vorgängen ohne Puffer; Verzögerung verschiebt das Projektende")]
    zuordnung(s, "PM-NPBEGR", T, "PM-L3", np_begr, "Was bedeutet **{a}** im Netzplan?", "Welcher Begriff passt: {b}?", rng=rng)
    for i in range(1, 13):
        d = rng.randint(2, 9)
        faz = rng.randint(0, 20)
        art = rng.choice(["fez", "saz"])
        if art == "fez":
            s.zahl("PM-NPEINF", i, T, "PM-L3", f"Ein Vorgang hat FAZ = {faz} und dauert {d} Tage. Wie lautet sein FEZ?", faz + d, "FEZ = FAZ + Dauer.", s=1)
        else:
            sez = faz + d + rng.randint(0, 5)
            s.zahl("PM-NPEINF", i, T, "PM-L3", f"Ein Vorgang hat SEZ = {sez} und dauert {d} Tage. Wie lautet sein SAZ?", sez - d, "SAZ = SEZ − Dauer.", s=1)

    # ---------- PM-L1: Projekte, Ziele, Stakeholder ----------
    merkmale = ["Einmaligkeit", "zeitliche Begrenzung (Anfang und Ende)", "begrenzte Ressourcen", "klares Ziel", "eigene Projektorganisation", "Komplexität und Risiko"]
    aussagen(s, "PM-MERKMAL", T, "PM-L1", "Welche Merkmale kennzeichnen ein Projekt?", merkmale,
             ["regelmäßige Wiederholung derselben Tätigkeit", "unbegrenzte Laufzeit", "kein festes Budget", "Routineaufgabe im Tagesgeschäft"], n=10, k_richtig=(2, 3), rng=rng)
    projekt_ja = [("Einführung eines neuen ERP-Systems", "Projekt"), ("Umzug des Rechenzentrums", "Projekt"), ("tägliche Datensicherung", "kein Projekt (Routine)"),
                  ("Monatliche Gehaltsabrechnung", "kein Projekt (Routine)"), ("Entwicklung einer neuen Kunden-App", "Projekt"),
                  ("Passwort eines Nutzers zurücksetzen", "kein Projekt (Routine)"), ("Migration aller Clients auf ein neues Betriebssystem", "Projekt"),
                  ("Wöchentliches Einspielen von Updates", "kein Projekt (Routine)")]
    for i, (a, b) in enumerate(projekt_ja, 1):
        s.mehrfach("PM-ISTPROJ", i, T, "PM-L1", f"Ist das ein Projekt? **{a}**", [b], ["kein Projekt (Routine)" if b == "Projekt" else "Projekt"],
                   "Projekte sind einmalig, zeitlich begrenzt und zielgerichtet; wiederkehrende Aufgaben sind Routine.", s=1)
    smart = [("S", "spezifisch"), ("M", "messbar"), ("A", "attraktiv / akzeptiert"), ("R", "realistisch"), ("T", "terminiert")]
    zuordnung(s, "PM-SMART", T, "PM-L1", smart, "Wofür steht das **{a}** in SMART?", "Welcher Buchstabe von SMART steht für **{b}**?", rng=rng)
    ziele = [("„Die Seite soll schneller werden.“", "nicht SMART – weder messbar noch terminiert"),
             ("„Bis 30.06. sinkt die Ladezeit der Startseite auf unter 2 Sekunden.“", "SMART formuliert"),
             ("„Wir wollen irgendwann papierlos arbeiten.“", "nicht SMART – nicht terminiert und unspezifisch"),
             ("„Bis Ende Q3 sind 100 % der 40 Clients auf Windows 11 migriert.“", "SMART formuliert")]
    zuordnung(s, "PM-SMARTBSP", T, "PM-L1", ziele, "Wie ist dieses Ziel zu bewerten? {a}", None, rng=rng)
    stake = [("Auftraggeber", "beauftragt und finanziert das Projekt"), ("Projektleiter", "plant, steuert und überwacht das Projekt"),
             ("Lenkungsausschuss", "trifft übergeordnete Entscheidungen und genehmigt Meilensteine"), ("Endanwender", "arbeitet später mit dem Ergebnis"),
             ("Betriebsrat", "muss z. B. bei Systemen zur Leistungskontrolle mitbestimmen"), ("Datenschutzbeauftragter", "prüft den Umgang mit personenbezogenen Daten")]
    zuordnung(s, "PM-STAKE", T, "PM-L1", stake, "Welche Rolle hat **{a}** im Projekt?", "Wer {b}?", rng=rng)
    dreieck = [("Der Funktionsumfang steigt, Termin bleibt fest", "Kosten steigen oder Qualität sinkt"),
               ("Das Budget wird gekürzt", "Umfang/Qualität sinkt oder Termin verschiebt sich"),
               ("Der Termin wird vorgezogen", "mehr Kosten (Ressourcen) oder weniger Umfang/Qualität")]
    zuordnung(s, "PM-DREIECK", T, "PM-L1", dreieck, "Magisches Dreieck (Zeit, Kosten, Qualität/Umfang): {a}. Was folgt typischerweise?", None, schwierigkeit=2, rng=rng)
    phasen = [("Initialisierung", 1), ("Definition / Planung", 2), ("Durchführung", 3), ("Abschluss", 4)]
    for i, (p, n) in enumerate(phasen, 1):
        s.zahl("PM-PHASE", i, T, "PM-L1", f"Klassische Projektphasen: Initialisierung, Planung, Durchführung, Abschluss. An welcher Stelle (1–4) steht **{p}**?", n,
               "Reihenfolge: Initialisierung → Planung → Durchführung (mit Controlling) → Abschluss.", s=1)
    risiko = [("Eintrittswahrscheinlichkeit 20 %, Schaden 50.000 €", 10000), ("Eintrittswahrscheinlichkeit 5 %, Schaden 200.000 €", 10000),
              ("Eintrittswahrscheinlichkeit 40 %, Schaden 8.000 €", 3200), ("Eintrittswahrscheinlichkeit 10 %, Schaden 75.000 €", 7500),
              ("Eintrittswahrscheinlichkeit 25 %, Schaden 12.000 €", 3000), ("Eintrittswahrscheinlichkeit 60 %, Schaden 4.500 €", 2700)]
    for i, (a, w) in enumerate(risiko, 1):
        s.zahl("PM-RISIKO", i, T, "PM-L1", f"Risikoanalyse: {a}. Wie hoch ist der Risikowert (Erwartungswert) in €?", w,
               "Risikowert = Eintrittswahrscheinlichkeit × Schadenshöhe.", einheit="€", s=2)

    # ---------- PM-L2: Lasten- und Pflichtenheft ----------
    lp = [("wird vom Auftraggeber erstellt", "Lastenheft"), ("beschreibt, WAS und WOFÜR gefordert ist", "Lastenheft"),
          ("wird vom Auftragnehmer erstellt", "Pflichtenheft"), ("beschreibt, WIE und WOMIT die Anforderungen umgesetzt werden", "Pflichtenheft"),
          ("ist Grundlage für die Angebotserstellung durch Lieferanten", "Lastenheft"), ("ist Grundlage für die spätere Abnahme der Umsetzung", "Pflichtenheft"),
          ("enthält die Systemarchitektur und gewählte Technologien", "Pflichtenheft"), ("enthält die Anforderungen aus Sicht der Fachabteilung", "Lastenheft")]
    for i, (a, b) in enumerate(lp, 1):
        s.mehrfach("PM-LASTPFL", i, T, "PM-L2", f"Lastenheft oder Pflichtenheft? Das Dokument **{a}**.", [b], ["Pflichtenheft" if b == "Lastenheft" else "Lastenheft", "Projekthandbuch"],
                   "Lastenheft = Was/Wofür (Auftraggeber). Pflichtenheft = Wie/Womit (Auftragnehmer).", s=1)
    anf = [("Das System soll Rechnungen als PDF exportieren.", "funktionale Anforderung"), ("Die Suche liefert Ergebnisse in unter 1 Sekunde.", "nicht-funktionale Anforderung"),
           ("Nutzer können ihr Passwort zurücksetzen.", "funktionale Anforderung"), ("Die Anwendung ist zu 99,9 % verfügbar.", "nicht-funktionale Anforderung"),
           ("Die Oberfläche ist barrierefrei nach WCAG 2.1 AA.", "nicht-funktionale Anforderung"), ("Ein Admin kann Benutzer sperren.", "funktionale Anforderung"),
           ("Die Software läuft auf Windows und Linux.", "nicht-funktionale Anforderung"), ("Das System versendet eine Bestellbestätigung per E-Mail.", "funktionale Anforderung")]
    for i, (a, b) in enumerate(anf, 1):
        s.mehrfach("PM-ANFART", i, T, "PM-L2", f"Welche Art von Anforderung ist das? „{a}“", [b],
                   ["nicht-funktionale Anforderung" if b.startswith("funk") else "funktionale Anforderung", "Rahmenbedingung des Budgets"],
                   "Funktional = WAS das System tun soll. Nicht-funktional = WIE GUT (Leistung, Sicherheit, Verfügbarkeit, Bedienbarkeit, Plattform).", s=2)
    moscow = [("Must have", "zwingend erforderlich"), ("Should have", "wichtig, aber nicht zwingend für den Start"), ("Could have", "wünschenswert, wenn Zeit bleibt"),
              ("Won't have (this time)", "wird bewusst in dieser Version nicht umgesetzt")]
    zuordnung(s, "PM-MOSCOW", T, "PM-L2", moscow, "Was bedeutet **{a}** bei der MoSCoW-Priorisierung?", "Welche MoSCoW-Kategorie: {b}?", rng=rng)

    # ---------- PM-L4: Gantt, Meilensteine, Agil ----------
    scrum = [("Product Owner", "verantwortet und priorisiert das Product Backlog"), ("Scrum Master", "sorgt dafür, dass Scrum verstanden und gelebt wird, beseitigt Hindernisse"),
             ("Developers", "setzen die Backlog-Einträge im Sprint um"), ("Sprint", "fester Zeitraum von höchstens einem Monat, in dem ein Inkrement entsteht"),
             ("Daily Scrum", "tägliches 15-Minuten-Treffen des Teams"), ("Sprint Review", "Ergebnis wird mit Stakeholdern begutachtet"),
             ("Sprint Retrospektive", "Team verbessert seine Zusammenarbeit"), ("Sprint Planning", "Team plant Ziel und Arbeit des Sprints"),
             ("Product Backlog", "geordnete Liste aller Anforderungen an das Produkt"), ("Sprint Backlog", "Auswahl an Einträgen plus Plan für den aktuellen Sprint"),
             ("Inkrement", "nutzbares Ergebnis am Ende eines Sprints"), ("User Story", "Anforderung aus Nutzersicht: Als … möchte ich … damit …"),
             ("Definition of Done", "gemeinsames Verständnis, wann ein Eintrag fertig ist")]
    zuordnung(s, "PM-SCRUM", T, "PM-L4", scrum, "Was ist bzw. macht **{a}** in Scrum?", "Welches Scrum-Element: {b}?", rng=rng)
    modelle = [("Wasserfallmodell", "Phasen nacheinander, Rücksprünge kaum vorgesehen"), ("V-Modell", "jeder Entwicklungsphase steht eine Testphase gegenüber"),
               ("Scrum", "iterativ in Sprints mit festen Rollen und Events"), ("Kanban", "visualisiert Arbeit auf einem Board und begrenzt parallele Aufgaben (WIP-Limit)"),
               ("Spiralmodell", "iterative Zyklen mit expliziter Risikoanalyse"), ("Prototyping", "frühe lauffähige Muster zur Klärung der Anforderungen")]
    zuordnung(s, "PM-MODELL", T, "PM-L4", modelle, "Was kennzeichnet das Vorgehensmodell **{a}**?", "Welches Modell: {b}?", rng=rng)
    plan = [("Gantt-Diagramm", "Balkendiagramm der Vorgänge auf einer Zeitachse"), ("Meilenstein", "Ereignis ohne Dauer, markiert ein wichtiges Zwischenergebnis"),
            ("Projektstrukturplan (PSP)", "zerlegt das Projekt hierarchisch in Teilaufgaben und Arbeitspakete"), ("Arbeitspaket", "kleinste Einheit im PSP mit Verantwortlichem, Dauer und Kosten"),
            ("Netzplan", "zeigt Abhängigkeiten der Vorgänge und den kritischen Pfad"), ("Burndown-Chart", "zeigt die verbleibende Arbeit im Sprint über die Zeit"),
            ("Kanban-Board", "Spalten wie To Do, In Arbeit, Erledigt")]
    zuordnung(s, "PM-PLAN", T, "PM-L4", plan, "Was ist ein(e) **{a}**?", "Welches Planungsinstrument: {b}?", rng=rng)
    for i in range(1, 11):
        sp = rng.choice([20, 24, 30, 32, 40])
        tage = rng.choice([8, 9, 10])
        rest = rng.randint(1, tage - 1)
        erledigt = rng.randint(4, sp - 4)
        s.zahl("PM-VELO", i, T, "PM-L4", f"Ein Team hat in den letzten drei Sprints {sp - 2}, {sp} und {sp + 2} Story Points geschafft. Mit wie vielen Story Points (Durchschnitt) sollte es den nächsten Sprint planen?",
               sp, f"Velocity = Durchschnitt = ({sp-2} + {sp} + {sp+2}) ÷ 3 = {sp}.", s=1)
    return s.fragen

from .basis import Sammler, aussagen, rng_fuer, zuordnung

T = "kommunikation"


def erzeugen():
    s = Sammler()
    rng = rng_fuer("kommunikation")

    # ---------- KOM-L1: Kommunikationsmodelle ----------
    vier = [("„Der Drucker ist schon wieder leer.“ – Information, dass kein Papier/Toner da ist", "Sachinhalt"),
            ("„Ich bin total gestresst heute.“ – was der Sprecher über sich verrät", "Selbstoffenbarung"),
            ("„Kannst du das nicht einmal richtig machen?“ – was der Sprecher vom anderen hält", "Beziehung"),
            ("„Die Ampel ist grün.“ – gemeint: Fahr los!", "Appell"),
            ("„Das Meeting beginnt um 10 Uhr.“ – reine Information", "Sachinhalt"),
            ("„Du kennst dich ja mit Excel aus …“ – Wertschätzung oder Abwertung zwischen den Zeilen", "Beziehung"),
            ("„Mir ist kalt.“ – gemeint: Mach bitte das Fenster zu!", "Appell"),
            ("„Ich habe das Ticket schon dreimal bearbeitet.“ – der Sprecher zeigt seinen Frust", "Selbstoffenbarung"),
            ("„Könnten Sie mir bis Freitag das Angebot schicken?“ – Aufforderung", "Appell"),
            ("„Der Server lief 99,9 % der Zeit.“ – Daten und Fakten", "Sachinhalt")]
    for i, (a, b) in enumerate(vier, 1):
        s.mehrfach("KOM-4OHR", i, T, "KOM-L1", f"Welche Seite der Nachricht (Schulz von Thun) steht hier im Vordergrund? {a}", [b],
                   [x for x in ["Sachinhalt", "Selbstoffenbarung", "Beziehung", "Appell"] if x != b],
                   "Vier Seiten: Sachinhalt (worüber ich informiere), Selbstoffenbarung (was ich von mir zeige), Beziehung (was ich von dir halte), Appell (wozu ich dich bringen will).", s=2)
    ebenen = [("Wortwahl und Inhalt der Sätze", "verbal"), ("Lautstärke, Sprechtempo und Betonung", "paraverbal"), ("Mimik, Gestik und Körperhaltung", "nonverbal"),
              ("Blickkontakt", "nonverbal"), ("Tonfall (freundlich oder gereizt)", "paraverbal"), ("Fachbegriffe in einer E-Mail", "verbal"),
              ("verschränkte Arme", "nonverbal"), ("Pausen beim Sprechen", "paraverbal")]
    for i, (a, b) in enumerate(ebenen, 1):
        s.mehrfach("KOM-EBENE", i, T, "KOM-L1", f"Zu welcher Kommunikationsebene gehört: **{a}**?", [b], [x for x in ["verbal", "paraverbal", "nonverbal"] if x != b],
                   "Verbal = Worte; paraverbal = wie gesprochen wird (Stimme); nonverbal = Körpersprache.", s=1)
    modell = [("Sender", "verschlüsselt (codiert) eine Nachricht"), ("Empfänger", "entschlüsselt (decodiert) und interpretiert die Nachricht"),
              ("Kanal", "Weg der Übertragung, z. B. Telefon, E-Mail, persönlich"), ("Störung / Rauschen", "beeinträchtigt die Übertragung, z. B. Lärm oder Missverständnisse"),
              ("Feedback", "Rückmeldung des Empfängers an den Sender"), ("Eisbergmodell", "nur ein kleiner Teil der Kommunikation (Sachebene) ist sichtbar, der größere Teil (Beziehungsebene) liegt darunter")]
    zuordnung(s, "KOM-MODELL", T, "KOM-L1", modell, "Was bezeichnet **{a}** im Kommunikationsmodell?", "Welcher Begriff passt: {b}?", rng=rng)
    watz = ["Man kann nicht nicht kommunizieren.", "Jede Kommunikation hat einen Inhalts- und einen Beziehungsaspekt.",
            "Kommunikation ist immer Ursache und Wirkung (Interpunktion).", "Menschliche Kommunikation bedient sich analoger und digitaler Modalitäten.",
            "Kommunikation ist symmetrisch oder komplementär."]
    aussagen(s, "KOM-WATZ", T, "KOM-L1", "Welche Aussagen sind Axiome von Paul Watzlawick?", watz,
             ["Wer schweigt, kommuniziert nicht.", "Nur der Sachinhalt einer Nachricht ist wichtig.", "Kommunikation findet nur verbal statt.",
              "Eine Nachricht hat genau eine Bedeutung."], n=8, k_richtig=(1, 3), rng=rng)
    ich = [("„Du hörst mir nie zu!“", "Du-Botschaft"), ("„Ich fühle mich übergangen, wenn meine Idee nicht besprochen wird.“", "Ich-Botschaft"),
           ("„Du machst immer alles falsch.“", "Du-Botschaft"), ("„Ich brauche die Zahlen bis 12 Uhr, damit ich den Bericht abschließen kann.“", "Ich-Botschaft"),
           ("„Sie haben schon wieder vergessen, das Ticket zu schließen.“", "Du-Botschaft"), ("„Mir ist wichtig, dass wir pünktlich anfangen.“", "Ich-Botschaft")]
    for i, (a, b) in enumerate(ich, 1):
        s.mehrfach("KOM-ICHDU", i, T, "KOM-L1", f"Ich- oder Du-Botschaft? {a}", [b], ["Du-Botschaft" if b == "Ich-Botschaft" else "Ich-Botschaft", "Appell-Botschaft"],
                   "Ich-Botschaften beschreiben die eigene Wahrnehmung und wirken weniger angreifend als Du-Botschaften.", s=1)

    # ---------- KOM-L2: Kundengespräche, Fragetechniken ----------
    fragen = [("„Wie arbeiten Sie aktuell mit dem System?“", "offene Frage"), ("„Nutzen Sie Windows 11?“", "geschlossene Frage"),
              ("„Möchten Sie den Termin am Dienstag oder am Donnerstag?“", "Alternativfrage"), ("„Sie wollen doch sicher auch die Premium-Version, oder?“", "Suggestivfrage"),
              ("„Wer möchte schon Daten verlieren?“", "rhetorische Frage"), ("„Was genau meinen Sie mit ‚langsam‘?“", "offene Frage"),
              ("„Habe ich Sie richtig verstanden, dass der Fehler nur morgens auftritt?“", "Kontrollfrage"),
              ("„Wann ist der Fehler zum ersten Mal aufgetreten?“", "offene Frage"), ("„Ist der Drucker eingeschaltet?“", "geschlossene Frage"),
              ("„Warum fragen Sie das?“ als Antwort auf eine Frage", "Gegenfrage"), ("„Sie sind doch bestimmt auch der Meinung, dass das zu teuer ist?“", "Suggestivfrage"),
              ("„Sollen wir das per E-Mail oder telefonisch klären?“", "Alternativfrage")]
    zuordnung(s, "KOM-FRAGE", T, "KOM-L2", fragen, "Welche Fragetechnik wird verwendet? {a}", None, rng=rng)
    zweck = [("offene Frage", "Informationen sammeln, der Kunde erzählt ausführlich"), ("geschlossene Frage", "schnelle Bestätigung mit Ja/Nein"),
             ("Alternativfrage", "Entscheidung zwischen vorgegebenen Möglichkeiten herbeiführen"), ("Kontrollfrage", "sicherstellen, dass man richtig verstanden hat"),
             ("Suggestivfrage", "beeinflusst den Gesprächspartner in eine Richtung (vermeiden!)")]
    zuordnung(s, "KOM-FRAGEZW", T, "KOM-L2", zweck, "Wofür eignet sich eine **{a}** am besten?", "Welche Frageart dient dazu: {b}?", rng=rng)
    zuhoer = [("Paraphrasieren", "das Gehörte mit eigenen Worten wiederholen"), ("Verbalisieren", "die Gefühle des Gegenübers ansprechen"),
              ("Nachfragen", "unklare Punkte gezielt klären"), ("Zusammenfassen", "die wichtigsten Punkte am Ende bündeln"),
              ("Nonverbale Signale", "Nicken, Blickkontakt und zugewandte Haltung")]
    zuordnung(s, "KOM-ZUHOER", T, "KOM-L2", zuhoer, "Aktives Zuhören: Was bedeutet **{a}**?", "Welche Technik des aktiven Zuhörens: {b}?", rng=rng)
    aussagen(s, "KOM-BESCHW", T, "KOM-L2", "Ein verärgerter Kunde ruft wegen eines Ausfalls an. Wie verhältst du dich professionell?",
             ["ruhig bleiben und ausreden lassen", "Verständnis zeigen und das Problem zusammenfassen", "konkrete nächste Schritte und einen Termin nennen",
              "das Gespräch und die Lösung dokumentieren", "sachlich bleiben, auch wenn der Kunde laut wird"],
             ["dem Kunden die Schuld geben", "den Kunden unterbrechen und das Problem herunterspielen", "Versprechen machen, die nicht eingehalten werden können",
              "auflegen, wenn er laut wird", "mit Fachbegriffen beeindrucken"], n=10, k_richtig=(2, 3), rng=rng)
    phasen = [("Begrüßung und Kontaktaufnahme", 1), ("Bedarfsermittlung", 2), ("Lösungsvorschlag / Angebot", 3), ("Einwandbehandlung", 4), ("Abschluss und Verabschiedung", 5)]
    for i, (p, n) in enumerate(phasen, 1):
        s.zahl("KOM-PHASE", i, T, "KOM-L2", f"Ein Beratungsgespräch läuft typischerweise in 5 Phasen ab. An welcher Stelle steht **{p}**?", n,
               "Begrüßung → Bedarfsermittlung → Lösung/Angebot → Einwandbehandlung → Abschluss.", s=1)

    # ---------- KOM-L3: Arbeitsorganisation, Präsentation, KI ----------
    eis = [("Der Mailserver ist ausgefallen, alle warten.", "wichtig und dringend → sofort selbst erledigen"),
           ("Schulungskonzept für das nächste Quartal erstellen", "wichtig, nicht dringend → planen und terminieren"),
           ("Ein Kollege bittet um Toner für den Etagendrucker", "dringend, nicht wichtig → delegieren"),
           ("Newsletter von Anbietern durchlesen, die man nicht braucht", "weder wichtig noch dringend → nicht bearbeiten (Papierkorb)"),
           ("Die Lizenz der Firewall läuft heute Nacht ab", "wichtig und dringend → sofort selbst erledigen"),
           ("Dokumentation des Netzwerks aktualisieren (kein akuter Anlass)", "wichtig, nicht dringend → planen und terminieren"),
           ("Ein Anruf, der nur Kaffeebestellungen für das Team betrifft", "dringend, nicht wichtig → delegieren"),
           ("Sicherheitsupdate für eine aktiv ausgenutzte Lücke einspielen", "wichtig und dringend → sofort selbst erledigen"),
           ("Weiterbildung zur Cloud-Zertifizierung planen", "wichtig, nicht dringend → planen und terminieren"),
           ("Bunte Diagramme für eine interne Präsentation ohne Termin aufhübschen", "weder wichtig noch dringend → nicht bearbeiten (Papierkorb)")]
    zuordnung(s, "KOM-EISEN", T, "KOM-L3", eis, "Eisenhower-Matrix: Wie behandelst du diese Aufgabe? {a}", None, schwierigkeit=2, rng=rng)
    methode = [("Pareto-Prinzip", "mit 20 % des Aufwands lassen sich oft 80 % des Ergebnisses erreichen"), ("ALPEN-Methode", "Aufgaben notieren, Länge schätzen, Pufferzeit, Entscheidungen, Nachkontrolle"),
               ("ABC-Analyse", "Aufgaben nach Wichtigkeit in A, B und C einteilen"), ("Pomodoro-Technik", "25 Minuten konzentriert arbeiten, dann kurze Pause"),
               ("To-do-Liste", "Aufgaben sammeln und abhaken"), ("Mindmap", "Ideen um ein zentrales Thema verzweigt darstellen"),
               ("Brainstorming", "zunächst viele Ideen ohne Bewertung sammeln"), ("Kanban (persönlich)", "Aufgaben in Spalten To Do, Doing, Done visualisieren")]
    zuordnung(s, "KOM-METHODE", T, "KOM-L3", methode, "Was beschreibt die Methode **{a}**?", "Welche Methode: {b}?", rng=rng)
    praes = [("Einleitung", "Begrüßung, Thema, Ziel und Ablauf nennen"), ("Hauptteil", "Inhalte strukturiert und mit Beispielen darstellen"),
             ("Schluss", "Zusammenfassung, Fazit und Raum für Fragen"), ("Foliengestaltung", "wenig Text, gut lesbare Schrift, aussagekräftige Grafiken"),
             ("Zielgruppenanalyse", "Vorwissen und Erwartungen des Publikums klären")]
    zuordnung(s, "KOM-PRAES", T, "KOM-L3", praes, "Präsentation: Was gehört zu **{a}**?", "Welcher Teil/Schritt der Präsentation: {b}?", rng=rng)
    ki = ["Ergebnisse von KI-Werkzeugen auf Richtigkeit prüfen", "keine vertraulichen Kunden- oder Personaldaten in öffentliche KI-Dienste eingeben",
          "Urheberrechte und Lizenzen generierter Inhalte beachten", "betriebliche Regeln zur KI-Nutzung einhalten", "KI-Ausgaben können erfundene Fakten enthalten (Halluzinationen)"]
    aussagen(s, "KOM-KI", T, "KOM-L3", "Welche Aussagen zum Einsatz von KI-Werkzeugen im Betrieb treffen zu?", ki,
             ["KI-Ausgaben sind immer korrekt und müssen nicht geprüft werden", "Personenbezogene Daten dürfen ohne Weiteres in jeden KI-Chat kopiert werden",
              "Generierter Code ist automatisch sicher", "Für KI-Ergebnisse ist niemand verantwortlich"], n=10, k_richtig=(2, 3), rng=rng)
    team = [("Forming", "Orientierung: Teammitglieder lernen sich kennen, sind höflich und vorsichtig"), ("Storming", "Konflikte um Rollen und Vorgehen treten auf"),
            ("Norming", "Regeln und Rollen werden vereinbart, Zusammenhalt wächst"), ("Performing", "das Team arbeitet effektiv auf das Ziel hin"),
            ("Adjourning", "Auflösung des Teams nach Projektende")]
    zuordnung(s, "KOM-TEAM", T, "KOM-L3", team, "Teamphasen nach Tuckman: Was kennzeichnet **{a}**?", "Welche Teamphase: {b}?", rng=rng)
    konflikt = [("Win-win (Kooperation)", "beide Seiten erreichen ihre Interessen"), ("Kompromiss", "beide geben teilweise nach"),
                ("Durchsetzen", "eine Seite gewinnt auf Kosten der anderen"), ("Vermeiden", "der Konflikt wird nicht angesprochen"),
                ("Nachgeben", "eine Seite verzichtet zugunsten der anderen")]
    zuordnung(s, "KOM-KONFL", T, "KOM-L3", konflikt, "Konfliktlösung: Was bedeutet **{a}**?", "Welche Strategie: {b}?", rng=rng)
    return s.fragen

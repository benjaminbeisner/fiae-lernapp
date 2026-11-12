from .basis import Sammler, aussagen, rng_fuer, runden, zahl, zuordnung

T = "sicherheit"
V, I, A, AU = "Vertraulichkeit", "Integrität", "Verfügbarkeit", "Authentizität"


def erzeugen():
    s = Sammler()
    rng = rng_fuer("sicherheit")

    # ---------- SEC-L1: Schutzziele ----------
    massn = [("Verschlüsselung der Festplatte (BitLocker)", V), ("USV für den Server", A), ("Prüfsumme (Hash) beim Download vergleichen", I),
             ("RAID 1 für die Datenbankplatten", A), ("Zugriffsrechte nach dem Need-to-know-Prinzip", V), ("digitale Signatur einer E-Mail", AU),
             ("redundante Internetanbindung", A), ("TLS-verschlüsselte Webseite (Inhalt geheim halten)", V), ("Versionierung und Änderungsprotokoll von Dokumenten", I),
             ("Blickschutzfolie am Notebook", V), ("Klimaanlage im Serverraum", A), ("Zwei-Faktor-Anmeldung zur Identitätsprüfung", AU),
             ("regelmäßige Datensicherung", A), ("Zertifikat eines Webservers prüfen", AU), ("Eingabevalidierung gegen Manipulation von Datensätzen", I),
             ("Load Balancer mit mehreren Webservern", A), ("Aktenvernichter für Ausdrucke", V), ("Schreibschutz für Archivdaten (WORM)", I)]
    for i, (a, b) in enumerate(massn, 1):
        s.mehrfach("SEC-ZIELMASS", i, T, "SEC-L1", f"Welches Schutzziel wird durch diese Maßnahme **in erster Linie** unterstützt? {a}", [b],
                   [x for x in [V, I, A, AU] if x != b],
                   "Vertraulichkeit: nur Berechtigte sehen Daten. Integrität: Daten sind unverändert/korrekt. Verfügbarkeit: Systeme sind nutzbar. Authentizität: Echtheit von Absender/Daten.", s=2)
    bedr = [("Ein Bagger beschädigt die Glasfaserleitung zum Rechenzentrum.", A), ("Ein Angreifer liest unverschlüsselte Passwörter im WLAN mit.", V),
            ("Ein Virus verändert unbemerkt Zahlen in einer Tabelle.", I), ("Eine DDoS-Attacke legt den Webshop lahm.", A),
            ("Ein Notebook mit Kundendaten wird im Zug gestohlen.", V), ("Eine E-Mail gibt sich als Nachricht des Chefs aus.", AU),
            ("Ransomware verschlüsselt alle Dateien auf dem Server.", A), ("Ein Mitarbeiter ändert unberechtigt Gehaltsdaten.", I),
            ("Ein Kollege schaut beim Eintippen der PIN über die Schulter.", V), ("Ein Stromausfall legt den Serverraum lahm.", A)]
    for i, (a, b) in enumerate(bedr, 1):
        s.mehrfach("SEC-ZIELBED", i, T, "SEC-L1", f"Welches Schutzziel ist hier **vorrangig** verletzt? {a}", [b], [x for x in [V, I, A, AU] if x != b],
                   "Frage dich: Wurde etwas gelesen (V), verändert (I), unbenutzbar (A) oder gefälscht (Au)?", s=2)
    for i in range(1, 13):
        h = rng.choice([8760])
        p = rng.choice([99, 99.5, 99.9, 99.95, 99.99, 98, 97.5])
        art = rng.choice(["h", "min"])
        aus = h * (100 - p) / 100
        if art == "min":
            s.zahl("SEC-VERFUEG", i, T, "SEC-L1", f"Ein Dienst hat eine zugesicherte Verfügbarkeit von **{zahl(p)} %** pro Jahr (8.760 h). Wie viele **Minuten** Ausfall sind maximal erlaubt? (auf ganze Minuten)",
                   round(aus * 60), f"(100 − {zahl(p)}) % von 8.760 h = {zahl(aus)} h × 60 = {zahl(aus*60,0)} min.", einheit="min", tol=1, s=2)
        else:
            s.zahl("SEC-VERFUEG", i, T, "SEC-L1", f"Ein Dienst hat eine zugesicherte Verfügbarkeit von **{zahl(p)} %** pro Jahr (8.760 h). Wie viele **Stunden** Ausfall sind maximal erlaubt? (auf 2 Nachkommastellen)",
                   runden(aus), f"(100 − {zahl(p)}) % × 8.760 h = {zahl(aus)} h.", einheit="h", tol=0.01, s=2)
    schutzbedarf = [("normal", "Schadensauswirkungen sind begrenzt und überschaubar"), ("hoch", "Schadensauswirkungen können beträchtlich sein"),
                    ("sehr hoch", "Schadensauswirkungen können existenzbedrohend sein")]
    zuordnung(s, "SEC-SCHUTZB", T, "SEC-L1", schutzbedarf, "BSI-Schutzbedarfskategorie **{a}** bedeutet …", "Welche Schutzbedarfskategorie: {b}?", rng=rng)
    bsi = [("IT-Grundschutz-Kompendium", "Sammlung von Bausteinen mit Anforderungen für typische IT-Komponenten"), ("ISMS", "Managementsystem für Informationssicherheit, z. B. nach ISO 27001"),
           ("Maximumprinzip", "der höchste Schutzbedarf einer abhängigen Anwendung bestimmt den Schutzbedarf des Systems"),
           ("Kumulationseffekt", "viele kleine Schäden zusammen ergeben einen höheren Schutzbedarf"), ("Verteilungseffekt", "eine Anwendung ist auf mehrere Systeme verteilt, der Schutzbedarf des einzelnen Systems kann sinken")]
    zuordnung(s, "SEC-BSI", T, "SEC-L1", bsi, "Was bedeutet **{a}**?", "Welcher Begriff passt: {b}?", schwierigkeit=2, rng=rng)

    # ---------- SEC-L2: Verschlüsselung ----------
    alg = [("AES", "symmetrisch"), ("DES / 3DES", "symmetrisch"), ("ChaCha20", "symmetrisch"), ("Blowfish", "symmetrisch"), ("RSA", "asymmetrisch"),
           ("ECC (elliptische Kurven)", "asymmetrisch"), ("Diffie-Hellman", "asymmetrisch (Schlüsselaustausch)"), ("SHA-256", "Hashverfahren (keine Verschlüsselung)"),
           ("MD5", "Hashverfahren (keine Verschlüsselung)"), ("SHA-3", "Hashverfahren (keine Verschlüsselung)"), ("ElGamal", "asymmetrisch"), ("Twofish", "symmetrisch")]
    for i, (a, b) in enumerate(alg, 1):
        s.mehrfach("SEC-ALG", i, T, "SEC-L2", f"Zu welcher Art gehört **{a}**?", [b],
                   [x for x in ["symmetrisch", "asymmetrisch", "Hashverfahren (keine Verschlüsselung)", "asymmetrisch (Schlüsselaustausch)"] if x != b and not (b.startswith("asym") and x.startswith("asym"))],
                   "Symmetrisch: AES, DES, ChaCha20, Blowfish, Twofish. Asymmetrisch: RSA, ECC, ElGamal, Diffie-Hellman (Schlüsselaustausch). Hash: SHA-2/3, MD5.", s=1)
    for i in range(1, 16):
        n = rng.choice([3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100])
        art = rng.choice(["sym", "asym"])
        if art == "sym":
            s.zahl("SEC-SCHLANZ", i, T, "SEC-L2", f"**{n} Personen** wollen paarweise vertraulich kommunizieren. Wie viele Schlüssel werden bei **symmetrischer** Verschlüsselung benötigt?",
                   n * (n - 1) // 2, f"Jedes Paar braucht einen eigenen Schlüssel: n × (n − 1) ÷ 2 = {n} × {n-1} ÷ 2 = {n*(n-1)//2}.", s=2)
        else:
            s.zahl("SEC-SCHLANZ", i, T, "SEC-L2", f"**{n} Personen** wollen paarweise vertraulich kommunizieren. Wie viele Schlüssel werden bei **asymmetrischer** Verschlüsselung insgesamt benötigt?",
                   2 * n, f"Jede Person braucht ein Schlüsselpaar (öffentlich + privat): 2 × {n} = {2*n}.", s=2)
    wer = [("Alice will Bob eine vertrauliche Nachricht schicken. Womit verschlüsselt sie?", "mit Bobs öffentlichem Schlüssel"),
           ("Bob will die von Alice verschlüsselte Nachricht lesen. Womit entschlüsselt er?", "mit Bobs privatem Schlüssel"),
           ("Alice will eine Nachricht digital signieren. Womit signiert sie (den Hashwert)?", "mit Alices privatem Schlüssel"),
           ("Bob will Alices Signatur prüfen. Welchen Schlüssel braucht er?", "mit Alices öffentlichem Schlüssel")]
    for i, (a, b) in enumerate(wer, 1):
        alle = ["mit Bobs öffentlichem Schlüssel", "mit Bobs privatem Schlüssel", "mit Alices privatem Schlüssel", "mit Alices öffentlichem Schlüssel"]
        s.wahl("SEC-WERSCHL", i, T, "SEC-L2", a, b, [x for x in alle if x != b],
               "Verschlüsseln: öffentlicher Schlüssel des Empfängers. Signieren: eigener privater Schlüssel. Prüfen: öffentlicher Schlüssel des Absenders.", s=2)
    eig = [("schnell, auch für große Datenmengen geeignet", "symmetrische Verschlüsselung"), ("Problem: der gemeinsame Schlüssel muss sicher ausgetauscht werden", "symmetrische Verschlüsselung"),
           ("kein geheimer Schlüsselaustausch nötig, aber langsam", "asymmetrische Verschlüsselung"), ("Schlüsselpaar aus öffentlichem und privatem Schlüssel", "asymmetrische Verschlüsselung"),
           ("asymmetrisch einen Sitzungsschlüssel austauschen, dann symmetrisch verschlüsseln", "hybride Verschlüsselung"), ("Verfahren, das TLS/HTTPS nutzt", "hybride Verschlüsselung")]
    for i, (a, b) in enumerate(eig, 1):
        s.mehrfach("SEC-EIG", i, T, "SEC-L2", f"Welches Verfahren passt: **{a}**?", [b],
                   [x for x in ["symmetrische Verschlüsselung", "asymmetrische Verschlüsselung", "hybride Verschlüsselung"] if x != b], "Hybrid kombiniert die Vorteile beider Verfahren.", s=1)
    for i in range(1, 11):
        bit = rng.choice([40, 56, 64, 128, 256])
        mehr = rng.choice([1, 2, 8, 10, 16])
        s.zahl("SEC-BITS", i, T, "SEC-L2", f"Ein Schlüssel wird von {bit} auf {bit + mehr} Bit verlängert. Um welchen Faktor steigt die Anzahl möglicher Schlüssel?",
               2 ** mehr, f"Jedes zusätzliche Bit verdoppelt die Möglichkeiten: 2^{mehr} = {zahl(2**mehr,0)}.", s=2)

    # ---------- SEC-L3: Hash, Signatur, Zertifikat ----------
    hash_ = ["Aus dem Hashwert lässt sich die Eingabe nicht zurückrechnen.", "Kleine Änderungen der Eingabe ändern den Hashwert stark.",
             "Der Hashwert hat unabhängig von der Eingabegröße eine feste Länge.", "Gleiche Eingabe ergibt immer denselben Hashwert.",
             "Es soll praktisch unmöglich sein, zwei Eingaben mit gleichem Hash zu finden."]
    aussagen(s, "SEC-HASHEIG", T, "SEC-L3", "Welche Eigenschaften hat eine kryptografische Hashfunktion?", hash_,
             ["Ein Hashwert lässt sich mit dem richtigen Schlüssel wieder entschlüsseln.", "Der Hashwert ist immer so lang wie die Datei.",
              "MD5 gilt heute als sicher für Signaturen.", "Ein Hash garantiert die Vertraulichkeit der Daten."], n=10, k_richtig=(2, 3), rng=rng)
    sig = [("Hashwert der Nachricht bilden", 1), ("Hashwert mit dem privaten Schlüssel des Absenders verschlüsseln (Signatur)", 2),
           ("Nachricht und Signatur versenden", 3), ("Empfänger entschlüsselt die Signatur mit dem öffentlichen Schlüssel des Absenders", 4),
           ("Empfänger bildet selbst den Hash und vergleicht beide Werte", 5)]
    for i, (a, n) in enumerate(sig, 1):
        s.zahl("SEC-SIGABL", i, T, "SEC-L3", f"Digitale Signatur in 5 Schritten. An welcher Stelle steht: **{a}**?", n,
               "Hash bilden → mit privatem Schlüssel signieren → senden → mit öffentlichem Schlüssel prüfen → Hashwerte vergleichen.", s=2)
    zert = [("Zertifizierungsstelle (CA)", "bestätigt mit ihrer Signatur, dass ein öffentlicher Schlüssel zu einer Identität gehört"),
            ("X.509-Zertifikat", "enthält u. a. Inhaber, öffentlichen Schlüssel, Gültigkeitszeitraum und Signatur der CA"),
            ("Root-Zertifikat", "selbstsigniertes Zertifikat einer vertrauenswürdigen Stammzertifizierungsstelle"),
            ("Sperrliste (CRL) / OCSP", "prüft, ob ein Zertifikat vorzeitig widerrufen wurde"), ("PKI", "Infrastruktur zum Ausstellen, Verteilen und Prüfen von Zertifikaten"),
            ("selbstsigniertes Zertifikat", "vom Inhaber selbst unterschrieben, Browser zeigen eine Warnung"), ("Zertifikatskette", "Server-Zertifikat → Zwischenzertifikat → Root-Zertifikat"),
            ("HMAC", "Prüfsumme mit geheimem Schlüssel, sichert Integrität und Authentizität")]
    zuordnung(s, "SEC-ZERT", T, "SEC-L3", zert, "Was ist bzw. leistet **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)
    ziel_sig = [("digitale Signatur", "Integrität, Authentizität und Nichtabstreitbarkeit"), ("Verschlüsselung", "Vertraulichkeit"),
                ("Hashwert (ohne Schlüssel)", "Integrität (Erkennen von Veränderungen)"), ("TLS (HTTPS)", "Vertraulichkeit, Integrität und Authentizität des Servers")]
    zuordnung(s, "SEC-SIGZIEL", T, "SEC-L3", ziel_sig, "Welche Schutzziele unterstützt **{a}**?", None, schwierigkeit=2, rng=rng)
    protokolle = [("HTTPS", "HTTP über TLS"), ("SSH", "verschlüsselter Fernzugriff auf Server"), ("SFTP", "Dateiübertragung über SSH"),
                  ("IPsec", "verschlüsselt auf IP-Ebene, oft für Site-to-Site-VPN"), ("S/MIME", "Signatur und Verschlüsselung von E-Mails mit X.509-Zertifikaten"),
                  ("PGP / GPG", "E-Mail-Verschlüsselung mit Web of Trust"), ("WPA3", "aktueller Sicherheitsstandard für WLAN"), ("WireGuard", "schlankes modernes VPN-Protokoll")]
    zuordnung(s, "SEC-PROT", T, "SEC-L3", protokolle, "Was ist **{a}**?", "Welches Protokoll/Verfahren: {b}?", rng=rng)

    # ---------- SEC-L4: Anmeldung, Passwörter, 2FA ----------
    faktoren = [("Passwort", "Wissen"), ("PIN", "Wissen"), ("Sicherheitsfrage", "Wissen"), ("Smartcard", "Besitz"), ("Hardware-Token (z. B. FIDO2-Stick)", "Besitz"),
                ("Smartphone mit Authenticator-App", "Besitz"), ("Fingerabdruck", "Inhärenz (Biometrie)"), ("Gesichtserkennung", "Inhärenz (Biometrie)"),
                ("Iris-Scan", "Inhärenz (Biometrie)"), ("Einmal-Code per SMS", "Besitz")]
    for i, (a, b) in enumerate(faktoren, 1):
        s.mehrfach("SEC-FAKTOR", i, T, "SEC-L4", f"Zu welcher Faktorkategorie gehört **{a}**?", [b], [x for x in ["Wissen", "Besitz", "Inhärenz (Biometrie)"] if x != b],
                   "Wissen (etwas, das ich weiß), Besitz (etwas, das ich habe), Inhärenz (etwas, das ich bin).", s=1)
    kombi = [("Passwort + PIN", "keine Zwei-Faktor-Authentisierung (beides Wissen)"), ("Passwort + Code aus Authenticator-App", "Zwei-Faktor-Authentisierung"),
             ("Smartcard + PIN", "Zwei-Faktor-Authentisierung"), ("Fingerabdruck + Passwort", "Zwei-Faktor-Authentisierung"),
             ("Passwort + Sicherheitsfrage", "keine Zwei-Faktor-Authentisierung (beides Wissen)"), ("Hardware-Token + Fingerabdruck", "Zwei-Faktor-Authentisierung")]
    for i, (a, b) in enumerate(kombi, 1):
        s.mehrfach("SEC-2FA", i, T, "SEC-L4", f"Ist **{a}** eine Zwei-Faktor-Authentisierung?", [b],
                   [x for x in ["Zwei-Faktor-Authentisierung", "keine Zwei-Faktor-Authentisierung (beides Wissen)"] if x != b] + ["nur bei Administratoren"],
                   "2FA braucht zwei **verschiedene** Kategorien (Wissen, Besitz, Inhärenz).", s=1)
    for i in range(1, 16):
        zeichen, name = rng.choice([(10, "Ziffern (0–9)"), (26, "Kleinbuchstaben"), (52, "Groß- und Kleinbuchstaben"), (62, "Buchstaben und Ziffern")])
        laenge = rng.choice([4, 5, 6, 8]) if zeichen > 10 else rng.choice([4, 6, 8])
        while zeichen ** laenge >= 1e10:
            laenge -= 1
        s.zahl("SEC-KOMBI", i, T, "SEC-L4", f"Ein Passwort besteht aus genau **{laenge} Zeichen** aus **{zeichen} möglichen Zeichen** ({name}). Wie viele Kombinationen gibt es?",
               zeichen ** laenge, f"Zeichenvorrat ^ Länge = {zeichen}^{laenge} = {zahl(zeichen**laenge,0)}.", s=2)
    for i in range(1, 11):
        komb = rng.choice([10 ** 4, 10 ** 6, 26 ** 6, 62 ** 6, 10 ** 8])
        rate = rng.choice([1000, 10000, 100000, 1000000])
        sek = komb / rate
        s.zahl("SEC-BRUTE", i, T, "SEC-L4", f"Ein Angreifer testet **{zahl(rate,0)} Passwörter pro Sekunde**. Wie viele **Sekunden** braucht er höchstens für **{zahl(komb,0)} Kombinationen**? (auf 2 Nachkommastellen)",
               runden(sek), f"{zahl(komb,0)} ÷ {zahl(rate,0)} = {zahl(sek)} s (im Mittel die Hälfte).", einheit="s", tol=0.01, s=2)
    pw = ["mindestens 12 Zeichen oder eine lange Passphrase", "für jeden Dienst ein eigenes Passwort", "einen Passwortmanager verwenden",
          "wo möglich zusätzlich 2FA aktivieren", "Passwörter nach bekanntem Datenleck sofort ändern"]
    aussagen(s, "SEC-PWREGEL", T, "SEC-L4", "Welche Empfehlungen für Passwörter sind sinnvoll?", pw,
             ["das Passwort auf einem Zettel am Monitor notieren", "überall dasselbe starke Passwort nutzen", "den Namen des Haustiers verwenden",
              "Passwörter per E-Mail an Kollegen weitergeben", "nur Kleinbuchstaben verwenden, damit man es sich merken kann"], n=10, k_richtig=(2, 3), rng=rng)
    ident = [("Identifikation", "Benutzer gibt an, wer er ist (z. B. Benutzername)"), ("Authentisierung", "Benutzer legt einen Nachweis vor (z. B. Passwort)"),
             ("Authentifizierung", "System prüft den vorgelegten Nachweis"), ("Autorisierung", "System erteilt Rechte für bestimmte Aktionen"),
             ("Single Sign-on", "eine Anmeldung gilt für mehrere Anwendungen"), ("Least Privilege", "jeder erhält nur die Rechte, die er für seine Aufgabe braucht"),
             ("Passkey / FIDO2", "Anmeldung mit Schlüsselpaar statt Passwort, phishingresistent"), ("Salt", "Zufallswert, der vor dem Hashen an das Passwort angehängt wird")]
    zuordnung(s, "SEC-IDENT", T, "SEC-L4", ident, "Was bedeutet **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)

    # ---------- SEC-L5: Datensicherung ----------
    tage = ["Mo", "Di", "Mi", "Do", "Fr"]
    for i in range(1, 21):
        art = rng.choice(["inkrementell", "differenziell"])
        ausfall = rng.randint(1, 4)
        if art == "inkrementell":
            noetig = ["Vollsicherung (So)"] + [f"Inkrementell {t}" for t in tage[:ausfall]]
        else:
            noetig = ["Vollsicherung (So)", f"Differenziell {tage[ausfall-1]}"]
        s.zahl("SEC-RESTORE", i, T, "SEC-L5",
               f"Sonntags läuft eine Vollsicherung, montags bis freitags jeweils abends eine **{art}e** Sicherung. Am **{['Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag'][ausfall-1]}morgen** fällt der Server aus. "
               "Wie viele Sicherungen müssen mindestens zurückgespielt werden, um den Stand vom Vorabend herzustellen?",
               len(noetig), "Benötigt: " + ", ".join(noetig) + ". Inkrementell sichert die Änderungen seit der letzten Sicherung (alle Inkremente nötig), "
               "differenziell seit der letzten Vollsicherung (nur die letzte Differenz nötig).", s=2)
    for i in range(1, 16):
        voll = rng.choice([200, 400, 500, 800, 1000])
        aend = rng.choice([10, 20, 25, 40, 50])
        n = rng.choice([4, 5, 6])
        art = rng.choice(["inkrementell", "differenziell"])
        if art == "inkrementell":
            ges = voll + n * aend
            erkl = f"Jede inkrementelle Sicherung enthält nur die Änderungen eines Tages: {voll} + {n} × {aend} = {ges} GB."
        else:
            ges = voll + sum(aend * k for k in range(1, n + 1))
            erkl = f"Differenziell wächst täglich: {aend}, {2*aend}, … , {n*aend} GB. Summe mit Vollsicherung = {ges} GB."
        s.zahl("SEC-BACKUPVOL", i, T, "SEC-L5",
               f"Vollsicherung **{voll} GB**, danach **{n} Tage** lang **{art}e** Sicherungen. Täglich ändern sich **{aend} GB** (immer andere Daten). Wie viel Speicher belegen alle Sicherungen der Woche zusammen?",
               ges, erkl, einheit="GB", s=3)
    arten = [("Vollsicherung", "sichert alle Daten, braucht am meisten Platz und Zeit"), ("inkrementelle Sicherung", "sichert nur Änderungen seit der letzten Sicherung jeder Art"),
             ("differenzielle Sicherung", "sichert alle Änderungen seit der letzten Vollsicherung"), ("Spiegelung / Replikation", "hält eine aktuelle Kopie, schützt aber nicht vor Löschfehlern"),
             ("Snapshot", "Momentaufnahme eines Datenträgers oder einer VM zu einem Zeitpunkt"), ("Generationenprinzip (GFS)", "Großvater-Vater-Sohn: tägliche, wöchentliche und monatliche Sicherungen")]
    zuordnung(s, "SEC-BKART", T, "SEC-L5", arten, "Was kennzeichnet **{a}**?", "Welche Sicherungsart: {b}?", rng=rng)
    begriffe = [("3-2-1-Regel", "3 Kopien, 2 verschiedene Medien, 1 Kopie außer Haus"), ("RPO", "maximal tolerierbarer Datenverlust (Zeit seit letzter Sicherung)"),
                ("RTO", "maximal tolerierbare Zeit bis zur Wiederherstellung"), ("Offline-Backup", "Sicherung ohne ständige Verbindung zum Netz, schützt vor Ransomware"),
                ("Archivierung", "langfristige, unveränderte Aufbewahrung, z. B. wegen gesetzlicher Fristen"), ("Restore-Test", "regelmäßige Prüfung, ob sich Sicherungen wiederherstellen lassen")]
    zuordnung(s, "SEC-BKBEGR", T, "SEC-L5", begriffe, "Was bedeutet **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)
    for i in range(1, 11):
        gb = rng.choice([500, 1000, 2000, 4000])
        mbs = rng.choice([100, 150, 200, 250, 400])
        h = gb * 1000 / mbs / 3600
        s.zahl("SEC-BKZEIT", i, T, "SEC-L5", f"Eine Vollsicherung von **{zahl(gb)} GB** läuft mit **{mbs} MB/s**. Wie viele **Stunden** dauert sie? (auf 2 Nachkommastellen)",
               runden(h), f"{zahl(gb)} GB = {zahl(gb*1000)} MB ÷ {mbs} MB/s = {zahl(gb*1000/mbs)} s ÷ 3.600 = {zahl(h)} h.", einheit="h", tol=0.01, s=2)

    # ---------- SEC-L6: DSGVO ----------
    daten = [("Name und Anschrift eines Kunden", "personenbezogen"), ("IP-Adresse eines Website-Besuchers", "personenbezogen"),
             ("Gesundheitsdaten (Krankmeldung mit Diagnose)", "besondere Kategorie (Art. 9 DSGVO)"), ("Religionszugehörigkeit", "besondere Kategorie (Art. 9 DSGVO)"),
             ("Gewerkschaftszugehörigkeit", "besondere Kategorie (Art. 9 DSGVO)"), ("biometrische Daten zur Identifizierung (Fingerabdruck)", "besondere Kategorie (Art. 9 DSGVO)"),
             ("anonymisierte Umsatzstatistik ohne Personenbezug", "nicht personenbezogen"), ("Durchschnittstemperatur im Serverraum", "nicht personenbezogen"),
             ("Personalnummer eines Mitarbeiters", "personenbezogen"), ("E-Mail-Adresse vorname.nachname@firma.de", "personenbezogen"),
             ("ethnische Herkunft", "besondere Kategorie (Art. 9 DSGVO)"), ("Kfz-Kennzeichen eines Privatwagens", "personenbezogen")]
    for i, (a, b) in enumerate(daten, 1):
        s.mehrfach("SEC-DATENART", i, T, "SEC-L6", f"Wie sind diese Daten nach DSGVO einzuordnen? **{a}**", [b],
                   [x for x in ["personenbezogen", "besondere Kategorie (Art. 9 DSGVO)", "nicht personenbezogen"] if x != b],
                   "Personenbezogen: Bezug zu einer identifizierten oder identifizierbaren Person. Art. 9: Gesundheit, Religion, Herkunft, Biometrie, Gewerkschaft, Sexualleben u. a.", s=2)
    rechte = [("Auskunft über gespeicherte Daten", "Art. 15"), ("Berichtigung falscher Daten", "Art. 16"), ("Löschung („Recht auf Vergessenwerden“)", "Art. 17"),
              ("Einschränkung der Verarbeitung", "Art. 18"), ("Datenübertragbarkeit", "Art. 20"), ("Widerspruch gegen die Verarbeitung", "Art. 21")]
    zuordnung(s, "SEC-RECHTE", T, "SEC-L6", rechte, "In welchem Artikel der DSGVO steht das Recht auf **{a}**?", "Welches Betroffenenrecht regelt **{b} DSGVO**?", schwierigkeit=3, rng=rng)
    grund = [("Grundsatz der Zweckbindung", "Daten nur für festgelegte, eindeutige Zwecke verarbeiten"), ("Datenminimierung", "nur so viele Daten wie nötig erheben"),
             ("Speicherbegrenzung", "Daten löschen, sobald sie nicht mehr benötigt werden"), ("Rechtmäßigkeit", "Verarbeitung nur mit Rechtsgrundlage, z. B. Einwilligung oder Vertrag"),
             ("Richtigkeit", "Daten müssen sachlich richtig und aktuell sein"), ("Integrität und Vertraulichkeit", "Daten durch geeignete TOM schützen"),
             ("Rechenschaftspflicht", "Verantwortlicher muss die Einhaltung nachweisen können"), ("Transparenz", "Betroffene müssen verständlich informiert werden")]
    zuordnung(s, "SEC-GRUNDS", T, "SEC-L6", grund, "Was bedeutet der DSGVO-Grundsatz **{a}**?", "Welcher DSGVO-Grundsatz: {b}?", rng=rng)
    dsgvo_zahlen = [("Innerhalb von wie vielen Stunden muss eine Datenpanne der Aufsichtsbehörde gemeldet werden?", 72, "h"),
                    ("Innerhalb wie vieler Monate muss eine Auskunftsanfrage grundsätzlich beantwortet werden?", 1, "Monat"),
                    ("Ab wie vielen Personen, die ständig mit der automatisierten Verarbeitung personenbezogener Daten beschäftigt sind, ist in Deutschland ein Datenschutzbeauftragter Pflicht?", 20, "Personen"),
                    ("Bis zu wie viel Prozent des weltweiten Jahresumsatzes kann ein Bußgeld maximal betragen?", 4, "%")]
    for i, (a, w, eh) in enumerate(dsgvo_zahlen, 1):
        s.zahl("SEC-DSZAHL", i, T, "SEC-L6", a, w, "Meldung von Datenpannen: 72 h. Auskunft: 1 Monat. DSB in Deutschland ab 20 Personen (§ 38 BDSG). Bußgeld bis 20 Mio. € oder 4 % des Umsatzes.",
               einheit=eh, s=2)
    tom = [("Zutrittskontrolle", "Unbefugte kommen nicht in die Räume (Schlüssel, Chipkarte)"), ("Zugangskontrolle", "Unbefugte können Systeme nicht benutzen (Login, Sperrbildschirm)"),
           ("Zugriffskontrolle", "Berechtigte sehen nur die Daten, die sie brauchen (Rechtekonzept)"), ("Weitergabekontrolle", "Daten werden beim Transport geschützt (Verschlüsselung, VPN)"),
           ("Eingabekontrolle", "nachvollziehbar, wer wann welche Daten eingegeben oder geändert hat (Protokollierung)"),
           ("Verfügbarkeitskontrolle", "Daten sind gegen Verlust geschützt (Backup, USV)"), ("Pseudonymisierung", "Daten werden ohne Zusatzwissen keiner Person mehr zugeordnet"),
           ("Auftragsverarbeitungsvertrag (AVV)", "regelt die Verarbeitung durch einen Dienstleister im Auftrag")]
    zuordnung(s, "SEC-TOM", T, "SEC-L6", tom, "Was ist die Aufgabe von **{a}**?", "Welche Maßnahme/Kontrolle: {b}?", schwierigkeit=2, rng=rng)

    # ---------- SEC-L7: Schadsoftware, Angriffe ----------
    mal = [("Virus", "hängt sich an Dateien oder Programme und verbreitet sich, wenn diese ausgeführt werden"),
           ("Wurm", "verbreitet sich selbstständig über Netzwerke, ohne Wirtsdatei"), ("Trojaner", "tarnt sich als nützliches Programm und öffnet heimlich Zugang"),
           ("Ransomware", "verschlüsselt Daten und fordert Lösegeld"), ("Spyware", "spioniert Nutzerverhalten und Daten aus"), ("Keylogger", "zeichnet Tastatureingaben auf"),
           ("Rootkit", "versteckt sich tief im System und verschleiert Angreiferaktivitäten"), ("Botnetz", "ferngesteuerter Verbund infizierter Rechner, z. B. für DDoS"),
           ("Adware", "blendet ungewollt Werbung ein"), ("Backdoor", "versteckter Zugang unter Umgehung der Authentisierung")]
    zuordnung(s, "SEC-MAL", T, "SEC-L7", mal, "Was kennzeichnet **{a}**?", "Welche Schadsoftware {b}?", rng=rng)
    ang = [("Phishing", "gefälschte E-Mails oder Webseiten sollen Zugangsdaten abgreifen"), ("Spear-Phishing", "gezielte, persönlich zugeschnittene Phishing-Mail an bestimmte Personen"),
           ("CEO-Fraud", "Angreifer gibt sich als Chef aus und fordert eine dringende Überweisung"), ("Vishing", "Betrug per Telefonanruf"), ("Smishing", "Phishing per SMS"),
           ("Social Engineering", "Manipulation von Menschen, um an Informationen oder Zugang zu kommen"), ("Tailgating", "Unbefugter folgt einem Mitarbeiter durch eine gesicherte Tür"),
           ("Shoulder Surfing", "Ausspähen von Eingaben durch Über-die-Schulter-Schauen"), ("DDoS", "Überlastung eines Dienstes durch viele verteilte Anfragen"),
           ("Man-in-the-Middle", "Angreifer schaltet sich unbemerkt zwischen zwei Kommunikationspartner"), ("SQL-Injection", "Schadcode in Eingabefeldern verändert Datenbankabfragen"),
           ("Cross-Site-Scripting (XSS)", "Schadskript wird über eine Webseite im Browser anderer Nutzer ausgeführt"), ("Brute-Force", "systematisches Ausprobieren aller Passwörter"),
           ("Credential Stuffing", "erbeutete Zugangsdaten werden bei vielen anderen Diensten ausprobiert"), ("Zero-Day-Exploit", "Ausnutzen einer Lücke, für die es noch keinen Patch gibt"),
           ("Baiting", "präparierter USB-Stick wird ausgelegt, damit ihn jemand einsteckt")]
    zuordnung(s, "SEC-ANG", T, "SEC-L7", ang, "Was beschreibt **{a}**?", "Welcher Angriff: {b}?", rng=rng)
    schutz = [("SQL-Injection", "Prepared Statements / parametrisierte Abfragen"), ("Brute-Force auf Logins", "Kontosperre bzw. Verzögerung nach Fehlversuchen und 2FA"),
              ("Phishing", "Schulung der Mitarbeiter und Prüfen von Absender und Link"), ("Ransomware", "Offline-Backups und zeitnahes Patchen"),
              ("Man-in-the-Middle", "Ende-zu-Ende-Verschlüsselung und Zertifikatsprüfung"), ("Tailgating", "Vereinzelungsanlage und Sensibilisierung"),
              ("Cross-Site-Scripting", "Ausgaben im HTML maskieren (Escaping) und Content Security Policy"), ("Credential Stuffing", "für jeden Dienst ein eigenes Passwort und 2FA")]
    zuordnung(s, "SEC-SCHUTZ", T, "SEC-L7", schutz, "Welche Maßnahme schützt am besten gegen **{a}**?", None, schwierigkeit=2, rng=rng)
    phish = ["Absenderadresse passt nicht zur angeblichen Firma", "Zeitdruck oder Drohung („Konto wird heute gesperrt“)", "Link führt auf eine fremde Domain",
             "Aufforderung, Zugangsdaten einzugeben", "unerwarteter Anhang, z. B. .zip oder Office-Datei mit Makros"]
    aussagen(s, "SEC-PHISHMERK", T, "SEC-L7", "Woran erkennt man eine Phishing-Mail typischerweise?", phish,
             ["persönliche Anrede mit korrektem Namen beweist die Echtheit", "ein Firmenlogo im Text beweist die Echtheit", "HTTPS im Link beweist die Echtheit der Seite",
              "die Mail kam zu Bürozeiten"], n=10, k_richtig=(2, 3), rng=rng)
    sicher = [("Firewall", "filtert Netzwerkverkehr anhand von Regeln"), ("IDS", "erkennt verdächtigen Netzwerkverkehr und meldet ihn"),
              ("IPS", "erkennt Angriffe und blockiert sie aktiv"), ("DMZ", "separates Netzsegment für öffentlich erreichbare Server"),
              ("VPN", "verschlüsselter Tunnel über ein unsicheres Netz"), ("Sandbox", "isolierte Umgebung zum gefahrlosen Ausführen verdächtiger Dateien"),
              ("Honeypot", "absichtlich verwundbares Lockziel, um Angreifer zu beobachten"), ("Patchmanagement", "Sicherheitsupdates geplant und zeitnah einspielen"),
              ("Virenscanner (Endpoint Protection)", "erkennt Schadsoftware anhand von Signaturen und Verhalten")]
    zuordnung(s, "SEC-SICHER", T, "SEC-L7", sicher, "Was macht ein(e) **{a}**?", "Welche Schutzeinrichtung: {b}?", rng=rng)
    return s.fragen

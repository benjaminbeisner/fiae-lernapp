from .basis import Sammler, aussagen, rng_fuer, runden, zahl, zuordnung

T = "hardware"


def e(x):
    t = f"{runden(x, 2):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{t} €"


RAID = {
    0: ("Striping ohne Redundanz", 2, lambda n, g: n * g, 0),
    1: ("Spiegelung", 2, lambda n, g: g, None),
    5: ("Striping mit verteilter Parität", 3, lambda n, g: (n - 1) * g, 1),
    6: ("Striping mit doppelter Parität", 4, lambda n, g: (n - 2) * g, 2),
    10: ("Spiegelung und Striping kombiniert", 4, lambda n, g: n * g / 2, 1),
}


def erzeugen():
    s = Sammler()
    rng = rng_fuer("hardware")

    # ---------- HW-L3: RAID ----------
    for i in range(1, 26):
        lvl = rng.choice([0, 1, 5, 5, 6, 10])
        name, mind, kap, _ = RAID[lvl]
        if lvl == 1:
            n = 2
        elif lvl == 10:
            n = rng.choice([4, 6, 8])
        else:
            n = rng.randint(mind, 8)
        g = rng.choice([1, 2, 4, 8, 12, 16, 0.5])
        netto = kap(n, g)
        gtxt = f"{zahl(g*1000,0)} GB" if g < 1 else f"{zahl(g)} TB"
        s.zahl("HW-RAIDKAP", i, T, "HW-L3",
               f"Ein **RAID {lvl}** wird aus **{n} Festplatten** mit je **{gtxt}** gebaut. Wie viel **TB** Nutzkapazität stehen zur Verfügung?",
               netto, f"RAID {lvl} ({name}): " + {0: f"{n} × {zahl(g)} TB", 1: "Kapazität einer Platte", 5: f"({n} − 1) × {zahl(g)} TB",
                                                   6: f"({n} − 2) × {zahl(g)} TB", 10: f"{n} × {zahl(g)} TB ÷ 2"}[lvl] + f" = {zahl(netto)} TB.",
               einheit="TB", tol=0.01, s=2)
    for i in range(1, 16):
        lvl = rng.choice([0, 1, 5, 6, 10])
        name, mind, kap, _ = RAID[lvl]
        n = 2 if lvl == 1 else (rng.choice([4, 6, 8]) if lvl == 10 else rng.randint(mind, 8))
        g = rng.choice([1, 2, 4, 8])
        anteil = kap(n, g) / (n * g) * 100
        s.zahl("HW-RAIDANT", i, T, "HW-L3",
               f"Wie viel **Prozent** der Bruttokapazität sind bei einem **RAID {lvl}** aus **{n} gleich großen Platten** nutzbar? (auf 1 Nachkommastelle)",
               runden(anteil, 1), f"Nutzbar {zahl(kap(n, g))} TB von {zahl(n*g)} TB = {zahl(anteil,1)} %.", einheit="%", tol=0.1, s=2)
    for i, lvl in enumerate([0, 1, 5, 6, 10], 1):
        s.zahl("HW-RAIDMIN", i, T, "HW-L3", f"Wie viele Festplatten braucht ein **RAID {lvl}** mindestens?", RAID[lvl][1],
               "Mindestanzahl: RAID 0 → 2, RAID 1 → 2, RAID 5 → 3, RAID 6 → 4, RAID 10 → 4.", einheit="Platten", s=1)
    ausfall = [(0, "keine – fällt eine Platte aus, sind alle Daten verloren"), (1, "eine Platte (von zwei)"),
               (5, "genau eine beliebige Platte"), (6, "zwei beliebige Platten"), (10, "eine Platte pro Spiegelpaar")]
    zuordnung(s, "HW-RAIDAUS", T, "HW-L3", [(f"RAID {a}", b) for a, b in ausfall],
              "Wie viele Plattenausfälle verkraftet ein **{a}** ohne Datenverlust?", "Welches RAID verkraftet: {b}?", schwierigkeit=2, rng=rng)
    raidf = [("RAID 0", "Striping ohne Redundanz, maximale Geschwindigkeit"), ("RAID 1", "Spiegelung: alle Daten liegen doppelt vor"),
             ("RAID 5", "verteilte Parität, Nutzkapazität (n − 1) Platten"), ("RAID 6", "doppelte Parität, Nutzkapazität (n − 2) Platten"),
             ("RAID 10", "Stripeset aus gespiegelten Plattenpaaren")]
    zuordnung(s, "HW-RAIDBES", T, "HW-L3", raidf, "Was beschreibt **{a}**?", "Welches RAID-Level ist das: {b}?", rng=rng)
    aussagen(s, "HW-RAIDAUSS", T, "HW-L3", "Welche Aussagen zu RAID treffen zu?",
             ["Ein RAID ersetzt keine Datensicherung.", "RAID 1 erhöht die Ausfallsicherheit.", "RAID 0 erhöht die Lese- und Schreibgeschwindigkeit.",
              "Bei RAID 5 wird die Parität über alle Platten verteilt.", "Ein Hot-Spare springt automatisch für eine ausgefallene Platte ein."],
             ["RAID 0 schützt vor Datenverlust bei Plattenausfall.", "RAID schützt vor versehentlichem Löschen.",
              "RAID 1 verdoppelt die nutzbare Kapazität.", "Ein RAID 5 kann mit zwei Platten aufgebaut werden.", "Ransomware kann einem RAID 6 nichts anhaben."],
             n=10, k_richtig=(1, 3), rng=rng)

    # ---------- HW-L4: Strom und Energiekosten ----------
    geraete = [("ein Bürorechner", 45, 120), ("ein Monitor", 18, 35), ("ein Server", 180, 450), ("ein Switch", 25, 60),
               ("ein Laserdrucker", 15, 600), ("ein Notebook", 15, 65), ("ein NAS", 20, 45)]
    for i in range(1, 21):
        name, lo, hi = rng.choice(geraete)
        w = rng.randrange(lo, hi + 1, 5)
        std = rng.choice([8, 10, 12, 24])
        tage = rng.choice([220, 250, 365]) if std != 24 else 365
        preis = rng.choice([0.28, 0.30, 0.32, 0.35, 0.38, 0.40])
        kwh = w * std * tage / 1000
        s.zahl("HW-STROMKOSTEN", i, T, "HW-L4",
               f"{name[0].upper() + name[1:]} nimmt **{w} W** auf und läuft **{std} h am Tag** an **{tage} Tagen** im Jahr. Strompreis **{zahl(preis)} €/kWh**. Wie hoch sind die jährlichen Stromkosten?",
               runden(kwh * preis), f"{w} W × {std} h × {tage} = {zahl(w*std*tage)} Wh = {zahl(kwh)} kWh; × {zahl(preis)} € = {e(kwh*preis)}.",
               einheit="€", tol=0.02, s=2)
    for i in range(1, 16):
        w = rng.choice([20, 35, 60, 75, 100, 150, 250, 400, 650, 1200])
        std = rng.choice([1, 2, 5, 8, 10, 24, 100])
        s.zahl("HW-KWH", i, T, "HW-L4", f"Ein Gerät mit **{w} W** läuft **{std} Stunden**. Wie viele **kWh** verbraucht es?",
               runden(w * std / 1000, 3), f"{w} W × {std} h = {zahl(w*std)} Wh = {zahl(w*std/1000,3)} kWh.", einheit="kWh", tol=0.001, s=1)
    for i in range(1, 16):
        u = rng.choice([5, 12, 230])
        I = rng.choice([0.5, 1, 1.5, 2, 2.5, 3, 4, 10]) if u != 230 else rng.choice([0.2, 0.5, 1, 2, 4, 6.5])
        frag = rng.choice(["P", "I"])
        if frag == "P":
            s.zahl("HW-OHM", i, T, "HW-L4", f"Ein Gerät wird mit **{u} V** betrieben und nimmt **{zahl(I)} A** auf. Welche Leistung in **Watt** hat es?",
                   runden(u * I), f"P = U × I = {u} V × {zahl(I)} A = {zahl(u*I)} W.", einheit="W", tol=0.01, s=1)
        else:
            p = runden(u * I)
            s.zahl("HW-OHM", i, T, "HW-L4", f"Ein Netzteil liefert **{zahl(p)} W** bei **{u} V**. Welche Stromstärke in **Ampere** fließt?",
                   runden(I), f"I = P ÷ U = {zahl(p)} W ÷ {u} V = {zahl(I)} A.", einheit="A", tol=0.01, s=1)
    for i in range(1, 16):
        alt = rng.choice([120, 150, 200, 250, 350])
        neu = rng.choice([40, 60, 80, 100])
        anz = rng.choice([10, 15, 20, 25, 40, 60])
        std = rng.choice([8, 10])
        tage = rng.choice([220, 230, 250])
        preis = rng.choice([0.30, 0.32, 0.35])
        ers = (alt - neu) * std * tage * anz / 1000 * preis
        s.zahl("HW-ERSPARNIS", i, T, "HW-L4",
               f"**{anz} alte PCs** mit je **{alt} W** werden durch Geräte mit **{neu} W** ersetzt. Betrieb **{std} h/Tag** an **{tage} Tagen**, **{zahl(preis)} €/kWh**. Wie viel € werden pro Jahr gespart?",
               runden(ers), f"Differenz {alt-neu} W × {anz} Geräte × {std} h × {tage} Tage = {zahl((alt-neu)*anz*std*tage/1000)} kWh; × {zahl(preis)} € = {e(ers)}.",
               einheit="€", tol=0.05, s=3)
    for i in range(1, 13):
        wh = rng.choice([300, 450, 600, 900, 1200, 1500])
        last = rng.choice([150, 200, 300, 400, 450, 600])
        wg = rng.choice([1, 0.9, 0.8])
        minuten = wh * wg / last * 60
        txt = "" if wg == 1 else f" Davon sind nur **{int(wg*100)} %** nutzbar."
        s.zahl("HW-USV", i, T, "HW-L4",
               f"Eine USV hat einen Energiespeicher von **{wh} Wh**.{txt} Die angeschlossenen Geräte nehmen **{last} W** auf. Wie viele **Minuten** überbrückt sie? (auf 1 Nachkommastelle)",
               runden(minuten, 1), f"{wh} Wh" + ("" if wg == 1 else f" × {zahl(wg)}") + f" ÷ {last} W = {zahl(wh*wg/last,3)} h × 60 = {zahl(minuten,1)} min.",
               einheit="min", tol=0.1, s=2)
    for i in range(1, 11):
        va = rng.choice([500, 700, 1000, 1500, 2000, 3000])
        cos = rng.choice([0.6, 0.7, 0.8, 0.9])
        s.zahl("HW-VA", i, T, "HW-L4", f"Eine USV hat eine Scheinleistung von **{va} VA** und einen Leistungsfaktor von **{zahl(cos)}**. Wie viel Wirkleistung in **W** kann sie liefern?",
               runden(va * cos), f"P = S × cos φ = {va} VA × {zahl(cos)} = {zahl(va*cos)} W.", einheit="W", tol=0.01, s=2)
    usv = [("Offline-/Standby-USV (VFD)", "schaltet erst bei Netzausfall auf Batterie um, günstig, kurze Umschaltzeit"),
           ("Line-Interactive-USV (VI)", "regelt zusätzlich Spannungsschwankungen über einen Transformator aus"),
           ("Online-USV (VFI)", "versorgt die Last ständig über den Wechselrichter, keine Umschaltzeit")]
    zuordnung(s, "HW-USVART", T, "HW-L4", usv, "Was kennzeichnet eine **{a}**?", "Welche USV-Art {b}?", schwierigkeit=2, rng=rng)

    # ---------- HW-L1: Schnittstellen ----------
    schnitt = [("USB 2.0", "480 Mbit/s"), ("USB 3.2 Gen 1 (früher USB 3.0)", "5 Gbit/s"), ("USB 3.2 Gen 2", "10 Gbit/s"),
               ("USB 3.2 Gen 2x2", "20 Gbit/s"), ("Thunderbolt 3/4 bzw. USB4 (40)", "40 Gbit/s"), ("SATA III", "6 Gbit/s"),
               ("Gigabit-Ethernet", "1 Gbit/s"), ("Fast Ethernet", "100 Mbit/s"), ("10-Gigabit-Ethernet", "10 Gbit/s")]
    zuordnung(s, "HW-SCHRATE", T, "HW-L1", schnitt, "Welche maximale Brutto-Datenrate hat **{a}**?", "Welche Schnittstelle hat eine Datenrate von **{b}**?",
              schwierigkeit=2, rng=rng)
    zweck = [("HDMI", "überträgt digital Bild und Ton, typisch für Monitore, Beamer und TVs"),
             ("DisplayPort", "digitale Monitorschnittstelle, unterstützt Daisy-Chaining mehrerer Monitore (MST)"),
             ("USB-C", "verdrehsicherer Stecker, kann Daten, Video und Strom (Power Delivery) übertragen"),
             ("RJ45", "Stecker für Twisted-Pair-Netzwerkkabel"), ("M.2 (NVMe)", "Steckplatz für sehr schnelle SSDs über PCI Express"),
             ("SATA", "Anschluss für 2,5\"/3,5\"-Festplatten und SSDs"), ("PCI Express", "Steckplatz für Grafik-, Netzwerk- und Erweiterungskarten"),
             ("VGA", "analoge Bildschnittstelle, veraltet"), ("Bluetooth", "Funk-Nahbereichsverbindung für Headsets, Mäuse und Tastaturen"),
             ("LWL (Glasfaser)", "überträgt Daten mit Licht, unempfindlich gegen elektromagnetische Störungen"),
             ("Power over Ethernet (PoE)", "versorgt Geräte wie Access Points über das Netzwerkkabel mit Strom")]
    zuordnung(s, "HW-SCHZWECK", T, "HW-L1", zweck, "Was beschreibt **{a}** am besten?", "Welche Schnittstelle/Technik {b}?", rng=rng)
    kabel = [("Cat 5e", "1 Gbit/s"), ("Cat 6", "1 Gbit/s (10 Gbit/s bis 55 m)"), ("Cat 6A", "10 Gbit/s bis 100 m"), ("Cat 8", "25/40 Gbit/s bis 30 m")]
    zuordnung(s, "HW-KABEL", T, "HW-L1", kabel, "Welche Datenrate ist mit einem **{a}**-Kabel typischerweise möglich?", None, schwierigkeit=3, rng=rng)
    for i, (n, mx) in enumerate([("Twisted-Pair-Kupferkabel (Ethernet)", 100), ("USB 2.0 passiv", 5)], 1):
        s.zahl("HW-LAENGE", i, T, "HW-L1", f"Wie viele Meter darf ein **{n}** maximal lang sein (Standardangabe)?", mx,
               "Twisted Pair: 100 m pro Strecke (90 m fest + 10 m Patch). USB 2.0 passiv: 5 m.", einheit="m", s=2)

    # ---------- HW-L2: CPU, RAM, Speicher ----------
    komp = [("CPU", "führt Befehle aus und steuert die Verarbeitung"), ("Arbeitsspeicher (RAM)", "flüchtiger Speicher für laufende Programme und Daten"),
            ("Cache", "sehr schneller Zwischenspeicher direkt an der CPU"), ("ROM / Flash mit UEFI", "enthält die Firmware zum Starten des Rechners"),
            ("GPU", "berechnet Grafik, auch für parallele Berechnungen (KI) genutzt"), ("SSD", "nicht flüchtiger Speicher ohne bewegliche Teile"),
            ("HDD", "Magnetspeicher mit rotierenden Scheiben und Schreib-Lese-Kopf"), ("Chipsatz", "verbindet CPU mit Schnittstellen und Peripherie auf dem Mainboard"),
            ("Netzteil", "wandelt Wechselspannung in die Gleichspannungen für die Komponenten"), ("TPM", "Sicherheitschip, speichert Schlüssel z. B. für BitLocker")]
    zuordnung(s, "HW-KOMP", T, "HW-L2", komp, "Welche Aufgabe hat **{a}**?", "Welche Komponente: {b}?", rng=rng)
    vgl = [("Kein Datenverlust bei Stromausfall", "SSD und HDD, nicht RAM"), ("Sehr kurze Zugriffszeit, unempfindlich gegen Erschütterung", "SSD"),
           ("Günstigster Preis pro Terabyte bei großen Kapazitäten", "HDD"), ("Daten gehen beim Ausschalten verloren", "RAM")]
    zuordnung(s, "HW-SPVGL", T, "HW-L2", vgl, "Welche Speicherart passt? {a}", None, rng=rng)
    begriffe = [("Taktfrequenz", "Anzahl der Arbeitstakte pro Sekunde, angegeben in GHz"), ("Mehrkernprozessor", "mehrere Rechenkerne auf einem Chip für parallele Verarbeitung"),
                ("Hyper-Threading / SMT", "ein physischer Kern bearbeitet zwei Threads gleichzeitig"), ("TDP", "Wärmeleistung, die die Kühlung abführen können muss"),
                ("Dual-Channel", "zwei RAM-Module werden parallel angesprochen, höhere Bandbreite"), ("ECC-RAM", "erkennt und korrigiert Speicherfehler, typisch in Servern"),
                ("Virtualisierung", "mehrere virtuelle Maschinen laufen auf einer physischen Hardware"), ("IOPS", "Ein-/Ausgabeoperationen pro Sekunde eines Speichers"),
                ("UEFI", "Nachfolger des BIOS, unterstützt Secure Boot und GPT-Laufwerke"), ("Secure Boot", "startet nur signierte Bootloader")]
    zuordnung(s, "HW-BEGR", T, "HW-L2", begriffe, "Was bedeutet **{a}**?", "Welcher Begriff passt: {b}?", schwierigkeit=2, rng=rng)
    for i in range(1, 11):
        mhz = rng.choice([3200, 4800, 5600, 6000, 2666, 3600])
        bus = 64
        kanal = rng.choice([1, 2])
        gbs = mhz * 1e6 * bus / 8 * kanal / 1e9
        s.zahl("HW-RAMBAND", i, T, "HW-L2",
               f"RAM mit **{mhz} MT/s**, 64-Bit-Bus, **{'Dual' if kanal == 2 else 'Single'}-Channel**. Wie hoch ist die theoretische Bandbreite in **GB/s**? (auf 1 Nachkommastelle)",
               runden(gbs, 1), f"{mhz} × 10⁶ × 8 Byte" + (" × 2 Kanäle" if kanal == 2 else "") + f" = {zahl(gbs,1)} GB/s.", einheit="GB/s", tol=0.1, s=3)

    # ---------- HW-L5: Ergonomie, Green IT ----------
    ergo = [("Bildschirm-Oberkante", "auf Augenhöhe oder leicht darunter"), ("Sehabstand zum Monitor", "etwa 50–80 cm (Armlänge)"),
            ("Monitor zum Fenster", "seitlich, Blickrichtung parallel zum Fenster"), ("Ellenbogenwinkel beim Tippen", "etwa 90° oder etwas mehr"),
            ("Füße", "stehen flach auf dem Boden oder einer Fußstütze"), ("Bildschirmpausen", "regelmäßige kurze Unterbrechungen bzw. Tätigkeitswechsel"),
            ("Darstellung", "dunkle Schrift auf hellem Grund, flimmerfrei und entspiegelt")]
    zuordnung(s, "HW-ERGO", T, "HW-L5", ergo, "Ergonomischer Bildschirmarbeitsplatz – was gilt für: **{a}**?", None, schwierigkeit=1, rng=rng)
    siegel = [("Blauer Engel", "deutsches Umweltzeichen, u. a. für energiesparende und recyclinggerechte Geräte"),
              ("Energy Star", "Kennzeichen für energieeffiziente Bürogeräte"), ("TCO Certified", "Nachhaltigkeitszertifikat für IT-Produkte inkl. sozialer Kriterien"),
              ("EU-Energielabel", "Effizienzklassen A bis G, z. B. für Monitore"), ("CE-Kennzeichnung", "Hersteller erklärt die Einhaltung der EU-Vorschriften (kein Qualitäts- oder Umweltsiegel)"),
              ("80 PLUS", "Effizienzkennzeichnung für Netzteile"), ("WEEE / ElektroG", "regelt Rücknahme und Entsorgung von Elektroaltgeräten")]
    zuordnung(s, "HW-SIEGEL", T, "HW-L5", siegel, "Wofür steht **{a}**?", "Welches Zeichen/Regelwerk: {b}?", schwierigkeit=2, rng=rng)
    aussagen(s, "HW-GREEN", T, "HW-L5", "Welche Maßnahmen gehören zu Green IT?",
             ["Energiesparmodi und automatisches Abschalten nutzen", "Server virtualisieren und konsolidieren", "Geräte länger nutzen und reparieren",
              "Altgeräte fachgerecht recyceln", "Thin Clients statt leistungsstarker PCs einsetzen", "Drucke reduzieren und Duplexdruck nutzen"],
             ["Bildschirmschoner mit Animation statt Standby", "Jedes Jahr alle Geräte ersetzen", "Server dauerhaft mit voller Last laufen lassen",
              "Altgeräte über den Hausmüll entsorgen"], n=10, k_richtig=(2, 3), rng=rng)
    for i in range(1, 11):
        kauf = rng.choice([600, 800, 1000, 1200, 1500])
        strom = rng.choice([30, 45, 60, 80, 120])
        wart = rng.choice([50, 80, 100, 150])
        jahre = rng.choice([3, 4, 5])
        tco = kauf + jahre * (strom + wart)
        s.zahl("HW-TCO", i, T, "HW-L5",
               f"TCO-Rechnung: Anschaffung **{e(kauf)}**, Strom **{e(strom)}/Jahr**, Wartung/Support **{e(wart)}/Jahr**, Nutzung **{jahre} Jahre**. Wie hoch sind die Gesamtkosten?",
               tco, f"{e(kauf)} + {jahre} × ({e(strom)} + {e(wart)}) = {e(tco)}.", einheit="€", tol=0.01, s=2)
    return s.fragen

"""Aufgabenbereich: IT-Arbeitsplatz, Hardware, Energie, Beschaffung und Wirtschaft."""
from .bausteine_basis import CODE, F, K, N, R, T, TAB, Z, eur, zahl


def angebotsvergleich(rng, k):
    menge = rng.choice([8, 10, 12, 15, 20])
    a = (rng.choice([649, 699, 729, 749, 799]), rng.choice([5, 8, 10]), rng.choice([2, 3]), rng.choice([0, 49, 89]))
    b = (rng.choice([619, 659, 689, 709]), rng.choice([0, 3, 5]), rng.choice([0, 2]), rng.choice([0, 39, 120]))
    def bp(x):
        lp = menge * x[0]
        zep = lp * (1 - x[1] / 100)
        bar = zep * (1 - x[2] / 100)
        return lp, zep, bar, bar + x[3]
    ra, rb = bp(a), bp(b)
    besser = "A" if ra[3] < rb[3] else "B"
    kopf = ["", "Angebot A", "Angebot B"]
    zeilen = [["Listenpreis je Gerät (netto)", eur(a[0]), eur(b[0])], ["Rabatt", f"{a[1]} %", f"{b[1]} %"],
              ["Skonto bei Zahlung in 10 Tagen", f"{a[2]} %", f"{b[2]} %"], ["Versandkosten gesamt", eur(a[3]), eur(b[3])]]
    return {"thema": "wirtschaft", "intro": f"Für die {k['name']} sollen **{menge} Notebooks** beschafft werden. Zwei Angebote liegen vor:",
            "teile": [
                T("Berechnen Sie für beide Angebote den Bezugspreis der gesamten Lieferung. Skonto wird genutzt. Der Rechenweg ist anzugeben.", 5,
                  TAB(["Kalkulationsschritt", "Angebot A", "Angebot B"],
                      [["Listeneinkaufspreis", None, None], ["− Rabatt = Zieleinkaufspreis", None, None],
                       ["− Skonto = Bareinkaufspreis", None, None], ["+ Bezugskosten = Bezugspreis", None, None]]),
                  f"A: {eur(ra[0])} → {eur(ra[1])} → {eur(ra[2])} → **{eur(ra[3])}**. B: {eur(rb[0])} → {eur(rb[1])} → {eur(rb[2])} → **{eur(rb[3])}**. "
                  "Je richtig berechneter Zeile ca. 0,5 Punkte je Angebot, Folgefehler werden berücksichtigt.", daten=TAB(kopf, zeilen),
                  erwartet=[N(ra[i], 0.05) if j == 0 else N(rb[i], 0.05) for i in range(4) for j in range(2)]),
                T("Nennen Sie das günstigere Angebot und zwei weitere Kriterien, die neben dem Preis bei der Auswahl berücksichtigt werden sollten.", 3, Z(3),
                  f"Angebot {besser} ist günstiger (1 P.). Weitere Kriterien (je 1 P.), z. B. Lieferzeit, Garantie/Service, Zuverlässigkeit des Lieferanten, "
                  "Kompatibilität, Energieverbrauch, Zahlungsbedingungen."),
            ]}


def nutzwert(rng, k):
    krit = rng.sample(["Preis", "Leistung", "Service", "Energieverbrauch", "Garantie", "Lieferzeit"], 3)
    g = rng.choice([(50, 30, 20), (40, 35, 25), (40, 40, 20), (30, 50, 20)])
    p = {n: [rng.randint(4, 10) for _ in krit] for n in ["X", "Y"]}
    nw = {n: sum(a * b for a, b in zip(p[n], g)) / 100 for n in p}
    sieger = max(nw, key=nw.get)
    return {"thema": "wirtschaft", "intro": "Für einen neuen Monitor soll eine Nutzwertanalyse durchgeführt werden (Punkte 1 bis 10).",
            "teile": [
                T("Vervollständigen Sie die Nutzwertanalyse und ermitteln Sie das zu empfehlende Produkt.", 5,
                  TAB(["Kriterium", "Gewichtung", "Punkte X", "gewichtet X", "Punkte Y", "gewichtet Y"],
                      [[krit[i], f"{g[i]} %", str(p["X"][i]), None, str(p["Y"][i]), None] for i in range(3)] + [["Summe", "100 %", "", None, "", None]]),
                  "Gewichtete Punkte = Punkte × Gewichtung. " + "; ".join(f"{krit[i]}: X {zahl(p['X'][i]*g[i]/100)}, Y {zahl(p['Y'][i]*g[i]/100)}" for i in range(3))
                  + f". Summe X = **{zahl(nw['X'])}**, Y = **{zahl(nw['Y'])}** → Produkt {sieger} empfehlen" + (" (Gleichstand: weitere Kriterien heranziehen)" if nw['X'] == nw['Y'] else "") + ".",
                  erwartet=[N(p[n][i] * g[i] / 100, 0.01) for i in range(3) for n in ("X", "Y")] + [N(nw["X"], 0.01), N(nw["Y"], 0.01)]),
                T("Nennen Sie einen Vorteil und einen Nachteil der Nutzwertanalyse.", 2, Z(3),
                  "Vorteil: auch nicht-monetäre Kriterien werden vergleichbar, Entscheidung wird nachvollziehbar. Nachteil: Gewichtung und Punktvergabe sind subjektiv."),
            ]}


def energiekosten(rng, k):
    alt, neu = rng.choice([120, 140, 160, 180]), rng.choice([35, 45, 55, 65])
    n = rng.choice([12, 15, 20, 25, 30])
    std, tage, preis = rng.choice([8, 9, 10]), rng.choice([220, 230, 250]), rng.choice([0.30, 0.32, 0.35, 0.38])
    ers = (alt - neu) * n * std * tage / 1000 * preis
    return {"thema": "hardware", "intro": f"Bei der {k['name']} sollen **{n} Desktop-PCs** mit je **{alt} W** durch Mini-PCs mit **{neu} W** ersetzt werden. "
            f"Die Geräte laufen **{std} Stunden** an **{tage} Tagen** im Jahr, eine kWh kostet **{zahl(preis)} EUR**.",
            "teile": [
                T("Berechnen Sie die jährliche Ersparnis an Stromkosten. Der Rechenweg ist anzugeben.", 4, R(5),
                  f"({alt} W − {neu} W) × {n} × {std} h × {tage} = {zahl((alt-neu)*n*std*tage)} Wh = {zahl((alt-neu)*n*std*tage/1000)} kWh; "
                  f"× {zahl(preis)} EUR = **{eur(ers)}**.", erwartet=[N(ers, 0.05)]),
                T("Nennen Sie zwei weitere Maßnahmen der Green IT am Arbeitsplatz.", 2, Z(3),
                  "z. B. Energiesparmodus/automatisches Abschalten, schaltbare Steckdosenleisten, Geräte mit Energielabel/Blauer Engel, Thin Clients, Duplexdruck, längere Nutzung/Reparatur, fachgerechtes Recycling."),
            ]}


def usv(rng, k):
    wh, last = rng.choice([600, 900, 1200, 1500]), rng.choice([200, 300, 400, 450])
    wg = rng.choice([0.8, 0.9])
    m = wh * wg / last * 60
    return {"thema": "hardware", "intro": f"Der neue Server der {k['name']} soll über eine USV abgesichert werden.",
            "teile": [
                T(f"Die USV hat eine Batteriekapazität von **{wh} Wh**, davon sind **{int(wg*100)} %** nutzbar. Server und Switch nehmen zusammen **{last} W** auf. "
                  "Berechnen Sie die Überbrückungszeit in Minuten (auf eine Nachkommastelle).", 3, R(4),
                  f"{wh} Wh × {zahl(wg)} = {zahl(wh*wg)} Wh; ÷ {last} W = {zahl(wh*wg/last,3)} h × 60 = **{zahl(m,1)} min**.", erwartet=[N(m, 0.1)]),
                T("Beschreiben Sie den Unterschied zwischen einer Offline-USV (VFD) und einer Online-USV (VFI).", 3, Z(4),
                  "Offline/VFD: Last hängt im Normalbetrieb direkt am Netz, bei Ausfall wird mit kurzer Umschaltzeit auf Batterie umgeschaltet; günstig. "
                  "Online/VFI: Last wird ständig über Gleichrichter/Wechselrichter versorgt, keine Umschaltzeit, filtert Störungen; teurer, für kritische Server."),
            ]}


def raid(rng, k):
    n, g = rng.choice([4, 5, 6]), rng.choice([2, 4, 8])
    return {"thema": "hardware", "intro": f"Im Server sollen **{n} Festplatten** mit je **{g} TB** eingesetzt werden.",
            "teile": [
                T("Ermitteln Sie die nutzbare Kapazität für die folgenden RAID-Level.", 3, TAB(["RAID-Level", "Nutzkapazität in TB", "Ausfallsicherheit (Anzahl Platten)"],
                  [["RAID 0", None, None], ["RAID 5", None, None], ["RAID 6", None, None]]),
                  f"RAID 0: {n*g} TB, 0 Platten. RAID 5: {(n-1)*g} TB, 1 Platte. RAID 6: {(n-2)*g} TB, 2 Platten. Je Zeile 1 Punkt.",
                  erwartet=[N(n * g), N(0), N((n - 1) * g), N(1), N((n - 2) * g), N(2)]),
                T("Ein Kollege meint, durch das RAID sei keine Datensicherung mehr nötig. Nehmen Sie Stellung.", 2, Z(3),
                  "Falsch: RAID schützt nur vor Plattenausfall, nicht vor versehentlichem Löschen, Ransomware, Brand, Diebstahl oder logischen Fehlern. Backup bleibt nötig."),
            ]}


def schnittstellen(rng, k):
    return {"thema": "hardware", "intro": "An den neuen Arbeitsplätzen sollen zwei Monitore, ein Headset und eine Dockingstation genutzt werden.",
            "teile": [
                T("Ordnen Sie den Anforderungen jeweils eine geeignete Schnittstelle zu.", 4,
                  TAB(["Anforderung", "Schnittstelle"], [["Zwei Monitore hintereinander an einem Ausgang (Daisy Chain)", None],
                                                          ["Notebook laden, Bild und Daten über ein Kabel", None],
                                                          ["Kabelloses Headset im Nahbereich", None], ["Netzwerk mit 1 Gbit/s per Kabel", None]]),
                  "DisplayPort (MST) bzw. Thunderbolt; USB-C mit Power Delivery/Thunderbolt; Bluetooth; RJ45/Gigabit-Ethernet. Je 1 Punkt.",
                  erwartet=[K("displayport", "dp", "thunderbolt"), K("usb-c", "usb c", "usbc", "thunderbolt", "usb4", "usb 4"), K("bluetooth", "bt"),
                            K("rj45", "rj-45", "rj 45", "ethernet", "lan", "twisted")]),
                T("Nennen Sie die maximale Brutto-Datenrate von USB 3.2 Gen 1 und von USB 2.0.", 2, F("USB 3.2 Gen 1:", "USB 2.0:"),
                  "USB 3.2 Gen 1: 5 Gbit/s; USB 2.0: 480 Mbit/s.", erwartet=[N(5), N(480)]),
            ]}


def ergonomie(rng, k):
    return {"thema": "hardware", "intro": "Die Mitarbeitenden klagen über Nacken- und Augenbeschwerden an den neuen Bildschirmarbeitsplätzen.",
            "teile": [T("Nennen Sie vier Anforderungen an einen ergonomischen Bildschirmarbeitsplatz.", 4, Z(5),
                        "z. B. Bildschirmoberkante auf/unter Augenhöhe, Sehabstand ca. 50–80 cm, Monitor seitlich zum Fenster, entspiegelt, höhenverstellbarer Stuhl/Tisch, "
                        "Unterarme waagerecht, Füße flach, ausreichende Beleuchtung, regelmäßige Pausen. Je 1 Punkt.")]}


def leasing(rng, k):
    kauf, rate, mon = rng.choice([4800, 6000, 7200]), rng.choice([150, 180, 210, 240]), rng.choice([24, 36])
    ges = rate * mon
    return {"thema": "wirtschaft", "intro": f"Ein neuer Multifunktionsdrucker kostet **{eur(kauf)}**. Alternativ wird ein Leasing mit **{eur(rate)}** pro Monat über **{mon} Monate** angeboten.",
            "teile": [
                T("Berechnen Sie die Differenz zwischen Leasing-Gesamtkosten und Kaufpreis.", 2, R(3),
                  f"{mon} × {eur(rate)} = {eur(ges)}; − {eur(kauf)} = **{eur(ges-kauf)}**" + (" (Leasing teurer)." if ges > kauf else " (Leasing günstiger)."),
                  erwartet=[N(ges - kauf, 0.05)]),
                T("Nennen Sie zwei Vorteile des Leasings gegenüber dem Kauf.", 2, Z(3),
                  "z. B. schont Liquidität/kein hoher Kapitaleinsatz, planbare Raten als Betriebsausgabe, Austausch gegen neue Geräte nach Laufzeit, Service oft enthalten."),
                T(f"Bei einem Kauf wird linear über **5 Jahre** abgeschrieben. Berechnen Sie den jährlichen Abschreibungsbetrag und den Restbuchwert nach 2 Jahren.", 2,
                  F("Abschreibung pro Jahr:", "Restbuchwert nach 2 Jahren:"), f"{eur(kauf)} ÷ 5 = **{eur(kauf/5)}**; Restbuchwert {eur(kauf)} − 2 × {eur(kauf/5)} = **{eur(kauf*3/5)}**.",
                  erwartet=[N(kauf / 5, 0.05), N(kauf * 3 / 5, 0.05)]),
            ]}


def vertragsarten(rng, k):
    return {"thema": "wirtschaft", "intro": f"Die {k['name']} möchte zwei Leistungen beauftragen: (1) die Erstellung einer individuellen Netzwerkdokumentation, (2) monatlich 10 Stunden Vor-Ort-Support.",
            "teile": [
                T("Ordnen Sie beiden Leistungen die passende Vertragsart zu und begründen Sie kurz.", 4,
                  TAB(["Leistung", "Vertragsart", "Begründung"], [["Netzwerkdokumentation", None, None], ["Vor-Ort-Support", None, None]]),
                  "(1) Werkvertrag: ein Ergebnis/Erfolg ist geschuldet, Abnahme. (2) Dienstvertrag: Tätigkeit ist geschuldet, kein bestimmter Erfolg. Je 2 Punkte.",
                  erwartet=[K("werkvertrag", "werk"), None, K("dienstvertrag", "dienst"), None]),
                T("Die gelieferten Monitore haben Pixelfehler. Nennen Sie das Recht, das der Käufer zuerst geltend machen muss, und zwei Rechte, die danach möglich sind.", 3, Z(3),
                  "Zuerst Nacherfüllung (Nachbesserung oder Ersatzlieferung). Danach (bei Fehlschlagen): Rücktritt, Minderung, ggf. Schadensersatz."),
            ]}


def kamera_speicher(rng, k):
    mbit, n, std = rng.choice([4, 6, 8, 12]), rng.choice([4, 6, 8]), rng.choice([24, 48, 72])
    tb = mbit * n * std * 3600 / 8 / 1_000_000
    return {"thema": "einheiten", "intro": f"Für das Lager werden **{n} Überwachungskameras** installiert. Jede Kamera erzeugt einen Videostrom von **{mbit} Mbit/s**.",
            "teile": [
                T(f"Berechnen Sie den Speicherbedarf in **TB**, wenn die Aufnahmen aller Kameras **{std} Stunden** aufbewahrt werden (1 TB = 10¹² Byte, auf zwei Nachkommastellen). Der Rechenweg ist anzugeben.", 4, R(6),
                  f"{mbit} Mbit/s × {n} × {zahl(std*3600)} s = {zahl(mbit*n*std*3600)} Mbit ÷ 8 = {zahl(mbit*n*std*3600/8)} MB = **{zahl(tb)} TB**.", erwartet=[N(tb, 0.01)]),
                T("Nennen Sie eine Vorgabe der DSGVO, die bei der Videoüberwachung beachtet werden muss.", 1, Z(2),
                  "z. B. Hinweisschild/Transparenz, Zweckbindung, Speicherbegrenzung/Löschfrist, Datenminimierung, Mitbestimmung Betriebsrat."),
            ]}


def festplatte_anzeige(rng, k):
    tb = rng.choice([1, 2, 4, 8])
    tib = tb * 10**12 / 2**40
    return {"thema": "einheiten", "teile": [
        T(f"Ein Kunde beschwert sich: Seine neue **{tb}-TB-SSD** wird vom Betriebssystem nur mit etwa **{zahl(tib)} TB** angezeigt. Erklären Sie die Ursache und belegen Sie sie mit einer Rechnung.", 4, Z(5),
          f"Hersteller rechnen dezimal (1 TB = 10¹² Byte), das Betriebssystem binär (1 TiB = 2⁴⁰ Byte), zeigt aber „TB“ an. {tb} × 10¹² ÷ 2⁴⁰ = **{zahl(tib)} TiB**. Es fehlt kein Speicher."),
    ]}


def tco(rng, k):
    a, s, w, j = rng.choice([900, 1100, 1300]), rng.choice([40, 60, 80]), rng.choice([90, 120, 150]), rng.choice([4, 5])
    b = (a - 250, s + 30, w + 20)
    ta, tb = a + j * (s + w), b[0] + j * (b[1] + b[2])
    return {"thema": "hardware", "teile": [
        T(f"Vergleichen Sie zwei Arbeitsplatzrechner über **{j} Jahre** anhand der Gesamtkosten (TCO).", 4,
          TAB(["", "Rechner 1", "Rechner 2"], [["Anschaffung", eur(a), eur(b[0])], ["Strom pro Jahr", eur(s), eur(b[1])],
                                                 ["Wartung pro Jahr", eur(w), eur(b[2])], [f"TCO über {j} Jahre", None, None]]),
          f"Rechner 1: {eur(a)} + {j} × {eur(s+w)} = **{eur(ta)}**; Rechner 2: {eur(b[0])} + {j} × {eur(b[1]+b[2])} = **{eur(tb)}**. Je 2 Punkte.",
          erwartet=[N(ta, 0.05), N(tb, 0.05)]),
    ]}


def ssd_hdd(rng, k):
    return {"thema": "hardware", "teile": [
        T("Für den Dateiserver werden SSDs und HDDs verglichen. Nennen Sie je einen Vorteil von SSD und HDD sowie einen Einsatzzweck, für den HDDs weiterhin sinnvoll sind.", 3, Z(4),
          "SSD: kurze Zugriffszeit, hohe IOPS, robust, leise, sparsam. HDD: günstiger pro TB, hohe Kapazitäten. Einsatz HDD: Backup-/Archivspeicher, große Datenablagen (NAS)."),
    ]}


BAUSTEINE = [angebotsvergleich, nutzwert, energiekosten, usv, raid, schnittstellen, ergonomie, leasing, vertragsarten,
             kamera_speicher, festplatte_anzeige, tco, ssd_hdd]

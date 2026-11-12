from .basis import Sammler, aussagen, rng_fuer, runden, zahl, zuordnung

T = "wirtschaft"
PRODUKTE = ["Notebooks", "Monitore", "Dockingstationen", "Headsets", "Drucker", "Switches", "Tastatur-Maus-Sets", "Tablets",
            "Webcams", "USV-Anlagen", "SSD-Laufwerke", "Server-Racks", "Lizenzpakete", "Access Points"]


def e(x):
    """Euro-Betrag mit zwei Nachkommastellen."""
    t = f"{runden(x, 2):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{t} €"


def erzeugen():
    s = Sammler()
    rng = rng_fuer("wirtschaft")

    # ---------- WIR-L1: Rabatt, Skonto, USt, Bezugskalkulation ----------
    for i in range(1, 16):
        preis = rng.choice([450, 799, 1200, 1499, 2350, 3600, 4800, 980, 12500, 650, 2890])
        r = rng.choice([5, 8, 10, 12, 15, 20, 25])
        erg = preis * (1 - r / 100)
        s.zahl("WIR-RABATT", i, T, "WIR-L1",
               f"Der Listenpreis beträgt **{e(preis)}** netto. Der Lieferant gewährt **{r} % Rabatt**. Wie hoch ist der Zieleinkaufspreis in €?",
               runden(erg), f"{e(preis)} − {r} % ({e(preis*r/100)}) = {e(erg)}.", einheit="€", tol=0.01, s=1)
    for i in range(1, 16):
        betrag = rng.choice([1180, 2400, 3520, 845, 9900, 15600, 499.90, 1234.56, 7250])
        sk = rng.choice([2, 3])
        erg = betrag * (1 - sk / 100)
        s.zahl("WIR-SKONTO", i, T, "WIR-L1",
               f"Eine Rechnung über **{e(betrag)}** wird innerhalb der Skontofrist bezahlt (**{sk} % Skonto**). Welcher Betrag wird überwiesen?",
               runden(erg), f"Skonto: {e(betrag*sk/100)}. {e(betrag)} − {e(betrag*sk/100)} = {e(erg)}.", einheit="€", tol=0.01, s=1)
    for i in range(1, 16):
        netto = rng.choice([100, 250, 420, 799, 1250, 2000, 3480, 89.90, 15000, 640])
        st = 19
        s.zahl("WIR-BRUTTO", i, T, "WIR-L1", f"Ein Artikel kostet **{e(netto)}** netto. Wie hoch ist der Bruttopreis bei 19 % Umsatzsteuer?",
               runden(netto * 1.19), f"{e(netto)} × 1,19 = {e(netto*1.19)}.", einheit="€", tol=0.01, s=1)
    for i in range(1, 16):
        brutto = rng.choice([119, 595, 1190, 2380, 357, 4760, 999, 1499, 249.90, 714])
        s.zahl("WIR-NETTO", i, T, "WIR-L1", f"Ein Angebot nennt **{e(brutto)}** brutto (inkl. 19 % USt). Wie hoch ist der Nettopreis?",
               runden(brutto / 1.19), f"{e(brutto)} ÷ 1,19 = {e(brutto/1.19)} (nicht × 0,81 rechnen!).", einheit="€", tol=0.01, s=2)
    for i in range(1, 16):
        brutto = rng.choice([119, 595, 1190, 2380, 357, 4760, 999, 1499, 249.90, 714])
        s.zahl("WIR-UST", i, T, "WIR-L1", f"Wie viel Umsatzsteuer (19 %) ist in einem Bruttobetrag von **{e(brutto)}** enthalten?",
               runden(brutto - brutto / 1.19), f"Netto = {e(brutto)} ÷ 1,19 = {e(brutto/1.19)}; USt = {e(brutto - brutto/1.19)}.", einheit="€", tol=0.01, s=2)
    for i in range(1, 21):
        menge = rng.choice([5, 8, 10, 12, 20, 25, 40])
        stueck = rng.choice([89, 129, 249, 389, 549, 799, 1150])
        r = rng.choice([5, 10, 15, 20])
        sk = rng.choice([2, 3])
        fracht = rng.choice([0, 25, 49, 60, 120, 150])
        lp = menge * stueck
        zep = lp * (1 - r / 100)
        bp = zep * (1 - sk / 100) + fracht
        prod = rng.choice(PRODUKTE)
        s.zahl("WIR-BEZUG", i, T, "WIR-L1",
               f"Bezugskalkulation: {menge} {prod} zu je **{e(stueck)}** netto, **{r} % Rabatt**, **{sk} % Skonto**, Versandkosten **{e(fracht)}**. "
               f"Wie hoch ist der Bezugspreis (Einstandspreis) der gesamten Lieferung?",
               runden(bp), f"Listenpreis {e(lp)} − {r} % Rabatt = {e(zep)} (Zieleinkaufspreis) − {sk} % Skonto = {e(zep*(1-sk/100))} (Bareinkaufspreis) "
               f"+ {e(fracht)} Bezugskosten = **{e(bp)}**.", einheit="€", tol=0.02, s=3)
    for i in range(1, 13):
        ek = rng.choice([400, 650, 900, 1200, 1800, 2500])
        hk = rng.choice([10, 15, 20, 25, 30])
        gw = rng.choice([5, 8, 10, 12, 15, 20])
        sk = rng.choice([0, 2, 3])
        selbst = ek * (1 + hk / 100)
        bvp = selbst * (1 + gw / 100)
        zvp = bvp / (1 - sk / 100)
        if sk:
            text = (f"Verkaufskalkulation: Bezugspreis **{e(ek)}**, Handlungskosten **{hk} %**, Gewinn **{gw} %**, Kundenskonto **{sk} %** (im Hundert). "
                    "Wie hoch ist der Zielverkaufspreis (netto)?")
            erkl = (f"Selbstkosten = {e(ek)} × {1+hk/100:.2f}".replace(".", ",") + f" = {e(selbst)}; + {gw} % Gewinn = {e(bvp)} (Barverkaufspreis); "
                    f"÷ {1-sk/100:.2f}".replace(".", ",") + f" für Skonto = **{e(zvp)}**.")
        else:
            text = f"Verkaufskalkulation: Bezugspreis **{e(ek)}**, Handlungskosten **{hk} %**, Gewinn **{gw} %**. Wie hoch ist der Nettoverkaufspreis?"
            erkl = f"Selbstkosten = {e(selbst)}; + {gw} % Gewinn = **{e(bvp)}**."
        s.zahl("WIR-VERKAUF", i, T, "WIR-L1", text, runden(zvp), erkl, einheit="€", tol=0.02, s=3)
    for i in range(1, 11):
        alt = rng.choice([800, 1200, 1500, 2000, 450])
        neu = alt * (1 - rng.choice([10, 15, 20, 25, 30]) / 100)
        pz = (alt - neu) / alt * 100
        s.zahl("WIR-PROZENT", i, T, "WIR-L1", f"Ein Preis sinkt von **{e(alt)}** auf **{e(neu)}**. Um wie viel Prozent ist er gesunken?",
               runden(pz, 1), f"({e(alt)} − {e(neu)}) ÷ {e(alt)} × 100 = {zahl(pz,1)} %.", einheit="%", tol=0.1, s=1)

    # ---------- WIR-L2: Angebotsvergleich, Nutzwertanalyse ----------
    for i in range(1, 16):
        angebote = []
        for name in ["A", "B", "C"]:
            lp = rng.choice([1800, 1950, 2000, 2100, 2200, 2300])
            r = rng.choice([0, 5, 10, 15])
            sk = rng.choice([0, 2, 3])
            fr = rng.choice([0, 30, 50, 90, 120])
            bp = lp * (1 - r / 100) * (1 - sk / 100) + fr
            angebote.append((name, lp, r, sk, fr, runden(bp)))
        if len({a[5] for a in angebote}) < 3:
            continue
        best = min(angebote, key=lambda a: a[5])
        tab = "| Angebot | Listenpreis | Rabatt | Skonto | Versand |\n|---|---|---|---|---|\n" + "\n".join(
            f"| {a[0]} | {e(a[1])} | {a[2]} % | {a[3]} % | {e(a[4])} |" for a in angebote)
        s.wahl("WIR-ANGEBOT", i, T, "WIR-L2", f"Welches Angebot hat den niedrigsten Bezugspreis (Skonto wird genutzt)?\n\n{tab}",
               f"Angebot {best[0]}", [f"Angebot {a[0]}" for a in angebote if a is not best] + ["Alle sind gleich teuer"],
               "Bezugspreise: " + "; ".join(f"{a[0]} = {e(a[5])}" for a in angebote) + ".", s=3)
    kriterien = ["Preis", "Leistung", "Service", "Energieverbrauch", "Lieferzeit", "Garantie"]
    for i in range(1, 21):
        k = rng.sample(kriterien, 3)
        g = rng.choice([(50, 30, 20), (40, 40, 20), (40, 35, 25), (60, 25, 15), (30, 50, 20), (45, 30, 25)])
        punkte = {n: [rng.randint(3, 10) for _ in k] for n in ["X", "Y"]}
        nw = {n: sum(p * w for p, w in zip(punkte[n], g)) / 100 for n in punkte}
        frage_nach = rng.choice(["X", "Y"])
        tab = "| Kriterium | Gewicht | Punkte X | Punkte Y |\n|---|---|---|---|\n" + "\n".join(
            f"| {k[j]} | {g[j]} % | {punkte['X'][j]} | {punkte['Y'][j]} |" for j in range(3))
        s.zahl("WIR-NUTZWERT", i, T, "WIR-L2", f"Nutzwertanalyse (Punkte 1–10). Berechne den gewichteten Nutzwert von **Produkt {frage_nach}** (auf 2 Nachkommastellen).\n\n{tab}",
               runden(nw[frage_nach]), f"Nutzwert {frage_nach} = " + " + ".join(f"{punkte[frage_nach][j]} × {g[j]/100:.2f}".replace(".", ",") for j in range(3))
               + f" = {zahl(nw[frage_nach])}. (Zum Vergleich: X = {zahl(nw['X'])}, Y = {zahl(nw['Y'])}.)", tol=0.01, s=2)
    nwa = [("Gewichtung der Kriterien", "muss in Summe 100 % ergeben"), ("Vorteil der Nutzwertanalyse", "bezieht auch nicht-monetäre Kriterien ein"),
           ("Nachteil der Nutzwertanalyse", "Gewichtung und Punktvergabe sind subjektiv"),
           ("Quantitativer Angebotsvergleich", "vergleicht Angebote anhand der Bezugspreise"),
           ("Qualitativer Angebotsvergleich", "berücksichtigt z. B. Service, Qualität und Zuverlässigkeit"),
           ("K.-o.-Kriterium", "schließt ein Angebot bei Nichterfüllung sofort aus")]
    zuordnung(s, "WIR-NWAF", T, "WIR-L2", nwa, "Was trifft zu? **{a}** …", "Wofür steht: „{b}“?", rng=rng)

    # ---------- WIR-L3: Abschreibung, Leasing, Amortisation ----------
    for i in range(1, 16):
        ak = rng.choice([1200, 2400, 3600, 4500, 6000, 9000, 12000, 18000, 30000])
        nd = rng.choice([3, 4, 5, 6, 8])
        s.zahl("WIR-AFA", i, T, "WIR-L3",
               f"Ein Server kostet **{e(ak)}** netto, Nutzungsdauer **{nd} Jahre**. Wie hoch ist die jährliche lineare Abschreibung?",
               runden(ak / nd), f"{e(ak)} ÷ {nd} = {e(ak/nd)} pro Jahr.", einheit="€", tol=0.01, s=1)
    for i in range(1, 16):
        ak = rng.choice([1200, 2400, 3600, 4500, 6000, 9000, 12000])
        nd = rng.choice([3, 4, 5, 6])
        n = rng.randint(1, nd - 1)
        rbw = ak - ak / nd * n
        s.zahl("WIR-RBW", i, T, "WIR-L3",
               f"Anschaffungskosten **{e(ak)}**, lineare Abschreibung über **{nd} Jahre**. Wie hoch ist der Restbuchwert nach **{n} Jahr{'en' if n > 1 else ''}**?",
               runden(rbw), f"AfA pro Jahr {e(ak/nd)}; {e(ak)} − {n} × {e(ak/nd)} = {e(rbw)}.", einheit="€", tol=0.01, s=2)
    for i in range(1, 16):
        kauf = rng.choice([3000, 4500, 6000, 9000, 12000])
        rate = rng.choice([90, 120, 150, 199, 250, 320])
        monate = rng.choice([24, 36, 48])
        sonder = rng.choice([0, 0, 500, 1000])
        gesamt = rate * monate + sonder
        frage = (f"Leasing: monatliche Rate **{e(rate)}**, Laufzeit **{monate} Monate**" + (f", Sonderzahlung **{e(sonder)}**" if sonder else "")
                 + f". Kaufpreis wäre **{e(kauf)}**. Wie viel € kostet das Leasing insgesamt **mehr** als der Kauf? (negativ, wenn günstiger)")
        s.zahl("WIR-LEASING", i, T, "WIR-L3", frage, runden(gesamt - kauf),
               f"Leasing gesamt = {monate} × {e(rate)}" + (f" + {e(sonder)}" if sonder else "") + f" = {e(gesamt)}; − {e(kauf)} = {e(gesamt-kauf)}.",
               einheit="€", tol=0.01, s=2)
    for i in range(1, 16):
        inv = rng.choice([5000, 8000, 12000, 15000, 24000, 36000])
        ers = rng.choice([150, 250, 400, 500, 750, 1000, 1200])
        mon = inv / ers
        s.zahl("WIR-AMORT", i, T, "WIR-L3",
               f"Eine neue Software kostet **{e(inv)}** und spart monatlich **{e(ers)}** Personalkosten. Nach wie vielen **Monaten** hat sie sich amortisiert? (auf 1 Nachkommastelle)",
               runden(mon, 1), f"Amortisationszeit = Investition ÷ Ersparnis pro Monat = {e(inv)} ÷ {e(ers)} = {zahl(mon,1)} Monate.", einheit="Monate", tol=0.1, s=2)
    aussagen(s, "WIR-LEASAUS", T, "WIR-L3", "Welche Aussagen zum Leasing treffen zu?",
             ["Der Leasinggeber bleibt Eigentümer.", "Leasing schont die Liquidität bei der Anschaffung.", "Leasingraten sind in der Regel als Betriebsausgabe absetzbar.",
              "Die Geräte können nach Laufzeitende oft gegen neue getauscht werden."],
             ["Der Leasingnehmer wird sofort Eigentümer.", "Leasing ist über die Laufzeit immer günstiger als ein Kauf.",
              "Beim Leasing wird das Gerät beim Leasingnehmer abgeschrieben (Standardfall).", "Leasing ist nur für Privatpersonen möglich."],
             n=10, k_richtig=(1, 3), rng=rng)

    # ---------- WIR-L4: Verträge ----------
    vertraege = [("Ein Unternehmen kauft 20 Monitore beim Händler.", "Kaufvertrag"),
                 ("Ein Entwickler soll eine fertige App liefern, die abgenommen wird.", "Werkvertrag"),
                 ("Ein Administrator wird stundenweise für Support bezahlt, ein Erfolg ist nicht geschuldet.", "Dienstvertrag"),
                 ("Ein Kunde nutzt einen Server im Rechenzentrum gegen monatliches Entgelt.", "Mietvertrag"),
                 ("Ein Bürodrucker wird für 36 Monate gegen Raten überlassen, Eigentümer bleibt die Bank.", "Leasingvertrag"),
                 ("Ein Unternehmen erwirbt das Recht, eine Software zu nutzen.", "Lizenzvertrag"),
                 ("Eine Mitarbeiterin wird unbefristet als Fachinformatikerin eingestellt.", "Arbeitsvertrag"),
                 ("Ein Freund leiht dir kostenlos seinen Beamer fürs Wochenende.", "Leihvertrag"),
                 ("Ein Systemhaus erstellt eine individuelle Netzwerkdokumentation als Ergebnis.", "Werkvertrag"),
                 ("Eine Firma beauftragt eine Schulung über 2 Tage.", "Dienstvertrag")]
    zuordnung(s, "WIR-VERTRAG", T, "WIR-L4", vertraege, "Welche Vertragsart liegt vor? {a}", None, schwierigkeit=2, rng=rng)
    stoerungen = [("Der Lieferant liefert defekte Ware.", "Mangelhafte Lieferung (Schlechtleistung)"),
                  ("Der fest vereinbarte Liefertermin wird überschritten.", "Lieferungsverzug"),
                  ("Der Kunde nimmt die ordnungsgemäß gelieferte Ware nicht an.", "Annahmeverzug"),
                  ("Der Kunde zahlt nach Ablauf des Zahlungsziels nicht.", "Zahlungsverzug"),
                  ("Statt 10 Notebooks werden nur 8 geliefert.", "Mangelhafte Lieferung (Schlechtleistung)"),
                  ("Es werden Notebooks eines anderen Modells geliefert.", "Mangelhafte Lieferung (Schlechtleistung)")]
    zuordnung(s, "WIR-STOERUNG", T, "WIR-L4", stoerungen, "Welche Vertragsstörung liegt vor? {a}", None, rng=rng)
    rechte = [("Nacherfüllung (Nachbesserung oder Ersatzlieferung)", "vorrangiges Recht des Käufers bei mangelhafter Lieferung"),
              ("Rücktritt oder Minderung", "erst möglich, wenn die Nacherfüllung fehlschlägt"),
              ("Gewährleistung", "gesetzlich, beim Kauf neuer Sachen 2 Jahre"),
              ("Garantie", "freiwillige, vertragliche Zusage des Herstellers oder Händlers"),
              ("Beweislastumkehr", "im ersten Jahr nach Übergabe muss beim Verbrauchsgüterkauf der Händler beweisen, dass kein Mangel vorlag"),
              ("Mahnung", "macht den Schuldner in der Regel erst in Verzug, wenn kein fester Termin vereinbart war"),
              ("Unverzügliche Prüfung und Mängelrüge", "Pflicht beim zweiseitigen Handelskauf (zwischen Kaufleuten)")]
    zuordnung(s, "WIR-RECHTE", T, "WIR-L4", rechte, "Was trifft zu: **{a}** ist …", "Welcher Begriff passt: {b}?", schwierigkeit=2, rng=rng)
    alter = [(5, "geschäftsunfähig"), (6, "geschäftsunfähig"), (7, "beschränkt geschäftsfähig"), (12, "beschränkt geschäftsfähig"),
             (16, "beschränkt geschäftsfähig"), (17, "beschränkt geschäftsfähig"), (18, "voll geschäftsfähig"), (35, "voll geschäftsfähig")]
    for i, (a, g) in enumerate(alter, 1):
        s.wahl("WIR-GESCHFAEHIG", i, T, "WIR-L4", f"Eine Person ist **{a} Jahre** alt. Wie ist sie geschäftsfähig?", g,
               [x for x in ["geschäftsunfähig", "beschränkt geschäftsfähig", "voll geschäftsfähig", "deliktsfähig, aber nicht geschäftsfähig"] if x != g],
               "Unter 7: geschäftsunfähig; 7–17: beschränkt geschäftsfähig (Taschengeldparagraf); ab 18: voll geschäftsfähig.", s=1)
    zustande = [("Ein Händler schickt unaufgefordert einen Katalog.", "Aufforderung zur Abgabe eines Angebots (kein Antrag)"),
                ("Ein Kunde bestellt verbindlich aufgrund eines Katalogs.", "Antrag"),
                ("Der Händler schickt eine Auftragsbestätigung auf die Bestellung.", "Annahme"),
                ("Ein Lieferant macht einem bestimmten Kunden ein verbindliches Angebot, der Kunde bestellt genau dazu.", "Annahme"),
                ("Waren im Onlineshop werden mit Preis angezeigt.", "Aufforderung zur Abgabe eines Angebots (kein Antrag)")]
    zuordnung(s, "WIR-ZUSTANDE", T, "WIR-L4", zustande, "Wie ist die Willenserklärung rechtlich einzuordnen? {a}", None, schwierigkeit=2, rng=rng)

    # ---------- WIR-L5: Kosten, Stundensätze ----------
    kosten = [("Miete für das Büro", "fixe Kosten"), ("Gehalt eines festangestellten Mitarbeiters", "fixe Kosten"),
              ("Materialkosten pro verkauftem Gerät", "variable Kosten"), ("Versicherungsbeiträge", "fixe Kosten"),
              ("Provision je Verkauf", "variable Kosten"), ("Abschreibung auf Server (linear)", "fixe Kosten"),
              ("Verpackungskosten je Lieferung", "variable Kosten"), ("Stromkosten der Produktion pro Stück", "variable Kosten"),
              ("Leasingrate für Firmenwagen", "fixe Kosten"), ("Lizenzgebühr je ausgeliefertem Gerät", "variable Kosten"),
              ("Grundgebühr des Internetanschlusses", "fixe Kosten"), ("Frachtkosten je Bestellung", "variable Kosten")]
    for i, (a, b) in enumerate(kosten, 1):
        s.mehrfach("WIR-FIXVAR", i, T, "WIR-L5", f"Sind diese Kosten fix oder variabel? **{a}**", [b],
                   ["variable Kosten" if b == "fixe Kosten" else "fixe Kosten", "sprungfixe Kosten"],
                   "Fixe Kosten fallen unabhängig von der Menge an, variable Kosten steigen mit der Menge.", s=1)
    for i in range(1, 16):
        jahr = rng.choice([180000, 240000, 320000, 450000, 96000, 150000])
        std = rng.choice([1200, 1400, 1500, 1600, 1680, 2000]) * rng.choice([1, 2, 3])
        s.zahl("WIR-STUNDENSATZ", i, T, "WIR-L5",
               f"Ein IT-Team verursacht im Jahr **{e(jahr)}** Kosten und kann **{zahl(std)} Stunden** fakturieren. Wie hoch muss der Stundensatz mindestens sein, um die Kosten zu decken?",
               runden(jahr / std), f"{e(jahr)} ÷ {zahl(std)} h = {e(jahr/std)} pro Stunde.", einheit="€", tol=0.01, s=2)
    for i in range(1, 16):
        fix = rng.choice([12000, 20000, 30000, 45000, 60000])
        p = rng.choice([80, 120, 150, 199, 250])
        kv = rng.choice([30, 45, 60, 70, 90])
        if kv >= p:
            kv = p // 2
        menge = fix / (p - kv)
        s.zahl("WIR-BREAKEVEN", i, T, "WIR-L5",
               f"Fixkosten **{e(fix)}**, Verkaufspreis **{e(p)}** pro Stück, variable Kosten **{e(kv)}** pro Stück. Ab welcher Stückzahl wird die Gewinnschwelle erreicht? (aufrunden)",
               -(-fix // (p - kv)), f"Deckungsbeitrag pro Stück = {e(p)} − {e(kv)} = {e(p-kv)}. Break-even = {e(fix)} ÷ {e(p-kv)} = {zahl(menge,2)} → {-(-fix // (p - kv))} Stück.",
               einheit="Stück", s=3)
    for i in range(1, 13):
        p = rng.choice([80, 120, 150, 199, 250, 499])
        kv = rng.choice([30, 45, 60, 70, 90, 120])
        m = rng.choice([100, 250, 400, 1000])
        if kv >= p:
            kv = p // 3
        s.zahl("WIR-DB", i, T, "WIR-L5",
               f"Verkaufspreis **{e(p)}**, variable Stückkosten **{e(kv)}**, Absatz **{m} Stück**. Wie hoch ist der Gesamtdeckungsbeitrag?",
               (p - kv) * m, f"DB/Stück = {e(p-kv)}; × {m} = {e((p-kv)*m)}.", einheit="€", tol=0.01, s=2)
    for i in range(1, 11):
        std = rng.choice([4, 6, 7.5, 12, 16, 24])
        satz = rng.choice([65, 75, 85, 95, 110])
        anf = rng.choice([0, 35, 49, 60])
        netto = std * satz + anf
        s.zahl("WIR-RECHNUNG", i, T, "WIR-L5",
               f"Ein Einsatz dauert **{zahl(std,1)} h** zu **{e(satz)}/h** netto, dazu eine Anfahrtspauschale von **{e(anf)}**. Wie hoch ist der Bruttobetrag der Rechnung (19 % USt)?",
               runden(netto * 1.19), f"Netto = {zahl(std,1)} × {e(satz)} + {e(anf)} = {e(netto)}; × 1,19 = {e(netto*1.19)}.", einheit="€", tol=0.02, s=2)

    # ---------- WIR-L6: Markt und Rechtsformen ----------
    markt = [("viele Anbieter, viele Nachfrager", "Polypol"), ("wenige Anbieter, viele Nachfrager", "Angebotsoligopol"),
             ("ein Anbieter, viele Nachfrager", "Angebotsmonopol"), ("viele Anbieter, ein Nachfrager", "Nachfragemonopol"),
             ("viele Anbieter, wenige Nachfrager", "Nachfrageoligopol"), ("ein Anbieter, ein Nachfrager", "Zweiseitiges Monopol")]
    zuordnung(s, "WIR-MARKT", T, "WIR-L6", markt, "Welche Marktform liegt vor: **{a}**?", "Was kennzeichnet ein **{b}**?", rng=rng)
    rform = [("Einzelunternehmen", "Inhaber haftet allein und unbeschränkt mit dem Privatvermögen"),
             ("GbR", "mindestens zwei Gesellschafter, alle haften persönlich und gesamtschuldnerisch, kein Mindestkapital"),
             ("OHG", "Handelsgewerbe, alle Gesellschafter haften unbeschränkt"),
             ("KG", "Komplementär haftet unbeschränkt, Kommanditisten nur mit ihrer Einlage"),
             ("GmbH", "Haftung auf das Gesellschaftsvermögen beschränkt, Stammkapital mindestens 25.000 €"),
             ("UG (haftungsbeschränkt)", "Mini-GmbH, Stammkapital ab 1 €, Gewinne teilweise zurücklegen"),
             ("AG", "Grundkapital mindestens 50.000 €, Organe Vorstand, Aufsichtsrat, Hauptversammlung"),
             ("eG (Genossenschaft)", "fördert ihre Mitglieder, jedes Mitglied hat grundsätzlich eine Stimme")]
    zuordnung(s, "WIR-RFORM", T, "WIR-L6", rform, "Was kennzeichnet die Rechtsform **{a}**?", "Welche Rechtsform wird beschrieben: {b}?", schwierigkeit=2, rng=rng)
    rfz = [("Mindeststammkapital einer GmbH in €", 25000), ("Mindestgrundkapital einer AG in €", 50000), ("Mindeststammkapital einer UG in €", 1),
           ("Mindestens einzuzahlendes Stammkapital bei GmbH-Gründung (Bargründung) in €", 12500)]
    for i, (a, w) in enumerate(rfz, 1):
        s.zahl("WIR-RFZAHL", i, T, "WIR-L6", f"{a}?", w, "GmbH 25.000 € (mind. 12.500 € bei Gründung eingezahlt), UG 1 €, AG 50.000 €.", einheit="€", s=1)
    begriffe = [("Prokura", "umfassende Vollmacht für fast alle Geschäfte, wird ins Handelsregister eingetragen"),
                ("Handlungsvollmacht", "Vollmacht für gewöhnliche Geschäfte, nicht im Handelsregister"),
                ("Handelsregister", "öffentliches Verzeichnis der Kaufleute beim Amtsgericht"),
                ("Angebot (Markt)", "Menge der Güter, die Anbieter zu einem Preis verkaufen wollen"),
                ("Gleichgewichtspreis", "Preis, bei dem angebotene und nachgefragte Menge übereinstimmen"),
                ("Kartell", "Absprache rechtlich selbstständiger Unternehmen, meist verboten")]
    zuordnung(s, "WIR-BEGRIFF", T, "WIR-L6", begriffe, "Was bedeutet **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)
    return s.fragen

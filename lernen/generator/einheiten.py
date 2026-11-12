from .basis import Sammler, rng_fuer, runden, zahl, zuordnung

T = "einheiten"
DEZ = ["Byte", "KB", "MB", "GB", "TB", "PB"]
BIN = ["Byte", "KiB", "MiB", "GiB", "TiB", "PiB"]


def erzeugen():
    s = Sammler()
    rng = rng_fuer("einheiten")

    # ---------- EIN-L1: Bit, Byte, Präfixe, Zahlensysteme ----------
    i = 0
    while i < 15:
        a = rng.randint(1, 4)
        b = rng.choice([x for x in range(0, 5) if x != a and abs(x - a) <= 2])
        wert = rng.choice([1, 2, 4, 5, 8, 12, 16, 20, 25, 50, 64, 128, 250, 500, 750, 1500, 2500])
        erg = wert * 1000 ** (a - b)
        if erg < 0.01 or erg > 1e9:
            continue
        i += 1
        stufen = "eine Stufe" if abs(a - b) == 1 else f"{abs(a-b)} Stufen"
        s.zahl("EIN-DEZ", i, T, "EIN-L1", f"Rechne um (Dezimalpräfixe, Faktor 1000): **{zahl(wert)} {DEZ[a]}** = ? {DEZ[b]}",
               runden(erg, 4), f"Von {DEZ[a]} nach {DEZ[b]}: {stufen} mit Faktor 1000, also {zahl(wert)} {'×' if a > b else '÷'} {zahl(1000**abs(a-b), 0)} = {zahl(erg, 4)}.",
               einheit=DEZ[b], s=1)
    i = 0
    while i < 15:
        a = rng.randint(1, 4)
        b = rng.choice([x for x in range(0, 5) if x != a and abs(x - a) <= 2])
        wert = rng.choice([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 3, 6, 10, 5120, 8192])
        erg = wert * 1024 ** (a - b)
        if erg < 0.01 or erg > 1e10 or round(erg, 4) != erg:
            continue
        i += 1
        s.zahl("EIN-BIN", i, T, "EIN-L1", f"Rechne um (Binärpräfixe, Faktor 1024): **{zahl(wert)} {BIN[a]}** = ? {BIN[b]}",
               erg, f"Je Stufe Faktor 1024: {zahl(wert)} {'×' if a > b else '÷'} 1024{'' if abs(a-b) == 1 else '^' + str(abs(a-b))} = {zahl(erg, 4)}.",
               einheit=BIN[b], s=2)
    for i in range(1, 13):
        stufe = rng.choice([3, 4])
        wert = rng.choice([250, 500, 960, 1000, 2000, 4000, 8000, 128, 256, 512])
        bytes_ = wert * 1000 ** stufe
        erg = bytes_ / 1024 ** stufe
        s.zahl("EIN-HERSTELLER", i, T, "EIN-L1",
               f"Eine Festplatte wird mit **{zahl(wert)} {DEZ[stufe]}** verkauft. Wie viele **{BIN[stufe]}** zeigt das Betriebssystem an? (auf 2 Nachkommastellen)",
               runden(erg, 2), f"{zahl(wert)} × 1000^{stufe} Byte ÷ 1024^{stufe} = {zahl(erg)} {BIN[stufe]}. Hersteller rechnen dezimal, viele Betriebssysteme binär.",
               einheit=BIN[stufe], tol=0.01, s=2)
    for i in range(1, 13):
        n = rng.randint(5, 255)
        s.zahl("EIN-BIN2DEZ", i, T, "EIN-L1", f"Wandle die Binärzahl `{n:b}` in eine Dezimalzahl um.", n,
               f"{n:b}₂ = {' + '.join(str(2**k) for k in range(n.bit_length()-1, -1, -1) if n >> k & 1)} = {n}.", s=1)
    for i in range(1, 13):
        n = rng.randint(5, 255)
        s.wahl("EIN-DEZ2BIN", i, T, "EIN-L1", f"Welche Binärzahl entspricht der Dezimalzahl **{n}**?", f"{n:08b}",
               [f"{n ^ (1 << rng.randint(0,7)):08b}", f"{(n + 1) % 256:08b}", f"{int(f'{n:08b}'[::-1], 2):08b}", f"{(n - 2) % 256:08b}"],
               f"{n} = {' + '.join(str(2**k) for k in range(7, -1, -1) if n >> k & 1)} → {n:08b}.", s=1)
    for i in range(1, 13):
        n = rng.randint(16, 4095)
        s.zahl("EIN-HEX2DEZ", i, T, "EIN-L1", f"Wandle die Hexadezimalzahl `{n:X}` in eine Dezimalzahl um.", n,
               f"{n:X}₁₆ = " + " + ".join(f"{int(c,16)}×16^{len(f'{n:X}')-1-k}" for k, c in enumerate(f"{n:X}")) + f" = {n}.", s=2)
    for i in range(1, 13):
        n = rng.randint(16, 255)
        s.wahl("EIN-DEZ2HEX", i, T, "EIN-L1", f"Welche Hexadezimalzahl entspricht der Dezimalzahl **{n}**?", f"{n:X}",
               [f"{n:X}"[::-1] if f"{n:X}"[::-1] != f"{n:X}" else f"{n+16:X}", f"{n+1:X}", f"{n-16:X}", f"{n}"],
               f"{n} ÷ 16 = {n//16} Rest {n%16} → {n:X}.", s=2)
    for i in range(1, 11):
        n = rng.randint(16, 255)
        s.wahl("EIN-HEX2BIN", i, T, "EIN-L1", f"Welche Binärdarstellung hat `0x{n:02X}`?", f"{n >> 4:04b} {n & 15:04b}",
               [f"{n & 15:04b} {n >> 4:04b}" if (n & 15) != (n >> 4) else f"{(n>>4)^1:04b} {n & 15:04b}",
                f"{(n ^ 0x11) >> 4:04b} {(n ^ 0x11) & 15:04b}", f"{(n+1) >> 4 & 15:04b} {(n+1) & 15:04b}"],
               "Jede Hex-Ziffer entspricht genau 4 Bit (einem Nibble).", s=2)
    for i in range(1, 9):
        b = rng.choice([4, 6, 8, 10, 12, 16, 24, 32])
        s.zahl("EIN-WERTE", i, T, "EIN-L1", f"Wie viele verschiedene Werte lassen sich mit **{b} Bit** darstellen?", 2 ** b,
               f"2^{b} = {zahl(2**b, 0)}.", s=1)
    praefixe = [("Kilo (k)", "10³ = 1.000"), ("Mega (M)", "10⁶ = 1.000.000"), ("Giga (G)", "10⁹"), ("Tera (T)", "10¹²"), ("Peta (P)", "10¹⁵"),
                ("Kibi (Ki)", "2¹⁰ = 1.024"), ("Mebi (Mi)", "2²⁰ = 1.048.576"), ("Gibi (Gi)", "2³⁰"), ("Tebi (Ti)", "2⁴⁰"),
                ("Milli (m)", "10⁻³"), ("Mikro (µ)", "10⁻⁶"), ("Nano (n)", "10⁻⁹")]
    zuordnung(s, "EIN-PRAEFIX", T, "EIN-L1", praefixe, "Für welchen Faktor steht der Präfix **{a}**?",
              "Welcher Präfix steht für den Faktor **{b}**?", schwierigkeit=1, rng=rng)

    # ---------- EIN-L2: Datenraten, Speicherbedarf ----------
    for i in range(1, 16):
        groesse = rng.choice([100, 250, 500, 700, 1000, 1500, 2000, 4000, 4700, 8000, 10000])  # MB
        rate = rng.choice([16, 25, 50, 100, 250, 500, 1000])  # Mbit/s
        sek = groesse * 8 / rate
        s.zahl("EIN-DAUER", i, T, "EIN-L2",
               f"Eine Datei mit **{zahl(groesse)} MB** wird über eine Leitung mit **{rate} Mbit/s** übertragen. Wie viele **Sekunden** dauert das (ohne Overhead, auf 1 Nachkommastelle)?",
               runden(sek, 1), f"{zahl(groesse)} MB × 8 = {zahl(groesse*8)} Mbit; ÷ {rate} Mbit/s = {zahl(sek,1)} s.", einheit="s", tol=0.1, s=2)
    for i in range(1, 13):
        groesse = rng.choice([1, 2, 4, 5, 8, 10, 20, 50])  # GB
        min_ = rng.choice([1, 2, 4, 5, 8, 10, 16, 20])
        rate = groesse * 8000 / (min_ * 60)
        s.zahl("EIN-RATE", i, T, "EIN-L2",
               f"**{groesse} GB** sollen in **{min_} Minuten** übertragen werden. Welche Datenrate in **Mbit/s** ist mindestens nötig? (1 GB = 1.000 MB, auf 2 Nachkommastellen)",
               runden(rate, 2), f"{groesse} GB = {zahl(groesse*8000)} Mbit; ÷ {min_*60} s = {zahl(rate)} Mbit/s.", einheit="Mbit/s", tol=0.01, s=2)
    for i in range(1, 13):
        b, h = rng.choice([(1920, 1080), (1280, 720), (3840, 2160), (2560, 1440), (1024, 768), (800, 600), (4000, 3000)])
        tiefe = rng.choice([8, 16, 24, 32])
        mb = b * h * tiefe / 8 / 1_000_000
        s.zahl("EIN-BILD", i, T, "EIN-L2",
               f"Ein unkomprimiertes Bild hat **{b} × {h} Pixel** und eine Farbtiefe von **{tiefe} Bit**. Wie groß ist es in **MB** (1 MB = 1.000.000 Byte, auf 2 Nachkommastellen)?",
               runden(mb, 2), f"{b} × {h} = {zahl(b*h)} Pixel × {tiefe} Bit ÷ 8 = {zahl(b*h*tiefe//8)} Byte ≈ {zahl(mb)} MB.", einheit="MB", tol=0.01, s=2)
    for i in range(1, 11):
        rate = rng.choice([44100, 48000])
        bits = rng.choice([16, 24])
        kan = rng.choice([1, 2])
        minuten = rng.choice([1, 3, 4, 5, 10])
        mb = rate * bits * kan * minuten * 60 / 8 / 1_000_000
        s.zahl("EIN-AUDIO", i, T, "EIN-L2",
               f"Eine unkomprimierte Audioaufnahme: **{zahl(rate)} Hz**, **{bits} Bit**, **{'Stereo' if kan == 2 else 'Mono'}**, **{minuten} min**. Wie groß ist sie in **MB** (1 MB = 10⁶ Byte, auf 2 Nachkommastellen)?",
               runden(mb, 2), f"{zahl(rate)} × {bits} × {kan} × {minuten*60} s ÷ 8 = {zahl(mb*1e6,0)} Byte ≈ {zahl(mb)} MB.", einheit="MB", tol=0.01, s=3)
    for i in range(1, 11):
        anz = rng.choice([200, 500, 1000, 2500, 5000, 10000])
        kb = rng.choice([150, 250, 300, 400, 500, 800])
        gb = anz * kb / 1_000_000
        s.zahl("EIN-SPEICHER", i, T, "EIN-L2",
               f"Ein Archiv soll **{zahl(anz)} Dokumente** mit durchschnittlich **{kb} KB** speichern. Wie viel Speicher in **GB** wird benötigt (dezimal, auf 3 Nachkommastellen)?",
               runden(gb, 3), f"{zahl(anz)} × {kb} KB = {zahl(anz*kb)} KB = {zahl(gb,3)} GB.", einheit="GB", tol=0.001, s=1)
    for i in range(1, 11):
        mbit = rng.choice([16, 50, 100, 250, 500, 1000])
        s.zahl("EIN-MBITMB", i, T, "EIN-L2", f"Ein Anschluss hat **{mbit} Mbit/s**. Wie viele **MB pro Sekunde** sind das maximal?",
               runden(mbit / 8, 3), f"{mbit} ÷ 8 = {zahl(mbit/8,3)} MB/s (8 Bit = 1 Byte).", einheit="MB/s", tol=0.01, s=1)
    for i in range(1, 9):
        gb = rng.choice([20, 50, 100, 200, 500])
        mbit = rng.choice([10, 20, 40, 50, 100])
        std = gb * 8000 / mbit / 3600
        s.zahl("EIN-BACKUPZEIT", i, T, "EIN-L2",
               f"Ein Online-Backup von **{gb} GB** wird mit einem Upload von **{mbit} Mbit/s** hochgeladen. Wie viele **Stunden** dauert das (auf 2 Nachkommastellen)?",
               runden(std, 2), f"{gb} GB × 8.000 = {zahl(gb*8000)} Mbit ÷ {mbit} = {zahl(gb*8000/mbit)} s ÷ 3.600 = {zahl(std)} h.", einheit="h", tol=0.01, s=2)
    return s.fragen

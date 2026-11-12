from .basis import Sammler, aussagen, rng_fuer, zuordnung

T = "programmierung"


def code(src):
    return f"\n\n```\n{src.strip()}\n```\n"


def ausfuehren(src, var="x"):
    umg = {}
    exec(src, {"__builtins__": {"range": range, "len": len, "print": lambda *a: None, "int": int, "str": str, "abs": abs, "max": max, "min": min}}, umg)
    return umg[var]


def py(v):
    return repr(v) if not isinstance(v, bool) else str(v)


def erzeugen():
    s = Sammler()
    rng = rng_fuer("programmierung")

    # ---------- PRG-L1: Datentypen und Operatoren ----------
    for i in range(1, 21):
        a, b = rng.randint(7, 60), rng.randint(2, 9)
        op = rng.choice(["%", "//", "/", "*", "-", "+", "**"])
        if op == "**":
            a, b = rng.randint(2, 5), rng.randint(2, 4)
        expr = f"{a} {op} {b}"
        w = eval(expr)
        w = round(w, 2) if isinstance(w, float) else w
        erkl = {"%": f"% liefert den Rest der ganzzahligen Division: {a} = {a//b} × {b} + {a%b}.",
                "//": f"// ist die ganzzahlige Division (abrunden): {a} ÷ {b} = {a/b:.3f}".replace(".", ",") + f" → {a//b}.",
                "/": "/ liefert in Python immer eine Kommazahl (float).", "**": f"** ist die Potenz: {a}^{b} = {a**b}."}.get(op, f"{expr} = {w}.")
        s.zahl("PRG-OP", i, T, "PRG-L1", f"Welchen Wert hat `x` nach der Anweisung?{code(f'x = {expr}')}(bei Kommazahlen auf 2 Stellen)", w, erkl,
               tol=0.01 if op == "/" else 0, s=1)
    for i in range(1, 21):
        a, b, c = rng.randint(1, 20), rng.randint(1, 20), rng.randint(1, 20)
        vorlage = rng.choice(["a > b and b > c", "a > b or b > c", "not (a == b)", "a % 2 == 0 and c % 2 == 1", "a >= b or not c < 10",
                              "(a + b) > c and a != c", "a < b < c", "not a > b and c > b"])
        w = eval(vorlage, {}, {"a": a, "b": b, "c": c})
        s.mehrfach("PRG-BOOL", i, T, "PRG-L1", f"Gegeben ist `a = {a}`, `b = {b}`, `c = {c}`. Welchen Wert hat der Ausdruck `{vorlage}`?",
                   [str(w)], [str(not w), "Fehler"], f"Ausdruck schrittweise auswerten: and = beide wahr, or = mindestens einer wahr, not kehrt um. Ergebnis: {w}.", s=2)
    typen = [("42", "Integer (ganze Zahl)"), ("3.14", "Float / Gleitkommazahl"), ('"Hallo"', "String (Zeichenkette)"), ("True", "Boolean (Wahrheitswert)"),
             ("[1, 2, 3]", "Liste / Array"), ('"42"', "String (Zeichenkette)"), ("-7", "Integer (ganze Zahl)"), ("0.0", "Float / Gleitkommazahl"),
             ("False", "Boolean (Wahrheitswert)"), ('{"name": "Ada"}', "Dictionary (Schlüssel-Wert-Paare)"), ("'A'", "String (Zeichenkette)")]
    zuordnung(s, "PRG-TYP", T, "PRG-L1", typen, "Welchen Datentyp hat der Wert `{a}` in Python?", None, schwierigkeit=1, rng=rng)
    passend = [("Postleitzahl (mit führender Null, z. B. 01067)", "String"), ("Anzahl Mitarbeiter", "Integer"), ("Nettopreis eines Artikels", "Float bzw. Decimal"),
               ("Ist der Kunde volljährig?", "Boolean"), ("Telefonnummer +49 30 1234", "String"), ("Temperatur mit Nachkommastellen", "Float bzw. Decimal"),
               ("Hausnummer wie 12a", "String"), ("Lagerbestand in Stück", "Integer"), ("Newsletter abonniert ja/nein", "Boolean")]
    zuordnung(s, "PRG-TYPWAHL", T, "PRG-L1", passend, "Welcher Datentyp eignet sich am besten für: **{a}**?", None, schwierigkeit=1, rng=rng)
    konv = [('int("12") + 3', "15"), ('"12" + "3"', '"123"'), ('str(5) + "5"', '"55"'), ("int(7.9)", "7"), ('"ab" * 3', '"ababab"'),
            ("len(\"Hallo\")", "5"), ("10 / 4", "2.5"), ("10 // 4", "2"), ("float(3)", "3.0"), ("bool(0)", "False")]
    zuordnung(s, "PRG-KONV", T, "PRG-L1", konv, "Was liefert der Python-Ausdruck `{a}`?", None, schwierigkeit=2, rng=rng)

    # ---------- PRG-L2: Verzweigungen und Schleifen ----------
    for i in range(1, 21):
        a, b, st = rng.randint(0, 5), rng.randint(6, 15), rng.choice([1, 1, 2, 3])
        src = f"x = 0\nfor i in range({a}, {b}{', ' + str(st) if st != 1 else ''}):\n    x = x + i"
        w = ausfuehren(src)
        werte = list(range(a, b, st))
        s.zahl("PRG-FORSUM", i, T, "PRG-L2", f"Welchen Wert hat `x` nach dem Programm?{code(src)}", w,
               f"range({a}, {b}{', ' + str(st) if st != 1 else ''}) liefert {werte} (die Obergrenze {b} gehört nicht dazu). Summe = {w}.", s=2)
    for i in range(1, 16):
        start, ende, schritt = rng.randint(1, 5), rng.randint(20, 100), rng.choice([2, 3, 5, 7])
        op = rng.choice(["+", "*"])
        if op == "*":
            schritt = rng.choice([2, 3])
        src = f"x = {start}\nz = 0\nwhile x < {ende}:\n    x = x {op} {schritt}\n    z = z + 1"
        w = ausfuehren(src, "z")
        s.zahl("PRG-WHILE", i, T, "PRG-L2", f"Wie oft wird der Schleifenrumpf ausgeführt? (Wert von `z` am Ende){code(src)}", w,
               f"x durchläuft {', '.join(str(v) for v in _verlauf(start, ende, op, schritt))}; die Bedingung wird geprüft, bevor der Rumpf läuft. z = {w}.", s=2)
    for i in range(1, 16):
        n, m = rng.randint(2, 6), rng.randint(2, 6)
        inner = rng.choice([f"range({m})", "range(i)", f"range(i, {m + 1})"])
        src = f"x = 0\nfor i in range({n}):\n    for j in {inner}:\n        x = x + 1"
        w = ausfuehren(src)
        s.zahl("PRG-NESTED", i, T, "PRG-L2", f"Welchen Wert hat `x` nach den verschachtelten Schleifen?{code(src)}", w,
               "Durchläufe der inneren Schleife je i: " + " + ".join(str(len(eval(inner, {"range": range}, {"i": k}))) for k in range(n)) + f" = {w}.", s=3)
    for i in range(1, 21):
        g1, g2 = sorted(rng.sample(range(10, 90, 5), 2))
        p = rng.randint(0, 100)
        src = (f"punkte = {p}\nif punkte >= {g2}:\n    x = \"A\"\nelif punkte >= {g1}:\n    x = \"B\"\nelse:\n    x = \"C\"")
        w = ausfuehren(src)
        s.mehrfach("PRG-IF", i, T, "PRG-L2", f"Welchen Wert hat `x`?{code(src)}", [f'"{w}"'], [f'"{v}"' for v in "ABC" if v != w],
                   f"Die Bedingungen werden von oben geprüft, der erste zutreffende Zweig gewinnt: {p} → \"{w}\".", s=1)
    schleifen = [("kopfgesteuerte Schleife (while)", "prüft die Bedingung vor jedem Durchlauf, läuft evtl. gar nicht"),
                 ("fußgesteuerte Schleife (do-while)", "läuft mindestens einmal, Bedingung wird am Ende geprüft"),
                 ("Zählschleife (for)", "läuft eine vorher bekannte Anzahl von Durchläufen"),
                 ("Endlosschleife", "Abbruchbedingung wird nie erreicht"), ("break", "beendet die Schleife sofort"),
                 ("continue", "springt sofort zum nächsten Schleifendurchlauf")]
    zuordnung(s, "PRG-SCHLART", T, "PRG-L2", schleifen, "Was beschreibt **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)

    # ---------- PRG-L3: Schreibtischtest ----------
    for i in range(1, 16):
        a, b = rng.randint(12, 120), rng.randint(6, 90)
        src = f"a = {a}\nb = {b}\nwhile b != 0:\n    r = a % b\n    a = b\n    b = r\nx = a"
        s.zahl("PRG-GGT", i, T, "PRG-L3", f"Führe einen Schreibtischtest durch. Welchen Wert hat `x` am Ende?{code(src)}", ausfuehren(src),
               f"Das ist der euklidische Algorithmus: x ist der größte gemeinsame Teiler von {a} und {b}.", s=3)
    for i in range(1, 16):
        n = rng.randint(100, 99999)
        src = f"n = {n}\nx = 0\nwhile n > 0:\n    x = x + n % 10\n    n = n // 10"
        s.zahl("PRG-QUER", i, T, "PRG-L3", f"Welchen Wert hat `x` am Ende?{code(src)}", ausfuehren(src),
               f"n % 10 liefert die letzte Ziffer, n // 10 entfernt sie. x ist die Quersumme von {n}.", s=2)
    for i in range(1, 16):
        liste = rng.sample(range(1, 60), rng.randint(5, 8))
        art = rng.choice(["max", "min", "count", "sum_even"])
        if art == "max":
            src = f"z = {liste}\nx = z[0]\nfor w in z:\n    if w > x:\n        x = w"
            hinw = "Maximumsuche"
        elif art == "min":
            src = f"z = {liste}\nx = z[0]\nfor w in z:\n    if w < x:\n        x = w"
            hinw = "Minimumsuche"
        elif art == "count":
            g = rng.randint(15, 45)
            src = f"z = {liste}\nx = 0\nfor w in z:\n    if w > {g}:\n        x = x + 1"
            hinw = f"Zählen der Werte größer {g}"
        else:
            src = f"z = {liste}\nx = 0\nfor w in z:\n    if w % 2 == 0:\n        x = x + w"
            hinw = "Summe der geraden Zahlen"
        s.zahl("PRG-LISTE", i, T, "PRG-L3", f"Welchen Wert hat `x` am Ende?{code(src)}", ausfuehren(src), f"Der Algorithmus ist eine {hinw}.", s=2)
    for i in range(1, 13):
        n = rng.randint(3, 7)
        art = rng.choice(["fak", "fib", "pot"])
        if art == "fak":
            src = f"x = 1\nfor i in range(1, {n} + 1):\n    x = x * i"
            h = f"Fakultät {n}!"
        elif art == "fib":
            src = f"a = 0\nb = 1\nfor i in range({n}):\n    a, b = b, a + b\nx = a"
            h = f"die {n}. Fibonacci-Zahl"
        else:
            b_ = rng.randint(2, 4)
            src = f"x = 1\ni = 0\nwhile i < {n}:\n    x = x * {b_}\n    i = i + 1"
            h = f"{b_}^{n}"
        s.zahl("PRG-KLASSIK", i, T, "PRG-L3", f"Welchen Wert hat `x` am Ende?{code(src)}", ausfuehren(src), f"Das Programm berechnet {h} = {ausfuehren(src)}.", s=2)
    for i in range(1, 13):
        liste = rng.sample(range(1, 40), 5)
        src = f"z = {liste}\nfor j in range(len(z) - 1):\n    if z[j] > z[j + 1]:\n        z[j], z[j + 1] = z[j + 1], z[j]\nx = z"
        w = ausfuehren(src)
        falsch = [str(sorted(liste)), str(liste), str(list(reversed(w)))]
        s.wahl("PRG-BUBBLE", i, T, "PRG-L3", f"Welchen Inhalt hat `x` nach **einem** Durchlauf?{code(src)}", str(w), falsch,
               "Ein Bubblesort-Durchlauf vergleicht Nachbarn und tauscht sie; danach steht nur das größte Element sicher am Ende.", s=3)
    for i in range(1, 13):
        a, b = rng.randint(1, 30), rng.randint(1, 30)
        variante = rng.choice(["falsch", "richtig", "temp"])
        if variante == "falsch":
            src = f"a = {a}\nb = {b}\na = b\nb = a"
        elif variante == "richtig":
            src = f"a = {a}\nb = {b}\nhilf = a\na = b\nb = hilf"
        else:
            src = f"a = {a}\nb = {b}\na = a + b\nb = a - b\na = a - b"
        w = (ausfuehren(src, "a"), ausfuehren(src, "b"))
        moegl = [(a, b), (b, a), (b, b), (a, a)]
        s.wahl("PRG-TAUSCH", i, T, "PRG-L3", f"Welche Werte haben `a` und `b` am Ende?{code(src)}", f"a = {w[0]}, b = {w[1]}",
               [f"a = {x}, b = {y}" for x, y in moegl if (x, y) != w],
               "Ohne Hilfsvariable wird beim direkten Zuweisen der ursprüngliche Wert überschrieben." if variante == "falsch"
               else "Die Werte werden korrekt getauscht.", s=2)

    # ---------- PRG-L4: Funktionen, Listen, Fehler ----------
    for i in range(1, 21):
        liste = rng.sample(range(1, 50), rng.randint(5, 7))
        idx = rng.choice(["[0]", "[2]", "[-1]", "[-2]", "[1:3]", "[:2]", "[3:]", "[len(z) - 1]"])
        w = eval("z" + idx, {"len": len}, {"z": liste})
        falsch = []
        for alt in ["[1]", "[3]", "[-1]", "[0]", "[1:4]", "[:3]", "[2:]"]:
            v = eval("z" + alt, {"len": len}, {"z": liste})
            if type(v) is type(w) and v != w:
                falsch.append(str(v))
        falsch.append("IndexError")
        s.wahl("PRG-INDEX", i, T, "PRG-L4", f"Gegeben `z = {liste}`. Was liefert `z{idx}`?", str(w), falsch,
               "Indizes beginnen bei 0; negative Indizes zählen von hinten (-1 = letztes Element); bei z[a:b] ist b exklusiv.", s=2)
    for i in range(1, 16):
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        f = rng.choice([("def f(a, b):\n    return a * b + 1", lambda a, b: a * b + 1),
                        ("def f(a, b):\n    if a > b:\n        return a - b\n    return b - a", lambda a, b: abs(a - b)),
                        ("def f(a, b=2):\n    return a ** b", None),
                        ("def f(a, b):\n    s = 0\n    for i in range(a):\n        s = s + b\n    return s", lambda a, b: a * b)])
        if f[1] is None:
            aufruf = f"f({a})"
            w = a ** 2
        else:
            aufruf = f"f({a}, {b})"
            w = f[1](a, b)
        s.zahl("PRG-FUNK", i, T, "PRG-L4", f"Welchen Wert liefert der Aufruf `{aufruf}`?{code(f[0])}", w,
               "Parameter werden in der Reihenfolge der Argumente belegt; fehlt ein Argument, gilt der Standardwert." , s=2)
    fehler = [("Es fehlt ein Doppelpunkt nach `if x > 3`", "Syntaxfehler"), ("Division durch null zur Laufzeit", "Laufzeitfehler"),
              ("Die Schleife summiert bis n − 1 statt bis n", "logischer Fehler"), ("Zugriff auf `liste[10]` bei 5 Elementen", "Laufzeitfehler"),
              ("Es wird `+` statt `*` gerechnet, das Programm läuft aber", "logischer Fehler"), ("Ein Variablenname ist falsch geschrieben (NameError)", "Laufzeitfehler"),
              ("Eine Klammer wird nicht geschlossen", "Syntaxfehler"), ("Die Abbruchbedingung wird nie wahr", "logischer Fehler"),
              ("`int(\"abc\")` wird ausgeführt", "Laufzeitfehler"), ("Falsche Einrückung im Python-Block", "Syntaxfehler")]
    for i, (a, b) in enumerate(fehler, 1):
        s.mehrfach("PRG-FEHLER", i, T, "PRG-L4", f"Welche Fehlerart liegt vor? {a}.", [b], [x for x in ["Syntaxfehler", "Laufzeitfehler", "logischer Fehler"] if x != b],
                   "Syntaxfehler: Code ist ungültig. Laufzeitfehler: Abbruch beim Ausführen. Logischer Fehler: läuft, aber falsches Ergebnis.", s=1)
    for i in range(1, 11):
        liste = rng.sample(range(1, 30), 4)
        op = rng.choice([("z.append(7)", lambda z: z + [7]), ("z.insert(0, 7)", lambda z: [7] + z), ("z.pop()", lambda z: z[:-1]),
                         ("z.remove(z[1])", lambda z: z[:1] + z[2:]), ("z.sort()", sorted), ("z.reverse()", lambda z: z[::-1])])
        w = op[1](list(liste))
        falsch = [str(liste), str(list(reversed(w))), str(w[1:]), str(sorted(w, reverse=True))]
        s.wahl("PRG-LISTOP", i, T, "PRG-L4", f"`z = {liste}`. Welchen Inhalt hat `z` nach `{op[0]}`?", str(w), falsch,
               "append hängt an, insert fügt an Position ein, pop entfernt das letzte, remove das erste passende Element.", s=2)
    struktur = [("Array/Liste", "Elemente mit festem Index, Zugriff über die Position"), ("Stack (Stapel)", "LIFO – das zuletzt abgelegte Element wird zuerst entnommen"),
                ("Queue (Warteschlange)", "FIFO – das zuerst eingefügte Element wird zuerst entnommen"), ("Dictionary / Map", "Zugriff auf Werte über einen eindeutigen Schlüssel"),
                ("Rekursion", "eine Funktion ruft sich selbst auf und braucht eine Abbruchbedingung"), ("Parameter", "Platzhalter in der Funktionsdefinition"),
                ("Rückgabewert", "Ergebnis, das eine Funktion mit return liefert"), ("lokale Variable", "nur innerhalb der Funktion sichtbar")]
    zuordnung(s, "PRG-STRUKT", T, "PRG-L4", struktur, "Was beschreibt **{a}**?", "Welcher Begriff passt: {b}?", rng=rng)

    # ---------- PRG-L5: Ausführung, Paradigmen, Werkzeuge ----------
    ausf = [("Compiler", "übersetzt den gesamten Quellcode vor der Ausführung in Maschinencode"), ("Interpreter", "führt den Quellcode Anweisung für Anweisung direkt aus"),
            ("Bytecode + virtuelle Maschine", "Zwischencode, der plattformunabhängig in einer Laufzeitumgebung läuft (z. B. Java, C#)"),
            ("Just-in-Time-Compiler", "übersetzt Bytecode während der Laufzeit in Maschinencode"), ("Linker", "verbindet übersetzte Objektdateien und Bibliotheken zu einem Programm"),
            ("Debugger", "hält das Programm an Haltepunkten an und zeigt Variablenwerte"), ("IDE", "Entwicklungsumgebung mit Editor, Debugger und Build-Werkzeugen"),
            ("Versionsverwaltung (Git)", "speichert Änderungsstände des Codes und ermöglicht Zusammenarbeit")]
    zuordnung(s, "PRG-AUSF", T, "PRG-L5", ausf, "Was macht ein(e) **{a}**?", "Welches Werkzeug/Konzept {b}?", rng=rng)
    sprachen = [("C", "kompiliert"), ("C++", "kompiliert"), ("Python", "interpretiert (bzw. Bytecode)"), ("JavaScript im Browser", "interpretiert / JIT"),
                ("Java", "Bytecode in der JVM"), ("C#", "Bytecode in der .NET-Laufzeit (CLR)"), ("Go", "kompiliert"), ("PHP", "interpretiert (bzw. Bytecode)")]
    zuordnung(s, "PRG-SPRACHE", T, "PRG-L5", sprachen, "Wie wird **{a}** typischerweise ausgeführt?", None, schwierigkeit=2, rng=rng)
    paradig = [("prozedural", "Programm als Folge von Anweisungen und Prozeduren/Funktionen"), ("objektorientiert", "Klassen und Objekte mit Attributen und Methoden"),
               ("funktional", "Funktionen ohne Seiteneffekte, unveränderliche Daten"), ("deklarativ (z. B. SQL)", "beschreibt WAS das Ergebnis sein soll, nicht WIE"),
               ("ereignisgesteuert", "Code reagiert auf Ereignisse wie Klicks oder Nachrichten")]
    zuordnung(s, "PRG-PARADIGMA", T, "PRG-L5", paradig, "Was kennzeichnet die **{a}e** Programmierung?" if False else "Was kennzeichnet das Paradigma **{a}**?",
              "Welches Paradigma: {b}?", rng=rng)
    git = [("git clone", "kopiert ein entferntes Repository auf den eigenen Rechner"), ("git add", "merkt Änderungen für den nächsten Commit vor (Staging)"),
           ("git commit", "speichert vorgemerkte Änderungen als neuen Stand mit Nachricht"), ("git push", "überträgt lokale Commits ins entfernte Repository"),
           ("git pull", "holt Änderungen vom entfernten Repository und führt sie zusammen"), ("git branch", "legt Zweige an oder listet sie auf"),
           ("git merge", "führt einen anderen Zweig in den aktuellen zusammen"), ("git status", "zeigt geänderte und vorgemerkte Dateien")]
    zuordnung(s, "PRG-GIT", T, "PRG-L5", git, "Was bewirkt `{a}`?", "Welcher Git-Befehl {b}?", rng=rng)
    tests = [("Unit-Test", "prüft einzelne Funktionen oder Klassen isoliert"), ("Integrationstest", "prüft das Zusammenspiel mehrerer Komponenten"),
             ("Systemtest", "prüft das Gesamtsystem gegen die Anforderungen"), ("Abnahmetest", "der Kunde prüft, ob die Anforderungen erfüllt sind"),
             ("Black-Box-Test", "testet nur anhand von Ein- und Ausgaben, ohne den Code zu kennen"), ("White-Box-Test", "testet mit Kenntnis des Codes, z. B. alle Zweige"),
             ("Regressionstest", "prüft nach Änderungen, ob Bestehendes noch funktioniert")]
    zuordnung(s, "PRG-TEST", T, "PRG-L5", tests, "Was ist ein **{a}**?", "Welche Testart {b}?", schwierigkeit=2, rng=rng)
    return s.fragen


def _verlauf(start, ende, op, schritt):
    x, werte = start, [start]
    while x < ende:
        x = x + schritt if op == "+" else x * schritt
        werte.append(x)
    return werte

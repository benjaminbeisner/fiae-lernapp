"""Erzeugt die Übungsprüfung als ausfüllbare PDF (AcroForm) und die Lösungshinweise."""
import io
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Preformatted

B, H = A4
LINKS, RECHTS_RAND, OBEN, UNTEN = 18 * mm, 22 * mm, 18 * mm, 20 * mm
BREITE = B - LINKS - RECHTS_RAND
GRAU = colors.HexColor("#555555")
HELL = colors.HexColor("#eef1f6")
LINIE = colors.HexColor("#9aa3b2")

ERSATZ = {"→": "->", "−": "-", "≈": "ca.", "≥": ">=", "≤": "<=", "⁰": "^0", "⁴": "^4", "⁵": "^5", "⁶": "^6", "⁷": "^7",
          "⁸": "^8", "⁹": "^9", "√": "Wurzel ", "–": "-", "✓": "x"}

TEXT = ParagraphStyle("t", fontName="Helvetica", fontSize=10, leading=13.5)
KLEIN = ParagraphStyle("k", parent=TEXT, fontSize=8.5, leading=11)
FETT = ParagraphStyle("f", parent=TEXT, fontName="Helvetica-Bold", fontSize=12, leading=15)
ZELLE = ParagraphStyle("z", parent=TEXT, fontSize=9, leading=11.5)
CODE = ParagraphStyle("c", fontName="Courier", fontSize=9, leading=11.5)


def sauber(t: str) -> str:
    for a, b in ERSATZ.items():
        t = t.replace(a, b)
    return t


def markup(t: str) -> str:
    t = sauber(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', t)
    return t.replace("\n", "<br/>")


class Blatt:
    """Kleiner Layout-Helfer: schreibt von oben nach unten und bricht bei Bedarf um."""

    def __init__(self, titel_kopf, nummer, formular=True):
        self.puffer = io.BytesIO()
        self.c = canvas.Canvas(self.puffer, pagesize=A4)
        self.c.setTitle(titel_kopf)
        self.kopf, self.nummer, self.formular = titel_kopf, nummer, formular
        self.seite = 0
        self.feldnr = 0
        self.neue_seite(erste=True)

    # ---------- Seitenrahmen ----------
    def neue_seite(self, erste=False):
        if not erste:
            self._fuss()
            self.c.showPage()
        self.seite += 1
        self.y = H - OBEN
        if self.seite > 1:
            self.c.setFont("Helvetica", 8)
            self.c.setFillColor(GRAU)
            self.c.drawString(LINKS, H - 11 * mm, self.kopf)
            self.c.drawRightString(B - RECHTS_RAND, H - 11 * mm, f"Prüfungsnummer {self.nummer}")
            self.c.setFillColor(colors.black)
            if self.formular:
                self.c.setStrokeColor(LINIE)
                self.c.line(B - RECHTS_RAND + 4 * mm, UNTEN, B - RECHTS_RAND + 4 * mm, H - OBEN)
                self.c.saveState()
                self.c.setFont("Helvetica", 7)
                self.c.setFillColor(GRAU)
                self.c.translate(B - 8 * mm, H / 2)
                self.c.rotate(90)
                self.c.drawCentredString(0, 0, "Korrekturrand")
                self.c.restoreState()

    def _fuss(self):
        self.c.setFont("Helvetica", 7.5)
        self.c.setFillColor(GRAU)
        self.c.drawString(LINKS, 10 * mm, "Selbst erstellte Übungsaufgaben im Stil der AP1 – keine Original-Prüfung der IHK/ZPA.")
        self.c.drawRightString(B - RECHTS_RAND, 10 * mm, f"Seite {self.seite}")
        self.c.setFillColor(colors.black)

    def platz(self, hoehe):
        if self.y - hoehe < UNTEN:
            self.neue_seite()

    def abstand(self, h):
        self.y -= h

    # ---------- Inhalte ----------
    def absatz(self, text, stil=TEXT, einzug=0, breite=None):
        p = Paragraph(markup(text), stil)
        w, h = p.wrap((breite or BREITE) - einzug, H)
        self.platz(h)
        p.drawOn(self.c, LINKS + einzug, self.y - h)
        self.y -= h

    def code(self, text):
        p = Preformatted(sauber(text), CODE)
        w, h = p.wrap(BREITE - 8 * mm, H)
        self.platz(h + 6 * mm)
        self.c.setFillColor(HELL)
        self.c.setStrokeColor(LINIE)
        self.c.rect(LINKS, self.y - h - 5 * mm, BREITE, h + 5 * mm, fill=1, stroke=1)
        self.c.setFillColor(colors.black)
        p.drawOn(self.c, LINKS + 4 * mm, self.y - h - 2.5 * mm)
        self.y -= h + 5 * mm

    def _feld(self, x, y, w, h, mehrzeilig=False, schrift="Helvetica", groesse=10):
        if not self.formular:
            return
        self.feldnr += 1
        self.c.acroForm.textfield(name=f"f{self.feldnr}", x=x, y=y, width=w, height=h, borderWidth=0, fillColor=None,
                                  borderColor=None, textColor=colors.HexColor("#123a8c"), fontName=schrift, fontSize=groesse,
                                  fieldFlags="multiline" if mehrzeilig else "", forceBorder=False)

    def zeilen(self, n):
        hoehe = n * 8 * mm
        self.platz(hoehe)
        self.c.setStrokeColor(LINIE)
        for i in range(1, n + 1):
            yy = self.y - i * 8 * mm
            self.c.line(LINKS, yy, LINKS + BREITE, yy)
        self._feld(LINKS, self.y - hoehe, BREITE, hoehe, mehrzeilig=True, groesse=11)
        self.y -= hoehe

    def rechnen(self, n):
        hoehe = n * 8 * mm
        self.platz(hoehe + 10 * mm)
        self.c.setStrokeColor(colors.HexColor("#c9d0db"))
        self.c.setLineWidth(0.4)
        k = 5 * mm
        x = LINKS
        while x <= LINKS + BREITE + 0.1:
            self.c.line(x, self.y - hoehe, x, self.y)
            x += k
        yy = self.y
        while yy >= self.y - hoehe - 0.1:
            self.c.line(LINKS, yy, LINKS + BREITE, yy)
            yy -= k
        self.c.setLineWidth(1)
        self._feld(LINKS, self.y - hoehe, BREITE, hoehe, mehrzeilig=True, schrift="Courier", groesse=10)
        self.y -= hoehe + 2 * mm
        self.felder(["Ergebnis:"])

    def felder(self, labels):
        for lab in labels:
            p = Paragraph(markup(lab), TEXT)
            lw = min(max(p.minWidth() + 4 * mm, 40 * mm), 95 * mm)
            w, h = p.wrap(lw, H)
            zeile = max(h, 8 * mm)
            self.platz(zeile + 1 * mm)
            p.drawOn(self.c, LINKS, self.y - zeile + 1.5 * mm)
            self.c.setStrokeColor(LINIE)
            self.c.line(LINKS + lw, self.y - zeile + 1 * mm, LINKS + BREITE, self.y - zeile + 1 * mm)
            self._feld(LINKS + lw, self.y - zeile + 1.2 * mm, BREITE - lw, 6.5 * mm)
            self.y -= zeile + 1 * mm

    def tabelle(self, kopf, zeilen, ausfuellbar=True):
        n = len(kopf)
        laengen = [max(len(sauber(str(kopf[i]))), *(len(sauber(str(z[i] or ""))) for z in zeilen)) for i in range(n)]
        laengen = [max(l, 14 if any(z[i] is None for z in zeilen) else 4, len(str(kopf[i])) + 3) for i, l in enumerate(laengen)]
        breiten = [BREITE * l / sum(laengen) for l in laengen]
        alle = [kopf] + zeilen
        hoehen = []
        for r, z in enumerate(alle):
            h = 0
            for i, zelle in enumerate(z):
                if zelle:
                    st = ParagraphStyle("zb", parent=ZELLE, fontName="Helvetica-Bold") if r == 0 else ZELLE
                    h = max(h, Paragraph(markup(str(zelle)), st).wrap(breiten[i] - 3 * mm, H)[1])
            leer = r > 0 and any(c is None for c in z)
            hoehen.append(max(h + 3 * mm, 10 * mm if leer else 6.5 * mm))
        self.platz(sum(hoehen))
        y = self.y
        self.c.setStrokeColor(colors.HexColor("#6b7383"))
        for r, z in enumerate(alle):
            x = LINKS
            for i, zelle in enumerate(z):
                if r == 0:
                    self.c.setFillColor(HELL)
                    self.c.rect(x, y - hoehen[r], breiten[i], hoehen[r], fill=1, stroke=1)
                    self.c.setFillColor(colors.black)
                else:
                    self.c.rect(x, y - hoehen[r], breiten[i], hoehen[r], fill=0, stroke=1)
                if zelle is None:
                    if ausfuellbar:
                        self._feld(x + 0.6 * mm, y - hoehen[r] + 0.6 * mm, breiten[i] - 1.2 * mm, hoehen[r] - 1.2 * mm,
                                   mehrzeilig=hoehen[r] > 11 * mm, groesse=9)
                elif zelle != "":
                    st = ParagraphStyle("zb", parent=ZELLE, fontName="Helvetica-Bold") if r == 0 else ZELLE
                    p = Paragraph(markup(str(zelle)), st)
                    w, h = p.wrap(breiten[i] - 3 * mm, H)
                    p.drawOn(self.c, x + 1.5 * mm, y - 1.5 * mm - h)
                x += breiten[i]
            y -= hoehen[r]
        self.y = y

    def fertig(self):
        self._fuss()
        self.c.save()
        return self.puffer.getvalue()


HINWEISE = [
    "Prüfen Sie, ob der Aufgabensatz vollständig ist (4 Aufgaben).",
    "Tragen Sie Ihren Namen und das Datum auf dem Deckblatt ein.",
    "Lesen Sie zuerst die Ausgangssituation und die jeweilige Aufgabe vollständig durch.",
    "Halten Sie sich an die Vorgaben der Aufgabenstellung, z. B. die Anzahl geforderter Angaben. Werden mehr Angaben gemacht, werden nur die ersten bewertet.",
    "Antworten Sie stichwortartig, sofern nicht ausdrücklich ganze Sätze gefordert sind.",
    "Bei Rechenaufgaben muss der Rechenweg erkennbar sein. Ein nicht programmierbarer Taschenrechner ist erlaubt.",
    "Die Bearbeitungszeit beträgt 90 Minuten. Stellen Sie sich einen Wecker.",
    "Die PDF ist ausfüllbar (z. B. mit Edge, Firefox, Adobe Acrobat oder auf dem Tablet). Sie können sie auch ausdrucken.",
]


def _antwort_hoehe(a):
    art = a[0]
    if art == "zeilen":
        return a[1] * 8 * mm
    if art == "rechnen":
        return a[1] * 8 * mm + 12 * mm
    if art == "felder":
        return len(a[1]) * 9 * mm
    if art == "tabelle":
        return 7 * mm + len(a[2]) * 10 * mm
    return a[1] * 6 * mm


def _text_hoehe(text, breite=BREITE):
    return Paragraph(markup(text), TEXT).wrap(breite, H)[1]


def _label(i):
    return "abcdefghijklmnop"[i] + ")"


def aufgaben_pdf(p: dict) -> bytes:
    bl = Blatt("Übungsprüfung AP1 · Fachinformatiker/-in", p["nummer"])
    c = bl.c
    # ---------- Deckblatt ----------
    c.setFont("Helvetica", 9)
    c.drawString(LINKS, H - 20 * mm, "Vor- und Familienname")
    c.line(LINKS + 36 * mm, H - 21 * mm, LINKS + 120 * mm, H - 21 * mm)
    bl._feld(LINKS + 36 * mm, H - 20.5 * mm, 84 * mm, 6 * mm)
    c.drawString(LINKS + 125 * mm, H - 20 * mm, "Datum")
    c.line(LINKS + 137 * mm, H - 21 * mm, B - RECHTS_RAND, H - 21 * mm)
    bl._feld(LINKS + 137 * mm, H - 20.5 * mm, B - RECHTS_RAND - LINKS - 137 * mm, 6 * mm)
    c.setFillColor(HELL)
    c.rect(LINKS, H - 78 * mm, BREITE, 48 * mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(LINKS + 6 * mm, H - 44 * mm, "Übungsprüfung AP1")
    c.setFont("Helvetica", 13)
    c.drawString(LINKS + 6 * mm, H - 53 * mm, "Teil 1 der Abschlussprüfung · Einrichten eines IT-gestützten Arbeitsplatzes")
    c.drawString(LINKS + 6 * mm, H - 61 * mm, "Fachinformatikerin / Fachinformatiker")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LINKS + 6 * mm, H - 72 * mm, "4 Aufgaben  ·  90 Minuten Prüfungszeit  ·  100 Punkte")
    c.setFont("Helvetica", 9)
    c.drawRightString(B - RECHTS_RAND - 4 * mm, H - 72 * mm, f"Prüfungsnummer {p['nummer']}")
    bl.y = H - 90 * mm
    bl.absatz("**Bearbeitungshinweise**", FETT)
    bl.abstand(2 * mm)
    for i, h in enumerate(HINWEISE, 1):
        bl.absatz(f"{i}. {h}", KLEIN)
        bl.abstand(1.2 * mm)
    bl.abstand(8 * mm)
    bl.absatz("**Bewertung** (nach dem Bearbeiten mit den Lösungshinweisen selbst eintragen)", TEXT)
    bl.abstand(2 * mm)
    bl.tabelle(["", "1. Aufgabe", "2. Aufgabe", "3. Aufgabe", "4. Aufgabe", "Gesamt"], [["Punkte", None, None, None, None, None]])
    bl.abstand(8 * mm)
    bl.absatz("Diese Übungsprüfung wurde automatisch aus selbst geschriebenen Aufgaben zusammengestellt und orientiert sich am Aufbau "
              "von Teil 1 der Abschlussprüfung (AO 2020). Sie ist keine Prüfung der IHK oder der ZPA.", KLEIN)
    bl.neue_seite()
    # ---------- Ausgangssituation ----------
    bl.absatz("**Die Aufgaben 1 bis 4 beziehen sich auf folgende Ausgangssituation:**")
    bl.abstand(2 * mm)
    bl.absatz(p["situation"])
    bl.abstand(6 * mm)
    for nr, a in enumerate(p["aufgaben"], 1):
        if nr > 1:
            bl.neue_seite()
        bl.absatz(f"**{nr}. Aufgabe ({a['punkte']} Punkte)**", FETT)
        bl.abstand(3 * mm)
        teil = 0
        for b in a["bausteine"]:
            if b.get("intro"):
                bl.platz(_text_hoehe(b["intro"]) + 35 * mm)
                bl.absatz(b["intro"])
                bl.abstand(2.5 * mm)
            mehrere = len(b["teile"]) > 1
            haupt = _label(teil)
            for j, t in enumerate(b["teile"]):
                label = f"{haupt[0]}{'abcdefgh'[j]})" if mehrere else haupt
                if t.get("daten"):
                    bl.tabelle(t["daten"][1], t["daten"][2], ausfuellbar=False)
                    bl.abstand(3 * mm)
                if t.get("code"):
                    bl.code(t["code"])
                    bl.abstand(3 * mm)
                bl.platz(_text_hoehe(t["text"], BREITE - 22 * mm) + 2.5 * mm + min(_antwort_hoehe(t["antwort"]), 110 * mm))
                y0 = bl.y
                bl.absatz(f"{label} {t['text']}", breite=BREITE - 22 * mm)
                c.setFont("Helvetica", 9)
                c.drawRightString(LINKS + BREITE, y0 - 10, f"{t['punkte']} Punkt{'e' if t['punkte'] != 1 else ''}")
                bl.abstand(2.5 * mm)
                art = t["antwort"][0]
                if art == "zeilen":
                    bl.zeilen(t["antwort"][1])
                elif art == "rechnen":
                    bl.rechnen(t["antwort"][1])
                elif art == "felder":
                    bl.felder(t["antwort"][1])
                elif art == "tabelle":
                    bl.tabelle(t["antwort"][1], t["antwort"][2])
                elif art == "code":
                    n = t["antwort"][1]
                    bl.platz(n * 6 * mm)
                    c.setStrokeColor(LINIE)
                    c.rect(LINKS, bl.y - n * 6 * mm, BREITE, n * 6 * mm)
                    bl._feld(LINKS + 1 * mm, bl.y - n * 6 * mm + 1 * mm, BREITE - 2 * mm, n * 6 * mm - 2 * mm, mehrzeilig=True, schrift="Courier")
                    bl.y -= n * 6 * mm
                bl.abstand(6 * mm)
            teil += 1
    return bl.fertig()


def loesung_pdf(p: dict) -> bytes:
    bl = Blatt("Lösungshinweise zur Übungsprüfung AP1", p["nummer"], formular=False)
    bl.absatz("**Lösungshinweise zur Übungsprüfung AP1**", ParagraphStyle("g", parent=FETT, fontSize=17, leading=21))
    bl.abstand(2 * mm)
    bl.absatz(f"Prüfungsnummer {p['nummer']} · Andere fachlich richtige Lösungen sind ebenfalls zu werten. "
              "Bei Rechenaufgaben werden Folgefehler berücksichtigt.", KLEIN)
    bl.abstand(6 * mm)
    for nr, a in enumerate(p["aufgaben"], 1):
        bl.absatz(f"**{nr}. Aufgabe ({a['punkte']} Punkte)**", FETT)
        bl.abstand(2 * mm)
        teil = 0
        for b in a["bausteine"]:
            mehrere = len(b["teile"]) > 1
            haupt = _label(teil)
            for j, t in enumerate(b["teile"]):
                label = f"{haupt[0]}{'abcdefgh'[j]})" if mehrere else haupt
                bl.absatz(f"**{label}** ({t['punkte']} P.)")
                teile = re.split(r"```\n?(.*?)\n?```", t["loesung"], flags=re.S)
                for k, stueck in enumerate(teile):
                    if k % 2:
                        bl.code(stueck)
                    elif stueck.strip():
                        bl.absatz(stueck.strip(), einzug=6 * mm)
                bl.abstand(3 * mm)
            teil += 1
        bl.abstand(4 * mm)
    bl.absatz("**Notenschlüssel (IHK)**", FETT)
    bl.abstand(2 * mm)
    bl.tabelle(["Punkte", "100–92", "91–81", "80–67", "66–50", "49–30", "29–0"],
               [["Note", "1 (sehr gut)", "2 (gut)", "3 (befriedigend)", "4 (ausreichend)", "5 (mangelhaft)", "6 (ungenügend)"]], ausfuellbar=False)
    return bl.fertig()

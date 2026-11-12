"""Aufgabenbereich: IT-Sicherheit, Datenschutz, Kommunikation und Arbeitsorganisation."""
from .bausteine_basis import F, R, T, TAB, Z, zahl


def schutzziele(rng, k):
    m = rng.sample([("Festplattenverschlüsselung der Notebooks", "Vertraulichkeit"), ("USV für den Server", "Verfügbarkeit"),
                    ("Hashwert beim Download prüfen", "Integrität"), ("RAID 1 im Server", "Verfügbarkeit"),
                    ("Berechtigungskonzept für Ordner", "Vertraulichkeit"), ("digitale Signatur von Angeboten", "Authentizität/Integrität"),
                    ("Änderungsprotokoll in der Datenbank", "Integrität"), ("redundante Internetanbindung", "Verfügbarkeit")], 4)
    return {"thema": "sicherheit", "teile": [
        T("Nennen Sie die drei klassischen Schutzziele der Informationssicherheit.", 2, Z(2), "Vertraulichkeit, Integrität, Verfügbarkeit (alle drei: 2 P., zwei: 1 P.)."),
        T("Ordnen Sie den Maßnahmen das Schutzziel zu, das sie in erster Linie unterstützen.", 4, TAB(["Maßnahme", "Schutzziel"], [[a, None] for a, _ in m]),
          "; ".join(f"{a}: {b}" for a, b in m) + "."),
    ]}


def backup(rng, k):
    art = rng.choice(["inkrementell", "differenziell"])
    tag = rng.choice(["Mittwoch", "Donnerstag", "Freitag"])
    n = {"Mittwoch": 2, "Donnerstag": 3, "Freitag": 4}[tag]
    voll, aend = rng.choice([400, 600, 800]), rng.choice([20, 30, 40])
    noetig = "Vollsicherung vom Sonntag + " + (", ".join(["Mo", "Di", "Mi", "Do"][:n]) + " (alle Inkremente)" if art == "inkrementell"
                                                 else f"die differenzielle Sicherung vom {['Mo', 'Di', 'Mi', 'Do'][n-1]}")
    speicher = voll + (n * aend if art == "inkrementell" else sum(aend * i for i in range(1, n + 1)))
    return {"thema": "sicherheit", "intro": f"Die {k['name']} sichert sonntags vollständig ({voll} GB) und montags bis freitags abends **{art}**. Täglich ändern sich ca. {aend} GB (jeweils andere Dateien).",
            "teile": [
                T(f"Am **{tag}morgen** fällt der Server aus. Nennen Sie die Sicherungen, die zurückgespielt werden müssen.", 2, Z(2), noetig + "."),
                T(f"Berechnen Sie den Speicherplatz, den alle Sicherungen von Sonntag bis einschließlich {['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag'][n-1]} belegen.", 2, R(3),
                  f"{voll} GB + " + (f"{n} × {aend} GB" if art == "inkrementell" else " + ".join(f"{aend*i} GB" for i in range(1, n + 1))) + f" = **{speicher} GB**."),
                T("Erläutern Sie die 3-2-1-Regel.", 2, Z(3), "3 Kopien der Daten, auf 2 unterschiedlichen Speichermedien, 1 Kopie außer Haus (offsite/offline)."),
            ]}


def zwei_faktor(rng, k):
    return {"thema": "sicherheit", "teile": [
        T("Für den Fernzugriff soll eine Zwei-Faktor-Authentisierung eingeführt werden. Nennen Sie die drei Faktorkategorien mit je einem Beispiel.", 3, Z(3),
          "Wissen (Passwort, PIN), Besitz (Smartcard, Token, Smartphone-App), Inhärenz/Biometrie (Fingerabdruck, Gesicht)."),
        T("Begründen Sie, ob „Passwort + PIN“ eine Zwei-Faktor-Authentisierung ist.", 1, Z(2), "Nein, beide gehören zur Kategorie Wissen."),
    ]}


def verschluesselung(rng, k):
    n = rng.choice([5, 8, 10, 12, 20])
    return {"thema": "sicherheit", "teile": [
        T("Beschreiben Sie das Prinzip der hybriden Verschlüsselung und nennen Sie ein Beispiel für ihren Einsatz.", 3, Z(4),
          "Ein zufälliger symmetrischer Sitzungsschlüssel wird mit dem öffentlichen Schlüssel des Empfängers (asymmetrisch) ausgetauscht; die eigentlichen Daten werden schnell symmetrisch verschlüsselt. Beispiel: TLS/HTTPS, S/MIME, PGP."),
        T(f"**{n} Mitarbeitende** sollen paarweise vertraulich kommunizieren. Berechnen Sie die Anzahl der benötigten Schlüssel bei symmetrischer und bei asymmetrischer Verschlüsselung.", 2,
          F("symmetrisch:", "asymmetrisch:"), f"symmetrisch n(n−1)/2 = {n*(n-1)//2}; asymmetrisch 2n = {2*n}."),
    ]}


def dsgvo(rng, k):
    d = rng.sample([("Name und Telefonnummer eines Kunden", "personenbezogen"), ("Diagnose in einer Krankmeldung", "besondere Kategorie (Art. 9)"),
                    ("Anonyme Besucherstatistik", "nicht personenbezogen"), ("IP-Adresse eines Website-Besuchers", "personenbezogen"),
                    ("Religionszugehörigkeit für die Lohnabrechnung", "besondere Kategorie (Art. 9)"), ("Raumtemperatur im Serverraum", "nicht personenbezogen")], 3)
    return {"thema": "sicherheit", "teile": [
        T("Ordnen Sie die Daten ein: nicht personenbezogen, personenbezogen oder besondere Kategorie (Art. 9 DSGVO).", 3, TAB(["Daten", "Einordnung"], [[a, None] for a, _ in d]),
          "; ".join(f"{a}: {b}" for a, b in d) + "."),
        T("Nennen Sie zwei Rechte der betroffenen Person nach der DSGVO.", 2, Z(2), "z. B. Auskunft (Art. 15), Berichtigung (16), Löschung (17), Einschränkung (18), Datenübertragbarkeit (20), Widerspruch (21)."),
        T("Innerhalb welcher Frist muss eine Datenpanne der Aufsichtsbehörde gemeldet werden?", 1, F("Frist:"), "72 Stunden nach Bekanntwerden."),
    ]}


def tom(rng, k):
    t = rng.sample([("Chipkarte für den Serverraum", "Zutrittskontrolle"), ("automatische Bildschirmsperre", "Zugangskontrolle"),
                    ("Rechtekonzept für die Mandantenakten", "Zugriffskontrolle"), ("VPN für die Datenübertragung zwischen Standorten", "Weitergabekontrolle"),
                    ("Protokollierung von Änderungen", "Eingabekontrolle"), ("tägliche Datensicherung", "Verfügbarkeitskontrolle")], 4)
    return {"thema": "sicherheit", "teile": [
        T("Ordnen Sie die technischen und organisatorischen Maßnahmen (TOM) der passenden Kontrolle zu.", 4, TAB(["Maßnahme", "Kontrollart"], [[a, None] for a, _ in t]),
          "; ".join(f"{a}: {b}" for a, b in t) + "."),
    ]}


def phishing(rng, k):
    return {"thema": "sicherheit", "intro": "Eine Mitarbeiterin erhält eine E-Mail, angeblich von der Bank, mit der Aufforderung, sich wegen einer Kontosperrung sofort über einen Link anzumelden.",
            "teile": [T("Nennen Sie drei Merkmale, an denen Phishing-Mails erkannt werden können.", 3, Z(3),
                        "z. B. falsche/ähnliche Absenderdomain, Zeitdruck/Drohung, Link auf fremde Domain, Aufforderung zur Eingabe von Zugangsdaten, unpersönliche Anrede, Rechtschreibfehler, unerwartete Anhänge."),
                      T("Nennen Sie zwei organisatorische Maßnahmen gegen Phishing.", 2, Z(2), "Schulung/Sensibilisierung, Meldeweg für verdächtige Mails, Phishing-Simulationen, Vier-Augen-Prinzip bei Zahlungen.")]}


def passwort(rng, k):
    z, l = rng.choice([(62, 6), (26, 8), (10, 6), (36, 6)])
    rate = rng.choice([10**6, 10**7])
    return {"thema": "sicherheit", "teile": [
        T(f"Ein Passwort besteht aus genau **{l} Zeichen** aus einem Zeichenvorrat von **{z} Zeichen**. Ein Angreifer testet **{zahl(rate,0)} Passwörter pro Sekunde**. "
          "Berechnen Sie die Anzahl möglicher Passwörter und die maximale Dauer eines Brute-Force-Angriffs in Stunden.", 3, R(4),
          f"{z}^{l} = {zahl(z**l,0)} Kombinationen; ÷ {zahl(rate,0)} = {zahl(z**l/rate)} s ÷ 3.600 = **{zahl(z**l/rate/3600)} h**."),
        T("Nennen Sie zwei Maßnahmen gegen Brute-Force-Angriffe.", 2, Z(2), "Kontosperre/Verzögerung nach Fehlversuchen, lange Passwörter/Passphrasen, 2FA, Captcha, Überwachung der Anmeldeversuche."),
    ]}


def signatur(rng, k):
    return {"thema": "sicherheit", "teile": [
        T("Angebote sollen digital signiert versendet werden. Beschreiben Sie, wie eine digitale Signatur erstellt und vom Empfänger geprüft wird.", 4, Z(6),
          "Absender bildet Hashwert des Dokuments und verschlüsselt ihn mit seinem privaten Schlüssel (Signatur). Empfänger entschlüsselt die Signatur mit dem öffentlichen Schlüssel des Absenders, "
          "bildet selbst den Hash und vergleicht beide. Gleich → unverändert und echt (Integrität, Authentizität)."),
    ]}


def verfuegbarkeit(rng, k):
    p = rng.choice([99.5, 99.9, 99.95])
    h = 8760 * (100 - p) / 100
    return {"thema": "sicherheit", "teile": [
        T(f"Der Dienstleister garantiert eine Verfügbarkeit von **{zahl(p)} %** pro Jahr (365 Tage). Berechnen Sie die maximal zulässige Ausfallzeit in Stunden und Minuten.", 3, R(3),
          f"8.760 h × {zahl(100-p)} % = {zahl(h)} h = **{zahl(h*60,0)} min** (≈ {int(h)} h {round((h-int(h))*60)} min)."),
    ]}


def vier_ohren(rng, k):
    satz = rng.choice(["„Der Ausdruck ist ja schon wieder nicht fertig.“", "„Das Ticket liegt seit drei Tagen bei Ihnen.“", "„Der Server ist ja schon wieder langsam.“"])
    return {"thema": "kommunikation", "intro": f"Ein Kunde sagt am Telefon: {satz}",
            "teile": [T("Erläutern Sie die Aussage anhand der vier Seiten einer Nachricht nach Schulz von Thun.", 4, Z(5),
                        "Sachinhalt: Fakt (z. B. Ausdruck nicht fertig). Selbstoffenbarung: Kunde ist verärgert/gestresst. Beziehung: zweifelt an der Zuverlässigkeit des Gegenübers. "
                        "Appell: Kümmern Sie sich sofort darum! Je Seite 1 Punkt.")]}


def fragetechniken(rng, k):
    return {"thema": "kommunikation", "intro": "Im Beratungsgespräch soll der Bedarf des Kunden ermittelt werden.",
            "teile": [T("Erläutern Sie offene und geschlossene Fragen und formulieren Sie zu beiden ein passendes Beispiel für das Gespräch.", 4, Z(5),
                        "Offene Fragen (W-Fragen) lassen ausführliche Antworten zu, sammeln Informationen: „Wie arbeiten Sie aktuell mit …?“ Geschlossene Fragen erlauben Ja/Nein, "
                        "bestätigen Fakten: „Nutzen Sie bereits Windows 11?“")]}


def eisenhower(rng, k):
    a = rng.sample([("Der Mailserver ist ausgefallen.", "A: sofort selbst erledigen"), ("Schulungskonzept für nächstes Quartal", "B: planen/terminieren"),
                    ("Toner im Etagendrucker nachfüllen", "C: delegieren"), ("Werbe-Newsletter lesen", "D: nicht bearbeiten"),
                    ("Firewall-Lizenz läuft heute ab", "A: sofort selbst erledigen"), ("Netzwerkdokumentation aktualisieren", "B: planen/terminieren")], 4)
    return {"thema": "kommunikation", "teile": [
        T("Ordnen Sie die Aufgaben nach dem Eisenhower-Prinzip ein und nennen Sie die jeweilige Handlung.", 4, TAB(["Aufgabe", "Einordnung/Handlung"], [[x, None] for x, _ in a]),
          "; ".join(f"{x}: {y}" for x, y in a) + "."),
    ]}


def ki(rng, k):
    return {"thema": "kommunikation", "intro": f"Die {k['name']} möchte einen KI-Chatbot zum Formulieren von Kundenmails einsetzen.",
            "teile": [T("Nennen Sie zwei Chancen und zwei Risiken des Einsatzes.", 4, Z(5),
                        "Chancen: Zeitersparnis, einheitliche Formulierungen, Entlastung bei Routine, 24/7. Risiken: falsche/erfundene Aussagen, Datenschutz (Kundendaten an Dritte), "
                        "Urheberrecht, Abhängigkeit, fehlende Nachvollziehbarkeit – Ergebnisse müssen geprüft werden.")]}


def beschwerde(rng, k):
    return {"thema": "kommunikation", "teile": [
        T("Ein verärgerter Kunde ruft wegen eines Ausfalls an. Nennen Sie drei Verhaltensweisen für ein professionelles Beschwerdegespräch.", 3, Z(4),
          "ruhig und sachlich bleiben, ausreden lassen/aktiv zuhören, Verständnis zeigen, Problem zusammenfassen, konkrete Lösung/nächste Schritte und Termin nennen, dokumentieren."),
    ]}


BAUSTEINE = [schutzziele, backup, zwei_faktor, verschluesselung, dsgvo, tom, phishing, passwort, signatur, verfuegbarkeit,
             vier_ohren, fragetechniken, eisenhower, ki, beschwerde]

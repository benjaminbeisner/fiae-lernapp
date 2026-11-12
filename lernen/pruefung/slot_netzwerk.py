"""Aufgabenbereich: Netzwerk und Projektmanagement."""
import ipaddress

from ..generator.projekt import netzplan, wege
from .bausteine_basis import F, R, T, TAB, Z, zahl


def ip_grundlagen(rng, k):
    p = rng.choice([22, 23, 25, 26, 27, 28])
    ip = f"192.168.{rng.randint(1, 250)}.{rng.randint(1, 254)}" if rng.random() < .6 else f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
    net = ipaddress.IPv4Interface(f"{ip}/{p}").network
    return {"thema": "netzwerk", "intro": f"Ein neuer Drucker der {k['name']} erhält die IP-Adresse **{ip}/{p}**.",
            "teile": [T("Ermitteln Sie die folgenden Angaben.", 4, F("Subnetzmaske:", "Anzahl nutzbarer Hostadressen:", "Netzadresse:", "Broadcast-Adresse:"),
                        f"Maske {net.netmask}; Hosts 2^{32-p} − 2 = {2**(32-p)-2}; Netz {net.network_address}; Broadcast {net.broadcast_address}. Je 1 Punkt.")]}


def subnetting(rng, k):
    basis = ipaddress.IPv4Network(f"172.{rng.randint(16, 31)}.{rng.randint(0, 255)}.0/24")
    n = rng.choice([4, 6, 8])
    bits = (n - 1).bit_length()
    subs = list(basis.subnets(prefixlen_diff=bits))
    zeilen = []
    loes = []
    for i in (0, 1, len(subs) - 1):
        s = subs[i]
        h = list(s.hosts())
        zeilen.append([f"Subnetz {i+1}", None, None, None, None])
        loes.append(f"Subnetz {i+1}: {s.network_address}, {h[0]}, {h[-1]}, {s.broadcast_address}")
    abteil = ", ".join(["Verwaltung", "Lager", "Vertrieb", "Gäste-WLAN", "Server", "Technik", "Kasse", "Kameras"][:n])
    return {"thema": "netzwerk", "intro": f"Das Netz **{basis}** soll in **{n} gleich große Subnetze** für folgende Bereiche aufgeteilt werden: {abteil}.",
            "teile": [
                T("Ermitteln Sie das neue Präfix und die Anzahl nutzbarer Hosts je Subnetz.", 2, F("Präfix:", "Hosts je Subnetz:"),
                  f"{n} Subnetze → {bits} zusätzliche Bits → /{24+bits}; Hosts 2^{8-bits} − 2 = {2**(8-bits)-2}."),
                T("Vervollständigen Sie die Tabelle.", 6, TAB(["", "Netzadresse", "erste Hostadresse", "letzte Hostadresse", "Broadcast"], zeilen),
                  "; ".join(loes) + ". Je Zeile 2 Punkte."),
            ]}


def fehlersuche(rng, k):
    fehler = rng.sample([
        ("Patchkabel am PC defekt", "Link-LED prüfen, Kabel tauschen/testen", "Kabel ersetzen"),
        ("DHCP-Server nicht erreichbar", "ipconfig: Adresse 169.254.x.x (APIPA)?", "DHCP-Server/Netzverbindung prüfen, ipconfig /renew"),
        ("Namensauflösung funktioniert nicht", "ping auf IP klappt, auf Namen nicht; nslookup", "DNS-Server-Eintrag korrigieren"),
        ("Standardgateway falsch eingetragen", "ipconfig /all, ping auf Gateway", "richtiges Gateway eintragen"),
        ("IP-Adresse doppelt vergeben", "Fehlermeldung Adresskonflikt, arp -a", "eindeutige Adresse/DHCP-Reservierung"),
        ("Netzwerkdose nicht gepatcht", "Dose/Port am Patchfeld und Switch nachverfolgen", "Dose im Verteiler auf Switchport patchen"),
    ], 3)
    return {"thema": "netzwerk", "intro": "Ein Mitarbeiter meldet, dass er keine Webseiten aufrufen kann.",
            "teile": [T("Ergänzen Sie zu jedem möglichen Fehler eine Überprüfung und eine Fehlerbehebung.", 6,
                        TAB(["Möglicher Fehler", "Überprüfung", "Fehlerbehebung"], [[f[0], None, None] for f in fehler]),
                        " | ".join(f"{f[0]}: {f[1]} → {f[2]}" for f in fehler) + ". Je Zelle 1 Punkt, andere sinnvolle Lösungen sind zulässig.")]}


def ipv6(rng, k):
    adr = rng.sample(["2001:0db8:0000:0000:0000:0000:0000:0001", "fe80:0000:0000:0000:0202:b3ff:fe1e:8329",
                      "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "2001:0db8:0a0b:12f0:0000:0000:0000:0001"], 2)
    return {"thema": "netzwerk", "intro": f"Die {k['name']} möchte künftig IPv6 einsetzen.",
            "teile": [
                T("Kürzen Sie die folgenden Adressen so weit wie möglich.", 2, F(*[f"{a}:" for a in adr]),
                  "; ".join(f"{a} → {ipaddress.IPv6Address(a).compressed}" for a in adr) + "."),
                T("Beschreiben Sie zwei Unterschiede zwischen IPv4 und IPv6.", 2, Z(4),
                  "z. B. 32 vs. 128 Bit Adresslänge, dezimal mit Punkten vs. hexadezimal mit Doppelpunkten, kein Broadcast bei IPv6 (Multicast), SLAAC-Autokonfiguration, NAT bei IPv6 nicht nötig, vereinfachter Header."),
            ]}


def dhcp(rng, k):
    return {"thema": "netzwerk", "teile": [
        T("Die Clients sollen ihre Adressen per DHCP erhalten. Bringen Sie die vier DHCP-Nachrichten in die richtige Reihenfolge und nennen Sie zwei Angaben, die der DHCP-Server neben der IP-Adresse übermittelt.", 4,
          Z(4), "Discover → Offer → Request → Acknowledge (2 P.). Weitere Angaben (je 1 P.): Subnetzmaske, Standardgateway, DNS-Server, Lease-Dauer."),
    ]}


def osi(rng, k):
    el = rng.sample([("Switch", "2"), ("Router", "3"), ("HTTP", "7"), ("TCP", "4"), ("Hub", "1"), ("IP", "3"), ("MAC-Adresse", "2"), ("DNS", "7"), ("UDP", "4")], 4)
    return {"thema": "netzwerk", "teile": [
        T("Ordnen Sie die Begriffe der jeweiligen Schicht des OSI-Modells zu (Nummer der Schicht).", 4, TAB(["Begriff", "OSI-Schicht"], [[e[0], None] for e in el]),
          "; ".join(f"{a}: Schicht {b}" for a, b in el) + ". Je 1 Punkt."),
    ]}


def ports(rng, k):
    p = rng.sample([("HTTPS", "443"), ("SSH", "22"), ("DNS", "53"), ("SMTP", "25"), ("RDP", "3389"), ("IMAPS", "993"), ("HTTP", "80")], 3)
    return {"thema": "netzwerk", "teile": [
        T("In der Firewall sollen Dienste freigegeben werden. Nennen Sie die Standard-Ports.", 3, TAB(["Dienst", "Port"], [[a, None] for a, _ in p]),
          "; ".join(f"{a}: {b}" for a, b in p) + "."),
    ]}


def wlan(rng, k):
    return {"thema": "netzwerk", "intro": "Für Gäste und Kunden soll ein WLAN eingerichtet werden.",
            "teile": [T("Nennen Sie drei Maßnahmen, um das Firmennetz vor den Gästen zu schützen bzw. das Gäste-WLAN abzusichern.", 3, Z(4),
                        "z. B. eigenes VLAN/Gastnetz getrennt vom Firmennetz, Client-Isolation, WPA3/WPA2-Verschlüsselung, Captive Portal mit Nutzungsbedingungen, "
                        "zeitlich begrenzte Zugangscodes, Bandbreitenbegrenzung, Firewall-Regeln nur Internetzugang.")]}


def netzplan_aufgabe(rng, k):
    while True:
        namen, vor, dauer, faz, fez, saz, sez, gp, fp, ende = netzplan(rng, rng.choice([6, 7]))
        krit = [w for w in wege(namen, vor) if all(gp[y] == 0 for y in w)]
        if krit and any(gp[y] > 0 for y in namen):
            break
    schritte = ["Ist-Analyse", "Konzept erstellen", "Hardware bestellen", "Verkabelung", "Server einrichten", "Clients einrichten", "Test und Abnahme"]
    kopf = TAB(["Vorgang", "Beschreibung", "Dauer (Tage)", "Vorgänger"], [[x, schritte[i], str(dauer[x]), ", ".join(vor[x]) or "–"] for i, x in enumerate(namen)])
    return {"thema": "projektmanagement", "intro": f"Für das Projekt „{k['projekt']}“ liegt folgende Vorgangsliste vor (Beginn Tag 0).",
            "teile": [
                T("Vervollständigen Sie die Tabelle.", 6, TAB(["Vorgang", "FAZ", "FEZ", "SAZ", "SEZ", "GP"], [[x, None, None, None, None, None] for x in namen]),
                  " | ".join(f"{x}: {faz[x]}, {fez[x]}, {saz[x]}, {sez[x]}, GP {gp[x]}" for x in namen) + ". Folgefehler berücksichtigen.", daten=kopf),
                T("Nennen Sie die Projektdauer und den kritischen Pfad.", 2, F("Projektdauer:", "Kritischer Pfad:"),
                  f"Projektdauer {ende} Tage; kritischer Pfad: {' → '.join(krit[0])}."),
            ]}


def lasten_pflicht(rng, k):
    return {"thema": "projektmanagement", "teile": [
        T(f"Die {k['name']} hat ein Lastenheft übergeben. Erläutern Sie den Unterschied zwischen Lasten- und Pflichtenheft und nennen Sie, wer das jeweilige Dokument erstellt.", 4, Z(5),
          "Lastenheft: vom Auftraggeber, beschreibt WAS und WOFÜR (Anforderungen). Pflichtenheft: vom Auftragnehmer, beschreibt WIE und WOMIT die Anforderungen umgesetzt werden; Grundlage der Abnahme."),
    ]}


def anforderungen(rng, k):
    a = rng.sample([("Rechnungen können als PDF exportiert werden.", "funktional"), ("Die Suche antwortet in unter einer Sekunde.", "nicht-funktional"),
                    ("Mitarbeitende können Termine anlegen.", "funktional"), ("Das System ist zu 99,5 % verfügbar.", "nicht-funktional"),
                    ("Die Oberfläche ist barrierefrei.", "nicht-funktional"), ("Ein Admin kann Konten sperren.", "funktional")], 4)
    return {"thema": "projektmanagement", "teile": [
        T("Kennzeichnen Sie die Anforderungen als funktional oder nicht-funktional.", 4, TAB(["Anforderung", "funktional / nicht-funktional"], [[x, None] for x, _ in a]),
          "; ".join(f"{x} → {y}" for x, y in a) + "."),
    ]}


def smart(rng, k):
    return {"thema": "projektmanagement", "teile": [
        T("Der Projektleiter formuliert das Ziel: „Das neue System soll schneller sein.“ Erläutern Sie, warum das Ziel nicht SMART ist, und formulieren Sie es SMART.", 3, Z(4),
          "Nicht messbar und nicht terminiert (unspezifisch). Beispiel: „Bis zum 31.03. sinkt die durchschnittliche Ladezeit der Auftragsübersicht auf unter 2 Sekunden.“"),
    ]}


def scrum(rng, k):
    return {"thema": "projektmanagement", "intro": "Die Buchungsanwendung soll agil mit Scrum entwickelt werden.",
            "teile": [T("Nennen Sie die drei Verantwortlichkeiten (Rollen) in Scrum und beschreiben Sie jeweils eine Aufgabe.", 3, Z(4),
                        "Product Owner: priorisiert das Product Backlog; Scrum Master: sorgt für Scrum, beseitigt Hindernisse; Developers: setzen Backlog-Einträge im Sprint um."),
                      T("Nennen Sie zwei Scrum-Events.", 1, Z(2), "Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospektive (Sprint)."),
                      ]}


def stakeholder(rng, k):
    return {"thema": "projektmanagement", "teile": [
        T(f"Nennen Sie drei Stakeholder des Projekts „{k['projekt']}“ und jeweils ein mögliches Interesse.", 3, Z(4),
          "z. B. Geschäftsführung (Kosten, Termin), Mitarbeitende/Anwender (einfache Bedienung), Betriebsrat (keine Leistungskontrolle), Datenschutzbeauftragter (DSGVO), Kunden, Lieferanten."),
    ]}


def datenrate(rng, k):
    gb, mbit = rng.choice([2, 5, 10, 20]), rng.choice([50, 100, 250])
    s = gb * 8000 / mbit
    return {"thema": "netzwerk", "teile": [
        T(f"Ein Software-Update mit **{gb} GB** wird über eine Leitung mit **{mbit} Mbit/s** verteilt. Berechnen Sie die Übertragungsdauer in Minuten (ohne Overhead, 1 GB = 1.000 MB).", 3, R(4),
          f"{gb} GB × 8.000 = {zahl(gb*8000)} Mbit ÷ {mbit} = {zahl(s)} s ÷ 60 = **{zahl(s/60)} min**."),
    ]}


BAUSTEINE = [ip_grundlagen, subnetting, fehlersuche, ipv6, dhcp, osi, ports, wlan, netzplan_aufgabe, lasten_pflicht, anforderungen,
             smart, scrum, stakeholder, datenrate]

"""Zusatzabschnitte für die Lektionen: decken alles ab, was die erzeugten Fragen abfragen."""

V = {}

V["SEC-L1"] = """
| Schutzziel | Frage dahinter | Typische Maßnahmen |
|---|---|---|
| Vertraulichkeit | Wer darf die Daten **sehen**? | Verschlüsselung, Zugriffsrechte, Blickschutz, Aktenvernichter |
| Integrität | Sind die Daten **unverändert und korrekt**? | Hashwerte/Prüfsummen, Versionierung, Protokolle, Eingabevalidierung, WORM |
| Verfügbarkeit | Ist das System **nutzbar**, wenn man es braucht? | USV, RAID, Backup, Redundanz, Klimatisierung, Load Balancer |
| Authentizität | Ist der Absender/die Quelle **echt**? | digitale Signatur, Zertifikate, 2FA |

**Verfügbarkeit in Prozent:** erlaubter Ausfall = (100 % − Verfügbarkeit) × Gesamtzeit. Ein Jahr hat 8.760 h. Beispiel 99,9 %: 0,1 % × 8.760 h = 8,76 h ≈ 526 min.

**Schutzbedarf nach BSI:** normal (begrenzte Schäden), hoch (beträchtliche Schäden), sehr hoch (existenzbedrohend).
- **Maximumprinzip:** Der höchste Schutzbedarf der Anwendungen auf einem System bestimmt den Schutzbedarf des Systems.
- **Kumulationseffekt:** Viele kleine Schäden zusammen ergeben einen höheren Schutzbedarf.
- **Verteilungseffekt:** Ist eine Anwendung auf mehrere Systeme verteilt, kann der Schutzbedarf eines einzelnen Systems sinken.
- **IT-Grundschutz-Kompendium:** Bausteine mit Anforderungen für typische Komponenten. **ISMS:** Managementsystem für Informationssicherheit (z. B. ISO 27001).
"""

V["SEC-L2"] = """
| Verfahren | Art |
|---|---|
| AES, DES/3DES, ChaCha20, Blowfish, Twofish | symmetrisch |
| RSA, ECC, ElGamal | asymmetrisch |
| Diffie-Hellman | asymmetrisch (Schlüsselaustausch) |
| SHA-256, SHA-3, MD5 | Hashverfahren, **keine** Verschlüsselung |

**Anzahl der Schlüssel bei n Personen:** symmetrisch braucht jedes Paar einen eigenen Schlüssel: **n × (n − 1) ÷ 2**. Asymmetrisch braucht jede Person ein Schlüsselpaar: **2 × n**. Beispiel 10 Personen: 45 bzw. 20 Schlüssel.

**Wer nimmt welchen Schlüssel?** Alice schickt Bob etwas Vertrauliches: Verschlüsseln mit **Bobs öffentlichem**, Entschlüsseln mit **Bobs privatem** Schlüssel. Alice signiert: mit **Alices privatem** Schlüssel; Bob prüft mit **Alices öffentlichem** Schlüssel.

**Schlüssellänge:** Jedes zusätzliche Bit verdoppelt die Anzahl möglicher Schlüssel. 8 Bit mehr = 2⁸ = 256-mal so viele.
"""

V["SEC-L3"] = """
**Eigenschaften einer kryptografischen Hashfunktion:** feste Länge des Ergebnisses, nicht umkehrbar (Einwegfunktion), gleiche Eingabe → gleicher Hash, kleine Änderung → völlig anderer Hash, Kollisionen praktisch nicht auffindbar. MD5 und SHA-1 gelten als unsicher.

**Signatur in 5 Schritten:** 1. Hash der Nachricht bilden → 2. Hash mit privatem Schlüssel des Absenders verschlüsseln (= Signatur) → 3. Nachricht + Signatur senden → 4. Empfänger entschlüsselt die Signatur mit dem öffentlichen Schlüssel des Absenders → 5. Empfänger bildet selbst den Hash und vergleicht.

| Begriff | Bedeutung |
|---|---|
| CA (Zertifizierungsstelle) | bestätigt mit ihrer Signatur, dass ein öffentlicher Schlüssel zu einer Identität gehört |
| X.509-Zertifikat | Inhaber, öffentlicher Schlüssel, Gültigkeit, Aussteller, Signatur der CA |
| Root-Zertifikat | selbstsigniert, von einer Stammzertifizierungsstelle; im Betriebssystem/Browser hinterlegt |
| Zertifikatskette | Server-Zertifikat → Zwischenzertifikat → Root-Zertifikat |
| CRL / OCSP | Prüfung, ob ein Zertifikat widerrufen wurde |
| PKI | Infrastruktur zum Ausstellen, Verteilen und Prüfen von Zertifikaten |
| selbstsigniertes Zertifikat | vom Inhaber selbst unterschrieben → Browserwarnung |
| HMAC | Prüfsumme mit geheimem Schlüssel: Integrität + Authentizität |

**Was sichert was?** Verschlüsselung → Vertraulichkeit. Hash → Integrität. Signatur → Integrität, Authentizität, Nichtabstreitbarkeit. TLS → Vertraulichkeit, Integrität, Authentizität des Servers.

| Protokoll | Zweck |
|---|---|
| HTTPS | HTTP über TLS |
| SSH / SFTP | verschlüsselter Fernzugriff / Dateiübertragung über SSH |
| IPsec, WireGuard | VPN (IPsec oft Site-to-Site, WireGuard schlank und modern) |
| S/MIME, PGP/GPG | E-Mail signieren und verschlüsseln (S/MIME mit X.509, PGP mit Web of Trust) |
| WPA3 | aktueller WLAN-Sicherheitsstandard |
"""

V["SEC-L4"] = """
| Kategorie | Beispiele |
|---|---|
| Wissen | Passwort, PIN, Sicherheitsfrage |
| Besitz | Smartcard, Hardware-Token (FIDO2), Smartphone mit Authenticator-App, SMS-Code |
| Inhärenz (Biometrie) | Fingerabdruck, Gesicht, Iris |

**2FA** braucht zwei Faktoren aus **verschiedenen** Kategorien. Passwort + PIN ist keine 2FA (beides Wissen).

**Kombinationen:** Zeichenvorrat ^ Länge. 4-stellige PIN: 10⁴ = 10.000. 6 Kleinbuchstaben: 26⁶. **Brute-Force-Dauer** = Kombinationen ÷ Versuche pro Sekunde (im Mittel die Hälfte).

**Begriffe:** Identifikation (ich sage, wer ich bin) → Authentisierung (ich lege einen Nachweis vor) → Authentifizierung (das System prüft) → Autorisierung (Rechte werden erteilt). **Least Privilege:** nur die nötigsten Rechte. **Single Sign-on:** eine Anmeldung für mehrere Dienste. **Passkey/FIDO2:** Anmeldung per Schlüsselpaar, phishingresistent. **Salt:** Zufallswert, der vor dem Hashen an das Passwort angehängt wird.
"""

V["SEC-L5"] = """
| Art | Sichert | Wiederherstellen braucht |
|---|---|---|
| Vollsicherung | alles | nur die Vollsicherung |
| inkrementell | Änderungen seit der **letzten Sicherung** | Vollsicherung + **alle** Inkremente danach |
| differenziell | Änderungen seit der **letzten Vollsicherung** | Vollsicherung + **letzte** Differenzsicherung |

**Speicherbedarf:** Bei täglich gleich großen Änderungen wächst die differenzielle Sicherung jeden Tag (1×, 2×, 3× …), die inkrementelle bleibt gleich groß.

**Weitere Begriffe:** Spiegelung/Replikation (aktuelle Kopie, schützt nicht vor Löschfehlern), Snapshot (Momentaufnahme), Offline-Backup (ohne Netzverbindung, schützt vor Ransomware), Archivierung (langfristig, unverändert), Restore-Test (Wiederherstellung regelmäßig prüfen). **RPO:** maximal tolerierter Datenverlust. **RTO:** maximal tolerierte Wiederherstellungszeit.

**Sicherungsdauer** = Datenmenge ÷ Geschwindigkeit, z. B. 1.000 GB = 1.000.000 MB ÷ 200 MB/s = 5.000 s ≈ 1,39 h.
"""

V["SEC-L6"] = """
**Personenbezogen** ist alles, was sich einer Person zuordnen lässt: Name, Adresse, E-Mail, Personalnummer, IP-Adresse, Kfz-Kennzeichen. **Besondere Kategorien (Art. 9):** Gesundheit, Religion, ethnische Herkunft, Gewerkschaft, Biometrie zur Identifizierung, politische Meinung, Sexualleben. Anonyme Statistiken oder Messwerte ohne Personenbezug sind nicht personenbezogen.

| Recht | Artikel |
|---|---|
| Auskunft | Art. 15 |
| Berichtigung | Art. 16 |
| Löschung („Recht auf Vergessenwerden“) | Art. 17 |
| Einschränkung der Verarbeitung | Art. 18 |
| Datenübertragbarkeit | Art. 20 |
| Widerspruch | Art. 21 |

**Grundsätze (Art. 5):** Rechtmäßigkeit, Transparenz, Zweckbindung, Datenminimierung, Richtigkeit, Speicherbegrenzung, Integrität und Vertraulichkeit, Rechenschaftspflicht.

**Zahlen:** Datenpanne innerhalb von **72 Stunden** melden. Auskunft grundsätzlich innerhalb **eines Monats**. Datenschutzbeauftragter in Deutschland ab **20 Personen**, die ständig automatisiert personenbezogene Daten verarbeiten. Bußgeld bis 20 Mio. € oder **4 %** des weltweiten Jahresumsatzes.

| Kontrolle (TOM) | Ziel | Beispiel |
|---|---|---|
| Zutrittskontrolle | keine Unbefugten in den Räumen | Schlüssel, Chipkarte |
| Zugangskontrolle | keine Unbefugten am System | Login, Bildschirmsperre |
| Zugriffskontrolle | nur nötige Daten sehen | Rechtekonzept |
| Weitergabekontrolle | Schutz beim Transport | Verschlüsselung, VPN |
| Eingabekontrolle | nachvollziehbar, wer was geändert hat | Protokollierung |
| Verfügbarkeitskontrolle | Schutz vor Verlust | Backup, USV |

**Auftragsverarbeitungsvertrag (AVV):** regelt, wie ein Dienstleister Daten im Auftrag verarbeitet.
"""

V["SEC-L7"] = """
| Schadsoftware | Merkmal |
|---|---|
| Virus | hängt sich an Dateien, verbreitet sich beim Ausführen |
| Wurm | verbreitet sich selbstständig über das Netz |
| Trojaner | tarnt sich als nützliches Programm |
| Ransomware | verschlüsselt Daten, fordert Lösegeld |
| Spyware / Keylogger | spioniert aus / zeichnet Tastatureingaben auf |
| Rootkit | versteckt sich tief im System |
| Backdoor | versteckter Zugang |
| Botnetz | ferngesteuerte infizierte Rechner, z. B. für DDoS |
| Adware | ungewollte Werbung |

| Angriff | Merkmal | Schutz |
|---|---|---|
| Phishing / Spear-Phishing | gefälschte Nachrichten, bei Spear gezielt auf eine Person | Schulung, Absender und Link prüfen |
| Vishing / Smishing | per Telefon / per SMS | Rückruf über bekannte Nummer |
| CEO-Fraud | angeblicher Chef fordert Überweisung | Vier-Augen-Prinzip, Rückfrage |
| Tailgating / Shoulder Surfing | hinterherlaufen / über die Schulter schauen | Vereinzelungsanlage, Sichtschutz |
| Baiting | präparierter USB-Stick wird ausgelegt | keine fremden Datenträger anschließen |
| DDoS | Überlastung durch viele Anfragen | Filter, CDN, Redundanz |
| Man-in-the-Middle | Angreifer sitzt zwischen den Partnern | Ende-zu-Ende-Verschlüsselung, Zertifikate prüfen |
| SQL-Injection | Eingaben verändern SQL-Abfragen | Prepared Statements |
| XSS | Skript läuft im Browser anderer Nutzer | Escaping, Content Security Policy |
| Brute-Force / Credential Stuffing | Durchprobieren / erbeutete Daten woanders testen | Kontosperre, 2FA, eigene Passwörter |
| Zero-Day-Exploit | Lücke ohne Patch | schnelles Patchmanagement, Härtung |

**Schutzeinrichtungen:** Firewall (filtert nach Regeln), IDS (erkennt und meldet), IPS (erkennt und blockiert), DMZ (eigenes Netz für öffentliche Server), VPN, Sandbox (isoliert ausführen), Honeypot (Lockziel), Virenscanner, Patchmanagement.

**Phishing erkennen:** falsche Absenderdomain, Zeitdruck/Drohung, Link auf fremde Domain, Aufforderung zur Passworteingabe, unerwartete Anhänge. Logo, korrekte Anrede oder HTTPS beweisen **nicht**, dass eine Mail echt ist.
"""

V["WIR-L1"] = """
**Bezugskalkulation (Einkauf):**

| Schritt | Rechnung |
|---|---|
| Listeneinkaufspreis | Menge × Stückpreis |
| − Rabatt | → Zieleinkaufspreis |
| − Skonto | → Bareinkaufspreis |
| + Bezugskosten (Fracht, Verpackung) | → **Bezugspreis (Einstandspreis)** |

**Verkaufskalkulation:** Bezugspreis + Handlungskosten (%) = Selbstkosten; + Gewinn (%) = Barverkaufspreis; Kundenskonto wird **im Hundert** gerechnet: Zielverkaufspreis = Barverkaufspreis ÷ (1 − Skontosatz).

**Netto aus Brutto:** Brutto ÷ 1,19 (nicht × 0,81!). **Enthaltene USt:** Brutto − Netto.
"""

V["WIR-L2"] = """
**Quantitativer Angebotsvergleich:** Für jedes Angebot den Bezugspreis berechnen (Rabatt, Skonto, Versand) und den günstigsten wählen. **Qualitativer Vergleich:** Service, Qualität, Zuverlässigkeit, Lieferzeit.

**Nutzwertanalyse in 4 Schritten:** Kriterien festlegen → gewichten (Summe **100 %**) → Punkte vergeben → Punkte × Gewicht summieren. Beispiel: Preis 50 % × 8 + Service 30 % × 6 + Garantie 20 % × 9 = 4 + 1,8 + 1,8 = 7,6.
- **Vorteil:** auch nicht-monetäre Kriterien zählen.
- **Nachteil:** Gewichtung und Punktvergabe sind subjektiv.
- **K.-o.-Kriterium:** Wird es nicht erfüllt, scheidet das Angebot sofort aus.
"""

V["WIR-L3"] = """
**Lineare Abschreibung (AfA):** jährlicher Betrag = Anschaffungskosten ÷ Nutzungsdauer. **Restbuchwert** nach n Jahren = Anschaffungskosten − n × AfA.

**Leasing vs. Kauf:** Gesamtkosten Leasing = Rate × Monate + Sonderzahlung, dann mit dem Kaufpreis vergleichen. Der **Leasinggeber bleibt Eigentümer**, die Liquidität wird geschont, Raten sind in der Regel Betriebsausgaben, und nach Laufzeitende ist oft ein Tausch gegen neue Geräte möglich. Leasing ist über die Laufzeit **nicht** automatisch günstiger.

**Amortisationszeit** = Investition ÷ Ersparnis (oder Rückfluss) pro Zeiteinheit.
"""

V["WIR-L4"] = """
| Vertrag | Kennzeichen |
|---|---|
| Kaufvertrag | Eigentum an einer Sache gegen Geld |
| Werkvertrag | ein **Erfolg/Ergebnis** ist geschuldet, mit Abnahme (z. B. fertige App, Dokumentation) |
| Dienstvertrag | eine **Tätigkeit** ist geschuldet, kein Erfolg (z. B. Support nach Stunden, Schulung) |
| Mietvertrag | Gebrauch gegen Entgelt |
| Leihvertrag | Gebrauch **unentgeltlich** |
| Leasingvertrag | Gebrauch gegen Raten, Eigentümer bleibt der Leasinggeber |
| Lizenzvertrag | Nutzungsrecht an Software |
| Arbeitsvertrag | abhängige Beschäftigung |

**Vertragsstörungen:** mangelhafte Lieferung (defekt, falsche Menge, falsche Ware), Lieferungsverzug, Annahmeverzug (Kunde nimmt nicht an), Zahlungsverzug. Bei Mängeln zuerst **Nacherfüllung**; erst wenn sie fehlschlägt, Rücktritt oder Minderung. Zwischen Kaufleuten gilt: Ware unverzüglich prüfen und Mängel rügen. Im ersten Jahr nach Übergabe gilt beim Verbrauchsgüterkauf die **Beweislastumkehr** zugunsten des Kunden. Ohne festen Termin braucht es für den Verzug meist eine **Mahnung**.

**Geschäftsfähigkeit:** unter 7 Jahren geschäftsunfähig, 7–17 beschränkt geschäftsfähig (Taschengeldparagraf), ab 18 voll geschäftsfähig.

**Antrag und Annahme:** Kataloge, Werbung und Shop-Anzeigen sind nur eine **Aufforderung zur Abgabe eines Angebots**. Die Bestellung darauf ist der **Antrag**, die Auftragsbestätigung die **Annahme**. Bestellt der Kunde genau auf ein verbindliches Angebot, ist seine Bestellung die Annahme.
"""

V["WIR-L5"] = """
**Beispiele:** fix sind Miete, Gehälter, Versicherungen, lineare Abschreibung, Leasingraten, Grundgebühren. Variabel sind Material je Stück, Provision je Verkauf, Verpackung und Fracht je Lieferung, Lizenzgebühr je Gerät.

**Deckungsbeitrag (DB)** je Stück = Preis − variable Stückkosten. Gesamt-DB = DB je Stück × Menge.

**Break-even-Menge** = Fixkosten ÷ DB je Stück, immer **aufrunden** (angefangene Stücke zählen).

**Rechnung erstellen:** Stunden × Stundensatz + Pauschalen = netto; × 1,19 = brutto.
"""

V["WIR-L6"] = """
| | ein Nachfrager | wenige Nachfrager | viele Nachfrager |
|---|---|---|---|
| **ein Anbieter** | zweiseitiges Monopol | – | Angebotsmonopol |
| **wenige Anbieter** | – | – | Angebotsoligopol |
| **viele Anbieter** | Nachfragemonopol | Nachfrageoligopol | Polypol |

| Rechtsform | Haftung / Kapital |
|---|---|
| Einzelunternehmen | Inhaber haftet allein und unbeschränkt |
| GbR | mind. 2 Gesellschafter, alle haften persönlich, kein Mindestkapital |
| OHG | Handelsgewerbe, alle haften unbeschränkt |
| KG | Komplementär unbeschränkt, Kommanditisten nur mit Einlage |
| GmbH | Stammkapital **25.000 €** (mind. 12.500 € bei Gründung eingezahlt), Haftung mit Gesellschaftsvermögen |
| UG (haftungsbeschränkt) | ab **1 €**, muss Gewinne teilweise zurücklegen |
| AG | Grundkapital **50.000 €**, Vorstand, Aufsichtsrat, Hauptversammlung |
| eG | fördert Mitglieder, grundsätzlich eine Stimme je Mitglied |

**Weitere Begriffe:** Prokura (umfassende Vollmacht, im Handelsregister), Handlungsvollmacht (gewöhnliche Geschäfte, nicht eingetragen), Handelsregister (beim Amtsgericht), Gleichgewichtspreis (Angebot = Nachfrage), Kartell (verbotene Absprache).
"""

V["NET-L1"] = """
**Umrechnung Präfix ↔ Maske:** /24 = 255.255.255.0, /25 = .128, /26 = .192, /27 = .224, /28 = .240, /29 = .248, /30 = .252. /16 = 255.255.0.0, /20 = 255.255.240.0, /22 = 255.255.252.0.

**Netz- und Broadcastadresse:** IP-Adresse UND Maske → Netzadresse (alle Hostbits 0). Alle Hostbits auf 1 → Broadcast. Nutzbar ist alles dazwischen. **Hosts** = 2^(32 − Präfix) − 2.

**Oktett binär → dezimal:** Stellenwerte 128 64 32 16 8 4 2 1, z. B. 11100000 = 128 + 64 + 32 = 224.

**Besondere Adressen:** 127.0.0.0/8 Loopback, 169.254.0.0/16 APIPA (kein DHCP), 100.64.0.0/10 Carrier-Grade-NAT, 224–239.x.x.x Multicast, 255.255.255.255 Broadcast an alle. Achtung: 172.15.x.x und 172.32.x.x sind **öffentlich**, nur 172.16–172.31 sind privat.
"""

V["NET-L2"] = """
**Schrittweite (Blockgröße):** 2^(32 − Präfix). Bei /26 sind es 64: Netze beginnen bei .0, .64, .128, .192. Das **k. Subnetz** beginnt bei (k − 1) × Blockgröße.

**Wie viele Subnetze?** Von /a auf /b entstehen 2^(b − a) Subnetze. Für **n** Subnetze braucht man so viele zusätzliche Bits, dass 2^Bits ≥ n.

**Hostbereich:** Netzadresse + 1 bis Broadcast − 1. Beispiel 192.168.1.64/27: Broadcast .95, Hosts .65 bis .94.
"""

V["NET-L3"] = """
**Aufbau:** 128 Bit = 8 Blöcke × 16 Bit, je Block 4 Hex-Ziffern. LAN-Subnetze sind üblicherweise **/64** (64 Bit Netz, 64 Bit Interface Identifier).

**Kürzen:** Nur **führende** Nullen je Block weglassen (`0db8` → `db8`, aber `12f0` bleibt `12f0`). Genau **eine** zusammenhängende Folge von 0-Blöcken (die längste) durch `::` ersetzen. Zweimal `::` ist ungültig.

**Adressarten:** `fe80::/10` Link-Local, `fc00::/7` (meist `fd…`) Unique Local, `2000::/3` global, `ff00::/8` Multicast, `::1` Loopback, `::` unspezifiziert.

**Subnetze aus einem Präfix:** aus /56 werden 2^(64 − 56) = 256 /64-Netze.
"""

V["NET-L4"] = """
| OSI-Schicht | Beispiele |
|---|---|
| 7 Anwendung | HTTP, DNS, SMTP, FTP, DHCP, SSH |
| 6 Darstellung | Kodierung, Verschlüsselung (Formate) |
| 5 Sitzung | Sitzungssteuerung |
| 4 Transport | TCP, UDP, Ports, Segment |
| 3 Vermittlung | IP, ICMP (ping), Router, Layer-3-Switch, Paket |
| 2 Sicherung | MAC-Adresse, Switch, Bridge, Access Point, ARP, Frame |
| 1 Bitübertragung | Kabel, Glasfaser, Hub, Repeater |

**Ports:**

| Dienst | Port | Dienst | Port |
|---|---|---|---|
| FTP | 21 | POP3 / POP3S | 110 / 995 |
| SSH | 22 | IMAP / IMAPS | 143 / 993 |
| Telnet | 23 | NTP | 123 |
| SMTP / Submission | 25 / 587 | SNMP | 161 |
| DNS | 53 | LDAP | 389 |
| DHCP-Server | 67 | HTTPS | 443 |
| HTTP | 80 | SMB | 445 |
| RDP | 3389 | MySQL/MariaDB | 3306 |

**TCP:** verbindungsorientiert (Drei-Wege-Handshake), Reihenfolge, Neuübertragung, Flusskontrolle; für HTTP(S), E-Mail. **UDP:** verbindungslos, wenig Overhead; für DNS-Anfragen, Streaming, VoIP.

**Geräte:** Router (zwischen Netzen, IP), Switch (MAC, gezielt an einen Port), Hub (an alle Ports), Access Point (WLAN ↔ LAN), Firewall (filtert nach Regeln), Repeater (verstärkt), Modem (wandelt Signale), PoE-Switch (Strom übers Netzwerkkabel).
"""

V["NET-L5"] = """
**DHCP-Ablauf (DORA):** Discover → Offer → Request → Acknowledge. Zugewiesen werden IP-Adresse, Maske, Gateway, DNS-Server und die Lease-Dauer.

| DNS-Eintrag | Bedeutung |
|---|---|
| A / AAAA | Name → IPv4 / IPv6 |
| MX | Mailserver der Domain |
| CNAME | Alias auf einen anderen Namen |
| PTR | IP → Name (Reverse Lookup) |
| NS | zuständiger Nameserver |
| TXT | freier Text (SPF, Verifizierung) |
| SOA | Verwaltungsangaben der Zone |

**Befehle:** `ping` (Erreichbarkeit), `tracert`/`traceroute` (Weg), `ipconfig /all` (Konfiguration), `/release` und `/renew` (DHCP neu), `/flushdns` (DNS-Cache leeren), `nslookup` (DNS abfragen), `netstat` (Verbindungen, Ports), `arp -a` (IP ↔ MAC), `ip addr` (Linux).

**Fehlersuche:** 169.254.x.x → kein DHCP erreicht. IP erreichbar, Name nicht → DNS. Nur lokales Netz erreichbar → Gateway. `ping 127.0.0.1` scheitert → TCP/IP-Stack. Keine LED → Kabel/Port. Neue Geräte bekommen keine Adresse → DHCP-Pool erschöpft.
"""

V["HW-L1"] = """
| Schnittstelle | max. Datenrate (brutto) |
|---|---|
| USB 2.0 | 480 Mbit/s |
| USB 3.2 Gen 1 (USB 3.0) | 5 Gbit/s |
| USB 3.2 Gen 2 / Gen 2x2 | 10 / 20 Gbit/s |
| Thunderbolt 3/4, USB4 | 40 Gbit/s |
| SATA III | 6 Gbit/s |
| Fast / Gigabit / 10-Gigabit-Ethernet | 100 Mbit/s / 1 Gbit/s / 10 Gbit/s |

**Zweck:** HDMI (Bild und Ton, TV/Beamer), DisplayPort (Monitore, Daisy-Chaining), USB-C (verdrehsicher, Daten, Video, Strom per Power Delivery), RJ45 (Twisted Pair), M.2 NVMe (schnelle SSD über PCIe), SATA (2,5"/3,5"-Laufwerke), PCI Express (Erweiterungskarten), VGA (analog, veraltet), Bluetooth (Funk, Nahbereich), LWL (Licht, störunempfindlich), PoE (Strom übers Netzwerkkabel).

**Kabel:** Cat 5e 1 Gbit/s, Cat 6 1 Gbit/s (10 Gbit/s bis 55 m), Cat 6A 10 Gbit/s bis 100 m, Cat 8 25/40 Gbit/s bis 30 m. Twisted Pair maximal **100 m** pro Strecke, USB 2.0 passiv 5 m.
"""

V["HW-L2"] = """
| Komponente | Aufgabe |
|---|---|
| CPU | führt Befehle aus |
| Cache | sehr schneller Zwischenspeicher an der CPU |
| RAM | flüchtiger Arbeitsspeicher |
| GPU | Grafik und parallele Berechnungen |
| Chipsatz | verbindet CPU mit Schnittstellen |
| UEFI (Flash) | Firmware zum Starten, Secure Boot, GPT |
| TPM | Sicherheitschip für Schlüssel (z. B. BitLocker) |
| Netzteil | wandelt Wechsel- in Gleichspannung |
| SSD / HDD | nicht flüchtig; SSD schnell und robust, HDD günstig pro TB |

**Begriffe:** Taktfrequenz (GHz), Mehrkern, Hyper-Threading/SMT (2 Threads pro Kern), TDP (abzuführende Wärme), Dual-Channel (zwei Module parallel), ECC-RAM (korrigiert Fehler), Virtualisierung, IOPS (Ein-/Ausgaben pro Sekunde), Secure Boot (nur signierte Bootloader).

**RAM-Bandbreite** = Transfers pro Sekunde × 8 Byte (64-Bit-Bus) × Kanäle. DDR5-4800 Single-Channel: 4.800 × 10⁶ × 8 Byte = 38,4 GB/s.
"""

V["HW-L3"] = """
| RAID | Prinzip | min. Platten | Nutzkapazität | verkraftet |
|---|---|---|---|---|
| 0 | Striping | 2 | n × Größe | keinen Ausfall |
| 1 | Spiegelung | 2 | 1 Platte | eine Platte |
| 5 | verteilte Parität | 3 | (n − 1) × Größe | eine beliebige Platte |
| 6 | doppelte Parität | 4 | (n − 2) × Größe | zwei beliebige Platten |
| 10 | Stripe über Spiegel | 4 | n × Größe ÷ 2 | eine Platte pro Spiegelpaar |

**Anteil nutzbar** = Nutzkapazität ÷ Bruttokapazität. RAID 5 mit 4 Platten: 3/4 = 75 %.

**Wichtig:** Ein RAID ersetzt **kein Backup**. Es schützt nicht vor Löschen, Ransomware oder Brand. Ein **Hot-Spare** springt automatisch für eine ausgefallene Platte ein.
"""

V["HW-L4"] = """
**Grundformeln:** P = U × I, I = P ÷ U. Energie in kWh = W × h ÷ 1.000. Kosten = kWh × Preis.

**Jahreskosten:** W × Stunden pro Tag × Tage ÷ 1.000 × Preis. **Ersparnis** bei Gerätetausch: Leistungsdifferenz × Anzahl × Stunden × Tage ÷ 1.000 × Preis.

**USV:** Überbrückungszeit = nutzbare Energie (Wh) ÷ Last (W), × 60 für Minuten. Wirkleistung W = Scheinleistung VA × Leistungsfaktor (cos φ).

| USV-Art | Arbeitsweise |
|---|---|
| Offline/Standby (VFD) | schaltet erst bei Ausfall um, günstig |
| Line-Interactive (VI) | regelt zusätzlich Spannungsschwankungen |
| Online (VFI) | Last läuft ständig über den Wechselrichter, keine Umschaltzeit |
"""

V["HW-L5"] = """
| Arbeitsplatz | Empfehlung |
|---|---|
| Bildschirmoberkante | auf oder leicht unter Augenhöhe |
| Sehabstand | etwa 50–80 cm |
| Monitor zum Fenster | seitlich, Blick parallel zum Fenster |
| Ellenbogen | etwa 90° oder etwas mehr |
| Füße | flach auf dem Boden oder einer Fußstütze |
| Darstellung | dunkle Schrift auf hellem Grund, entspiegelt |
| Pausen | regelmäßig kurz unterbrechen oder Tätigkeit wechseln |

| Zeichen | Bedeutung |
|---|---|
| Blauer Engel | deutsches Umweltzeichen |
| Energy Star | energieeffiziente Bürogeräte |
| TCO Certified | Nachhaltigkeit inkl. sozialer Kriterien |
| EU-Energielabel | Effizienzklassen A bis G |
| 80 PLUS | Effizienz von Netzteilen |
| CE | Hersteller erklärt EU-Konformität, kein Umweltsiegel |
| WEEE / ElektroG | Rücknahme und Entsorgung von Altgeräten |

**TCO (Gesamtkosten)** = Anschaffung + Jahre × (Strom + Wartung/Support + …).
"""

V["PRG-L1"] = """
| Operator | Bedeutung | Beispiel |
|---|---|---|
| `%` | Rest der ganzzahligen Division | `17 % 5` = 2 |
| `//` | ganzzahlige Division (abrunden) | `17 // 5` = 3 |
| `/` | Division, Ergebnis immer float | `10 / 4` = 2.5 |
| `**` | Potenz | `2 ** 3` = 8 |

**Datentypen:** `42` int, `3.14` float, `"Hallo"` und `'A'` str, `True` bool, `[1, 2]` Liste, `{"name": "Ada"}` Dictionary. **Passender Typ:** Postleitzahl, Telefonnummer, Hausnummer → String; Mengen → Integer; Preise → Float/Decimal; Ja/Nein → Boolean.

**Umwandlungen:** `int("12") + 3` = 15, `"12" + "3"` = "123", `str(5) + "5"` = "55", `int(7.9)` = 7 (abgeschnitten), `"ab" * 3` = "ababab", `float(3)` = 3.0, `bool(0)` = False.

**Logik:** `and` (beide wahr), `or` (mindestens einer), `not` (kehrt um). `a < b < c` bedeutet `a < b and b < c`.
"""

V["PRG-L2"] = """
**range:** `range(a, b, schritt)` zählt von a bis **ausschließlich** b. `range(0, 10, 3)` → 0, 3, 6, 9.

**Verschachtelte Schleifen:** Die innere Schleife läuft bei jedem Durchlauf der äußeren komplett. Anzahl = Summe der inneren Durchläufe (bei festen Grenzen: außen × innen).

**while zählen:** Vor jedem Durchlauf wird die Bedingung geprüft. Schreibe die Werte der Variable mit, bis die Bedingung falsch ist.

**if/elif/else:** Von oben nach unten prüfen, der **erste** zutreffende Zweig gewinnt.

| Begriff | Bedeutung |
|---|---|
| kopfgesteuert (while) | prüft vorher, läuft evtl. nie |
| fußgesteuert (do-while) | läuft mindestens einmal |
| Zählschleife (for) | bekannte Anzahl Durchläufe |
| `break` | beendet die Schleife sofort |
| `continue` | springt zum nächsten Durchlauf |
"""

V["PRG-L3"] = """
**Typische Algorithmen, die du erkennen solltest:**
- `while b != 0: r = a % b; a = b; b = r` → **größter gemeinsamer Teiler** (Euklid).
- `x = x + n % 10; n = n // 10` → **Quersumme**.
- `if w > x: x = w` → **Maximum**, mit `<` das Minimum.
- `if bedingung: x = x + 1` → **Zählen**.
- `x = x * i` für i von 1 bis n → **Fakultät**. `a, b = b, a + b` → **Fibonacci**.
- Nachbarn vergleichen und tauschen → **ein Bubblesort-Durchlauf**: danach steht das größte Element am Ende.

**Tauschen:** `a = b; b = a` geht schief (beide haben dann den Wert von b). Richtig ist eine Hilfsvariable (`hilf = a; a = b; b = hilf`) oder der Rechentrick `a = a + b; b = a - b; a = a - b`.
"""

V["PRG-L4"] = """
**Indizes und Ausschnitte:** `z[0]` erstes, `z[-1]` letztes, `z[-2]` vorletztes Element. `z[1:3]` liefert Index 1 und 2 (Ende exklusiv), `z[:2]` die ersten zwei, `z[3:]` ab Index 3. Ein Index außerhalb der Liste führt zu `IndexError`.

**Listenmethoden:** `append(x)` hängt an, `insert(0, x)` fügt vorne ein, `pop()` entfernt das letzte, `remove(x)` das erste passende Element, `sort()` sortiert, `reverse()` dreht um.

**Funktionen:** Parameter werden in der Reihenfolge belegt; ein Parameter mit Standardwert (`b=2`) darf fehlen. `return` liefert das Ergebnis.

**Fehlerarten:** Syntaxfehler (Code ungültig: fehlender Doppelpunkt, offene Klammer, falsche Einrückung), Laufzeitfehler (Abbruch beim Ausführen: Division durch null, IndexError, NameError, `int("abc")`), logischer Fehler (läuft, aber falsches Ergebnis).

| Struktur | Prinzip |
|---|---|
| Liste/Array | Zugriff über Index |
| Stack | LIFO – zuletzt rein, zuerst raus |
| Queue | FIFO – zuerst rein, zuerst raus |
| Dictionary | Zugriff über Schlüssel |
| Rekursion | Funktion ruft sich selbst auf, braucht Abbruchbedingung |
"""

V["PRG-L5"] = """
| Sprache | Ausführung |
|---|---|
| C, C++, Go | kompiliert |
| Java | Bytecode in der JVM |
| C# | Bytecode in der .NET-Laufzeit (CLR) |
| Python, PHP | interpretiert (intern Bytecode) |
| JavaScript im Browser | interpretiert / JIT |

**Werkzeuge:** Linker (verbindet Objektdateien), JIT-Compiler (übersetzt zur Laufzeit), Debugger (Haltepunkte, Variablen), IDE (Editor, Debugger, Build), Git (Versionen).

**Paradigmen:** prozedural, objektorientiert, funktional, deklarativ (SQL: WAS statt WIE), ereignisgesteuert.

| Git | Wirkung |
|---|---|
| `clone` | Repository kopieren |
| `status` | Änderungen anzeigen |
| `add` | für den Commit vormerken |
| `commit` | Stand speichern |
| `push` / `pull` | hochladen / holen und zusammenführen |
| `branch` / `merge` | Zweig anlegen / zusammenführen |

**Testarten:** Unit-Test (einzelne Funktion), Integrationstest (Zusammenspiel), Systemtest (Gesamtsystem), Abnahmetest (durch den Kunden), Black-Box (nur Ein-/Ausgabe), White-Box (mit Codekenntnis), Regressionstest (nach Änderungen).
"""

V["DB-L1"] = """
**Begriffe:** Attribut = Spalte, Tupel/Datensatz = Zeile. **Schlüsselkandidat:** eindeutige Attribut(kombination). **Zusammengesetzter Schlüssel:** aus mehreren Attributen (z. B. Bestellnummer + Positionsnummer). **Surrogatschlüssel:** künstliche ID ohne fachliche Bedeutung. `NOT NULL`: Pflichtfeld. `UNIQUE`: keine Wiederholung.

**Guter Primärschlüssel:** eindeutig und stabil, z. B. Personal-, Kunden-, Artikel-, Rechnungsnummer oder Kennzeichen. Namen, Orte und Farben wiederholen sich.

| Datentyp | Verwendung |
|---|---|
| INT | ganze Zahlen |
| DECIMAL(10,2) | Geldbeträge |
| VARCHAR(n) / CHAR(n) | Text variabler / fester Länge (z. B. PLZ) |
| TEXT | lange Texte |
| DATE / DATETIME | Datum / Datum mit Uhrzeit |
| BOOLEAN | Wahrheitswert |
"""

V["DB-L2"] = """
**Beispiele:** 1:1 Person–Personalausweis, Land–Hauptstadt. 1:n Kunde–Bestellung, Abteilung–Mitarbeiter, Rechnung–Position. m:n Student–Kurs, Projekt–Mitarbeiter, Autor–Buch, Artikel–Lieferant. Tipp: Frage in **beide** Richtungen, wie viele es jeweils sein können.

**Chen-Notation:** Rechteck = Entität, Raute = Beziehung, Ellipse = Attribut, unterstrichen = Primärschlüssel, doppelte Ellipse = mehrwertiges, gestrichelte = abgeleitetes Attribut.

**Anzahl Tabellen:** 1:1 → kann eine Tabelle sein, 1:n → 2 Tabellen (Fremdschlüssel auf der n-Seite), m:n → 3 Tabellen (Zwischentabelle, die auch Beziehungsattribute wie „Stunden“ aufnimmt).
"""

V["DB-L3"] = """
**Verstöße erkennen:**
- **1NF:** mehrere Werte in einem Feld („0301234, 0171555“), zusammengesetzte Felder (ganze Adresse), Wiederholungsgruppen (Kurs1, Kurs2, Kurs3).
- **2NF:** Bei zusammengesetztem Schlüssel hängt ein Attribut nur von **einem Teil** ab (Artikelbezeichnung nur von ArtNr).
- **3NF:** Ein Nicht-Schlüsselattribut hängt von einem **anderen Nicht-Schlüsselattribut** ab (Ort von PLZ, Abteilungsname von AbtNr).

**Anomalien:** Einfügeanomalie (kann nicht speichern, ohne andere Daten einzutragen), Änderungsanomalie (an vielen Stellen ändern), Löschanomalie (ungewollter Informationsverlust). Ursache ist **Redundanz**. Normalisierung erzeugt mehr Tabellen, macht Abfragen aber nicht automatisch schneller.
"""

V["DB-L4"] = """
| Schlüsselwort | Wirkung |
|---|---|
| `SELECT` / `FROM` | Spalten / Tabelle |
| `WHERE` | Zeilen filtern |
| `ORDER BY … ASC/DESC` | sortieren |
| `LIMIT n OFFSET m` | n Zeilen, vorher m überspringen |
| `DISTINCT` | Doppelte entfernen |
| `LIKE '%e%'` | Textmuster (% beliebig viele Zeichen, _ genau eins) |
| `BETWEEN a AND b` | inklusive beider Grenzen |
| `IN (…)` | Wert aus einer Liste |
| `IS NULL` | fehlender Wert |

**Teilsprachen:** DDL (CREATE, ALTER, DROP), DML (SELECT, INSERT, UPDATE, DELETE), DCL (GRANT, REVOKE), TCL (COMMIT, ROLLBACK).

**Daten ändern:** `INSERT INTO` fügt ein, `UPDATE … SET … WHERE` ändert, `DELETE FROM … WHERE` löscht. Ohne WHERE sind **alle** Zeilen betroffen.
"""

V["DB-L5"] = """
**Aggregate:** `COUNT(*)` zählt Zeilen, `COUNT(DISTINCT x)` verschiedene Werte, `SUM`, `AVG`, `MIN`, `MAX`. Ohne passende Zeilen liefert SUM `NULL`.

**GROUP BY** bildet Gruppen gleicher Werte; die Aggregatfunktion wird **pro Gruppe** berechnet. **HAVING** filtert danach ganze Gruppen (WHERE filtert vorher einzelne Zeilen).

| Join | liefert |
|---|---|
| INNER JOIN | nur Zeilen mit Partner in beiden Tabellen |
| LEFT JOIN | alle Zeilen links, rechts ggf. NULL |
| RIGHT JOIN | alle Zeilen rechts, links ggf. NULL |
| CROSS JOIN / `FROM A, B` | jede mit jeder: Zeilen A × Zeilen B |

**Kunden ohne Bestellung finden:** `LEFT JOIN` und `WHERE b.id IS NULL`.
"""

V["PM-L1"] = """
**Projekt oder Routine?** Projekte sind einmalig, zeitlich begrenzt, zielgerichtet, haben begrenzte Ressourcen, eine eigene Organisation und Risiko (z. B. ERP-Einführung, Migration, Umzug). Tägliche Sicherung oder Gehaltsabrechnung sind Routine.

**SMART:** spezifisch, messbar, attraktiv/akzeptiert, realistisch, terminiert. „Die Seite soll schneller werden“ ist nicht SMART, „Bis 30.06. lädt die Startseite in unter 2 s“ schon.

**Rollen:** Auftraggeber (beauftragt, finanziert), Projektleiter (plant, steuert), Lenkungsausschuss (übergeordnete Entscheidungen), Endanwender, Betriebsrat (Mitbestimmung bei Leistungskontrolle), Datenschutzbeauftragter.

**Magisches Dreieck:** Ändert sich eine Ecke (Zeit, Kosten, Qualität/Umfang), müssen die anderen nachgeben.

**Risikowert** = Eintrittswahrscheinlichkeit × Schadenshöhe, z. B. 20 % × 50.000 € = 10.000 €.
"""

V["PM-L2"] = """
**Funktionale Anforderungen** beschreiben, WAS das System tun soll (PDF-Export, Passwort zurücksetzen, Benutzer sperren). **Nicht-funktionale** beschreiben, WIE GUT (Antwortzeit, Verfügbarkeit, Barrierefreiheit, Plattformen, Sicherheit).

**Lastenheft:** vom Auftraggeber, beschreibt Was und Wofür, Grundlage für Angebote. **Pflichtenheft:** vom Auftragnehmer, beschreibt Wie und Womit (Architektur, Technologien), Grundlage für die Abnahme.

**MoSCoW:** Must have (zwingend), Should have (wichtig), Could have (wünschenswert), Won't have this time (bewusst nicht).
"""

V["PM-L3"] = """
**Vorgehen mit einer Vorgangsliste:**
1. Vorwärts: Startvorgänge haben FAZ 0. FAZ = **größtes** FEZ aller Vorgänger, FEZ = FAZ + Dauer.
2. Projektdauer = FEZ des letzten Vorgangs.
3. Rückwärts: letzter Vorgang SEZ = Projektende. SEZ = **kleinstes** SAZ aller Nachfolger, SAZ = SEZ − Dauer.
4. Gesamtpuffer GP = SAZ − FAZ. Freier Puffer FP = kleinstes FAZ der Nachfolger − eigenes FEZ.
5. Kritischer Pfad: alle Vorgänge mit GP = 0, das ist der längste Weg.
"""

V["PM-L4"] = """
| Scrum | Bedeutung |
|---|---|
| Product Owner | verantwortet und priorisiert das Product Backlog |
| Scrum Master | sorgt für gelebtes Scrum, beseitigt Hindernisse |
| Developers | setzen die Einträge um |
| Sprint | höchstens 1 Monat, Ergebnis ist ein Inkrement |
| Sprint Planning / Daily Scrum | Sprint planen / tägliches 15-Minuten-Treffen |
| Sprint Review / Retrospektive | Ergebnis mit Stakeholdern / Zusammenarbeit verbessern |
| Product / Sprint Backlog | alle Anforderungen / Auswahl für den Sprint |
| User Story | „Als … möchte ich … damit …“ |
| Definition of Done | wann ein Eintrag fertig ist |

**Velocity:** durchschnittlich geschaffte Story Points pro Sprint, Grundlage für die Planung.

**Vorgehensmodelle:** Wasserfall (Phasen nacheinander), V-Modell (jeder Phase steht ein Test gegenüber), Scrum (Sprints), Kanban (Board mit WIP-Limit), Spiralmodell (Zyklen mit Risikoanalyse), Prototyping (frühe Muster).

**Planungswerkzeuge:** Gantt-Diagramm (Balken auf Zeitachse), Meilenstein (Ereignis ohne Dauer), Projektstrukturplan (Zerlegung in Arbeitspakete), Arbeitspaket (kleinste Einheit mit Verantwortlichem), Netzplan (Abhängigkeiten), Burndown-Chart (Restarbeit im Sprint), Kanban-Board.
"""

V["KOM-L1"] = """
**Beispiele für die vier Seiten:** „Die Ampel ist grün“ → Appell: Fahr los! „Ich bin gestresst“ → Selbstoffenbarung. „Kannst du das nicht richtig machen?“ → Beziehung. „Das Meeting beginnt um 10 Uhr“ → Sachinhalt.

**Ebenen:** verbal (Worte), paraverbal (Stimme: Lautstärke, Tempo, Betonung, Tonfall, Pausen), nonverbal (Mimik, Gestik, Haltung, Blickkontakt).

**Sender-Empfänger-Modell:** Sender codiert, Empfänger decodiert, Kanal überträgt, Störungen beeinträchtigen, Feedback gibt Rückmeldung.

**Watzlawicks Axiome:** Man kann nicht nicht kommunizieren. Jede Kommunikation hat Inhalts- und Beziehungsaspekt. Kommunikation ist Ursache und Wirkung (Interpunktion). Sie ist analog und digital. Sie ist symmetrisch oder komplementär.
"""

V["KOM-L2"] = """
| Frageart | Beispiel | Zweck |
|---|---|---|
| offen | „Wie arbeiten Sie damit?“ | Informationen sammeln |
| geschlossen | „Ist der Drucker an?“ | Ja/Nein, schnell bestätigen |
| Alternativfrage | „Dienstag oder Donnerstag?“ | Entscheidung herbeiführen |
| Kontrollfrage | „Habe ich richtig verstanden, dass …?“ | Verständnis sichern |
| Suggestivfrage | „Sie wollen doch sicher …?“ | beeinflusst – vermeiden |
| rhetorische Frage | „Wer will schon Daten verlieren?“ | erwartet keine Antwort |
| Gegenfrage | „Warum fragen Sie das?“ | Zeit gewinnen, Hintergrund klären |

**Aktives Zuhören:** paraphrasieren (mit eigenen Worten wiederholen), verbalisieren (Gefühle ansprechen), nachfragen, zusammenfassen, nonverbale Signale.

**Beratungsgespräch in 5 Phasen:** Begrüßung → Bedarfsermittlung → Lösungsvorschlag → Einwandbehandlung → Abschluss.
"""

V["KOM-L3"] = """
| Eisenhower | Handlung |
|---|---|
| wichtig und dringend | sofort selbst erledigen |
| wichtig, nicht dringend | planen und terminieren |
| dringend, nicht wichtig | delegieren |
| weder noch | nicht bearbeiten |

**Methoden:** Pareto (20 % Aufwand, 80 % Ergebnis), ALPEN (Aufgaben, Länge, Puffer, Entscheidungen, Nachkontrolle), ABC-Analyse, Pomodoro (25 min Arbeit, kurze Pause), Mindmap, Brainstorming (erst sammeln, nicht bewerten), persönliches Kanban.

**Präsentation:** Zielgruppe analysieren. Einleitung (Thema, Ziel, Ablauf), Hauptteil (strukturiert, Beispiele), Schluss (Fazit, Fragen). Folien mit wenig Text und guten Grafiken.

**Teamphasen (Tuckman):** Forming (kennenlernen), Storming (Konflikte), Norming (Regeln), Performing (produktiv), Adjourning (Auflösung).

**Konfliktstrategien:** Win-win, Kompromiss, Durchsetzen, Vermeiden, Nachgeben.

**KI im Betrieb:** Ergebnisse prüfen (Halluzinationen), keine vertraulichen oder personenbezogenen Daten in öffentliche Dienste, Urheberrechte beachten, betriebliche Regeln einhalten. Die Verantwortung bleibt beim Menschen.
"""

V["UML-L1"] = """
**Klassen lesen:** oben der Name, in der Mitte die Attribute (`- name: String`), unten die Methoden (`+ getName(): String`). Der Typ nach dem Doppelpunkt hinter der Klammer ist der **Rückgabetyp**; `void` heißt keine Rückgabe.

| Begriff | Bedeutung |
|---|---|
| Objekt | konkrete Instanz einer Klasse |
| Konstruktor | wird beim Erzeugen aufgerufen |
| Kapselung | Attribute privat, Zugriff über Getter/Setter |
| statisch (unterstrichen) | gehört zur Klasse, nicht zum Objekt |
| abstrakt (kursiv) | kann nicht direkt instanziiert werden |
| Interface | legt Methoden fest, die Klassen umsetzen müssen |
| Polymorphie | gleicher Aufruf, je nach Objekt anderes Verhalten |
| Überschreiben | Unterklasse ersetzt eine geerbte Methode |
"""

V["UML-L2"] = """
| Beziehung | Darstellung | Beispiel |
|---|---|---|
| Assoziation | einfache Linie | Kunde gibt Bestellung auf |
| Aggregation | leere Raute am Ganzen | Mannschaft – Spieler (Teile existieren allein) |
| Komposition | gefüllte Raute am Ganzen | Gebäude – Raum, Rechnung – Position (Teile sterben mit) |
| Vererbung | leeres Dreieck zur Oberklasse | Auto ist ein Fahrzeug |
| Realisierung | gestrichelt mit leerem Dreieck | Klasse implementiert Interface |
| Abhängigkeit | gestrichelter offener Pfeil | nutzt kurzzeitig |

**Multiplizitäten:** `1` genau eins, `0..1` höchstens eins, `*` bzw. `0..*` beliebig viele, `1..*` mindestens eins, `2..5` zwei bis fünf. Sie stehen an dem Ende, dessen Anzahl sie beschreiben.
"""

V["UML-L3"] = """
**Use-Case-Diagramm:** Akteur (Strichmännchen), Anwendungsfall (Ellipse), Systemgrenze (Rechteck), «include» (wird immer mit ausgeführt), «extend» (nur unter Bedingung).

**Aktivitätsdiagramm:** Startknoten (gefüllter Kreis), Endknoten (Kreis mit Ring), Ablaufende (Kreis mit Kreuz), Aktion (abgerundetes Rechteck), Raute (Verzweigung/Zusammenführung), dicker Balken (Gabelung/Vereinigung), Swimlane (Verantwortliche), [Guard] an Kanten.

**Sequenzdiagramm:** Lebenslinie (gestrichelte Senkrechte), synchrone Nachricht (gefüllte Spitze, Sender wartet), asynchrone (offene Spitze), Antwort (gestrichelter Pfeil), Aktivierungsbalken, alt-Fragment (Alternative).

| Strukturdiagramme | Verhaltensdiagramme |
|---|---|
| Klassen-, Objekt-, Komponenten-, Verteilungsdiagramm | Use-Case-, Aktivitäts-, Sequenz-, Zustandsdiagramm |
"""

V["EIN-L1"] = """
| Präfix | Faktor | Präfix | Faktor |
|---|---|---|---|
| Kilo (k) | 10³ | Kibi (Ki) | 2¹⁰ = 1.024 |
| Mega (M) | 10⁶ | Mebi (Mi) | 2²⁰ |
| Giga (G) | 10⁹ | Gibi (Gi) | 2³⁰ |
| Tera (T) | 10¹² | Tebi (Ti) | 2⁴⁰ |
| Peta (P) | 10¹⁵ | Milli / Mikro / Nano | 10⁻³ / 10⁻⁶ / 10⁻⁹ |

**Festplattengröße:** Hersteller rechnen dezimal, viele Betriebssysteme binär: 1 TB = 10¹² Byte ÷ 2⁴⁰ ≈ 0,91 TiB.

**Umrechnen:** Binär → dezimal über Stellenwerte (…, 16, 8, 4, 2, 1). Dezimal → hex: wiederholt durch 16 teilen, Reste von unten lesen (10–15 = A–F). Jede Hex-Ziffer entspricht genau 4 Bit. Mit n Bit lassen sich 2ⁿ Werte darstellen.
"""

V["EIN-L2"] = """
**Merke:** Datenraten in **Bit**, Dateigrößen in **Byte**. 1 Byte = 8 Bit, also Mbit/s ÷ 8 = MB/s.

**Übertragungszeit** = Größe in MB × 8 ÷ Rate in Mbit/s. **Benötigte Rate** = Größe in Mbit ÷ Zeit in s. Stunden = Sekunden ÷ 3.600.

**Bild (unkomprimiert):** Breite × Höhe × Farbtiefe (Bit) ÷ 8 = Byte. **Audio (unkomprimiert):** Abtastrate × Bittiefe × Kanäle × Sekunden ÷ 8 = Byte. **Speicherbedarf vieler Dateien:** Anzahl × Durchschnittsgröße.
"""

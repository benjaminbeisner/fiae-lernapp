import ipaddress

from .basis import Sammler, rng_fuer, zahl, zuordnung

T = "netzwerk"


def _maske(p):
    return str(ipaddress.IPv4Network(f"0.0.0.0/{p}").netmask)


def _zufalls_ip(rng, privat=True):
    art = rng.choice(["10", "172", "192"]) if privat else "pub"
    if art == "10":
        return f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
    if art == "172":
        return f"172.{rng.randint(16,31)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
    if art == "192":
        return f"192.168.{rng.randint(0,255)}.{rng.randint(1,254)}"
    return f"{rng.choice([62,80,85,91,141,193,212,217])}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"


def _v6_falsch(lang, kurz):
    bloecke = [b.lstrip("0") or "0" for b in lang.split(":")]
    ohne_kuerzung = ":".join(bloecke)
    # typischer Fehler 1: Nullen am Ende eines Blocks gestrichen
    fehler1 = kurz
    for b in lang.split(":"):
        if b.endswith("0") and b.strip("0"):
            fehler1 = kurz.replace(b.lstrip("0"), b.lstrip("0").rstrip("0"), 1)
            break
    # typischer Fehler 2: zwei Mal "::"
    nullen = [i for i, b in enumerate(bloecke) if b == "0"]
    fehler2 = ohne_kuerzung.replace(":0:", "::", 2)
    # typischer Fehler 3: "::" an der falschen (kürzeren) Stelle bzw. gar nicht gekürzt
    fehler3 = ohne_kuerzung
    kandidaten = [fehler1, fehler2, fehler3, kurz.replace("::", ":0:"), kurz.replace("::", ":")]
    falsch = []
    for k in kandidaten:
        if k != kurz and k not in falsch:
            falsch.append(k)
    return falsch


def erzeugen():
    s = Sammler()
    rng = rng_fuer("netz")

    # ---------- NET-L1: IPv4 und Maske ----------
    for i in range(1, 13):
        p = rng.choice([8, 12, 16, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30])
        s.wahl("NET-MASKE", i, T, "NET-L1", f"Welche Subnetzmaske gehört zum Präfix **/{p}**?",
               _maske(p), [_maske(x) for x in rng.sample([q for q in range(8, 31) if q != p], 3)],
               f"/{p} bedeutet {p} Einsen von links: {_maske(p)}.", s=1)
    for i, p in enumerate([8, 16, 19, 21, 24, 25, 26, 27, 28, 29, 30, 22], 1):
        s.zahl("NET-CIDR", i, T, "NET-L1", f"Die Subnetzmaske lautet **{_maske(p)}**. Wie lautet das Präfix in CIDR-Schreibweise? (nur die Zahl)",
               p, f"Zähle die Einsen der Maske im Binärsystem: {_maske(p)} = /{p}.", s=1)
    for i in range(1, 13):
        p = rng.choice([22, 23, 24, 25, 26, 27, 28, 29, 30])
        s.zahl("NET-HOSTS", i, T, "NET-L1", f"Wie viele Hosts (nutzbare Adressen) passen in ein IPv4-Netz mit dem Präfix **/{p}**?",
               2 ** (32 - p) - 2, f"Hostbits: 32 − {p} = {32-p}. Nutzbar: 2^{32-p} − 2 = {2**(32-p)-2} (Netz- und Broadcastadresse abziehen).", s=1)
    for i in range(1, 16):
        ip = _zufalls_ip(rng)
        p = rng.choice([16, 20, 22, 24, 25, 26, 27, 28, 29])
        net = ipaddress.IPv4Interface(f"{ip}/{p}").network
        falsch = {str(net.broadcast_address), str(ipaddress.IPv4Interface(f"{ip}/{min(p+2,30)}").network.network_address),
                  str(ipaddress.IPv4Interface(f"{ip}/{max(p-2,8)}").network.network_address), ip}
        falsch.discard(str(net.network_address))
        s.wahl("NET-NETZADR", i, T, "NET-L1", f"Ein Rechner hat die Adresse **{ip}/{p}**. Wie lautet die Netzadresse?",
               str(net.network_address), sorted(falsch), f"IP-Adresse UND Maske ({net.netmask}) ergibt {net.network_address}.", s=2)
    for i in range(1, 16):
        ip = _zufalls_ip(rng)
        p = rng.choice([20, 22, 23, 24, 25, 26, 27, 28, 29])
        net = ipaddress.IPv4Interface(f"{ip}/{p}").network
        falsch = {str(net.network_address), str(net.broadcast_address - 1),
                  str(ipaddress.IPv4Interface(f"{ip}/{min(p+1,30)}").network.broadcast_address),
                  str(ipaddress.IPv4Interface(f"{ip}/{max(p-1,8)}").network.broadcast_address)}
        falsch.discard(str(net.broadcast_address))
        s.wahl("NET-BROADCAST", i, T, "NET-L1", f"Wie lautet die Broadcastadresse des Netzes, in dem **{ip}/{p}** liegt?",
               str(net.broadcast_address), sorted(falsch),
               f"Netz {net}: alle Hostbits auf 1 ergibt {net.broadcast_address}.", s=2)
    for i in range(1, 13):
        ip = _zufalls_ip(rng)
        p = rng.choice([24, 25, 26, 27, 28])
        net = ipaddress.IPv4Interface(f"{ip}/{p}").network
        hosts = list(net.hosts())
        drin = str(rng.choice(hosts))
        andere = net.supernet() if rng.random() < .5 else net
        aussen = [str(a) for a in (net.broadcast_address + 1, net.network_address - 1, net.broadcast_address + 17) if a not in net]
        frage = f"Welche Adresse liegt im selben Netz wie **{ip}/{p}** und kann einem Host zugewiesen werden?"
        s.wahl("NET-SELBESNETZ", i, T, "NET-L1", frage, drin, aussen + [str(net.network_address), str(net.broadcast_address)],
               f"Das Netz ist {net}, nutzbar sind {hosts[0]} bis {hosts[-1]}.", s=2)
    privat = [("10.12.4.1", "privat (10.0.0.0/8)"), ("172.20.1.5", "privat (172.16.0.0/12)"), ("192.168.178.20", "privat (192.168.0.0/16)"),
              ("172.32.0.1", "öffentlich"), ("8.8.8.8", "öffentlich"), ("169.254.10.3", "APIPA / link-local"),
              ("127.0.0.1", "Loopback"), ("192.169.1.1", "öffentlich"), ("10.255.255.254", "privat (10.0.0.0/8)"),
              ("172.15.200.1", "öffentlich"), ("172.31.255.1", "privat (172.16.0.0/12)"), ("192.168.0.1", "privat (192.168.0.0/16)"),
              ("100.64.1.1", "Carrier-Grade-NAT (100.64.0.0/10)"), ("224.0.0.5", "Multicast"), ("255.255.255.255", "Broadcast an alle")]
    for i, (ip, art) in enumerate(privat, 1):
        andere = list(dict.fromkeys(a for _, a in privat if a != art and not (art.startswith("privat") and a.startswith("privat"))))
        rng.shuffle(andere)
        s.wahl("NET-ADRART", i, T, "NET-L1", f"Um welche Art von IPv4-Adresse handelt es sich bei **{ip}**?", art, andere[:3],
               "Private Bereiche: 10.0.0.0/8, 172.16.0.0/12 (172.16–172.31), 192.168.0.0/16. 169.254.x.x = APIPA, 127.x = Loopback, 224–239 = Multicast.", s=1)
    for i, (dez, binz) in enumerate([(192, "11000000"), (168, "10101000"), (255, "11111111"), (224, "11100000"), (240, "11110000"),
                                     (248, "11111000"), (252, "11111100"), (128, "10000000"), (10, "00001010"), (172, "10101100"),
                                     (254, "11111110"), (64, "01000000")], 1):
        s.zahl("NET-OKTETT", i, T, "NET-L1", f"Ein Oktett einer Subnetzmaske lautet binär `{binz}`. Welcher Dezimalwert ist das?",
               dez, f"{binz} = {dez}. Stellenwerte: 128, 64, 32, 16, 8, 4, 2, 1.", s=1)

    # ---------- NET-L2: Subnetting ----------
    for i in range(1, 16):
        basis_p = rng.choice([16, 20, 22, 24])
        n = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 30])
        bits = (n - 1).bit_length()
        neu = basis_p + bits
        s.zahl("NET-SUBPRAEFIX", i, T, "NET-L2",
               f"Ein Netz mit dem Präfix /{basis_p} soll in mindestens **{n} gleich große Subnetze** geteilt werden. Welches Präfix haben die Subnetze?",
               neu, f"{n} Subnetze brauchen {bits} zusätzliche Bits (2^{bits} = {2**bits} ≥ {n}). /{basis_p} + {bits} = /{neu}.", s=2)
    for i in range(1, 16):
        h = rng.choice([5, 10, 14, 20, 25, 30, 40, 50, 60, 62, 70, 100, 120, 126, 200, 250, 300, 500, 1000])
        bits = (h + 2 - 1).bit_length()
        p = 32 - bits
        s.zahl("NET-PRAEFIXHOSTS", i, T, "NET-L2",
               f"Ein Subnetz soll **{h} Hosts** aufnehmen, aber so klein wie möglich sein. Welches Präfix wählst du?",
               p, f"{h} Hosts + Netz + Broadcast = {h+2} Adressen. 2^{bits} = {2**bits} reicht, also {bits} Hostbits: 32 − {bits} = /{p}.", s=2)
    for i in range(1, 13):
        a = rng.choice([16, 20, 22, 24])
        b = a + rng.randint(1, 6)
        s.zahl("NET-ANZSUB", i, T, "NET-L2", f"Wie viele Subnetze mit dem Präfix /{b} entstehen aus einem Netz /{a}?",
               2 ** (b - a), f"{b} − {a} = {b-a} geliehene Bits, 2^{b-a} = {2**(b-a)} Subnetze.", s=1)
    for i in range(1, 16):
        third = rng.randint(0, 250)
        basis = ipaddress.IPv4Network(f"192.168.{third}.0/24") if rng.random() < .6 else ipaddress.IPv4Network(f"10.{rng.randint(0,255)}.0.0/16")
        extra = rng.randint(2, 4)
        subs = list(basis.subnets(prefixlen_diff=extra))
        k = rng.randint(2, len(subs))
        ziel = subs[k - 1]
        falsch = {str(subs[k - 2].network_address), str(subs[k % len(subs)].network_address), str(ziel.broadcast_address),
                  str(ziel.network_address + 1)}
        falsch.discard(str(ziel.network_address))
        s.wahl("NET-NTESSUB", i, T, "NET-L2",
               f"Das Netz **{basis}** wird in {len(subs)} gleich große Subnetze geteilt. Wie lautet die Netzadresse des **{k}. Subnetzes**?",
               str(ziel.network_address), sorted(falsch),
               f"Neues Präfix /{ziel.prefixlen}, Schrittweite {ziel.num_addresses} Adressen. Das {k}. Subnetz beginnt bei {ziel.network_address}.", s=3)
    for i in range(1, 13):
        third = rng.randint(0, 250)
        p = rng.choice([25, 26, 27, 28, 29])
        net = ipaddress.IPv4Network(f"192.168.{third}.0/{p}")
        net = list(ipaddress.IPv4Network(f"192.168.{third}.0/24").subnets(new_prefix=p))[rng.randint(0, 2 ** (p - 24) - 1)]
        hosts = list(net.hosts())
        frage = f"Welcher Bereich nutzbarer Hostadressen gehört zum Subnetz **{net}**?"
        r = f"{hosts[0]} bis {hosts[-1]}"
        falsch = [f"{net.network_address} bis {net.broadcast_address}", f"{hosts[0]} bis {net.broadcast_address}",
                  f"{hosts[0]} bis {hosts[-1] + net.num_addresses}"]
        s.wahl("NET-HOSTBEREICH", i, T, "NET-L2", frage, r, falsch, f"Netzadresse {net.network_address} und Broadcast {net.broadcast_address} sind nicht nutzbar.", s=2)
    for i in range(1, 11):
        p = rng.choice([25, 26, 27, 28, 29, 30])
        s.zahl("NET-SCHRITT", i, T, "NET-L2", f"In welchen Schritten (Blockgröße) steigen die Netzadressen im letzten Oktett bei Subnetzen mit **/{p}**?",
               2 ** (32 - p), f"/{p} hat {32-p} Hostbits, Blockgröße 2^{32-p} = {2**(32-p)}.", s=1)

    # ---------- NET-L3: IPv6 ----------
    beispiele = ["2001:0db8:0000:0000:0000:0000:0000:0001", "2001:0db8:0a0b:12f0:0000:0000:0000:0001",
                 "fe80:0000:0000:0000:0202:b3ff:fe1e:8329", "2001:0db8:0000:0042:0000:8a2e:0370:7334",
                 "2a02:0c207:3020:4554:0000:0000:0000:0001", "fd00:0000:0000:0001:0000:0000:0000:00ab",
                 "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "2001:0db8:0001:0000:0000:0000:0000:0000",
                 "ff02:0000:0000:0000:0000:0000:0000:0001", "2003:00e6:0f00:0100:0000:0000:0000:0010",
                 "2001:0db8:0000:0000:0001:0000:0000:0001", "fe80:0000:0000:0000:0000:0000:0000:0001"]
    for i, lang in enumerate(beispiele, 1):
        lang = ":".join(b[-4:].zfill(4) for b in lang.split(":"))
        adr = ipaddress.IPv6Address(lang)
        kurz = adr.compressed
        falsch = _v6_falsch(lang, kurz)
        s.wahl("NET-V6KURZ", i, T, "NET-L3", f"Wie lautet die korrekt gekürzte Schreibweise von `{lang}`?", kurz, falsch,
               "Führende Nullen je Block weglassen und genau **eine** zusammenhängende Folge von 0-Blöcken durch :: ersetzen (die längste).", s=2)
        s.wahl("NET-V6KURZ", i + 20, T, "NET-L3", f"Wie lautet die vollständige Schreibweise von `{kurz}`?", adr.exploded,
               [adr.exploded.replace("0000:", "", 1), adr.exploded[:-4] + "1000" if not adr.exploded.endswith("1000") else adr.exploded[:-4] + "0100",
                ":".join(b.zfill(4) for b in kurz.replace("::", ":").strip(":").split(":"))],
               "Jeder der 8 Blöcke hat 4 Hex-Ziffern; :: steht für so viele 0000-Blöcke, dass es 8 werden.", s=2)
    typen = [("fe80::1a2b:3cff:fe4d:5e6f", "Link-Local-Adresse"), ("2001:db8:1::5", "Globale Unicast-Adresse (bzw. Dokumentationsbereich)"),
             ("fd12:3456:789a::1", "Unique Local Address (ULA)"), ("ff02::1", "Multicast-Adresse"), ("::1", "Loopback-Adresse"),
             ("2a00:1450:4001::200e", "Globale Unicast-Adresse (bzw. Dokumentationsbereich)"), ("fe80::1", "Link-Local-Adresse"),
             ("fc00::abcd", "Unique Local Address (ULA)"), ("ff05::2", "Multicast-Adresse"), ("::", "Nicht spezifizierte Adresse")]
    for i, (a, t) in enumerate(typen, 1):
        andere = list(dict.fromkeys(x for _, x in typen if x != t))
        rng.shuffle(andere)
        s.wahl("NET-V6TYP", i, T, "NET-L3", f"Um welchen Adresstyp handelt es sich bei `{a}`?", t, andere[:3],
               "fe80::/10 Link-Local, fc00::/7 (meist fd..) ULA, ff00::/8 Multicast, 2000::/3 global, ::1 Loopback, :: unspezifiziert.", s=1)
    for i in range(1, 13):
        a = rng.choice([32, 40, 48, 52, 56, 60])
        b = rng.choice([x for x in [48, 56, 60, 64] if x > a])
        s.zahl("NET-V6SUB", i, T, "NET-L3", f"Ein Provider vergibt ein **/{a}**-Präfix. Wie viele **/{b}**-Subnetze lassen sich daraus bilden?",
               2 ** (b - a), f"{b} − {a} = {b-a} Bits, 2^{b-a} = {zahl(2**(b-a),0)} Subnetze.", s=2)
    fakten6 = [("Wie viele Bit lang ist eine IPv6-Adresse?", 128), ("Wie viele Bit lang ist eine IPv4-Adresse?", 32),
               ("Aus wie vielen Blöcken besteht eine IPv6-Adresse?", 8), ("Wie viele Bit hat ein Block einer IPv6-Adresse?", 16),
               ("Welche Präfixlänge hat üblicherweise ein IPv6-Subnetz im LAN?", 64),
               ("Wie viele Bit hat der Interface Identifier in einem /64-Netz?", 64),
               ("Wie viele Hex-Ziffern hat ein vollständig geschriebener IPv6-Block?", 4)]
    for i, (frage, wert) in enumerate(fakten6, 1):
        s.zahl("NET-V6Z", i, T, "NET-L3", frage, wert, "IPv6: 128 Bit = 8 Blöcke × 16 Bit (je 4 Hex-Ziffern); LAN-Subnetze sind /64.", s=1)

    # ---------- NET-L4: OSI, Geräte, Protokolle, Ports ----------
    schichten = {1: "Schicht 1 – Bitübertragung", 2: "Schicht 2 – Sicherung", 3: "Schicht 3 – Vermittlung", 4: "Schicht 4 – Transport",
                 5: "Schicht 5 – Sitzung", 6: "Schicht 6 – Darstellung", 7: "Schicht 7 – Anwendung"}
    elemente = [("Repeater", 1), ("Hub", 1), ("Netzwerkkabel / Glasfaser", 1), ("Switch", 2), ("Bridge", 2), ("MAC-Adresse", 2),
                ("Ethernet-Frame", 2), ("Router", 3), ("IP-Adresse", 3), ("ICMP (ping)", 3), ("Paket (Packet)", 3), ("TCP", 4), ("UDP", 4),
                ("Portnummer", 4), ("Segment", 4), ("HTTP", 7), ("DNS", 7), ("SMTP", 7), ("FTP", 7), ("DHCP", 7), ("SSH", 7),
                ("Access Point (WLAN)", 2), ("ARP (Zuordnung IP → MAC)", 2), ("Layer-3-Switch", 3)]
    zuordnung(s, "NET-OSI", T, "NET-L4", [(a, schichten[b]) for a, b in elemente],
              "Welcher OSI-Schicht wird **{a}** zugeordnet?", None, schwierigkeit=1, rng=rng)
    for i, (n, name) in enumerate(schichten.items(), 1):
        s.zahl("NET-OSINR", i, T, "NET-L4", f"Welche Nummer hat die OSI-Schicht **{name.split('– ')[1]}**?", n,
               "Merksatz von unten: **B**itte **S**chicken **V**ielleicht **T**ausend **S**chöne **D**arstellungs-**A**nwendungen (1–7).", s=1)
    ports = [("HTTP", "80"), ("HTTPS", "443"), ("SSH", "22"), ("Telnet", "23"), ("FTP (Steuerkanal)", "21"), ("SMTP", "25"),
             ("DNS", "53"), ("POP3", "110"), ("IMAP", "143"), ("IMAPS", "993"), ("POP3S", "995"), ("RDP", "3389"),
             ("DHCP (Server)", "67"), ("SNMP", "161"), ("LDAP", "389"), ("SMB", "445"), ("NTP", "123"), ("MySQL/MariaDB", "3306"),
             ("SMTP Submission (STARTTLS)", "587")]
    zuordnung(s, "NET-PORT", T, "NET-L4", [(a, b, f"{a} nutzt standardmäßig Port {b}.") for a, b in ports],
              "Welchen Standard-Port verwendet **{a}**?", "Welcher Dienst nutzt standardmäßig Port **{b}**?", schwierigkeit=2, rng=rng)
    tcpudp = [("Verbindungsorientiert mit Drei-Wege-Handshake", "TCP"), ("Garantiert Reihenfolge und erneutes Senden verlorener Daten", "TCP"),
              ("Geringer Overhead, keine Empfangsbestätigung", "UDP"), ("Typisch für Live-Streaming und VoIP", "UDP"),
              ("Typisch für HTTP(S) und E-Mail", "TCP"), ("Typisch für DNS-Anfragen", "UDP"), ("Flusskontrolle über Fenstergröße", "TCP"),
              ("Verbindungslos", "UDP")]
    for i, (a, b) in enumerate(tcpudp, 1):
        s.mehrfach("NET-TCPUDP", i, T, "NET-L4", f"Welches Transportprotokoll passt? **{a}**", [b], ["UDP" if b == "TCP" else "TCP", "ICMP"],
                   "TCP: zuverlässig, verbindungsorientiert. UDP: schnell, verbindungslos, ohne Bestätigung.", s=1)
    geraete = [("verbindet unterschiedliche Netze und leitet anhand von IP-Adressen weiter", "Router"),
               ("leitet Frames anhand der MAC-Adresse gezielt an einen Port weiter", "Switch"),
               ("sendet eingehende Signale an alle Ports weiter", "Hub"),
               ("verbindet WLAN-Geräte mit dem kabelgebundenen Netz", "Access Point"),
               ("filtert Datenverkehr anhand von Regeln zwischen Netzen", "Firewall"),
               ("verstärkt ein Signal, um die Reichweite zu erhöhen", "Repeater"),
               ("wandelt Signale zwischen Telefon-/Kabelleitung und Netzwerk um", "Modem"),
               ("stellt Geräte über das Netzwerk mit Strom per Ethernet-Kabel (PoE) bereit", "PoE-Switch")]
    zuordnung(s, "NET-GERAET", T, "NET-L4", geraete, "Welches Gerät **{a}**?", "Was macht ein **{b}**?", schwierigkeit=1, rng=rng)

    # ---------- NET-L5: DHCP, DNS, Fehlersuche ----------
    records = [("A", "ordnet einem Namen eine IPv4-Adresse zu"), ("AAAA", "ordnet einem Namen eine IPv6-Adresse zu"),
               ("MX", "nennt den Mailserver einer Domain"), ("CNAME", "ist ein Alias, der auf einen anderen Namen zeigt"),
               ("PTR", "ordnet einer IP-Adresse einen Namen zu (Reverse Lookup)"), ("NS", "nennt den zuständigen Nameserver der Zone"),
               ("TXT", "enthält freien Text, z. B. SPF- oder Verifizierungsangaben"), ("SOA", "enthält Verwaltungsangaben zur Zone (Start of Authority)")]
    zuordnung(s, "NET-DNSREC", T, "NET-L5", records, "Was beschreibt ein DNS-Eintrag vom Typ **{a}**?",
              "Welcher DNS-Eintragstyp {b}?", schwierigkeit=2, rng=rng)
    befehle = [("ping", "prüft, ob ein Ziel per ICMP erreichbar ist"), ("tracert / traceroute", "zeigt die Router auf dem Weg zum Ziel"),
               ("ipconfig /all", "zeigt unter Windows IP-Adresse, Gateway, DNS-Server und MAC"), ("nslookup", "fragt DNS-Server nach Namen und Adressen"),
               ("ipconfig /release und /renew", "gibt die DHCP-Adresse frei und fordert eine neue an"), ("netstat", "zeigt offene Verbindungen und lauschende Ports"),
               ("arp -a", "zeigt die Zuordnung von IP- zu MAC-Adressen im lokalen Netz"), ("ipconfig /flushdns", "leert den DNS-Cache des Rechners"),
               ("ip addr (Linux)", "zeigt unter Linux die Adressen der Netzwerkschnittstellen")]
    zuordnung(s, "NET-BEFEHL", T, "NET-L5", befehle, "Was macht der Befehl `{a}`?", "Welcher Befehl {b}?", schwierigkeit=1, rng=rng)
    dora = ["DHCP Discover", "DHCP Offer", "DHCP Request", "DHCP Acknowledge"]
    for i, name in enumerate(dora, 1):
        s.zahl("NET-DORA", i, T, "NET-L5", f"An welcher Stelle (1–4) des DHCP-Ablaufs steht die Nachricht **{name}**?", i,
               "Ablauf DORA: Discover → Offer → Request → Acknowledge.", s=1)
    faelle = [("Ein PC hat die Adresse 169.254.23.7.", "Der PC hat keinen DHCP-Server erreicht (APIPA)."),
              ("ping 8.8.8.8 klappt, ping www.beispiel.de meldet 'Host nicht gefunden'.", "Die Namensauflösung (DNS) funktioniert nicht."),
              ("Ein PC erreicht Geräte im eigenen Netz, aber nichts außerhalb.", "Das Standardgateway fehlt oder ist falsch."),
              ("Zwei Geräte melden einen Adresskonflikt.", "Dieselbe IP-Adresse ist doppelt vergeben."),
              ("ping 127.0.0.1 schlägt fehl.", "Der TCP/IP-Stack des Rechners ist defekt oder deaktiviert."),
              ("Die Netzwerk-LED am PC leuchtet nicht.", "Es besteht keine physische Verbindung (Kabel/Port)."),
              ("Neue Rechner bekommen keine Adresse mehr, ältere funktionieren.", "Der DHCP-Adresspool ist erschöpft.")]
    zuordnung(s, "NET-FEHLER", T, "NET-L5", faelle, "Fehlersuche: {a} Was ist die wahrscheinlichste Ursache?", None, schwierigkeit=2, rng=rng)
    dhcp = [("IP-Adresse", True), ("Subnetzmaske", True), ("Standardgateway", True), ("DNS-Server", True), ("MAC-Adresse des Clients", False),
            ("Lease-Dauer", True), ("Benutzerpasswort", False), ("Hostname des Domänencontrollers als Pflichtangabe", False)]
    from .basis import aussagen
    aussagen(s, "NET-DHCPOPT", T, "NET-L5", "Welche Angaben kann ein DHCP-Server einem Client typischerweise zuweisen?",
             [a for a, r in dhcp if r], [a for a, r in dhcp if not r], n=8, k_richtig=(2, 3), anzahl=4, rng=rng)
    return s.fragen

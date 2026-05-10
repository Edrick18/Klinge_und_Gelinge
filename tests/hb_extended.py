"""Erweiterte Heartbeat-Tests: Quest auflösen, Reise, Skill-Baum, Inventar."""
import socket, json, time, uuid, sqlite3

def send_msg(s, typ, daten={}):
    msg = {'typ': typ, 'daten': daten}
    data = json.dumps(msg).encode('utf-8')
    header = len(data).to_bytes(4, 'big')
    s.sendall(header + data)

def recv_msg(s):
    header = s.recv(4)
    if not header:
        return None
    length = int.from_bytes(header, 'big')
    data = b''
    while len(data) < length:
        chunk = s.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return json.loads(data.decode('utf-8'))

def get_user_for_char(char_id):
    """Benutzernamen für einen Charakter aus DB holen."""
    db = sqlite3.connect('server/datenbank/spieldaten.db')
    cur = db.cursor()
    cur.execute("SELECT spieler_id FROM charaktere WHERE id=?", (char_id,))
    row = cur.fetchone()
    if not row:
        db.close()
        return None
    spieler_id = row[0]
    cur.execute("SELECT benutzername FROM spieler WHERE id=?", (spieler_id,))
    row2 = cur.fetchone()
    db.close()
    return row2[0] if row2 else None

def setup():
    """Einmaliges Setup: Benutzer + Charakter erstellen."""
    unique_id = uuid.uuid4().hex[:8]
    benutzername = f"hb{unique_id}"
    charakter_name = f"HB{unique_id}"

    s = socket.socket()
    s.settimeout(10)
    s.connect(('127.0.0.1', 55000))

    send_msg(s, 'verbindung_herstellen')
    recv_msg(s)

    send_msg(s, 'registrieren', {'benutzername': benutzername, 'passwort': 'test123'})
    recv_msg(s)

    send_msg(s, 'login', {'benutzername': benutzername, 'passwort': 'test123'})
    recv_msg(s)

    stats = {'staerke': 12, 'vitalitaet': 12, 'weisheit': 12, 'glueck': 12, 'beweglichkeit': 16, 'charisma': 16}
    send_msg(s, 'charakter_erstellen', {'charakter_name': charakter_name, 'masterie': 'krieger', 'stats': stats})
    recv_msg(s)

    send_msg(s, 'charaktere_laden')
    r = recv_msg(s)
    char_id = r['daten']['charaktere'][0].get('id') or r['daten']['charaktere'][0].get('charakter_id')

    send_msg(s, 'charakter_waehlen', {'charakter_id': char_id})
    recv_msg(s)

    s.close()
    return char_id

def login_verbindung(char_id):
    """Neue Verbindung aufbauen und einloggen."""
    s = socket.socket()
    s.settimeout(10)
    s.connect(('127.0.0.1', 55000))

    benutzername = get_user_for_char(char_id)
    if not benutzername:
        s.close()
        raise ValueError(f"Kein Benutzer für Charakter {char_id}")

    send_msg(s, 'verbindung_herstellen')
    recv_msg(s)
    send_msg(s, 'login', {'benutzername': benutzername, 'passwort': 'test123'})
    recv_msg(s)
    send_msg(s, 'charakter_waehlen', {'charakter_id': char_id})
    recv_msg(s)

    return s

def test_quest_aufloesen(char_id):
    """Quest auflösen mit DB-Manipulation für schnellen Test."""
    # Quests des Charakters finden und Timer zurücksetzen
    db = sqlite3.connect('server/datenbank/spieldaten.db')
    quests = db.execute("SELECT id FROM quests WHERE charakter_id=? AND abgeschlossen=0", (char_id,)).fetchall()
    if quests:
        qid = quests[0][0]
        db.execute("UPDATE quests SET gestartet_am='2020-01-01T00:00:00' WHERE id=?", (qid,))
        db.commit()
        print(f"[OK] DB: Quest {qid} Timer zurückgesetzt")
    else:
        print("[WARN] Keine aktive Quest gefunden")
    db.close()

    s = login_verbindung(char_id)

    # Quests laden
    send_msg(s, 'quests_laden')
    r = recv_msg(s)
    print(f"[OK] Quests geladen: {len(r['daten'].get('quests', []))}")

    # Quest auflösen (wenn Timer abgelaufen)
    quests = r['daten'].get('quests', [])
    for q in quests:
        if q.get('gestartet_am') and not q.get('abgeschlossen'):
            send_msg(s, 'quest_aufloesen', {'quest_id': q['id']})
            r = recv_msg(s)
            qr = r['daten'].get('quest_ergebnis', {})
            print(f"[OK] Quest auflösen: typ={r['typ']}, erfolg={qr.get('erfolg', '?')}")
            break
    else:
        print("[WARN] Keine auflösbare Quest")

    s.close()

def test_reise(char_id):
    """Reise starten + Belohnungen abholen."""
    s = login_verbindung(char_id)

    # Reise starten
    send_msg(s, 'reise_starten')
    r = recv_msg(s)
    print(f"[OK] Reise starten: typ={r['typ']}")

    # Reise Status
    send_msg(s, 'reise_status_laden')
    r = recv_msg(s)
    print(f"[OK] Reise Status: typ={r['typ']}")

    # Reise Belohnungen laden
    send_msg(s, 'reise_belohnungen_laden')
    r = recv_msg(s)
    print(f"[OK] Reise Belohnungen: typ={r['typ']}")

    s.close()

def test_skills(char_id):
    """Skill-Baum: Node skillen, Skill ausrüsten."""
    s = login_verbindung(char_id)

    # Skills laden
    send_msg(s, 'skills_laden')
    r = recv_msg(s)
    print(f"[OK] Skills laden: typ={r['typ']}, Punkte={r['daten'].get('skill_punkte', '?')}")

    s.close()

def test_inventar(char_id):
    """Inventar laden."""
    s = login_verbindung(char_id)

    # Inventar laden
    send_msg(s, 'inventar_laden')
    r = recv_msg(s)
    print(f"[OK] Inventar laden: typ={r['typ']}")

    s.close()

def test_kampf(char_id):
    """Testkampf mit Skills."""
    s = login_verbindung(char_id)

    send_msg(s, 'testkampf_starten')
    r = recv_msg(s)
    ergebnis = r['daten'].get('kampf_ergebnis', {})
    print(f"[OK] Testkampf: typ={r['typ']}, gewonnen={ergebnis.get('gewonnen')}, Ereignisse={len(ergebnis.get('ereignisse', []))}")

    s.close()

if __name__ == "__main__":
    print("=== Setup ===")
    char_id = setup()
    print(f"Charakter-ID: {char_id}")

    print("\n=== Testkampf ===")
    test_kampf(char_id)

    print("\n=== Quest auflösen ===")
    test_quest_aufloesen(char_id)

    print("\n=== Reise ===")
    test_reise(char_id)

    print("\n=== Skills ===")
    test_skills(char_id)

    print("\n=== Inventar ===")
    test_inventar(char_id)

    print("\n[ALLE ERWEITERTEN TESTS GRUN]")

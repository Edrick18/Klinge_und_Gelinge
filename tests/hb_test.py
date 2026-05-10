"""Heartbeat-Test: Kompletter Server-Test via TCP."""
import socket, json, time, uuid

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

def test_server():
    unique_id = uuid.uuid4().hex[:8]
    benutzername = f"hb{unique_id}"
    charakter_name = f"HB{unique_id}"

    s = socket.socket()
    s.settimeout(10)
    s.connect(('127.0.0.1', 55000))

    # 1. Verbindung
    send_msg(s, 'verbindung_herstellen')
    r = recv_msg(s)
    assert r['typ'] == 'verbindung_bestaetigt', f"Verbindung fehl: {r}"
    print("[OK] 1. Verbindung herstellen")

    # 2. Registrieren
    send_msg(s, 'registrieren', {'benutzername': benutzername, 'passwort': 'test123'})
    r = recv_msg(s)
    assert r['typ'] == 'registrieren_erfolg', f"Registrierung fehl: {r}"
    print("[OK] 2. Registrieren")

    # 3. Login
    send_msg(s, 'login', {'benutzername': benutzername, 'passwort': 'test123'})
    r = recv_msg(s)
    assert r['typ'] == 'login_erfolg', f"Login fehl: {r}"
    print("[OK] 3. Login")

    # 4. Charakter erstellen (Stats sum = 80)
    stats = {'staerke': 12, 'vitalitaet': 12, 'weisheit': 12, 'glueck': 12, 'beweglichkeit': 16, 'charisma': 16}
    send_msg(s, 'charakter_erstellen', {'charakter_name': charakter_name, 'masterie': 'krieger', 'stats': stats})
    r = recv_msg(s)
    assert r['typ'] == 'charakter_erstellt', f"Charakter erstellen fehl: {r}"
    print("[OK] 4. Charakter erstellen")

    # 5. Charaktere laden
    send_msg(s, 'charaktere_laden')
    r = recv_msg(s)
    assert r['typ'] == 'charaktere_antwort', f"Charaktere laden fehl: {r}"
    assert len(r['daten']['charaktere']) >= 1, f"Kein Charakter gefunden"
    char_id = r['daten']['charaktere'][0].get('id') or r['daten']['charaktere'][0].get('charakter_id')
    print(f"[OK] 5. Charaktere laden (ID: {char_id})")

    # 6. Charakter waehlen
    send_msg(s, 'charakter_waehlen', {'charakter_id': char_id})
    r = recv_msg(s)
    assert r['typ'] == 'charakter_gewaehlt', f"Char waehlen fehl: {r}"
    print("[OK] 6. Charakter waehlen")

    # 7. Testkampf
    send_msg(s, 'testkampf_starten')
    r = recv_msg(s)
    assert r['typ'] == 'kampf_ergebnis', f"Testkampf fehl: {r}"
    ergebnis = r['daten']['kampf_ergebnis']
    assert len(ergebnis.get('ereignisse', [])) > 0, "Kampf-Log leer"
    print(f"[OK] 7. Testkampf (gewonnen={ergebnis.get('gewonnen')}, Log={len(ergebnis['ereignisse'])})")

    # 8. Quests laden
    send_msg(s, 'quests_laden')
    r = recv_msg(s)
    assert r['typ'] == 'quests_antwort', f"Quests laden fehl: {r}"
    assert len(r['daten'].get('quests', [])) >= 1, f"Keine Quests"
    print(f"[OK] 8. Quests laden (Anzahl: {len(r['daten']['quests'])})")

    # 9. Quest annehmen
    quest_id = r['daten']['quests'][0]['id']
    send_msg(s, 'quest_annehmen', {'quest_id': quest_id})
    r = recv_msg(s)
    assert r['typ'] == 'quest_angenommen', f"Quest annehmen fehl: {r}"
    print(f"[OK] 9. Quest annehmen")

    # 10. Inventar laden
    send_msg(s, 'inventar_laden')
    r = recv_msg(s)
    assert r['typ'] == 'inventar_antwort', f"Inventar fehl: {r}"
    print(f"[OK] 10. Inventar laden")

    # 11. Skills laden
    send_msg(s, 'skills_laden')
    r = recv_msg(s)
    assert r['typ'] == 'skills_antwort', f"Skills fehl: {r}"
    print(f"[OK] 11. Skills laden (Punkte: {r['daten'].get('skill_punkte', '?')})")

    # 12. Reise Status
    send_msg(s, 'reise_status_laden')
    r = recv_msg(s)
    assert r['typ'] == 'reise_status_antwort', f"Reise Status fehl: {r}"
    print(f"[OK] 12. Reise Status")

    s.close()
    print("\n[ALLE TESTS GRUN]")
    return True

if __name__ == "__main__":
    test_server()

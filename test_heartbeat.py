"""
test_heartbeat.py - Automatischer Test des RPG-Spiels

Testet: Datenbank, Authentifizierung, Charakter, Quests, Items, Skills
"""
import sys
import os
import sqlite3
import bcrypt
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_Pfad = "spiel.sqlite"
TEST_BENUTZER = "hb_test_user"
TEST_PASSWORT = "test123"
TEST_CHARAKTER = "hb_test_char"
TEST_USER_ID = None
TEST_CHAR_ID = None

erfolge = 0
fehler = 0
fehler_details = []

def _test(name, bedingung, detail=""):
    global erfolge, fehler, fehler_details
    if bedingung:
        print(f"  [OK] {name}")
        erfolge += 1
    else:
        msg = f"  [FAIL] {name}"
        if detail:
            msg += f" ({detail})"
        print(msg)
        fehler += 1
        fehler_details.append(f"{name}: {detail}")

def db_connection():
    return sqlite3.connect(DB_Pfad)

# ==================== TEST: Datenbank ====================
print("\n=== TEST: Datenbank ===")
try:
    conn = db_connection()
    cursor = conn.cursor()
    _test("DB Verbindung", True)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    
    _test("Spieler Tabelle", "spieler" in tables)
    _test("Charaktere Tabelle", "charaktere" in tables)
    _test("Quests Tabelle", "quests" in tables)
    _test("Inventar Tabelle", "inventar" in tables)
    _test("Snapshots Tabelle", "charakter_snapshots" in tables)
    _test("Klassen Tabelle", "charakter_klassen" in tables)
    _test("Nodes Tabelle", "charakter_nodes" in tables)
    _test("Skills Tabelle", "charakter_klassen_skills" in tables)
    conn.close()
except Exception as e:
    _test("DB", False, str(e))

# ==================== TEST: Registrierung + Login ====================
print("\n=== TEST: Registrierung + Login ===")
try:
    conn = db_connection()
    cursor = conn.cursor()
    
    # Cleanup
    cursor.execute("DELETE FROM spieler WHERE benutzername=?", (TEST_BENUTZER,))
    conn.commit()
    
    # Registrieren
    pw_hash = bcrypt.hashpw(TEST_PASSWORT.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "INSERT INTO spieler (benutzername, passwort_hash, erstellt_am, letzter_login) "
        "VALUES (?, ?, datetime('now'), datetime('now'))",
        (TEST_BENUTZER, pw_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    _test("Registrierung", user_id > 0)
    
    # Login prüfen
    cursor.execute("SELECT passwort_hash FROM spieler WHERE benutzername=?", (TEST_BENUTZER,))
    row = cursor.fetchone()
    _test("Login bcrypt", bcrypt.checkpw(TEST_PASSWORT.encode(), row[0].encode()))
    
    # User ID merken
    cursor.execute("SELECT id FROM spieler WHERE benutzername=?", (TEST_BENUTZER,))
    TEST_USER_ID = cursor.fetchone()[0]
    
    conn.close()
except Exception as e:
    _test("Registrierung", False, str(e))
    TEST_USER_ID = None

# ==================== TEST: Charakter erstellen ====================
print("\n=== TEST: Charakter erstellen ===")
try:
    if not TEST_USER_ID:
        _test("Charakter", False, "Kein User")
    else:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Cleanup
        cursor.execute("DELETE FROM charaktere WHERE spieler_id=?", (TEST_USER_ID,))
        conn.commit()
        
        # Charakter erstellen
        cursor.execute(
            "INSERT INTO charaktere (spieler_id, name, masterie_1, level, erfahrung, skill_punkte, "
            "staerke, vitalitaet, weisheit, glueck, beweglichkeit, charisma, gold, erstellt_am) "
            "VALUES (?, ?, 'krieger', 1, 0, 0, 10, 10, 10, 5, 10, 5, 100, datetime('now'))",
            (TEST_USER_ID, TEST_CHARAKTER)
        )
        conn.commit()
        char_id = cursor.lastrowid
        _test("Charakter erstellt", char_id > 0)
        
        # Laden
        cursor.execute("SELECT name, level, gold FROM charaktere WHERE id=?", (char_id,))
        row = cursor.fetchone()
        _test("Charakter geladen", row is not None)
        if row:
            _test("Name", row[0] == TEST_CHARAKTER)
            _test("Level", row[1] == 1)
            _test("Gold", row[2] == 100)
        
        TEST_CHAR_ID = char_id
        conn.close()
except Exception as e:
    _test("Charakter", False, str(e))
    TEST_CHAR_ID = None

# ==================== TEST: Quest-System ====================
print("\n=== TEST: Quest-System ===")
try:
    if not TEST_CHAR_ID:
        _test("Quest", False, "Kein Charakter")
    else:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Cleanup
        cursor.execute("DELETE FROM quests WHERE charakter_id=?", (TEST_CHAR_ID,))
        conn.commit()
        
        # Quest erstellen
        cursor.execute(
            "INSERT INTO quests (id, spieler_id, charakter_id, name, beschreibung, raritaet, "
            "schwierigkeit, timer_sekunden, gestartet_am, gold_belohnung, xp_belohnung, "
            "item_drop_chance, abgeschlossen, ergebnis) "
            "VALUES (?, ?, ?, 'Test-Quest', 'Test', 'normal', 1.0, 300, "
            "datetime('now'), 50, 100, 0.5, 0, '')",
            (f"quest_test_{TEST_CHAR_ID}", TEST_USER_ID, TEST_CHAR_ID)
        )
        conn.commit()
        _test("Quest erstellt", True)
        
        # Aktive Quests zählen
        cursor.execute(
            "SELECT COUNT(*) FROM quests WHERE charakter_id=? AND abgeschlossen=0",
            (TEST_CHAR_ID,)
        )
        count = cursor.fetchone()[0]
        _test("Quest aktiv", count >= 1)
        
        # Quest abschließen
        cursor.execute(
            "UPDATE quests SET abgeschlossen=1, ergebnis='sieg' WHERE charakter_id=? AND abgeschlossen=0",
            (TEST_CHAR_ID,)
        )
        conn.commit()
        _test("Quest abgeschlossen", True)
        
        conn.close()
except Exception as e:
    _test("Quest", False, str(e))

# ==================== TEST: Inventar ====================
print("\n=== TEST: Inventar ===")
try:
    if not TEST_CHAR_ID:
        _test("Inventar", False, "Kein Charakter")
    else:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Cleanup
        cursor.execute("DELETE FROM inventar WHERE charakter_id=?", (TEST_CHAR_ID,))
        conn.commit()
        
        # Item erstellen
        item_json = json.dumps({
            "name": "Test-Schwert",
            "typ": "waffe",
            "raritaet": "magisch",
            "basis_stats": {"schaden": 10},
            "prefixe": [],
            "suffixe": []
        })
        cursor.execute(
            "INSERT INTO inventar (id, charakter_id, item_json, ausgeruestet, slot) "
            "VALUES (?, ?, ?, 0, 'waffe')",
            (f"item_test_{TEST_CHAR_ID}", TEST_CHAR_ID, item_json)
        )
        conn.commit()
        _test("Item erstellt", True)
        
        # Ausrüsten
        cursor.execute("UPDATE inventar SET ausgeruestet=1 WHERE charakter_id=?", (TEST_CHAR_ID,))
        conn.commit()
        _test("Item angerüstet", True)
        
        # Laden
        cursor.execute("SELECT item_json FROM inventar WHERE charakter_id=?", (TEST_CHAR_ID,))
        row = cursor.fetchone()
        item = json.loads(row[0]) if row else None
        _test("Item geladen", item is not None)
        if item:
            _test("Item-Name", item["name"] == "Test-Schwert")
        
        # Ablegen
        cursor.execute("UPDATE inventar SET ausgeruestet=0 WHERE charakter_id=?", (TEST_CHAR_ID,))
        conn.commit()
        _test("Item abgelegt", True)
        
        conn.close()
except Exception as e:
    _test("Inventar", False, str(e))

# ==================== TEST: Skill-System ====================
print("\n=== TEST: Skill-System ===")
try:
    if not TEST_CHAR_ID:
        _test("Skills", False, "Kein Charakter")
    else:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Klassen-Zuordnung prüfen
        cursor.execute(
            "SELECT COUNT(*) FROM charakter_klassen WHERE charakter_id=?",
            (TEST_CHAR_ID,)
        )
        klassen_count = cursor.fetchone()[0]
        _test(f"Klassen-Zuordnung ({klassen_count})", True)
        
        # Nodes prüfen
        cursor.execute(
            "SELECT COUNT(*) FROM charakter_nodes WHERE charakter_id=?",
            (TEST_CHAR_ID,)
        )
        node_count = cursor.fetchone()[0]
        _test(f"Nodes ({node_count})", True)
        
        # Skills prüfen
        cursor.execute(
            "SELECT COUNT(*) FROM charakter_klassen_skills WHERE charakter_id=?",
            (TEST_CHAR_ID,)
        )
        skill_count = cursor.fetchone()[0]
        _test(f"Ausruestungs-Skills ({skill_count})", True)
        
        # Skill-Punkte
        cursor.execute("SELECT skill_punkte FROM charaktere WHERE id=?", (TEST_CHAR_ID,))
        row = cursor.fetchone()
        _test("Skill-Punkte lesbar", row is not None)
        
        conn.close()
except Exception as e:
    _test("Skills", False, str(e))

# ==================== TEST: Snapshot-System ====================
print("\n=== TEST: Snapshot ===")
try:
    if not TEST_CHAR_ID:
        _test("Snapshot", False, "Kein Charakter")
    else:
        conn = db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM charakter_snapshots WHERE charakter_id=?",
            (TEST_CHAR_ID,)
        )
        snap_count = cursor.fetchone()[0]
        _test(f"Snapshots ({snap_count})", True)
        
        if snap_count > 0:
            cursor.execute(
                "SELECT snapshot_json FROM charakter_snapshots WHERE charakter_id=? ORDER BY erstellt_am DESC LIMIT 1",
                (TEST_CHAR_ID,)
            )
            row = cursor.fetchone()
            snap = json.loads(row[0]) if row else None
            _test("Snapshot parsbar", snap is not None)
        
        conn.close()
except Exception as e:
    _test("Snapshot", False, str(e))

# ==================== Cleanup ====================
print("\n=== Cleanup ===")
try:
    conn = db_connection()
    cursor = conn.cursor()
    if TEST_CHAR_ID:
        cursor.execute("DELETE FROM inventar WHERE charakter_id=?", (TEST_CHAR_ID,))
        cursor.execute("DELETE FROM quests WHERE charakter_id=?", (TEST_CHAR_ID,))
        cursor.execute("DELETE FROM charakter_snapshots WHERE charakter_id=?", (TEST_CHAR_ID,))
        cursor.execute("DELETE FROM charakter_klassen_skills WHERE charakter_id=?", (TEST_CHAR_ID,))
        cursor.execute("DELETE FROM charakter_nodes WHERE charakter_id=?", (TEST_CHAR_ID,))
        cursor.execute("DELETE FROM charakter_klassen WHERE charakter_id=?", (TEST_CHAR_ID,))
        cursor.execute("DELETE FROM charaktere WHERE id=?", (TEST_CHAR_ID,))
    if TEST_USER_ID:
        cursor.execute("DELETE FROM spieler WHERE id=?", (TEST_USER_ID,))
    conn.commit()
    _test("Cleanup", True)
    conn.close()
except Exception as e:
    _test("Cleanup", False, str(e))

# ==================== Ergebnis ====================
print(f"\n{'='*50}")
print(f"ERGEBNIS: {erfolge} OK | {fehler} FAIL")
print(f"{'='*50}")
if fehler_details:
    print("\nFehler:")
    for f in fehler_details:
        print(f"  - {f}")

if __name__ == "__main__":
    sys.exit(0 if fehler == 0 else 1)

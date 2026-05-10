"""
server/datenbank/datenbank.py - SQLite-Datenbank für Spielerdaten

Abhängigkeiten: sqlite3, bcrypt
"""

import sqlite3
import bcrypt
import json
from datetime import datetime, timedelta


class Datenbank:
    def __init__(self, db_pfad: str = "server/datenbank/spieldaten.db"):
        self.db_pfad = db_pfad
        self.verbindung = sqlite3.connect(self.db_pfad, check_same_thread=False)
        self.verbindung.row_factory = sqlite3.Row
        self._tabellen_erstellen()

    def _tabellen_erstellen(self):
        cursor = self.verbindung.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spieler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                benutzername TEXT UNIQUE NOT NULL,
                passwort_hash TEXT NOT NULL,
                erstellt_am TEXT NOT NULL,
                letzter_login TEXT,
                letzter_charakter_id INTEGER DEFAULT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charaktere (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spieler_id INTEGER NOT NULL REFERENCES spieler(id),
                name TEXT NOT NULL,
                masterie_1 TEXT NOT NULL,
                masterie_2 TEXT,
                level INTEGER DEFAULT 1,
                erfahrung INTEGER DEFAULT 0,
                skill_punkte INTEGER DEFAULT 0,
                staerke INTEGER DEFAULT 10,
                vitalitaet INTEGER DEFAULT 10,
                weisheit INTEGER DEFAULT 10,
                glueck INTEGER DEFAULT 10,
                beweglichkeit INTEGER DEFAULT 10,
                charisma INTEGER DEFAULT 10,
                gold INTEGER DEFAULT 0,
                erstellt_am TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                charakter_id INTEGER PRIMARY KEY REFERENCES charaktere(id),
                snapshot_json TEXT NOT NULL,
                erstellt_am TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                spieler_id INTEGER NOT NULL,
                charakter_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                beschreibung TEXT NOT NULL,
                raritaet TEXT NOT NULL,
                schwierigkeit REAL NOT NULL,
                timer_sekunden INTEGER NOT NULL,
                gestartet_am TEXT,
                gold_belohnung INTEGER NOT NULL,
                xp_belohnung INTEGER NOT NULL,
                item_drop_chance REAL NOT NULL,
                abgeschlossen INTEGER DEFAULT 0,
                ergebnis TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventar (
                id TEXT PRIMARY KEY,
                charakter_id INTEGER NOT NULL REFERENCES charaktere(id),
                item_json TEXT NOT NULL,
                ausgeruestet INTEGER DEFAULT 0,
                slot TEXT DEFAULT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charakter_klassen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charakter_id INTEGER NOT NULL REFERENCES charaktere(id),
                klassen_id TEXT NOT NULL,
                typ TEXT NOT NULL,
                aktiv INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charakter_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charakter_id INTEGER NOT NULL REFERENCES charaktere(id),
                klassen_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                stufe INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charakter_klassen_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charakter_id INTEGER NOT NULL REFERENCES charaktere(id),
                skill_id TEXT NOT NULL,
                klassen_id TEXT NOT NULL,
                skill_level INTEGER DEFAULT 1,
                ausgeruestet INTEGER DEFAULT 0,
                slot_typ TEXT DEFAULT NULL,
                slot_nummer INTEGER DEFAULT NULL,
                nutzungen INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charakter_reisen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charakter_id INTEGER NOT NULL REFERENCES charaktere(id),
                gestartet_am TEXT NOT NULL,
                aktiv INTEGER DEFAULT 1
            )
        """)
        try:
            cursor.execute("ALTER TABLE charakter_reisen ADD COLUMN max_dauer INTEGER DEFAULT 14400")
        except sqlite3.OperationalError:
            pass
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reise_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reise_id INTEGER NOT NULL REFERENCES charakter_reisen(id),
                quest_json TEXT NOT NULL,
                kampf_ergebnis_json TEXT,
                quest_zeit TEXT NOT NULL,
                belohnung_gold INTEGER DEFAULT 0,
                belohnung_xp INTEGER DEFAULT 0,
                abgeholt INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charakter_traenke (
                id TEXT PRIMARY KEY,
                charakter_id INTEGER NOT NULL REFERENCES charaktere(id),
                stat TEXT NOT NULL,
                stufe TEXT NOT NULL,
                bonus REAL NOT NULL,
                aktiv_bis TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_angebote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charakter_id INTEGER NOT NULL,
                slot INTEGER NOT NULL,
                typ TEXT NOT NULL,
                inhalt_json TEXT NOT NULL,
                preis INTEGER NOT NULL,
                gekauft INTEGER DEFAULT 0,
                generiert_am TEXT NOT NULL,
                gueltig_bis TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_rerolls (
                charakter_id INTEGER PRIMARY KEY,
                anzahl_heute INTEGER DEFAULT 0,
                letzter_reset TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arena_stats (
                charakter_id INTEGER PRIMARY KEY REFERENCES charaktere(id),
                rang_punkte INTEGER DEFAULT 0,
                siege INTEGER DEFAULT 0,
                niederlagen INTEGER DEFAULT 0,
                ehrenmarken INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arena_kaempfe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                angreifer_id INTEGER NOT NULL REFERENCES charaktere(id),
                verteidiger_id INTEGER NOT NULL REFERENCES charaktere(id),
                gewonnen INTEGER NOT NULL,
                rang_aenderung INTEGER NOT NULL,
                gold_belohnung INTEGER DEFAULT 0,
                xp_belohnung INTEGER DEFAULT 0,
                marken_belohnung INTEGER DEFAULT 0,
                gekämpft_am TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_verzauberungen (
                item_id TEXT PRIMARY KEY,
                charakter_id INTEGER NOT NULL,
                verstaerkung REAL DEFAULT 1.15,
                erstellt_am TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gilden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                beschreibung TEXT DEFAULT '',
                erstellt_am TEXT NOT NULL,
                kasse INTEGER DEFAULT 0,
                steuer INTEGER DEFAULT 0,
                stufe INTEGER DEFAULT 0,
                xp_bonus REAL DEFAULT 0.0,
                gold_bonus REAL DEFAULT 0.0,
                mitglieder_anzahl INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gilde_mitglieder (
                charakter_id INTEGER PRIMARY KEY,
                gilden_id INTEGER NOT NULL,
                rang TEXT DEFAULT 'mitglied',
                beigetreten_am TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gilde_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gilden_id INTEGER NOT NULL,
                charakter_name TEXT NOT NULL,
                aktion TEXT NOT NULL,
                erstellt_am TEXT NOT NULL
            )
        """)
        self.verbindung.commit()

    def spieler_erstellen(self, benutzername: str, passwort_hash: str) -> bool:
        try:
            cursor = self.verbindung.cursor()
            cursor.execute(
                "INSERT INTO spieler (benutzername, passwort_hash, erstellt_am) VALUES (?, ?, ?)",
                (benutzername, passwort_hash, datetime.now().isoformat())
            )
            self.verbindung.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def spieler_laden(self, benutzername: str):
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM spieler WHERE benutzername = ?", (benutzername,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def letzten_login_aktualisieren(self, spieler_id: int):
        cursor = self.verbindung.cursor()
        cursor.execute(
            "UPDATE spieler SET letzter_login = ? WHERE id = ?",
            (datetime.now().isoformat(), spieler_id)
        )
        self.verbindung.commit()

    def charakter_erstellen(self, spieler_id: int, name: str, masterie_1: str, stats: dict) -> int | None:
        try:
            cursor = self.verbindung.cursor()
            cursor.execute(
                """INSERT INTO charaktere (spieler_id, name, masterie_1, staerke, vitalitaet, weisheit, glueck, beweglichkeit, charisma, erstellt_am)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (spieler_id, name, masterie_1,
                 stats.get("staerke", 10), stats.get("vitalitaet", 10),
                 stats.get("weisheit", 10), stats.get("glueck", 10),
                 stats.get("beweglichkeit", 10), stats.get("charisma", 10),
                 datetime.now().isoformat())
            )
            self.verbindung.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def charaktere_laden(self, spieler_id: int) -> list:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM charaktere WHERE spieler_id = ?", (spieler_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def masterie_belegt(self, spieler_id: int, masterie_1: str) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT 1 FROM charaktere WHERE spieler_id = ? AND masterie_1 = ?", (spieler_id, masterie_1))
        return cursor.fetchone() is not None

    def spieler_hat_charaktere(self, spieler_id: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT COUNT(*) FROM charaktere WHERE spieler_id = ?", (spieler_id,))
        return cursor.fetchone()[0]

    def charakter_laden(self, charakter_id: int):
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        if row:
            daten = dict(row)
            standard_werte = {
                "masterie_2": None,
                "skill_punkte": 0,
                "gold": 0,
                "erfahrung": 0,
            }
            for key, value in standard_werte.items():
                if key not in daten or daten[key] is None:
                    daten[key] = value
            return daten
        return None

    def letzten_charakter_speichern(self, spieler_id: int, charakter_id: int):
        cursor = self.verbindung.cursor()
        cursor.execute(
            "UPDATE spieler SET letzter_charakter_id = ? WHERE id = ?",
            (charakter_id, spieler_id)
        )
        self.verbindung.commit()

    def letzten_charakter_laden(self, spieler_id: int):
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT letzter_charakter_id FROM spieler WHERE id = ?", (spieler_id,))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0]
        return None

    def snapshot_speichern(self, charakter_id: int, snapshot: dict):
        import json
        cursor = self.verbindung.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO charakter_snapshots (charakter_id, snapshot_json, erstellt_am)
               VALUES (?, ?, ?)""",
            (charakter_id, json.dumps(snapshot), datetime.now().isoformat())
        )
        self.verbindung.commit()

    def snapshot_laden(self, charakter_id: int):
        import json
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT snapshot_json FROM charakter_snapshots WHERE charakter_id = ?", (charakter_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def quests_laden(self, spieler_id: int, charakter_id: int) -> list:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT * FROM quests WHERE spieler_id = ? AND charakter_id = ? AND abgeschlossen = 0",
            (spieler_id, charakter_id)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def quest_speichern(self, quest: dict):
        cursor = self.verbindung.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO quests
               (id, spieler_id, charakter_id, name, beschreibung, raritaet, schwierigkeit,
                timer_sekunden, gestartet_am, gold_belohnung, xp_belohnung, item_drop_chance, abgeschlossen, ergebnis)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (quest.get("id"), quest.get("spieler_id"), quest.get("charakter_id"),
             quest.get("name"), quest.get("beschreibung"), quest.get("raritaet"),
             quest.get("schwierigkeit"), quest.get("timer_sekunden"), quest.get("gestartet_am"),
             quest.get("gold_belohnung"), quest.get("xp_belohnung"), quest.get("item_drop_chance"),
             1 if quest.get("abgeschlossen") else 0, quest.get("ergebnis"))
        )
        self.verbindung.commit()

    def quest_starten(self, quest_id: str, zeitstempel: str):
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE quests SET gestartet_am = ? WHERE id = ?", (zeitstempel, quest_id))
        self.verbindung.commit()

    def quest_abschliessen(self, quest_id: str, ergebnis: str):
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE quests SET abgeschlossen = 1, ergebnis = ? WHERE id = ?", (ergebnis, quest_id))
        self.verbindung.commit()

    def abgeschlossene_quests_loeschen(self, spieler_id: int, charakter_id: int):
        cursor = self.verbindung.cursor()
        cursor.execute("DELETE FROM quests WHERE spieler_id = ? AND charakter_id = ? AND abgeschlossen = 1",
                      (spieler_id, charakter_id))
        self.verbindung.commit()

    def alle_quests_loeschen(self, spieler_id: int, charakter_id: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "DELETE FROM quests WHERE spieler_id = ? AND charakter_id = ?",
            (spieler_id, charakter_id)
        )
        self.verbindung.commit()

    def quest_laden(self, quest_id: str):
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM quests WHERE id = ?", (quest_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def gold_hinzufuegen(self, charakter_id: int, betrag: int):
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE charaktere SET gold = gold + ? WHERE id = ?", (betrag, charakter_id))
        self.verbindung.commit()

    def xp_hinzufuegen(self, charakter_id: int, betrag: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE charaktere SET erfahrung = erfahrung + ? WHERE id = ?", (betrag, charakter_id))
        self.verbindung.commit()
        cursor.execute("SELECT erfahrung, level FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

    def level_up_pruefen(self, charakter_id: int) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT level, erfahrung FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        if not row:
            return {"level_up": False, "neues_level": 1}

        level = row[0]
        xp = row[1]

        from spiel.systeme.stat_berechnung import StatBerechnung
        xp_benoetigt = StatBerechnung.xp_fuer_naechstes_level(level)

        if xp >= xp_benoetigt:
            cursor.execute(
                """UPDATE charaktere SET level = level + 1,
                   staerke = ROUND(staerke * 1.3),
                   vitalitaet = ROUND(vitalitaet * 1.3),
                   weisheit = ROUND(weisheit * 1.3),
                   glueck = ROUND(glueck * 1.3),
                   beweglichkeit = ROUND(beweglichkeit * 1.3),
                   charisma = ROUND(charisma * 1.3),
                   erfahrung = erfahrung - ?,
                   skill_punkte = skill_punkte + 5
                   WHERE id = ?""",
                (xp_benoetigt, charakter_id)
            )
            self.verbindung.commit()
            cursor.execute("SELECT level FROM charaktere WHERE id = ?", (charakter_id,))
            neuer_level = cursor.fetchone()[0]
            return {"level_up": True, "neues_level": neuer_level}

        return {"level_up": False, "neues_level": level}

    def item_hinzufuegen(self, charakter_id: int, item: dict) -> None:
        import json
        cursor = self.verbindung.cursor()
        cursor.execute(
            "INSERT INTO inventar (id, charakter_id, item_json, ausgeruestet, slot) VALUES (?, ?, ?, 0, NULL)",
            (item.get("id"), charakter_id, json.dumps(item))
        )
        self.verbindung.commit()

    def inventar_laden(self, charakter_id: int) -> dict:
        import json
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT item_json, ausgeruestet, slot FROM inventar WHERE charakter_id = ?", (charakter_id,))
        rows = cursor.fetchall()

        inventar = []
        ausgeruestet = {}

        for row in rows:
            item = json.loads(row[0])
            is_ausgeruestet = row[1]
            slot = row[2]

            if is_ausgeruestet and slot:
                ausgeruestet[slot] = item
            else:
                inventar.append(item)

        return {"items": inventar, "ausgeruestet": ausgeruestet}

    def inventar_anzahl(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventar WHERE charakter_id = ? AND ausgeruestet = 0", (charakter_id,))
        return cursor.fetchone()[0]

    def item_ausruesten(self, charakter_id: int, item_id: str, slot: str) -> bool:
        cursor = self.verbindung.cursor()

        cursor.execute(
            "SELECT id FROM inventar WHERE charakter_id = ? AND id = ? AND ausgeruestet = 0",
            (charakter_id, item_id))
        if not cursor.fetchone():
            return False

        cursor.execute(
            "UPDATE inventar SET ausgeruestet = 0, slot = NULL WHERE charakter_id = ? AND slot = ? AND ausgeruestet = 1",
            (charakter_id, slot))

        cursor.execute(
            "UPDATE inventar SET ausgeruestet = 1, slot = ? WHERE charakter_id = ? AND id = ?",
            (slot, charakter_id, item_id))

        self.verbindung.commit()
        return True

    def item_ablegen(self, charakter_id: int, slot: str) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE inventar SET ausgeruestet = 0, slot = NULL WHERE charakter_id = ? AND ausgeruestet = 1 AND slot = ?",
                       (charakter_id, slot))
        self.verbindung.commit()
        return cursor.rowcount > 0

    def item_ablegen_by_id(self, charakter_id: int, item_id: str) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE inventar SET ausgeruestet = 0, slot = NULL WHERE charakter_id = ? AND ausgeruestet = 1 AND id = ?",
                       (charakter_id, item_id))
        self.verbindung.commit()
        return cursor.rowcount > 0

    def skill_baum_initialisieren(self, charakter_id: int, masterie: str, baum: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT id FROM charakter_skill_baeume WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                       (charakter_id, masterie, baum))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO charakter_skill_baeume (charakter_id, masterie, baum, punkte_investiert, freigeschaltete_skills) VALUES (?, ?, ?, 0, '[]')",
                           (charakter_id, masterie, baum))
            self.verbindung.commit()

    def skill_baum_laden(self, charakter_id: int, masterie: str, baum: int) -> dict | None:
        import json
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT punkte_investiert, freigeschaltete_skills FROM charakter_skill_baeume WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                       (charakter_id, masterie, baum))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "masterie": masterie,
            "baum": baum,
            "punkte_investiert": row[0],
            "freigeschaltete_skills": json.loads(row[1])
        }

    def alle_skill_baeume_laden(self, charakter_id: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT masterie, baum, punkte_investiert, freigeschaltete_skills FROM charakter_skill_baeume WHERE charakter_id = ?",
                       (charakter_id,))
        import json
        return [{"masterie": r[0], "baum": r[1], "punkte_investiert": r[2], "freigeschaltete_skills": json.loads(r[3])} for r in cursor.fetchall()]

    def punkte_investieren(self, charakter_id: int, masterie: str, baum: int, skill_id: str) -> dict:
        import json
        from spiel.systeme.skill_definitionen import ALLE_SKILLS
        cursor = self.verbindung.cursor()

        if not skill_id or skill_id in ("", "punkt"):
            cursor.execute("SELECT punkte_investiert, freigeschaltete_skills FROM charakter_skill_baeume WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                           (charakter_id, masterie, baum))
            row = cursor.fetchone()
            if not row:
                return {"erfolg": False, "nachricht": "Skill-Baum nicht initialisiert"}

            punkte_investiert = row[0]
            cursor.execute("SELECT skill_punkte FROM charaktere WHERE id = ?", (charakter_id,))
            char_row = cursor.fetchone()
            if not char_row or char_row[0] < 1:
                return {"erfolg": False, "nachricht": "Nicht genug Skill-Punkte"}

            cursor.execute("UPDATE charaktere SET skill_punkte = skill_punkte - 1 WHERE id = ?", (charakter_id,))
            cursor.execute("UPDATE charakter_skill_baeume SET punkte_investiert = punkte_investiert + 1 WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                           (charakter_id, masterie, baum))
            self.verbindung.commit()
            return {"erfolg": True, "freigeschaltet": None, "punkte_investiert": punkte_investiert + 1}

        skill_def = ALLE_SKILLS.get(skill_id)
        if not skill_def:
            return {"erfolg": False, "nachricht": "Skill nicht gefunden"}

        if skill_def["masterie"] != masterie or skill_def["baum"] != baum:
            return {"erfolg": False, "nachricht": "Skill gehört nicht zu diesem Baum"}

        cursor.execute("SELECT punkte_investiert, freigeschaltete_skills FROM charakter_skill_baeume WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                       (charakter_id, masterie, baum))
        row = cursor.fetchone()
        if not row:
            return {"erfolg": False, "nachricht": "Skill-Baum nicht initialisiert"}

        punkte_investiert = row[0]
        freigeschaltete = json.loads(row[1])

        if skill_id in freigeschaltete:
            return {"erfolg": False, "nachricht": "Skill bereits freigeschaltet"}

        punkte_benoetigt = skill_def["punkte_benoetigt"]

        if punkte_investiert < punkte_benoetigt:
            return {"erfolg": False, "nachricht": f"Noch {punkte_benoetigt - punkte_investiert} Punkte benötigt"}

        cursor.execute("UPDATE charakter_skill_baeume SET punkte_investiert = punkte_investiert + 1 WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                       (charakter_id, masterie, baum))

        freigeschaltete.append(skill_id)
        cursor.execute("UPDATE charakter_skill_baeume SET freigeschaltete_skills = ? WHERE charakter_id = ? AND masterie = ? AND baum = ?",
                       (json.dumps(freigeschaltete), charakter_id, masterie, baum))

        cursor.execute("SELECT id FROM charakter_skills WHERE charakter_id = ? AND skill_id = ?", (charakter_id, skill_id))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO charakter_skills (charakter_id, skill_id, skill_level, ausgeruestet, nutzungen) VALUES (?, ?, 1, 0, 0)",
                           (charakter_id, skill_id))

        self.verbindung.commit()
        return {"erfolg": True, "freigeschaltet": skill_id, "skill_name": skill_def["name"]}

    def skills_laden(self, charakter_id: int) -> list[dict]:
        from spiel.systeme.skill_definitionen import ALLE_SKILLS
        import json
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT skill_id, skill_level, ausgeruestet, ausruestungs_slot, nutzungen FROM charakter_skills WHERE charakter_id = ?",
                       (charakter_id,))
        result = []
        for row in cursor.fetchall():
            skill_def = ALLE_SKILLS.get(row[0])
            if skill_def:
                result.append({
                    "skill_id": row[0],
                    "skill_level": row[1],
                    "ausgeruestet": row[2],
                    "ausruestungs_slot": row[3],
                    "nutzungen": row[4],
                    "definition": skill_def
                })
        return result

    def ausgeruestete_skills_laden(self, charakter_id: int) -> dict:
        from spiel.systeme.skill_definitionen import skill_laden
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT skill_id, slot_nummer, slot_typ
            FROM charakter_klassen_skills
            WHERE charakter_id = ? AND ausgeruestet = 1
        """, (charakter_id,))

        aktiv = [None, None, None]
        passiv = [None, None]

        for row in cursor.fetchall():
            skill_id, slot_nummer, slot_typ = row
            skill_def = skill_laden(None, skill_id)
            if not skill_def:
                continue
            if slot_typ == "aktiv" and 1 <= slot_nummer <= 3:
                aktiv[slot_nummer - 1] = {"skill_id": skill_id, "definition": skill_def}
            elif slot_typ == "passiv" and 1 <= slot_nummer <= 2:
                passiv[slot_nummer - 1] = {"skill_id": skill_id, "definition": skill_def}

        return {"aktiv": aktiv, "passiv": passiv}

    def skill_nutzung_erhoehen(self, charakter_id: int, skill_id: str) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT skill_level, nutzungen FROM charakter_skills WHERE charakter_id = ? AND skill_id = ?",
                       (charakter_id, skill_id))
        row = cursor.fetchone()
        if not row:
            return {"level_up": False, "neues_level": 1}

        skill_level = row[0]
        nutzungen = row[1]
        neue_nutzungen = nutzungen + 1

        cursor.execute("SELECT level FROM charaktere WHERE id = ?", (charakter_id,))
        char_level = cursor.fetchone()[0]

        min_level = (char_level + 4) // 5
        if skill_level < min_level:
            return {"level_up": False, "neues_level": skill_level, "min_level": min_level}

        level_faktor = 1 + (skill_level * 0.2)
        threshold = skill_level * 10 * level_faktor

        if neue_nutzungen >= threshold:
            if skill_level < 20:
                cursor.execute("UPDATE charakter_skills SET skill_level = skill_level + 1, nutzungen = 0 WHERE charakter_id = ? AND skill_id = ?",
                               (charakter_id, skill_id))
                self.verbindung.commit()
                return {"level_up": True, "neues_level": skill_level + 1}

        cursor.execute("UPDATE charakter_skills SET nutzungen = ? WHERE charakter_id = ? AND skill_id = ?",
                       (neue_nutzungen, charakter_id, skill_id))
        self.verbindung.commit()
        return {"level_up": False, "neues_level": skill_level}

    def skill_punkte_abfragen(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT skill_punkte FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

    def klasse_hinzufuegen(self, charakter_id: int, klassen_id: str, typ: str) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "INSERT INTO charakter_klassen (charakter_id, klassen_id, typ) VALUES (?, ?, ?)",
            (charakter_id, klassen_id, typ)
        )
        self.verbindung.commit()

    def nodes_laden(self, charakter_id: int, klassen_id: str) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT node_id, stufe FROM charakter_nodes
            WHERE charakter_id = ? AND klassen_id = ?
        """, (charakter_id, klassen_id))
        return {row[0]: row[1] for row in cursor.fetchall()}

    def node_stufe_laden(self, charakter_id: int, klassen_id: str, node_id: str) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT stufe FROM charakter_nodes WHERE charakter_id = ? AND klassen_id = ? AND node_id = ?",
            (charakter_id, klassen_id, node_id)
        )
        row = cursor.fetchone()
        return row[0] if row else 0

    def skill_punkte_laden(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT skill_punkte FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

    def ausgeruestete_skills_laden(self, charakter_id: int) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT skill_id, slot_nummer, slot_typ FROM charakter_klassen_skills WHERE charakter_id = ? AND ausgeruestet = 1",
            (charakter_id,)
        )
        rows = cursor.fetchall()
        ausgeruestet = {"aktiv": [], "passiv": []}
        for row in rows:
            skill_id, slot, typ = row
            if typ == "aktiv":
                ausgeruestet["aktiv"].append({"skill_id": skill_id, "slot": slot})
            else:
                ausgeruestet["passiv"].append({"skill_id": skill_id, "slot": slot})
        return ausgeruestet

    def skill_freigeschaltet(self, charakter_id: int, skill_id: str) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT 1 FROM charakter_klassen_skills WHERE charakter_id = ? AND skill_id = ?",
            (charakter_id, skill_id)
        )
        return cursor.fetchone() is not None

    def max_mana_laden(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT max_mana FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        return row[0] if row else 100

    def passiv_reserviert_laden(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(s.mana_reserviert), 0)
            FROM charakter_klassen_skills cs
            JOIN skill_definitionen s ON cs.skill_id = s.skill_id
            WHERE cs.charakter_id = ? AND cs.ausgeruestet = 1 AND cs.slot_typ = 'passiv'
        """, (charakter_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

    def klassen_laden(self, charakter_id: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT klassen_id, typ FROM charakter_klassen WHERE charakter_id = ? AND aktiv = 1",
            (charakter_id,)
        )
        return [{"klassen_id": r[0], "typ": r[1]} for r in cursor.fetchall()]

    def skill_punkte_reduzieren(self, charakter_id: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "UPDATE charaktere SET skill_punkte = skill_punkte - 1 WHERE id = ? AND skill_punkte > 0",
            (charakter_id,)
        )
        self.verbindung.commit()

    def node_skillen(self, charakter_id: int, klassen_id: str, node_id: str) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT stufe FROM charakter_nodes WHERE charakter_id = ? AND klassen_id = ? AND node_id = ?",
            (charakter_id, klassen_id, node_id)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE charakter_nodes SET stufe = stufe + 1 WHERE charakter_id = ? AND klassen_id = ? AND node_id = ?",
                (charakter_id, klassen_id, node_id)
            )
            neue_stufe = row[0] + 1
        else:
            cursor.execute(
                "INSERT INTO charakter_nodes (charakter_id, klassen_id, node_id, stufe) VALUES (?, ?, ?, 1)",
                (charakter_id, klassen_id, node_id)
            )
            neue_stufe = 1
        self.verbindung.commit()
        return {"erfolg": True, "neue_stufe": neue_stufe}

    def node_initialisieren(self, charakter_id: int, klassen_id: str, node_id: str) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "INSERT INTO charakter_nodes (charakter_id, klassen_id, node_id, stufe) VALUES (?, ?, ?, 0)",
            (charakter_id, klassen_id, node_id)
        )
        self.verbindung.commit()

    def freigeschaltete_skills_laden(self, charakter_id: int) -> list[str]:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT skill_id FROM charakter_klassen_skills WHERE charakter_id = ?",
            (charakter_id,)
        )
        return [r[0] for r in cursor.fetchall()]

    def skill_hinzufuegen(self, charakter_id: int, skill_id: str, klassen_id: str) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT id FROM charakter_klassen_skills WHERE charakter_id = ? AND skill_id = ?",
            (charakter_id, skill_id)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO charakter_klassen_skills (charakter_id, skill_id, klassen_id, skill_level, ausgeruestet, nutzungen) VALUES (?, ?, ?, 1, 0, 0)",
                (charakter_id, skill_id, klassen_id)
            )
            self.verbindung.commit()

    def skills_laden(self, charakter_id: int) -> list[dict]:
        from spiel.systeme.skill_definitionen import skill_laden
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT skill_id, klassen_id, skill_level, ausgeruestet, slot_typ, slot_nummer, nutzungen FROM charakter_klassen_skills WHERE charakter_id = ?",
            (charakter_id,)
        )
        result = []
        for row in cursor.fetchall():
            skill_def = skill_laden(row[1], row[0])
            result.append({
                "skill_id": row[0],
                "klassen_id": row[1],
                "skill_level": row[2],
                "ausgeruestet": row[3],
                "slot_typ": row[4],
                "slot_nummer": row[5],
                "nutzungen": row[6],
                "definition": skill_def
            })
        return result

    def skill_ausruesten(self, charakter_id: int, skill_id: str, slot_typ: str, slot_nummer: int) -> dict:
        cursor = self.verbindung.cursor()

        cursor.execute("UPDATE charakter_klassen_skills SET ausgeruestet = 0, slot_typ = NULL, slot_nummer = NULL WHERE charakter_id = ? AND slot_typ = ? AND slot_nummer = ?",
                       (charakter_id, slot_typ, slot_nummer))

        cursor.execute("UPDATE charakter_klassen_skills SET ausgeruestet = 1, slot_typ = ?, slot_nummer = ? WHERE charakter_id = ? AND skill_id = ?",
                       (slot_typ, slot_nummer, charakter_id, skill_id))

        self.verbindung.commit()
        return {"erfolg": True, "nachricht": "Skill ausgerüstet"}

    def skill_ablegen(self, charakter_id: int, skill_id: str) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE charakter_klassen_skills SET ausgeruestet = 0, slot_typ = NULL, slot_nummer = NULL WHERE charakter_id = ? AND skill_id = ?",
                       (charakter_id, skill_id))
        self.verbindung.commit()
        return {"erfolg": True, "nachricht": "Skill abgelegt"}

    def reise_starten(self, charakter_id: int, max_dauer: int = 14400) -> int | None:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT id FROM charakter_reisen WHERE charakter_id = ? AND aktiv = 1", (charakter_id,))
        if cursor.fetchone():
            return None
        cursor.execute(
            "INSERT INTO charakter_reisen (charakter_id, gestartet_am, aktiv, max_dauer) VALUES (?, ?, 1, ?)",
            (charakter_id, datetime.now().isoformat(), max_dauer)
        )
        self.verbindung.commit()
        return cursor.lastrowid

    def reise_laden(self, charakter_id: int) -> dict | None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "SELECT id, charakter_id, gestartet_am, aktiv, max_dauer FROM charakter_reisen WHERE charakter_id = ? AND aktiv = 1",
            (charakter_id,)
        )
        reise = cursor.fetchone()
        if not reise:
            return None
        cursor.execute(
            "SELECT id, quest_json, kampf_ergebnis_json, quest_zeit, belohnung_gold, belohnung_xp, abgeholt FROM reise_quests WHERE reise_id = ? ORDER BY quest_zeit ASC",
            (reise["id"],)
        )
        quests = []
        for q in cursor.fetchall():
            quests.append({
                "id": q["id"],
                "quest_json": json.loads(q["quest_json"]) if q["quest_json"] else None,
                "kampf_ergebnis_json": json.loads(q["kampf_ergebnis_json"]) if q["kampf_ergebnis_json"] else None,
                "quest_zeit": q["quest_zeit"],
                "belohnung_gold": q["belohnung_gold"],
                "belohnung_xp": q["belohnung_xp"],
                "abgeholt": q["abgeholt"]
            })
        max_dauer = 14400
        try:
            max_dauer = reise["max_dauer"] if reise["max_dauer"] else 14400
        except (KeyError, IndexError):
            pass

        return {
            "id": reise["id"],
            "charakter_id": reise["charakter_id"],
            "gestartet_am": reise["gestartet_am"],
            "aktiv": reise["aktiv"],
            "max_dauer": max_dauer,
            "quests": quests
        }

    def reise_beenden(self, reise_id: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE charakter_reisen SET aktiv = 0 WHERE id = ?", (reise_id,))
        self.verbindung.commit()

    def reise_quest_hinzufuegen(self, reise_id: int, quest: dict, quest_zeit: str) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "INSERT INTO reise_quests (reise_id, quest_json, quest_zeit) VALUES (?, ?, ?)",
            (reise_id, json.dumps(quest), quest_zeit)
        )
        self.verbindung.commit()

    def reise_quest_ergebnis_speichern(self, reise_quest_id: int, kampf_json: dict, gold: int, xp: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute(
            "UPDATE reise_quests SET kampf_ergebnis_json = ?, belohnung_gold = ?, belohnung_xp = ? WHERE id = ?",
            (json.dumps(kampf_json), gold, xp, reise_quest_id)
        )
        self.verbindung.commit()

    def offene_reise_belohnungen(self, charakter_id: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT rq.id, rq.quest_json, rq.kampf_ergebnis_json, rq.belohnung_gold, rq.belohnung_xp, rq.abgeholt
            FROM reise_quests rq
            JOIN charakter_reisen cr ON rq.reise_id = cr.id
            WHERE cr.charakter_id = ? AND rq.kampf_ergebnis_json IS NOT NULL AND rq.abgeholt = 0
            ORDER BY rq.quest_zeit ASC
        """, (charakter_id,))
        result = []
        for q in cursor.fetchall():
            result.append({
                "id": q["id"],
                "quest_json": json.loads(q["quest_json"]),
                "kampf_ergebnis_json": json.loads(q["kampf_ergebnis_json"]),
                "belohnung_gold": q["belohnung_gold"],
                "belohnung_xp": q["belohnung_xp"],
                "abgeholt": q["abgeholt"]
            })
        return result

    def reise_belohnungen_abholen(self, charakter_id: int) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT rq.belohnung_gold, rq.belohnung_xp
            FROM reise_quests rq
            JOIN charakter_reisen cr ON rq.reise_id = cr.id
            WHERE cr.charakter_id = ? AND rq.kampf_ergebnis_json IS NOT NULL AND rq.abgeholt = 0
        """, (charakter_id,))
        gesamt_gold = 0
        gesamt_xp = 0
        for row in cursor.fetchall():
            gesamt_gold += row["belohnung_gold"]
            gesamt_xp += row["belohnung_xp"]
        cursor.execute("""
            UPDATE reise_quests SET abgeholt = 1
            WHERE id IN (
                SELECT rq.id FROM reise_quests rq
                JOIN charakter_reisen cr ON rq.reise_id = cr.id
                WHERE cr.charakter_id = ? AND rq.kampf_ergebnis_json IS NOT NULL AND rq.abgeholt = 0
            )
        """, (charakter_id,))
        cursor.execute("UPDATE charaktere SET gold = gold + ? WHERE id = ?", (gesamt_gold, charakter_id))
        cursor.execute("UPDATE charaktere SET erfahrung = erfahrung + ? WHERE id = ?", (gesamt_xp, charakter_id))
        self.verbindung.commit()
        return {"gold": gesamt_gold, "xp": gesamt_xp}

    def traeanke_laden(self, charakter_id: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT id, stat, stufe, bonus, aktiv_bis
            FROM charakter_traenke
            WHERE charakter_id = ?
            ORDER BY aktiv_bis ASC
        """, (charakter_id,))
        return [{"id": row["id"], "stat": row["stat"], "stufe": row["stufe"],
                 "bonus": row["bonus"], "aktiv_bis": row["aktiv_bis"]}
                for row in cursor.fetchall()]

    def trank_hinzufuegen(self, charakter_id: int, trank_id: str, stat: str,
                          stufe: str, bonus: float, aktiv_bis: str) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("""
                INSERT INTO charakter_traenke (id, charakter_id, stat, stufe, bonus, aktiv_bis)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (trank_id, charakter_id, stat, stufe, bonus, aktiv_bis))
            self.verbindung.commit()
            return True
        except Exception:
            return False

    def abgelaufene_traenke_entfernen(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        cursor.execute("""
            DELETE FROM charakter_traenke
            WHERE charakter_id = ? AND aktiv_bis < ?
        """, (charakter_id, jetzt))
        anzahl = cursor.rowcount
        self.verbindung.commit()
        return anzahl

    def trank_aktiv_fuer_stat(self, charakter_id: int, stat: str) -> bool:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM charakter_traenke
            WHERE charakter_id = ? AND stat = ? AND aktiv_bis >= ?
        """, (charakter_id, stat, jetzt))
        return cursor.fetchone()[0] > 0

    def trank_entfernen(self, charakter_id: int, trank_id: str) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("""
                DELETE FROM charakter_traenke
                WHERE id = ? AND charakter_id = ?
            """, (trank_id, charakter_id))
            self.verbindung.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

    def aktive_trank_anzahl(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM charakter_traenke
            WHERE charakter_id = ? AND aktiv_bis >= ?
        """, (charakter_id, jetzt))
        return cursor.fetchone()[0]

    def gold_abziehen(self, charakter_id: int, gold: int) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT gold FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        if row and row["gold"] >= gold:
            cursor.execute("UPDATE charaktere SET gold = gold - ? WHERE id = ?", (gold, charakter_id))
            self.verbindung.commit()
            return True
        return False

    def shop_laden(self, charakter_id: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        cursor.execute("""
            SELECT id, slot, typ, inhalt_json, preis, gekauft, gueltig_bis
            FROM shop_angebote
            WHERE charakter_id = ? AND gueltig_bis > ? AND gekauft = 0
            ORDER BY slot ASC
        """, (charakter_id, jetzt))
        result = []
        for row in cursor.fetchall():
            result.append({
                "id": row["id"],
                "slot": row["slot"],
                "typ": row["typ"],
                "inhalt": json.loads(row["inhalt_json"]),
                "preis": row["preis"],
                "gueltig_bis": row["gueltig_bis"]
            })
        return result

    def shop_generieren(self, charakter_id: int, angebote: list[dict], gueltig_bis: str) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("DELETE FROM shop_angebote WHERE charakter_id = ?", (charakter_id,))
        cursor.execute("""
            INSERT INTO shop_angebote (charakter_id, slot, typ, inhalt_json, preis, generiert_am, gueltig_bis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (charakter_id, 0, "temp", "{}", 0, datetime.now().isoformat(), gueltig_bis))
        cursor.execute("DELETE FROM shop_angebote WHERE charakter_id = ?", (charakter_id,))
        for angebot in angebote:
            cursor.execute("""
                INSERT INTO shop_angebote (charakter_id, slot, typ, inhalt_json, preis, generiert_am, gueltig_bis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (charakter_id, angebot["slot"], angebot["typ"],
                  json.dumps(angebot["inhalt"]), angebot["preis"],
                  datetime.now().isoformat(), gueltig_bis))
        self.verbindung.commit()
        return angebote

    def shop_angebot_kaufen(self, charakter_id: int, slot: int) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            UPDATE shop_angebote SET gekauft = 1
            WHERE charakter_id = ? AND slot = ? AND gekauft = 0
        """, (charakter_id, slot))
        self.verbindung.commit()
        return cursor.rowcount > 0

    def reroll_anzahl_laden(self, charakter_id: int) -> int:
        cursor = self.verbindung.cursor()
        heute = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT anzahl_heute, letzter_reset FROM shop_rerolls WHERE charakter_id = ?
        """, (charakter_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                INSERT INTO shop_rerolls (charakter_id, anzahl_heute, letzter_reset)
                VALUES (?, 0, ?)
            """, (charakter_id, heute))
            self.verbindung.commit()
            return 0
        if row["letzter_reset"] != heute:
            cursor.execute("""
                UPDATE shop_rerolls SET anzahl_heute = 0, letzter_reset = ? WHERE charakter_id = ?
            """, (heute, charakter_id))
            self.verbindung.commit()
            return 0
        return row["anzahl_heute"]

    def reroll_erhoehen(self, charakter_id: int) -> None:
        cursor = self.verbindung.cursor()
        heute = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE shop_rerolls SET anzahl_heute = anzahl_heute + 1, letzter_reset = ?
            WHERE charakter_id = ?
        """, (heute, charakter_id))
        self.verbindung.commit()

    def naechste_mitternacht(self) -> str:
        jetzt = datetime.now()
        morgen = jetzt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return morgen.isoformat()

    def arena_stats_laden(self, charakter_id: int) -> dict:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM arena_stats WHERE charakter_id = ?", (charakter_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                INSERT INTO arena_stats (charakter_id, rang_punkte, siege, niederlagen, ehrenmarken)
                VALUES (?, 0, 0, 0, 0)
            """, (charakter_id,))
            self.verbindung.commit()
            return {"charakter_id": charakter_id, "rang_punkte": 0, "siege": 0, "niederlagen": 0, "ehrenmarken": 0}
        return {
            "charakter_id": row["charakter_id"],
            "rang_punkte": row["rang_punkte"],
            "siege": row["siege"],
            "niederlagen": row["niederlagen"],
            "ehrenmarken": row["ehrenmarken"]
        }

    def arena_stats_aktualisieren(self, charakter_id: int, rang_delta: int, gewonnen: bool, gold: int, xp: int, marken: int) -> None:
        cursor = self.verbindung.cursor()
        neue_punkte = max(0, self.arena_stats_laden(charakter_id)["rang_punkte"] + rang_delta)
        siege_delta = 1 if gewonnen else 0
        niederlagen_delta = 0 if gewonnen else 1
        cursor.execute("""
            UPDATE arena_stats SET
                rang_punkte = ?,
                siege = siege + ?,
                niederlagen = niederlagen + ?,
                ehrenmarken = ehrenmarken + ?
            WHERE charakter_id = ?
        """, (neue_punkte, siege_delta, niederlagen_delta, marken, charakter_id))
        self.verbindung.commit()

    def arena_gegner_suchen(self, charakter_id: int, charakter_level: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        level_min = charakter_level - 5
        level_max = charakter_level + 5

        cursor.execute("""
            SELECT charakter_id, snapshot_json
            FROM charakter_snapshots
            WHERE charakter_id != ? AND json_extract(snapshot_json, '$.level') BETWEEN ? AND ?
            ORDER BY RANDOM() LIMIT 10
        """, (charakter_id, level_min, level_max))

        gegner = []
        for row in cursor.fetchall():
            if len(gegner) >= 3:
                break
            try:
                snapshot = json.loads(row["snapshot_json"])
                snapshot["charakter_id"] = row["charakter_id"]
                gegner.append(snapshot)
            except:
                pass

        if len(gegner) < 3:
            level_min = charakter_level - 10
            level_max = charakter_level + 10
            cursor.execute("""
                SELECT charakter_id, snapshot_json
                FROM charakter_snapshots
                WHERE charakter_id != ? AND json_extract(snapshot_json, '$.level') BETWEEN ? AND ?
                ORDER BY RANDOM() LIMIT 10
            """, (charakter_id, level_min, level_max))

            for row in cursor.fetchall():
                if len(gegner) >= 3:
                    break
                try:
                    snapshot = json.loads(row["snapshot_json"])
                    snapshot["charakter_id"] = row["charakter_id"]
                    gegner.append(snapshot)
                except:
                    pass

        return gegner

    def arena_kampf_speichern(self, angreifer_id: int, verteidiger_id: int, gewonnen: int, rang_delta: int, gold: int, xp: int, marken: int) -> None:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO arena_kaempfe (angreifer_id, verteidiger_id, gewonnen, rang_aenderung, gold_belohnung, xp_belohnung, marken_belohnung, gekämpft_am)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (angreifer_id, verteidiger_id, gewonnen, rang_delta, gold, xp, marken, jetzt))
        self.verbindung.commit()

    def item_verzaubern(self, item_id: str, charakter_id: int) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM item_verzauberungen WHERE item_id = ?", (item_id,))
        if cursor.fetchone():
            return False
        jetzt = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO item_verzauberungen (item_id, charakter_id, verstaerkung, erstellt_am)
            VALUES (?, ?, 1.15, ?)
        """, (item_id, charakter_id, jetzt))
        self.verbindung.commit()

    def gilde_erstellen(self, name: str, beschreibung: str, gildenmeister_charakter_id: int) -> int | None:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        try:
            cursor.execute("""
                INSERT INTO gilden (name, beschreibung, erstellt_am, mitglieder_anzahl)
                VALUES (?, ?, ?, 1)
            """, (name, beschreibung, jetzt))
            gilden_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO gilde_mitglieder (charakter_id, gilden_id, rang, beigetreten_am)
                VALUES (?, ?, 'gildenmeister', ?)
            """, (gildenmeister_charakter_id, gilden_id, jetzt))
            self.verbindung.commit()
            return gilden_id
        except:
            return None

    def gilde_laden(self, gilden_id: int) -> dict | None:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM gilden WHERE id = ?", (gilden_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "beschreibung": row["beschreibung"],
            "erstellt_am": row["erstellt_am"],
            "kasse": row["kasse"],
            "steuer": row["steuer"],
            "xp_bonus": row["xp_bonus"],
            "gold_bonus": row["gold_bonus"],
            "mitglieder_anzahl": row["mitglieder_anzahl"]
        }

    def gilde_laden_by_name(self, name: str) -> dict | None:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM gilden WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "beschreibung": row["beschreibung"],
            "erstellt_am": row["erstellt_am"],
            "kasse": row["kasse"],
            "steuer": row["steuer"],
            "xp_bonus": row["xp_bonus"],
            "gold_bonus": row["gold_bonus"],
            "mitglieder_anzahl": row["mitglieder_anzahl"]
        }

    def gilde_mitglied_laden(self, charakter_id: int) -> dict | None:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM gilde_mitglieder WHERE charakter_id = ?", (charakter_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "charakter_id": row["charakter_id"],
            "gilden_id": row["gilden_id"],
            "rang": row["rang"],
            "beigetreten_am": row["beigetreten_am"]
        }

    def gilde_beitreten(self, charakter_id: int, gilden_id: int) -> bool:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        try:
            cursor.execute("""
                INSERT INTO gilde_mitglieder (charakter_id, gilden_id, rang, beigetreten_am)
                VALUES (?, ?, 'mitglied', ?)
            """, (charakter_id, gilden_id, jetzt))
            cursor.execute("UPDATE gilden SET mitglieder_anzahl = mitglieder_anzahl + 1 WHERE id = ?", (gilden_id,))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilde_verlassen(self, charakter_id: int) -> bool:
        cursor = self.verbindung.cursor()
        mitglied = self.gilde_mitglied_laden(charakter_id)
        if not mitglied:
            return False
        try:
            cursor.execute("DELETE FROM gilde_mitglieder WHERE charakter_id = ?", (charakter_id,))
            cursor.execute("UPDATE gilden SET mitglieder_anzahl = mitglieder_anzahl - 1 WHERE id = ?", (mitglied["gilden_id"],))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilde_mitglieder_laden(self, gilden_id: int) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT gm.*, c.name, c.level, c.masterie_1 as klasse
            FROM gilde_mitglieder gm
            JOIN charaktere c ON c.id = gm.charakter_id
            WHERE gm.gilden_id = ?
        """, (gilden_id,))
        mitglieder = []
        for row in cursor.fetchall():
            mitglieder.append({
                "charakter_id": row["charakter_id"],
                "gilden_id": row["gilden_id"],
                "rang": row["rang"],
                "beigetreten_am": row["beigetreten_am"],
                "name": row["name"],
                "level": row["level"],
                "klasse": row["klasse"]
            })
        return mitglieder

    def gilde_steuer_setzen(self, gilden_id: int, steuer: int) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("UPDATE gilden SET steuer = ? WHERE id = ?", (steuer, gilden_id))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilde_kasse_einzahlen(self, gilden_id: int, betrag: int) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("UPDATE gilden SET kasse = kasse + ? WHERE id = ?", (betrag, gilden_id))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilde_stufe_erhoehen(self, gilden_id: int) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("SELECT stufe FROM gilden WHERE id = ?", (gilden_id,))
            row = cursor.fetchone()
            if not row:
                return False
            neue_stufe = row[0] + 1
            xp_bonus = neue_stufe * 0.05
            gold_bonus = neue_stufe * 0.05
            cursor.execute("""
                UPDATE gilden SET stufe = ?, xp_bonus = ?, gold_bonus = ? WHERE id = ?
            """, (neue_stufe, xp_bonus, gold_bonus, gilden_id))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilde_log_hinzufuegen(self, gilden_id: int, charakter_name: str, aktion: str) -> bool:
        cursor = self.verbindung.cursor()
        jetzt = datetime.now().isoformat()
        try:
            cursor.execute("""
                INSERT INTO gilde_log (gilden_id, charakter_name, aktion, erstellt_am)
                VALUES (?, ?, ?, ?)
            """, (gilden_id, charakter_name, aktion, jetzt))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilde_log_laden(self, gilden_id: int, limit: int = 20) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("""
            SELECT * FROM gilde_log WHERE gilden_id = ? ORDER BY erstellt_am DESC LIMIT ?
        """, (gilden_id, limit))
        log = []
        for row in cursor.fetchall():
            log.append({
                "id": row["id"],
                "gilden_id": row["gilden_id"],
                "charakter_name": row["charakter_name"],
                "aktion": row["aktion"],
                "erstellt_am": row["erstellt_am"]
            })
        return log

    def gilde_rang_setzen(self, gilden_id: int, charakter_id: int, rang: str) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("UPDATE gilde_mitglieder SET rang = ? WHERE charakter_id = ? AND gilden_id = ?",
                          (rang, charakter_id, gilden_id))
            self.verbindung.commit()
            return True
        except:
            return False

    def gilden_liste_laden(self, limit: int = 20) -> list[dict]:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT * FROM gilden ORDER BY mitglieder_anzahl DESC LIMIT ?", (limit,))
        gilden = []
        for row in cursor.fetchall():
            gilden.append({
                "id": row["id"],
                "name": row["name"],
                "beschreibung": row["beschreibung"],
                "mitglieder_anzahl": row["mitglieder_anzahl"],
                "kasse": row["kasse"],
                "steuer": row["steuer"]
            })
        return gilden

    def gilde_mitglied_kicken(self, gilden_id: int, charakter_id: int) -> bool:
        cursor = self.verbindung.cursor()
        try:
            cursor.execute("DELETE FROM gilde_mitglieder WHERE charakter_id = ? AND gilden_id = ?", (charakter_id, gilden_id))
            cursor.execute("UPDATE gilden SET mitglieder_anzahl = mitglieder_anzahl - 1 WHERE id = ?", (gilden_id,))
            self.verbindung.commit()
            return True
        except:
            return False
        return True

    def item_ist_verzaubert(self, item_id: str) -> bool:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT verstaerkung FROM item_verzauberungen WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        return row is not None

    def ehrenmarken_abziehen(self, charakter_id: int, anzahl: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE arena_stats SET ehrenmarken = ehrenmarken - ? WHERE charakter_id = ?", (anzahl, charakter_id))
        self.verbindung.commit()

    def gold_hinzufuegen(self, charakter_id: int, gold: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute("UPDATE charaktere SET gold = gold + ? WHERE id = ?", (gold, charakter_id))
        self.verbindung.commit()

    def xp_hinzufuegen(self, charakter_id: int, xp: int) -> None:
        cursor = self.verbindung.cursor()
        cursor.execute("SELECT erfahrung FROM charaktere WHERE id = ?", (charakter_id,))
        row = cursor.fetchone()
        if row:
            neue_xp = row["erfahrung"] + xp
            cursor.execute("UPDATE charaktere SET erfahrung = ? WHERE id = ?", (neue_xp, charakter_id))
            self.verbindung.commit()


def passwort_hashen(passwort: str) -> str:
    return bcrypt.hashpw(passwort.encode(), bcrypt.gensalt()).decode()


def passwort_pruefen(passwort: str, gespeicherter_hash: str) -> bool:
    return bcrypt.checkpw(passwort.encode(), gespeicherter_hash.encode())
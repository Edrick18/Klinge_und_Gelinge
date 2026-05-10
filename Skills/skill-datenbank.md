---
name: skill-datenbank
description: >
  Muss konsultiert werden BEVOR Datenbankcode geschrieben wird.
  Trigger: "SQLite", "Datenbank speichern", "Persistenz", "CRUD-Operationen",
  "Passwort hash", "Datenbank-Tabelle erstellen".
---

# skill-datenbank

Regeln für Datenbankzugriff und Persistenz im Projekt.

---

## Verzeichnisstruktur

| Komponente | Pfad |
|------------|------|
| Datenbank-Klasse | `server/datenbank/datenbank.py` |
| Datenbank-Datei | `server/datenbank/spieldaten.db` |

**Wichtig:** Datenbankdatei in `.gitignore` eintragen.

---

## SQLite-Entscheidungen

```
Datenbank-Operation?
  → Lesen: cursor.execute() → fetchone()/fetchall()
  → Schreiben: execute() → connection.commit()
  → Fehlerbehandlung: try/except mit rollback()

Neue Tabelle?
  → Immer "IF NOT EXISTS" verwenden
  → Primärschlüssel als erstes Feld
  → Fremdschlüssel mit REFERENCES
```

---

## Passwort-Sicherheit

```
Passwort speichern?
  → Niemals im Klartext!
  → Immer bcrypt: hash = bcrypt.hashpw(passwort.encode(), bcrypt.gensalt())
  → Login-Prüfung: bcrypt.checkpw(passwort.encode(), gespeicherter_hash)
```

---

## Import-Reihenfolge

Stdlib → Third-party → Lokal:
```python
import sqlite3, bcrypt
from server.datenbank.datenbank import Datenbank
```

---

## Transaktionen

| Situation | Regel |
|-----------|-------|
| Einzelne Operation | Automatisch commit |
| Mehrere Operationen | Alle ausführen, dann einmal commit |
| Fehler | `connection.rollback()` vor neuem Versuch |

---

## Datenmodell-Entscheidungen

```
Neue Tabelle erstellen?
  → Erst prüfen ob Spalte in bestehender Tabelle möglich
  → JSON für flexible Daten (z.B. item_json)
  → INTEGER für IDs, TEXT für Namen
  → timestamp als ISO-String speichern
```

---

## Pflichtprüfung

- [x] Enthält der Skill nur Regeln, keine Daten oder Werte?
- [x] Ist er unter 200 Zeilen?
- [x] Hat er mindestens einen Entscheidungsbaum oder eine Tabelle?
- [x] Ist der Trigger in `description` spezifisch genug?
- [x] Ist er in `skill-übersicht.md` eingetragen?
- [x] Gibt es Konflikte mit anderen Skills?
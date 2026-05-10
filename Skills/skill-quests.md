---
name: skill-quests
description: >
  Muss konsultiert werden BEVOR Quest-Code geschrieben wird.
  Trigger: "Quest generieren", "Taverne", "Quest annehmen", "Quest auflösen",
  "Quest-Belohnung", "Quest-Timer".
---

# skill-quests

Regeln für das Quest-System im Projekt.

---

## Grundprinzipien

| Prinzip | Entscheidung |
|---------|--------------|
| Wo generiert? | Server-seitig in `quest_generator.py` |
| Quest-Anzahl | 3 Quests pro Spieler (individuell) |
| Timer-Prüfung | Server prüft Ablauf, Client zeigt Fortschritt |
| Belohnung | Erst nach Auflösung gutgeschrieben |
| Regenerierung | Nach Abschluss neu generieren |

---

## Verzeichnisstruktur

| Komponente | Pfad |
|------------|------|
| Quest-Generierung | `server/logik/quest_generator.py` |
| Quest-Logik | `server/logik/quest_verwaltung.py` |
| Quest-Gegner | `server/logik/test_gegner.py` |
| Quest-Datenbank | `server/datenbank/datenbank.py` (Tabelle: quests) |

---

## Quest-Generierung Entscheidungen

```
Neue Quest generieren?
  → Rarität würfeln: normal (60%), selten (25%), episch (12%), legendaer (3%)
  → Schwierigkeit berechnen: Rarität multipliziert mit Basis
  → Timer setzen: Normal 3-5 Min, Selten 5-8 Min, Episch 8-12 Min, Legendär 12-20 Min
  → Belohnung berechnen: Gold = Level * Schwierigkeit * Basis, XP = Gold * 2

Quest-Typ wählen?
  → Kampfquest: Gegner aus quest_generator
  → Sammelquest: Items sammeln (später)
  → Exploration: Ort erreichen (später)
```

---

## Quest-Ablauf Entscheidungen

```
Quest anbieten (Taverne)?
  → 3 aktive Quests aus Datenbank laden
  → Abgelaufene Quests: neu generieren
  → Timer laufend: Client aktualisieren

Quest annehmen?
  → quest_id speichern, gestartet_am setzen
  → Quest-Kampf starten möglich

Quest auflösen?
  → Kampfsieg: Belohnung berechnen und gutschreiben
  → Kampfniederlage: Keine Belohnung
  → Quest als abgeschlossen markieren
  → Neue Quest generieren
```

---

## Import-Reihenfolge

Stdlib → Third-party → Lokal:
```python
import uuid, json, datetime
from server.logik.quest_verwaltung import QuestVerwaltung
from server.datenbank.datenbank import Datenbank
```

---

## Pflichtprüfung

- [x] Enthält der Skill nur Regeln, keine Daten oder Werte?
- [x] Ist er unter 200 Zeilen?
- [x] Hat er mindestens einen Entscheidungsbaum oder eine Tabelle?
- [x] Ist der Trigger in `description` spezifisch genug?
- [x] Ist er in `skill-übersicht.md` eingetragen?
- [x] Gibt es Konflikte mit anderen Skills?
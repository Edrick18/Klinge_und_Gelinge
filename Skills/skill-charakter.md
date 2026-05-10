---
name: skill-charakter
description: >
  Muss konsultiert werden BEVOR Charakter-Code geschrieben wird.
  Trigger: "Charakter erstellen", "Charakterauswahl", "Stats verteilen",
  "Masterie wählen", "Charakter speichern".
---

# skill-charakter

Regeln für Charaktersystem und Spielermechanik im Projekt.

---

## Grundprinzipien

| Prinzip | Entscheidung |
|---------|--------------|
| Wo gespeichert? | Server-seitig, Client hat nur ID |
| Stats berechnet? | Server-seitig in `stat_berechnung.py` |
| Masterie-Effekt? | Immer Server-seitig berechnen |
| Level-Up? | Server-seitig, XP + Gold gutschreiben |

---

## Verzeichnisstruktur

| Komponente | Pfad |
|------------|------|
| Charakter-Logik | `server/logik/charakter_verwaltung.py` |
| Stat-Berechnung | `spiel/systeme/stat_berechnung.py` |
| Charakter-Datenbank | `server/datenbank/datenbank.py` (Tabelle: charaktere) |

---

## Masterie-Entscheidungen

```
Masterie wählen?
  → 6 Optionen: staerke, vitalitaet, weisheit, glueck, beweglichkeit, charisma
  → Zwei Masterien pro Charakter möglich
  → Effekt: Jede Masterie erhöht einen Grundwert

Masterie-Effekt anwenden?
  → staerke → TP (Trefferpunkte)
  → vitalitaet → HP-Maximum
  → weisheit → Mana
  → glueck → Kritische Trefferchance
  → beweglichkeit → Initiative
  → charisma → XP-Bonus
```

---

## Stat-Verteilung Entscheidungen

```
Stats verteilen?
  → Basis-Wert: 10 (für alle gleich)
  → Verteilbare Punkte: 20
  → Min pro Wert: 10, Max pro Wert: 25
  → Summe: 60 (Basis) + 20 (verteilt) = 80

Stat bei Level-Up erhöhen?
  → Automatisch +1 auf zufälligen Stat oder nach Wahl?
  → Automatisch +1 auf Masterie-relevanten Stat
```

---

## Charakter-Erstellung Entscheidungen

```
Neuen Charakter erstellen?
  → Name prüfen: nicht leer, nicht doppelt
  → Masterie wählen: 2 Primär-Masterien
  → Stats verteilen: 20 Punkte auf 6 Stats
  → Speichern: Datenbank, ID zurückgeben

Charakter auswählen?
  → Alle Charaktere des Spielers laden
  → Beim Auswählen: aktiver_charakter_id setzen
  → Snapshot erstellen für Kampf
```

---

## Speicher-Entscheidungen

```
Charakter speichern?
  → Server-seitig in Datenbank
  → JSON für flexible Felder (stats als JSON)
  → Automatisch nach Änderungen

Charakter laden?
  → Nur bei Auswahl oder needed
  → Niemals komplett im Client speichern
```

---

## Import-Reihenfolge

Stdlib → Third-party → Lokal:
```python
import json, re
from server.datenbank.datenbank import Datenbank
from server.logik.charakter_verwaltung import CharakterVerwaltung
```

---

## Pflichtprüfung

- [x] Enthält der Skill nur Regeln, keine Daten oder Werte?
- [x] Ist er unter 200 Zeilen?
- [x] Hat er mindestens einen Entscheidungsbaum oder eine Tabelle?
- [x] Ist der Trigger in `description` spezifisch genug?
- [x] Ist er in `skill-übersicht.md` eingetragen?
- [x] Gibt es Konflikte mit anderen Skills?
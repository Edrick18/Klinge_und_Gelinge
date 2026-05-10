---
name: skill-kampfsystem
description: >
  Muss konsultiert werden BEVOR Kampfcode geschrieben wird.
  Trigger: "Kampf berechnen", "Auto-Combat", "Kampf-Engine", "Schaden berechnen",
  "Kampf-Log", "Kampfanimation".
---

# skill-kampfsystem

Regeln für das Kampfsystem im Projekt.

---

## Grundprinzipien

| Prinzip | Entscheidung |
|---------|--------------|
| Wo berechnet? | Server-seitig in `kampf_engine.py` |
| Zeitsteuerung | Vorherberechnung komplett, dann Client zeigt |
| Zufallssteuerung | Seed aus charakter_id + timestamp |
| Client-Rolle | Animation des vorberechneten Logs |

---

## Verzeichnisstruktur

| Komponente | Pfad |
|------------|------|
| Kampf-Engine | `server/logik/kampf_engine.py` |
| Testgegner | `server/logik/test_gegner.py` |
| Kampf-Anzeige | `spiel/szenen/kampf_anzeige_szene.py` |

---

## Kampf-Entscheidungen

```
Kampf starten?
  → Seed setzen: random.seed(charakter_id + unix_timestamp)
  → Spieler und Gegner laden
  → Schleife bis HP <= 0 oder Zeit abgelaufen
  → Ereignis-Log sammeln

Angriff berechnen?
  → Basis-Schaden = (Att * 2 - Verteidigung) * multiplier
  → Krit-Würfel: random.random() < crit_chance
  → Bonus: Fäule mechanic (später)

Kampf beenden?
  → Gewonnen: Gewinn-Log + Belohnung berechnen
  → Verloren: Verlust-Log, keine Belohnung
  → Ergebnis-Log zurückgeben
```

---

## Client-Entscheidungen

```
Kampf anzeigen?
  → Log-Ereignisse der Reihe nach abspielen
  → Zeit zwischen Ereignissen = delta in Log
  → HP-Balken animieren (smooth interpolation)
  → Keine Berechnungen im Client!

Kampf abbrechen?
  → Nicht erlaubt bei Auto-Combat
  → Zurück-Button deaktivieren während Kampf
```

---

## Import-Reihenfolge

Stdlib → Third-party → Lokal:
```python
import random, secrets, json
from server.logik.kampf_engine import KampfEngine
from server.logik.test_gegner import testkampfer_erstellen
```

---

## Pflichtprüfung

- [x] Enthält der Skill nur Regeln, keine Daten oder Werte?
- [x] Ist er unter 200 Zeilen?
- [x] Hat er mindestens einen Entscheidungsbaum oder eine Tabelle?
- [x] Ist der Trigger in `description` spezifisch genug?
- [x] Ist er in `skill-übersicht.md` eingetragen?
- [x] Gibt es Konflikte mit anderen Skills?
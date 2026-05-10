---
name: skill-items
description: >
  Muss konsultiert werden BEVOR Item-Code geschrieben wird.
  Trigger: "Item generieren", "Quest-Belohnung", "Item-Drop", "Inventar",
  "Rarität", "Affix", "Item-Slot".
---

# skill-items

Regeln für das Item-System im Projekt.

---

## Grundprinzipien

| Prinzip | Entscheidung |
|---------|--------------|
| Wo generiert? | Server-seitig in `server/logik/item_generator.py` |
| Was beeinflusst Rarität? | Zufall + Quest-Schwierigkeit |
| Wer legt Stats fest? | Server, basierend auf Item-Level |
| Client-Rolle? | Nur Anzeige, keine Generierung |

---

## Verzeichnisstruktur

| Komponente | Pfad |
|------------|------|
| Item-Generierung | `server/logik/item_generator.py` |
| Item-Konstanten | `spiel/systeme/item_typen.py` |
| Item-Datenbank | `server/datenbank/datenbank.py` (Tabelle: inventar) |

---

## Item-Typ Entscheidungen

```
Neues Item generieren?
  → Typ wählen: Waffe, Rüstung, Schmuck, Verbrauch
  → Slot bestimmen: helm, brust, handschuhe, schuhe, amulett, ring_1, ring_2, waffe, offhand
  → Level setzen: aus Quest-Level oder Charakter-Level
  → Rarität würfeln: normal (60%), magisch (25%), selten (10%), episch (4%), legendaer (1%)
```

---

## Affix-Entscheidungen

```
Affix hinzufügen?
  → Rarität = normal: Keine Affixe
  → Rarität = magisch: 1 Prefix + 1 Suffix
  → Rarität = selten: 2 Prefixe + 2 Suffixe
  → Rarität = episch: 3 Prefixe + 3 Suffixe
  → Rarität = legendaer: 4 Prefixe + 4 Suffixe

Affix-Typ wählen?
  → Stat-Typ: staerke, vitalitaet, weisheit, glueck, beweglichkeit, charisma
  → Präfix: +Stat, +Schaden, +HP
  → Suffix: +Krit, +Ausweichen, +Resistenz
```

---

## Item-Daten-Entscheidungen

```
Item speichern?
  → JSON in Datenbank: item_json als Text
  → Felder: id (UUID), charakter_id, item_json, ausgeruestet, slot

Item laden?
  → JSON parsen aus Datenbank
  → Stats berechnen aus basis_stats + prefixe + suffixe
```

---

## Import-Reihenfolge

Stdlib → Third-party → Lokal:
```python
import uuid, random, json
from spiel.systeme.item_typen import ...
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
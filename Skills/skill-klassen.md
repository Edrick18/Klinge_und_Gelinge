---
name: skill-klassen
description: >
  Muss konsultiert werden BEVOR Klassen, Masterien, Skill-Bäume oder
  Kern-Mechaniken implementiert werden. Regelt wie das Klassen-System
  aufgebaut ist, wo Daten liegen und wie Entscheidungen getroffen werden.
  Trigger: Klasse implementieren, Skill-Baum bauen, Kern-Mechanik hinzufügen,
  Masterie-System erweitern.
---

# skill-klassen

Regelt die Struktur des zweistufigen Masterie-Systems und der Skill-Bäume.
Konkrete Klassen-Daten (Namen, Werte, Nodes) liegen in `spiel/daten/klassen.json`.

---

## Zweistufiges Masterie-System

```
Stufe 1 (Charaktererstellung): Basis-Klasse wählen
  → 6 Basis-Klassen, eine pro Grundwert
  → Jede hat eigenen Skill-Baum + Kern-Mechanik
  → Kern-Mechanik ist NUR im Kampf aktiv, nicht kampfübergreifend

Stufe 2 (Level 25): Spezialisierung wählen
  → 3 Spezialisierungen pro Basis-Klasse (18 gesamt)
  → Basis-Baum bleibt vollständig erhalten
  → Spezialisierungs-Baum kommt zusätzlich dazu
  → Beide Bäume gleichzeitig aktiv
```

---

## Wo liegen die Daten?

| Datentyp | Datei |
|---|---|
| Klassen-Definitionen, Namen, Beschreibungen | `spiel/daten/klassen.json` |
| Node-Verbindungen und Baum-Struktur | `spiel/daten/klassen.json` |
| Skill-Werte (Cooldown, Mana, Skalierung) | `spiel/systeme/skill_definitionen.py` |
| Kern-Mechanik-Logik (Rage, Combo etc.) | `server/logik/kampf_engine.py` |
| Datenbankzugriff für Skills | `server/datenbank/datenbank.py` |
| Server-Validierung | `server/logik/skill_verwaltung.py` |

---

## Entscheidungsbaum: Wo kommt neue Klassen-Logik hin?

```
Ist es ein neuer Kampf-Effekt (Rage, Combo)?
  → server/logik/kampf_engine.py

Ist es eine neue Skill-Definition (Werte, Skalierung)?
  → spiel/systeme/skill_definitionen.py
  → Spiegelung der Struktur aus spiel/daten/klassen.json

Ist es eine neue Klassen-Beschreibung oder Node-Verbindung?
  → spiel/daten/klassen.json

Ist es UI für den Skill-Baum?
  → spiel/szenen/skill_szene.py

Ist es Server-Validierung (darf Spieler diesen Skill nutzen)?
  → server/logik/skill_verwaltung.py
```

---

## Kern-Mechanik Regeln

Jede Basis-Klasse hat genau eine Kern-Mechanik:
- Nur im Kampf aktiv — nach Kampfende zurückgesetzt
- Wird durch Angriffe, Treffer oder Skills aufgebaut
- Beeinflusst Kampfwerte (Schaden, Geschwindigkeit etc.)
- Skaliert mit Skill-Baum-Investitionen
- Maximaler Stapel-Wert steht in `spiel/daten/klassen.json`

---

## Skill-Baum Struktur

```
Jeder Baum hat:
- Obere Nodes: kleine Boni (mehrfach skillbar, max 3-5x)
  → Verbunden durch Pfade — man muss Nachbar-Node zuerst skillen
  → Definiert welche Skills freigeschaltet werden
- Untere Leiste: die eigentlichen Skills (Aktiv/Passiv)
  → Werden durch Punkte in verbundenen Nodes freigeschaltet
  → Schwellen in spiel/daten/klassen.json definiert

Punkte-Quelle: 1 Skill-Punkt pro Level-Up
Investierung: immer in einen der aktiven Bäume (Basis oder Spezialisierung)
```

---

## Validierungsregeln (server-seitig)

```
Punkt investieren:
  - Spieler hat skill_punkte > 0?
  - Ziel-Node ist Nachbar einer bereits geskilten Node ODER Start-Node?
  - Node hat noch freie Stufen (aktuell < max)?
  → Ja zu allen: Punkt investieren, skill_punkte reduzieren

Skill freischalten:
  - Punkte-Schwelle in verbundenen Nodes erreicht?
  → Ja: Skill wird freigeschaltet

Skill ausrüsten:
  - Skill ist freigeschaltet?
  - Skill-Typ passt zum Slot (aktiv/passiv)?
  - Mana-Reservierung unter 80%?
  → Ja zu allen: ausrüsten
```

---

## Pflichtprüfung

- [ ] Kern-Mechanik wird nach Kampfende zurückgesetzt?
- [ ] Node-Verbindungen werden server-seitig validiert?
- [ ] Basis-Baum bleibt bei Spezialisierung vollständig erhalten?
- [ ] Skill-Werte kommen aus `skill_definitionen.py`, nicht hardcoded?
- [ ] Neue Klassen-Daten in `klassen.json`, nicht im Code?

---
name: skill-projektstruktur
description: >
  Muss konsultiert werden BEVOR eine neue Datei oder ein neues Verzeichnis
  angelegt wird, BEVOR eine Datei verschoben oder umbenannt wird, und BEVOR
  ein neues System implementiert wird. Trigger: neue Datei anlegen, Ordner
  erstellen, Datei verschieben, Modul hinzufügen.
---

# skill-projektstruktur

Regelt wo Dateien hingehören und wie die Projektstruktur gepflegt wird.
Drei eiserne Trennungen: Spiel-Code in `spiel/`, Server-Code in `server/`,
Tests in `tests/`.

---

## Zwei Einstiegspunkte — nie mehr

| Datei | Zweck |
|---|---|
| `start.py` | Startet den Client |
| `server_start.py` | Startet den Server |

Neue Startlogik kommt in `spiel/kern/spiel.py` oder `server/kern/server_kern.py`.

---

## Wo gehört eine neue Datei hin?

```
Spiellogik ohne Rendering?  → spiel/systeme/
Rendering oder UI?          → spiel/ui/ oder spiel/szenen/
Spielobjekt mit Zustand?    → spiel/entitaeten/
Spielbereich (Scene)?       → spiel/szenen/
Mediendatei?                → spiel/assets/
JSON-Spieldaten?            → spiel/daten/

Server-Verbindungslogik?    → server/kern/
Server-Spiellogik?          → server/logik/
Datenbankzugriff?           → server/datenbank/

Client UND Server nutzen?   → netzwerk/

Test?                       → tests/[bereich]/test_[modulname].py

Hilfsfunktion?              → utils/

Nichts passt?
  → STOPP. Nummerierte Fragen an Entwickler. Ablageort vorschlagen.
```

---

## Neue Verzeichnisse

Nur anlegen wenn Entwickler es beauftragt ODER mehr als 3 thematisch
zusammenhängende Dateien ein Unterverzeichnis rechtfertigen.

Jedes neue Verzeichnis braucht: `__init__.py` + Eintrag in diesem Skill
+ Eintrag in `FORTSCHRITT.md`.

---

## Erweiterungstabelle

| Feature | Primäre Datei | Sekundäre Dateien |
|---|---|---|
| Neue Klasse/Masterie | `spiel/daten/klassen.json` | `spiel/systeme/skill_definitionen.py` |
| Neuer Gegnertyp | `spiel/entitaeten/gegner.py` | `spiel/daten/gegner.json` |
| Neues Item | `spiel/daten/items.json` | `spiel/systeme/inventar.py` |
| Neue Quest | `spiel/daten/quests.json` | `server/logik/quest_generator.py` |
| Neuer Spielbereich | `spiel/szenen/[name].py` | `spiel/kern/szenen_manager.py` |
| Neues Netzwerkpaket | `netzwerk/nachrichten.py` | `netzwerk/protokoll.py` |
| Neuer Skill | `skills/skill-[thema].md` | `skills/skill-übersicht.md` |

---

## Pflichtprüfung

- [ ] Liegt Spiel-Code ausschließlich in `spiel/`?
- [ ] Liegt Server-Code ausschließlich in `server/`?
- [ ] Liegen alle Tests in `tests/`?
- [ ] Hat jede neue `.py`-Datei einen Kommentar-Header?
- [ ] Sind alle `__init__.py` vorhanden?
- [ ] Gibt es exakt zwei Einstiegspunkte?
- [ ] Ist `FORTSCHRITT.md` aktualisiert?

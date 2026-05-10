---
name: skill-netzwerk
description: >
  Muss konsultiert werden BEVOR Netzwerkcode geschrieben wird.
  Trigger: "Server-Verbindung", "Client-Netzwerk", "TCP-Socket",
  "JSON-Nachricht", "Threading implementieren".
---

# skill-netzwerk

Regeln für Netzwerk- und Socket-Programmierung im Projekt.

---

## Verzeichnisstruktur

| Code-Typ | Pfad | Begründung |
|----------|------|------------|
| Gemeinsam | `netzwerk/` | Protokoll und Nachrichten für beide Seiten |
| Server-Kern | `server/kern/` | server_kern.py, verbindung.py |
| Client | `spiel/kern/` | netzwerk_client.py |

**Nachrichtentypen:** Konstanten in `netzwerk/nachrichten.py`

---

## Protokoll-Entscheidungen

```
Nachricht empfangen?
  → Ja: [4 Bytes Länge] + [JSON-Daten] lesen
  → Nein: Verbindung prüfen, neu verbinden oder trennen

TCP-Problem?
  → Fragmentierte Pakete: Längen-Header verwenden
  → Blockierung: Non-blocking sockets mit select()
  → Zeitüberschreitung: Timeout setzen (30s für Login, 10s für Aktionen)
```

---

## Threading-Entscheidungen

| Situation | Lösung |
|-----------|--------|
| Server: neuer Client | `threading.Thread(target=..., daemon=True).start()` |
| Client: Nachrichten empfangen | Hintergrund-Thread, Queue für UI |
| UI-Blockierung vermeiden | Niemals `socket.recv()` im Haupt-Thread |
| sauberer Shutdown | Flag `laufend = False` setzen, nicht `thread.join()` |

---

## Socket-Optionen

Immer vor `bind()`:
```python
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

---

## Import-Reihenfolge

Stdlib → Third-party → Lokal:
```python
import socket, threading, json, queue
import config
from netzwerk.nachrichten import ...
from netzwerk.protokoll import ...
```

---

## Verbindungsende

```
Verbindung beenden?
  → Socket schließen mit `socket.close()`
  → Client-Thread: Flag setzen, nicht warten
  → Server: Alle Verbindungen in Schleife trennen
```

---

## Pflichtprüfung

- [x] Enthält der Skill nur Regeln, keine Daten oder Werte?
- [x] Ist er unter 200 Zeilen?
- [x] Hat er mindestens einen Entscheidungsbaum oder eine Tabelle?
- [x] Ist der Trigger in `description` spezifisch genug?
- [x] Ist er in `skill-übersicht.md` eingetragen?
- [x] Gibt es Konflikte mit anderen Skills?
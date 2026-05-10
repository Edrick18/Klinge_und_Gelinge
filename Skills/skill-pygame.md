---
name: skill-pygame
description: >
  Muss konsultiert werden BEVOR irgendein pygame-Code geschrieben wird.
  Trigger: Game-Loop, Fenster, Szenen, Rendering, Events, Schriftarten,
  Delta-Zeit, Oberflächen, Eingabe, UI-Elemente zeichnen.
---

# skill-pygame

Regelt wie pygame-Code im Projekt strukturiert wird. Abweichungen sind Fehler.

---

## Kernregeln

| Regel | Grund |
|---|---|
| Alle Werte aus `config.py` | Änderungen an einer Stelle |
| Delta-Zeit immer in Sekunden als float | Frame-unabhängige Logik |
| `pygame.display.flip()` nur in `spiel.starten()` | Einmal pro Frame |
| Keine `pygame.font.Font()` in `zeichnen()` | Zu langsam, einmal laden |
| Szenen kommunizieren nie direkt | Immer über SzenenManager |
| Alle Positionen relativ zu `b` und `h` | Auflösungsunabhängig |

---

## Game-Loop Muster (unveränderlich)

```python
def starten(self):
    while self.laufend:
        delta_zeit = self.uhr.tick(config.FPS) / 1000.0
        events = pygame.event.get()
        self.szenen_manager.events_verarbeiten(events)
        self.szenen_manager.updaten(delta_zeit)
        self.fenster.fill(config.FARBE_HINTERGRUND)
        self.szenen_manager.zeichnen(self.fenster)
        pygame.display.flip()
```

---

## Szenen-Struktur

Jede Szene erbt von `BasisSzene` und implementiert genau drei Methoden:
`events_verarbeiten(events)`, `updaten(delta_zeit)`, `zeichnen(flaeche)`.

Szenenwechsel immer über SzenenManager, nie direkt in der Szene.

---

## Layout-Berechnung

Alle Positionen werden in `_layout_berechnen()` aus `b` und `h` berechnet
und als Instanzvariablen gespeichert. `_layout_berechnen()` wird in
`__init__` aufgerufen — vor dem ersten `nachricht_senden()`.

```python
def _layout_berechnen(self):
    b = config.AUFLOESUNG_BREITE
    h = config.AUFLOESUNG_HOEHE
    self.titel_y = int(h * 0.08)
    # ... alle weiteren Positionen
```

Klick-Rects werden in `_layout_berechnen()` erstellt — nie in `zeichnen()`.

---

## Entscheidungsbaum: Wo kommt neuer UI-Code hin?

```
Ist es Spiellogik?          → spiel/systeme/ (kein pygame-Import)
Ist es eine Szene?          → spiel/szenen/[name]_szene.py
Ist es ein wiederverwendbares UI-Element? → spiel/ui/[name].py
Ist es HUD (immer sichtbar)?→ spiel/ui/hud.py
```

---

## Rendering-Reihenfolge

1. Hintergrund füllen
2. Hintergrundelemente
3. Spielelemente
4. UI-Elemente (oberste Schicht)
5. Debug-Overlay (nur wenn `DEBUG=True` in `config.py`)
6. `pygame.display.flip()` — einmal, nur in `spiel.starten()`

---

## Pflichtprüfung

- [ ] Keine Magic Numbers — alles aus `config.py`?
- [ ] `_layout_berechnen()` in `__init__` aufgerufen?
- [ ] `pygame.display.flip()` nur in `spiel.starten()`?
- [ ] Keine `pygame.font.Font()` in `zeichnen()`?
- [ ] Alle Positionen relativ zu `b` und `h`?
- [ ] Klick-Rects identisch mit gezeichneten Elementen?

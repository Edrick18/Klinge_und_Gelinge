# FORTSCHRITT.md

## 2026-05-08

### Erledigt
- Server-Härtung: Alle Handler in verbindung.py in try/except gewickelt — Exception fangen, loggen, FEHLER senden statt crashen [Erfolgreich]
- Snapshot-Vollständigkeit: Snapshot nach Item anlegen/ablegen und Quest abschließen (mit Level-Up) jetzt automatisch aktualisiert [Erfolgreich]
- Skill-Szene UI: Nodes ausgegraut wenn keine Skill-Punkte mehr, ausgerüstete Skills zeigen Slot-Nummer (A1/P2) [Erfolgreich]
- Kampfanzeige: Gold + XP Belohnungen prominent anzeigen, Level-Up mit "⬆ LEVEL UP!" hervorheben [Erfolgreich]
- Reise-Szene: Offline-Belohnungen als Button (bereits implementiert) [Erfolgreich]
- Inventar: Item-Vergleich mit ▲/▼ Pfeilen — Stats werden mit ausgeruestetem Item im Slot verglichen [Erfolgreich]
- Automatischer Test (test_heartbeat.py) erstellt — 30 Tests, alle grün

## 2026-05-04

### Erledigt
- `config.py` erstellt: Globale Konstanten für Anzeige, Farben, Server und Spielbalancing
- `spiel/kern/` Grundgerüste erstellt: Spiel, SzenenManager, EreignisHandler, BasisSzene

## 2026-05-05

### Erledigt
- Phase 1 Schritt 1: Fenster + Ladebildschirm + Hauptmenü - [Erfolgreich]
- Phase 1 Schritt 2: Server + Client-Verbindung - [Erfolgreich]
- Phase 1 Schritt 3: Registrierung + Login - [Erfolgreich]
- Phase 2 Schritt 1: Charaktererstellung - [Erfolgreich]
- Phase 2 Schritt 2: Charakter-Übersicht mit Stats - [Erfolgreich]
- Phase 2 Schritt 3: Persistenz + Snapshot-System - [Erfolgreich]
- Phase 3 Schritt 1: Auto-Combat-Engine - [Erfolgreich]
- Bugfix: Kampf-Seed variabel - [Erfolgreich]
- Bugfix: Kampf-Seed auf secrets.randbits umgestellt - [Erfolgreich]
- UI-Fixes: Charaktererstellung Layout + Auswahl-Slots - [Erfolgreich]
- UI-Fix: Stat-Layout auflösungsunabhängig - [Erfolgreich]
- UI-Fix: Vertikale Abstände kompakter - [Erfolgreich]
- UI-Fix: Name-Feld Überlappung behoben - [Erfolgreich]
- Bugfix: Charakter-Auswahl Klick - [Erfolgreich]
- Phase 3 Schritt 2: Fäule-Fix + Kampfanzeige Polish - [Erfolgreich]
- Phase 3 komplett: Combat-Engine + Fäule getestet ✓ - [Erfolgreich]
- Phase 4 Schritt 1: Quest-System + Taverne - [Erfolgreich]
- Bugfix: Taverne Timer + Quest-Auflösung - [Erfolgreich]
- Bugfix: Quest-Status Wiederherstellung - [Erfolgreich]
- Bugfix: Alle Quests nach Abschluss neu generieren - [Erfolgreich]
- Phase 4 Schritt 2: Item-Generierung + Quest-Drops - [Erfolgreich]
- Bugfix item_drop + Inventar-Grundgerüst - [Erfolgreich]
- Bugfix: Kampfanzeige Layout + scrollbarer Log - [Erfolgreich]
- Bugfix: Kampfanzeige Zonen-Layout - [Erfolgreich]
- `server_start.py` erstellt (Einstiegspunkt Server)
- `netzwerk/` erstellt: nachrichten.py, protokoll.py
- `server/kern/` erstellt: server_kern.py, verbindung.py
- `spiel/kern/netzwerk_client.py` erstellt
- `skills/skill-netzwerk.md` erstellt
- `server/datenbank/datenbank.py` erstellt (SQLite + bcrypt)
- `server/logik/authentifizierung.py` erstellt
- `server/logik/charakter_verwaltung.py` erstellt
- `spiel/systeme/stat_berechnung.py` erstellt
- `spiel/szenen/charakter_uebersicht_szene.py` erstellt
- `spiel/szenen/login_szene.py` erstellt
- `spiel/szenen/charakter_auswahl_szene.py` erstellt
- `spiel/szenen/charakter_erstellung_szene.py` erstellt
- `spiel/szenen/stadt.py` erstellt
- `anforderungen.txt` erstellt (bcrypt, pygame-ce)
- `skills/skill-datenbank.md` erstellt
- `skills/skill-charakter.md` erstellt

### 2026-05-06
- Bugfix: Inventar Stats + Anlegen/Ablegen - [Erledigt]
  - Slot-Namen korrigiert (9 Slots statt 6)
  - Item-Details: basis_stats, prefixe, suffixe
  - Ablegen sendet item_id statt slot
  - Nach Anlegen/Ablegen: Inventar neu geladen
- Bugfix: Equipment-Slots Layout kompakter - [Erledigt]
  - 9 Slots dynamisch in h * 0.75
  - Zurück-Button bei h - 35, kein Überlappen
- Bugfix: item_ausruesten Reihenfolge korrigiert - [Erledigt]
  - Zuerst altes Item ablegen, dann neues anlegen
- Feature: Inventar Slot-Filter - [Erledigt]
  - Equipment-Slot anklicken → nur passende Items
  - "Alle anzeigen" Button zum Zurücksetzen
  - Filter-Anzeige über Grid
- Phase 5 Schritt 1: Skill-System Grundgerüst - [Erledigt]
  - skill_definitionen.py: 12 Bäume mit allen 96 Skills
  - Datenbank: charakter_skill_baeume, charakter_skills Tabellen
  - Nachrichtentypen für Skills
  - SkillVerwaltung für Punkt-Investitionen und Ausrüstung
  - Server-Verbindung erweitert
  - Snapshot mit ausgeruestete_skills

- Phase 5 Schritt 2: Skill-Baum UI - [Erledigt]
  - skill_szene.py mit Baum-Auswahl, Skill-Liste, Ausrüstungs-Panel
  - Charakter-Übersicht: Skills-Button verbunden
- Skill-Überarbeitung nach skill-autor.md Schema - [Erledigt]
  - skill-netzwerk.md, skill-datenbank.md, skill-items.md,
    skill-quests.md, skill-kampfsystem.md, skill-charakter.md überarbeitet

### 2026-05-07
- spiel/daten/ Ordner angelegt, klassen.json eingefügt
- Phase 5 Schritt 3: Skill-System Neuaufbau - [In Arbeit]
   - Alte Dateien gelöscht (skill_definitionen.py, skill_szene.py)
   - Neue Datenbank-Tabellen (charakter_klassen, charakter_nodes, charakter_klassen_skills)
   - Neue skill_definitionen.py mit klassen.json Lader
   - Neue Netzwerk-Nachrichten (KLASSEN_, SPEZIALISIERUNG_, NODE_)
   - Datenbank-Methoden hinzugefügt
   - WARNUNG: klassen.json muss noch mit allen Klassen vervollständigt werden
- Klassen-Umstrukturierung - [Erledigt]
   - spiel/daten/klassen/ Verzeichnis angelegt
   - klassen_index.json erstellt (Basis-Klassen Übersicht)
   - klassen/krieger.json (Krieger + Berserker, Ritter, Paladin vollständig)
   - klassen/waechter.json (Wächter + Bastian, Blutmagier, Kriegspriester Platzhalter)
   - klassen/zauberer.json, schicksalsritter.json, schatten.json, herold.json (Platzhalter)
   - Alte klassen.json gelöscht
   - skill_definitionen.py aktualisiert für Lazy Loading Struktur
- krieger.json Spezialisierungen vervollständigt - [Erledigt]
   - Ritter (Kampf-Haltung: Angriff/Verteidigung)
   - Paladin (Heilige Wut: Heilung bei Treffer ab 70 Rage)
- waechter.json Spezialisierungen vervollständigt - [Erledigt]
   - Bastian (Festung: +50% Schadenreduktion bei 5 Stapeln)
   - Blutmagier (Blutpakt: HP-Opfer wird von Stapeln absorbiert)
   - Kriegspriester (Heilige Absolution: +30% Skill-Wirkung nach Block)
- zauberer.json vervollständigt - [Erledigt]
   - Basis: Zauberer (Elementar-Ladungen: Feuer, Eis, Blitz)
   - Pyromant (Inferno: +50% Brennen bei 3 Feuer-Ladungen)
   - Frostmagier (Einfrieren: 2s Freeze bei 3 Eis-Ladungen + Kombination)
   - Sturmrufer (Sturmform: 30% Doppeltreffer bei 3 Blitz-Ladungen)
- schicksalsritter.json vervollständigt - [Erledigt]
   - Basis: Schicksalsritter (Fortune-Stapel: +1 Krit, +2 Ausweichen)
   - Glücksbringer (Schicksalsschlag: garantierter Krit springt weiter)
   - Schicksalsweber (Schicksalskontrolle: Stapel sperren/freigeben)
   - Rächer (Vergeltungsschlag: +50% Schaden nach Ausweichen)
- schatten.json vervollständigt - [Erledigt]
   - Basis: Schatten (Combo-Punkte: +1 AA, +2 Skill, 6s Verfall)
   - Assassine (Tödliche Konzentration: +20%/s Finisher bei 5 Combo)
   - Klingentänzer (Tanz-Rhythmus: +2 Combo nach Finisher)
   - Phantom (Schattenform: Auto-Ausweichen bei 5 Combo, +2 Combo)
- herold.json vervollständigt - [Erledigt]
   - Basis: Herold (Einfluss-Stapel: +1 Buff/Debuff, Dominanz bei 8)
   - Kriegsherr (Kriegsruf: +15% Schaden pro Buff bei Dominanz)
   - Hexer (Fluchverkettung: 20% Verstärkung bei 3+ Debuffs)
   - Seelenbinder (Seelenband: 15% Buff-Verstärkung pro Debuff)
- Phase 5 Schritt 3: Skill-System Infrastruktur fertiggestellt - [Erledigt]
   - skill_verwaltung.py neu geschrieben für Klassen-basiertes System
   - verbindung.py erweitert mit NODE_SKILLEN, SPEZIALISIERUNG_WAEHLEN, KLASSEN_LADEN
   - CHARAKTER_ERSTELLEN/WAEHLEN angepasst für neue Klasse-Mechanik
- Phase 5 Schritt 4A: Skill-Baum Darstellung - [Erledigt]
    - skill_szene.py neu erstellt mit Baum-Auswahl links
    - Node-Bereich mit Verbindungslinien und Farbkodierung
    - Skill-Leiste unten mit Status-Anzeige
    - Baum-Wechsel bei Klick funktioniert
 - 2026-05-07 - Phase 5 Schritt 4B: Node-Klick Interaktion - [Erledigt]
    - events_verarbeiten() mit Node-Klick Erkennung
    - _node_skillen() Methode für Server-Kommunikation
    - updaten() mit NODE_GESKILLT Antwort-Verarbeitung
    - Status-Nachrichten mit 3-Sekunden Timer
    - GRUNDWERT_ZU_KLASSE Mapping für korrekte Klassennamen
 - 2026-05-07 - Phase 5 Schritt 4C: Datenbank-Methoden Refactoring - [Erledigt]
    - skill_verwaltung.py: node_skillen, skills_laden, skill_ausruesten refaktoriert
    - datenbank.py: Neue Methoden (skill_punkte_reduzieren, nodes_laden, skill_punkte_laden, etc.)
    - Keine direkten verbindung.cursor() Aufrufe mehr in skill_verwaltung
 - 2026-05-07 - Phase 5 Schritt 4D: Skill ausrüsten/ablegen - [Erledigt]
    - skill_szene.py: Skill-Leiste Klick Erkennung
    - Ausrüstungs-Panel mit Skill-Details
    - Slot-Buttons für aktiv/passiv
    - Server-Kommunikation (SKILL_AUSRUESTEN, SKILL_ABLEGEN)
    - Hilfsmethoden (_slot_belegt, _text_umbrechen)
 - 2026-05-07 - Phase 5 Schritt 4D: Skill-Ausrüstung Feedback - [Erledigt]
    - _skill_status() korrigiert für bessere Logik
    - _skill_in_slot() Hilfsmethode hinzugefügt
    - Slot-Buttons zeigen "✓ Ausgerüstet" wenn Skill im Slot
    - Slot-Buttons zeigen "(belegt)" wenn anderer Skill im Slot
 - 2026-05-07 - Phase 5 Schritt 4D: Click-Handling Refactoring - [Erledigt]
    - events_verarbeiten() mit korrekter Klick-Reihenfolge
    - _panel_klick_verarbeiten(), _skill_leiste_klick(), _node_klick_verarbeiten()
    - _zurueck_zur_uebersicht() Helper für sauberen Szene-Wechsel
 - 2026-05-07 - Fix: Klassen-Namen aus JSON - [Erledigt]
    - charakter_erstellung_szene.py: Buttons zeigen "Krieger", "Wächter" etc.
    - charakter_uebersicht_szene.py: Masterie-Anzeige aus JSON
    - charakter_auswahl_szene.py: Slot-Anzeige mit Klassennamen
    - GRUNDWERT_ZU_KLASSE Mapping in allen 3 Szenen
 - 2026-05-07 - Phase 5 Schritt 5A: Skills in Combat-Engine - [Erledigt]
    - server/logik/kern_mechaniken.py: 6 Kern-Klassen (Rage, SchildStapel, etc.)
    - spiel/systeme/kampf_typen.py: 6 neue Ereignis-Typen
    - server/logik/kampf_engine.py: Skill-Anwendung, Cooldowns, Mana-Regen
    - server/logik/snapshot.py: klassen_id + ausgeruestete_skills mit Definitionen
 - 2026-05-07 - Phase 5 Schritt 5B: Skill-Icons + Cooldown-Balken - [Erledigt]
    - kampf_anzeige_szene.py: Skill-Leiste zwischen HP-Balken und Log
    - Mana-Balken über der Skill-Leiste
    - Cooldown-Balken unter jedem aktiven Skill-Icon
    - Skill-Ereignisse in lila im Log
    - Status-Effekt-Ereignisse in orange im Log
- 2026-05-07 - Dynamische Beschreibungen für Skills und Nodes - [6/6 Klassen]
     - skill_definitionen.py: beschreibung_generieren(), skill_beschreibung_mit_level()
     - krieger.json, waechter.json, schicksalsritter.json, schatten.json, herold.json, zauberer.json: Templates
     - skill_szene.py: Skill-Details mit level-skalierten Werten + Node-Tooltip
     - TEST 1-6: Alle bestanden
- 2026-05-07 - Phase 6: Offline-Reisen - [Erledigt]
     - Datenbank: charakter_reisen, reise_quests Tabellen + 7 neue Methoden
     - server/logik/reise_verwaltung.py: ReiseVerwaltung Klasse
     - netzwerk/nachrichten.py: 10 neue Nachrichtentypen
     - server/kern/verbindung.py: REISE_STARTEN, REISE_STATUS_LADEN, REISE_BELOHNUNGEN_LADEN, REISE_BELOHNUNGEN_ABHOLEN, REISE_BEENDEN Handler
     - spiel/szenen/reise_szene.py: ReiseSzene mit status/belohnungen/kampf Zuständen
     - spiel/szenen/charakter_uebersicht_szene.py: "Reisen" Button hinzugefügt
     - Fix: kern_mechaniken.py: schaden_multiplikator() in Basis-Klasse
     - Fix: reise_verwaltung.py: "gewonnen" statt "sieger" für Kampf-Ergebnis
     - Fix: datenbank.py: json Import hinzugefügt
     - Tests 1-8 BESTANDEN (Test 9 = GUI Leertaste = manuell)
- 2026-05-08 - Phase 7: Shop + Tränke - [Erledigt]
     - Datenbank: charakter_traenke Tabelle + 6 neue Methoden
     - Fix: datenbank.py >= statt > fuer Trank-Zeitvergleich
     - spiel/systeme/stat_berechnung.py: stats_mit_traenken() Methode
     - netzwerk/nachrichten.py: SHOP_LADEN, TRANK_KAUFEN, etc.
     - server/logik/shop_verwaltung.py: ShopVerwaltung mit Preisen + Validierung
     - server/kern/verbindung.py: SHOP_LADEN, TRANK_KAUFEN Handler
     - spiel/szenen/shop_szene.py: ShopSzene mit 18 Buttons + aktive Tränke
     - spiel/szenen/charakter_uebersicht_szene.py: Shop-Button hinzugefügt

- 2026-05-08 - Shop Umbau: 20 zufällige Slots - [Erledigt]
     - Datenbank: shop_angebote, shop_rerolls Tabellen + 6 neue Methoden
     - server/logik/shop_generator.py: ShopGenerator mit Items + Tränken
     - server/logik/shop_verwaltung.py: komplett neu mit Reroll-Logik
     - netzwerk/nachrichten.py: SHOP_REROLL, SHOP_KAUFEN, etc.
     - server/kern/verbindung.py: neue Shop-Handler + ItemGenerator init
     - spiel/szenen/shop_szene.py: 5×4 Grid mit Detail-Panel

- 2026-05-08 - Shop Layout: 12 Slots + Details + Tränke - [Erledigt]
     - server/logik/shop_generator.py: 12 statt 20 Slots
     - netzwerk/nachrichten.py: TRANK_ENTFERNEN, TRANK_ENTFERNT
     - server/kern/verbindung.py: TRANK_ENTFERNEN Handler
     - server/datenbank/datenbank.py: trank_entfernen() Methode
     - server/logik/shop_verwaltung.py: aktive_traenke in shop_daten_laden
     - spiel/szenen/shop_szene.py: komplett neues Layout (3×4 Grid links, Details oben rechts, Tränke unten rechts)

- 2026-05-08 - Shop Layout Fixes - [Erledigt]
     - FIX 1: slot_hoehe von h*0.20 auf h*0.15 reduziert
     - FIX 2: Detail-Panel auf h*0.64 vergrößert, Kaufen-Button bei h*0.72-50
     - FIX 3: Tränke nebeneinander (3 Spalten) mit X-Button zum Entfernen
     - FIX 4: Zurück-Button auf pygame.Rect(10, h-35, 90, 28)

- 2026-05-08 - Shop Detail-Panel Fixes - [Erledigt]
     - FIX 1: Kaufen-Button dynamisch unter allen Suffixen positioniert (y += 15 nach letztem Element)
     - FIX 2: btn_breite = 70% der Panel-Breite, zentriert
     - FIX 3: self.kaufen_button_rect als Instanzvariable gespeichert
     - FIX 4: _buttons_pruefen verwendet gespeichertes Rect statt neu berechnetem

- 2026-05-08 - Reise: Max-Timer Auswahl - [Erledigt]
     - reise_szene.py: 6 Dauer-Buttons (1h, 2h, 4h, 6h, 8h, 12h), default 4h
     - REISE_STARTEN sendet max_dauer an Server
     - server/logik/reise_verwaltung.py: reise_starten() akzeptiert max_dauer
     - server/datenbank/datenbank.py: max_dauer in charakter_reisen gespeichert/geladen
     - reise_szene.py: Fortschrittsbalken + Zeitdisplay (verbraucht/max_dauer)

- 2026-05-08 - Taverne: Sperre während Reise - [Erledigt]
     - taverne_szene.py: __init__ sendet REISE_STATUS_LADEN
     - updaten() setzt self.reise_aktiv bei REISE_STATUS_ANTWORT
     - zeichnen() zeigt halbtransparentes Overlay wenn reise_aktiv
     - events_verarbeiten() ignoriert Quest-Klicks während Reise

- 2026-05-09 - Phase 8: Arena - [Erledigt]
     - Datenbank: arena_stats, arena_kaempfe, item_verzauberungen Tabellen + Methoden
     - server/logik/arena_verwaltung.py: ArenaVerwaltung mit Rang-System, Shop, Verzauberungen
     - netzwerk/nachrichten.py: ARENA_LADEN, ARENA_KAMPF_STARTEN, etc.
     - server/kern/verbindung.py: Arena Handler implementiert
     - spiel/szenen/arena_szene.py: Arena-Szene mit Gegner-Auswahl, Kampf, Shop
     - charakter_uebersicht_szene.py: Arena-Button hinzugefügt
     - spiel/systeme/stat_berechnung.py: schriftrollen_bonus() für XP/Gold-Bonus

### Nächste Schritte
- Weitere Phasen gemäß Projektplan
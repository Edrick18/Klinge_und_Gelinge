# Klinge und Gelinge – ProjektRPG

## Für Tester

1. Lade `ProjektRPG.exe` von der [Releases-Seite](../../releases/latest) herunter
2. Starte `ProjektRPG.exe`
3. Das Spiel updated sich automatisch wenn eine neue Version verfügbar ist

---

## Projektstruktur (Entwickler)

```
eigenes spiel erstellen/
│
├── start.py                  ← Spiel starten (Tester-Version)
├── server_start.py           ← Produktions-Server starten
├── server_start_dev.py       ← DEV: Separater Server (Port 55001, eigene DB)
├── _start_dev.py             ← DEV: Spiel direkt per Python starten (localhost:55001)
│
├── config.py                 ← Alle Einstellungen (Version, Port, Host, Farben)
├── version.txt               ← Aktuelle Versionsnummer (für Auto-Update)
├── updater.py                ← Auto-Update Logik
├── duckdns_update.py         ← IPv6/DuckDNS beim Server-Start aktualisieren
│
├── dev.bat                   ← DEV: Server + Spiel auf einmal starten
├── build_release.bat         ← Exe bauen für Tester (klingeundgelinge.duckdns.org)
├── build_lokal.bat           ← Exe bauen zum lokalen Testen (localhost:55000)
├── server_start.bat          ← Shortcut: Server im eigenen Fenster starten
│
├── netzwerk/                 ← Netzwerk-Protokoll (Client + Server gemeinsam)
│   ├── nachrichten.py        ← Alle Nachrichtentypen als Konstanten
│   └── protokoll.py          ← JSON-Serialisierung / Deserialisierung
│
├── server/                   ← Server-Code (läuft nur bei Lutz lokal)
│   ├── kern/
│   │   ├── server_kern.py    ← TCP-Server, nimmt Verbindungen an
│   │   └── verbindung.py     ← Pro-Client-Thread, verarbeitet alle Nachrichten
│   ├── logik/
│   │   ├── authentifizierung.py
│   │   ├── charakter_verwaltung.py
│   │   ├── kampf_engine.py
│   │   ├── quest_verwaltung.py   ← Taverne-Quests
│   │   ├── reise_verwaltung.py   ← Offline-Reisen
│   │   ├── shop_verwaltung.py
│   │   ├── arena_verwaltung.py
│   │   ├── gilde_verwaltung.py
│   │   ├── skill_verwaltung.py
│   │   ├── item_generator.py
│   │   ├── shop_generator.py
│   │   ├── quest_generator.py
│   │   ├── snapshot.py
│   │   └── kern_mechaniken.py
│   └── datenbank/
│       ├── datenbank.py      ← Alle SQLite-Datenbankzugriffe
│       ├── spieldaten.db     ← Produktions-Datenbank (Tester-Accounts)
│       └── spieldaten_dev.db ← Dev-Datenbank (nach erstem dev.bat-Start)
│
├── spiel/                    ← Client-Code (wird in die Exe gepackt)
│   ├── kern/
│   │   ├── spiel.py          ← Pygame-Hauptschleife
│   │   ├── szenen_manager.py ← Szenenwechsel verwalten
│   │   ├── netzwerk_client.py← TCP-Verbindung zum Server
│   │   ├── ereignis_handler.py
│   │   └── basis_szene.py    ← Basisklasse für alle Szenen
│   ├── szenen/               ← Eine Datei = ein Spielbildschirm
│   │   ├── hauptmenue_szene.py
│   │   ├── login_szene.py
│   │   ├── charakter_auswahl_szene.py
│   │   ├── charakter_erstellung_szene.py
│   │   ├── charakter_uebersicht_szene.py
│   │   ├── stadt.py          ← Stadtübersicht (Hub)
│   │   ├── taverne_szene.py
│   │   ├── shop_szene.py
│   │   ├── inventar_szene.py
│   │   ├── skill_szene.py
│   │   ├── reise_szene.py
│   │   ├── arena_szene.py
│   │   ├── kampf_anzeige_szene.py
│   │   ├── gilde_szene.py
│   │   └── ladebildschirm.py
│   ├── systeme/              ← Spielregeln die Client + Server kennen
│   │   ├── stat_berechnung.py
│   │   ├── item_typen.py
│   │   ├── kampf_typen.py
│   │   ├── quest_typen.py
│   │   └── skill_definitionen.py
│   └── daten/
│       └── klassen/          ← Klassenbalancing als JSON (krieger, zauberer, ...)
│
├── werkzeuge/                ← Hilfsskripte (lokal, nicht im Git)
│   ├── _build_helper.py      ← config.py temporär tauschen beim Build
│   ├── _db_info.py           ← Zeigt Anzahl Einträge pro Tabelle
│   └── _db_reset.py          ← ALLE Spielerdaten löschen (Tabellen bleiben)
│
├── docs/                     ← Notizen, Planung (nicht im Git, nicht für Tester)
│   ├── UPDATE_ANLEITUNG.txt  ← Schritt-für-Schritt: neues Update pushen
│   ├── FORTSCHRITT.md
│   ├── klassen-definitionen.md
│   └── skills/               ← KI-Kontext Dateien
│
├── tests/                    ← Testskripte (lokal, nicht im Git)
├── dist/
│   ├── release/ProjektRPG.exe  ← Fertige Exe für Tester
│   └── lokal/ProjektRPG.exe    ← Fertige Exe zum lokalen Testen
└── build/                    ← PyInstaller Zwischendateien (automatisch)
```

---

## Schnellreferenz

| Was | Wie |
|-----|-----|
| Dev-Umgebung starten | `dev.bat` doppelklicken |
| Produktions-Server starten | `server_start.py` oder `server_start.bat` |
| Exe für Tester bauen | `build_release.bat` |
| Exe lokal testen | `build_lokal.bat` |
| Alle Accounts löschen | `py werkzeuge\_db_reset.py` |
| DB-Inhalt prüfen | `py werkzeuge\_db_info.py` |
| Update pushen | Siehe `docs/UPDATE_ANLEITUNG.txt` |

---

## Requirements

```
pip install pygame-ce pyinstaller
```

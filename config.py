"""
config.py - Globale Konstanten für Spiel und Server

Abhängigkeiten: keine externen Dependencies
"""

# ==================== ANZEIGE ====================

FENSTER_TITEL = "Projekt RPG"
AUFLOESUNG_BREITE = 1280
AUFLOESUNG_HOEHE = 720
FPS = 60
VOLLbild = False

# ==================== FARBEN (RGB) ====================

FARBE_SCHWARZ = (0, 0, 0)
FARBE_WEISS = (255, 255, 255)
FARBE_GRAU = (128, 128, 128)
FARBE_DUNKELGRAU = (64, 64, 64)

FARBE_HINTERGRUND = (18, 18, 18)
FARBE_PANEL = (30, 30, 30)
FARBE_RAND = (60, 60, 60)
FARBE_TEXT = (220, 220, 220)
FARBE_TEXT_GEDIMMT = (130, 130, 130)
FARBE_AKZENT = (180, 120, 60)

FARBE_HP = (180, 40, 40)
FARBE_MANA = (40, 80, 180)
FARBE_XP = (180, 160, 40)
FARBE_ERFOLG = (60, 160, 60)
FARBE_WARNUNG = (180, 100, 40)

# ==================== LADEBILDSCHIRM ====================

LADEBILDSCHIRM_DAUER = 2.0

# ==================== SERVER ====================

SERVER_HOST = "klingeundgelinge.duckdns.org"
SERVER_BIND_HOST = "0.0.0.0"
SERVER_PORT = 55000
SERVER_MAX_VERBINDUNGEN = 100
SERVER_TIMEOUT = 30

SPIEL_VERSION = "0.1.0"
VERSION_URL = "https://raw.githubusercontent.com/Edrick18/Klinge_und_gelinge/main/version.txt"
DOWNLOAD_URL = "https://github.com/Edrick18/Klinge_und_gelinge/releases/latest/download/ProjektRPG.exe"

# ==================== NETZWERK ====================

NETZWERK_PUFFER = 4096

# ==================== SPIELBALANCING ====================

BASIS_HP_PRO_KLASSE = {
    "krieger": 100,
    "magier": 70,
    "schurke": 85
}

XP_MULTIPLIKATOR = 1.0
LOOT_GLUCK_BASIS = 1.0
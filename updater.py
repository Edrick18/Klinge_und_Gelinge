import sys
import os
import urllib.request
import subprocess
import tempfile


def version_pruefen() -> tuple[str, str]:
    """Gibt (lokale_version, server_version) zurück"""
    try:
        from config import SPIEL_VERSION, VERSION_URL
        lokale_version = SPIEL_VERSION
        with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
            server_version = response.read().decode("utf-8").strip()
        return lokale_version, server_version
    except Exception:
        return "0.0.0", "0.0.0"


def update_verfuegbar() -> bool:
    lokale, server = version_pruefen()
    return lokale != server


def update_durchfuehren():
    """Lädt neue .exe herunter und startet neu"""
    from config import DOWNLOAD_URL

    try:
        temp_dir = tempfile.gettempdir()
        neue_exe = os.path.join(temp_dir, "ProjektRPG_neu.exe")
        aktuelle_exe = sys.executable

        print("Lade Update herunter...")
        urllib.request.urlretrieve(DOWNLOAD_URL, neue_exe)

        batch_inhalt = f"""@echo off
timeout /t 2 /nobreak > nul
move /y "{neue_exe}" "{aktuelle_exe}"
start "" "{aktuelle_exe}"
del "%~f0"
"""
        batch_pfad = os.path.join(temp_dir, "update.bat")
        with open(batch_pfad, "w") as f:
            f.write(batch_inhalt)

        subprocess.Popen(batch_pfad, shell=True)
        sys.exit(0)

    except Exception as e:
        print(f"Update fehlgeschlagen: {e}")
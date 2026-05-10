@echo off
cd /d "%~dp0"
echo ============================================
echo  Baue LOKALE Version (localhost:55000)
echo ============================================

:: Config sichern und auf localhost setzen
copy config.py config.py.bak >nul
py werkzeuge\_build_helper.py lokal

:: Alte Exe beenden falls sie noch laeuft
taskkill /f /im ProjektRPG.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: Bauen
py -m PyInstaller --onefile --name ProjektRPG ^
    --distpath "dist\lokal" ^
    --workpath "build\lokal" ^
    --specpath "." ^
    --paths "." ^
    --add-data "version.txt;." ^
    --add-data "config.py;." ^
    --add-data "spiel;spiel" ^
    --add-data "netzwerk;netzwerk" ^
    --add-data "spiel\daten;spiel\daten" ^
    --hidden-import config --hidden-import updater ^
    --hidden-import pygame --hidden-import sqlite3 ^
    --hidden-import spiel --hidden-import spiel.kern ^
    --hidden-import spiel.kern.spiel --hidden-import spiel.kern.netzwerk_client ^
    --hidden-import spiel.kern.szenen_manager --hidden-import spiel.kern.ereignis_handler ^
    --hidden-import spiel.kern.basis_szene ^
    --hidden-import spiel.szenen --hidden-import spiel.szenen.ladebildschirm ^
    --hidden-import spiel.szenen.hauptmenue_szene --hidden-import spiel.szenen.login_szene ^
    --hidden-import spiel.szenen.charakter_auswahl_szene --hidden-import spiel.szenen.charakter_erstellung_szene ^
    --hidden-import spiel.szenen.charakter_uebersicht_szene --hidden-import spiel.szenen.stadt ^
    --hidden-import spiel.szenen.taverne_szene --hidden-import spiel.szenen.shop_szene ^
    --hidden-import spiel.szenen.inventar_szene --hidden-import spiel.szenen.skill_szene ^
    --hidden-import spiel.szenen.reise_szene --hidden-import spiel.szenen.arena_szene ^
    --hidden-import spiel.szenen.kampf_anzeige_szene --hidden-import spiel.szenen.gilde_szene ^
    --hidden-import spiel.systeme --hidden-import spiel.systeme.quest_typen ^
    --hidden-import spiel.systeme.item_typen --hidden-import spiel.systeme.kampf_typen ^
    --hidden-import spiel.systeme.skill_definitionen --hidden-import spiel.systeme.stat_berechnung ^
    --hidden-import spiel.daten ^
    --hidden-import netzwerk --hidden-import netzwerk.protokoll --hidden-import netzwerk.nachrichten ^
    --collect-all spiel --collect-all netzwerk ^
    start.py

:: Config wiederherstellen
copy config.py.bak config.py >nul
del config.py.bak >nul
echo Config wiederhergestellt.

echo.
if exist "dist\lokal\ProjektRPG.exe" (
    echo  FERTIG ^> dist\lokal\ProjektRPG.exe
) else (
    echo  FEHLER: Exe wurde nicht erstellt!
)
pause

"""
server/kern/verbindung.py - Client-Verbindung in eigenem Thread

Abhängigkeiten: threading, netzwerk.protokoll, netzwerk.nachrichten, config, datenbank, authentifizierung, charakter_verwaltung
"""

import threading
import secrets
from datetime import datetime, timedelta

import config
from netzwerk.protokoll import Protokoll
from netzwerk.nachrichten import (
    VERBINDUNG_HERSTELLEN, VERBINDUNG_BESTAETIGT,
    REGISTRIEREN, REGISTRIEREN_ERFOLG, REGISTRIEREN_FEHLER,
    LOGIN, LOGIN_ERFOLG, LOGIN_FEHLER,
    SCHLUESSEL_BENUTZERNAME, SCHLUESSEL_PASSWORT, SCHLUESSEL_NACHRICHT, SCHLUESSEL_SPIELER_ID,
    CHARAKTERE_LADEN, CHARAKTERE_ANTWORT,
    CHARAKTER_ERSTELLEN, CHARAKTER_ERSTELLT, CHARAKTER_ERSTELLEN_FEHLER,
    CHARAKTER_WAEHLEN, CHARAKTER_GEWAEHLT,
    CHARAKTER_DETAILS_LADEN, CHARAKTER_DETAILS_ANTWORT,
    SCHLUESSEL_CHARAKTERE, SCHLUESSEL_CHARAKTER_ID, SCHLUESSEL_CHARAKTER_NAME,
    SCHLUESSEL_MASTERIE, SCHLUESSEL_STATS, SCHLUESSEL_CHARAKTER_DATEN,
    TESTKAMPF_STARTEN, KAMPF_ERGEBNIS, SCHLUESSEL_KAMPF_ERGEBNIS,
    QUESTS_LADEN, QUESTS_ANTWORT, QUEST_ANNEHMEN, QUEST_ANGENOMMEN, QUEST_AUFLOESEN, QUEST_TIMER_REDUZIEREN, QUEST_TIMER_REDUZIERT, QUEST_ERGEBNIS,
    SCHLUESSEL_QUESTS, SCHLUESSEL_QUEST_ID, SCHLUESSEL_QUEST_ERGEBNIS,
    INVENTAR_LADEN, INVENTAR_ANTWORT, SCHLUESSEL_ITEMS,
    ITEM_AUSRUESTEN, ITEM_ABLEGEN, SCHLUESSEL_ITEM_ID, SCHLUESSEL_SLOT,
    SKILLS_LADEN, SKILLS_ANTWORT, SCHLUESSEL_SKILLS, SCHLUESSEL_SKILL_ID,
    SKILL_PUNKT_INVESTIEREN, SKILL_PUNKT_INVESTIERT,
    SKILL_AUSRUESTEN, SKILL_AUSGERUESTET, SKILL_ABLEGEN, SKILL_ABGELEGT,
    SCHLUESSEL_SKILL_SLOT, SCHLUESSEL_SKILL_BAEUME, SCHLUESSEL_MASTERIE_BAUM,
    KLASSEN_LADEN, KLASSEN_ANTWORT, KLASSEN_INIT,
    SPEZIALISIERUNG_WAEHLEN, SPEZIALISIERUNG_GEWAEHLT,
    NODE_SKILLEN, NODE_GESKILLT, SCHLUESSEL_NODE_ID, SCHLUESSEL_KLASSEN_ID,
    REISE_STARTEN, REISE_GESTARTET, REISE_BEENDEN, REISE_BEENDET,
    REISE_STATUS_LADEN, REISE_STATUS_ANTWORT,
    REISE_BELOHNUNGEN_LADEN, REISE_BELOHNUNGEN_ANTWORT,
    REISE_BELOHNUNGEN_ABHOLEN, REISE_BELOHNUNGEN_ABGEHOLT,
    SCHLUESSEL_KAMPF_ERGEBNISSE, SCHLUESSEL_GESAMT_GOLD, SCHLUESSEL_GESAMT_XP, SCHLUESSEL_ANZAHL_QUESTS,
    SHOP_LADEN, SHOP_ANTWORT, SHOP_REROLL, SHOP_REROLL_ANTWORT,
    SHOP_KAUFEN, SHOP_GEKAUFT, SHOP_KAUFEN_FEHLER,
    TRANK_KAUFEN, TRANK_GEKAUFT, TRANK_KAUFEN_FEHLER,
    TRANK_ENTFERNEN, TRANK_ENTFERNT,
    SCHLUESSEL_TRANK_ID,
    SCHLUESSEL_SHOP_SLOT, SCHLUESSEL_ANGEBOTE,
    ARENA_LADEN, ARENA_ANTWORT, ARENA_KAMPF_STARTEN, ARENA_KAMPF_ERGEBNIS,
    ARENA_SHOP_KAUFEN, ARENA_SHOP_GEKAUFT, ARENA_VERZAUBERN, ARENA_VERZAUBERT,
    GILDE_LADEN, GILDE_ANTWORT, GILDE_ERSTELLEN, GILDE_ERSTELLT,
    GILDE_BEITRETEN, GILDE_BEIGETRETEN, GILDE_VERLASSEN, GILDE_VERLASSEN_OK,
    GILDE_STEUER_SETZEN, GILDE_STEUER_OK, GILDE_RANG_SETZEN, GILDE_RANG_OK,
    GILDE_KICK, GILDE_KICK_OK, GILDE_AUFSTEIGEN, GILDE_AUFGESTIEGEN,
    SCHLUESSEL_GEGNER_ID, SCHLUESSEL_ARTIKEL_ID, SCHLUESSEL_ITEM_ID,
    SCHLUESSEL_TRANK_ID, SCHLUESSEL_TRANK_STAT, SCHLUESSEL_TRANK_STUFE, SCHLUESSEL_TRAENKE,
    SCHLUESSEL_GILDEN_NAME, SCHLUESSEL_GILDEN_ID, SCHLUESSEL_STEUER, SCHLUESSEL_ZIEL_ID, SCHLUESSEL_RANG
)
from server.logik.authentifizierung import Authentifizierung
from server.logik.charakter_verwaltung import CharakterVerwaltung
from server.logik.kampf_engine import KampfEngine
from server.logik.test_gegner import testkampfer_erstellen
from server.logik.quest_verwaltung import QuestVerwaltung
from server.logik.skill_verwaltung import SkillVerwaltung
from server.logik.quest_generator import QuestGenerator
from server.logik.reise_verwaltung import ReiseVerwaltung
from server.logik.shop_verwaltung import ShopVerwaltung
from server.logik.arena_verwaltung import ArenaVerwaltung, rang_berechnen, ARENA_SHOP
from server.logik.item_generator import ItemGenerator
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from spiel.systeme.stat_berechnung import StatBerechnung
from server.logik.snapshot import Snapshot


class Verbindung:
    def __init__(self, socket, adresse, verbindungs_id: int, datenbank, server):
        self.socket = socket
        self.adresse = adresse
        self.verbindungs_id = verbindungs_id
        self.datenbank = datenbank
        self.server = server
        self.authentifizierung = Authentifizierung(datenbank)
        self.charakter_verwaltung = CharakterVerwaltung(datenbank)
        self.snapshot = Snapshot(datenbank)
        self.quest_verwaltung = QuestVerwaltung(datenbank)
        self.arena_verwaltung = ArenaVerwaltung(datenbank, KampfEngine)
        self.skill_verwaltung = SkillVerwaltung(datenbank)
        self.quest_generator = QuestGenerator()
        self.reise_verwaltung = ReiseVerwaltung(datenbank, self.quest_generator, KampfEngine)
        self.item_generator = ItemGenerator()
        self.shop_verwaltung = ShopVerwaltung(datenbank, self.item_generator)
        from server.logik.gilde_verwaltung import GildeVerwaltung
        self.gilde_verwaltung = GildeVerwaltung(datenbank)
        self.spieler_id = None
        self.aktiver_charakter_id = None
        self.laufend = False
        self.thread = None

    def starten(self):
        self.laufend = True
        self.thread = threading.Thread(target=self.nachrichten_loop, daemon=True)
        self.thread.start()

    def nachrichten_loop(self):
        print(f"Verbindung {self.verbindungs_id}: nachrichten_loop gestartet")
        while self.laufend:
            try:
                nachricht = Protokoll.empfangen(self.socket)
                if nachricht is None:
                    self.trennen()
                    break
                self._nachricht_verarbeiten(nachricht)
            except Exception as e:
                import traceback
                print(f"Nachrichten-Loop Fehler (Verbindung {self.verbindungs_id}): {e}\n{traceback.format_exc()}")
                self.trennen()
                break

    def _nachricht_verarbeiten(self, nachricht: dict):
        try:
            self._nachricht_verarbeiten_intern(nachricht)
        except Exception as e:
            import traceback
            error_log = f"Handler-Fehler (Verbindung {self.verbindungs_id}): {e}\n{traceback.format_exc()}"
            print(error_log)
            # FEHLER an Client senden (falls Verbindung noch da)
            try:
                from netzwerk.nachrichten import FEHLER
                self.senden(Protokoll.nachricht_erstellen(FEHLER, {
                    "nachricht": f"Server-Fehler: {str(e)}"
                }))
            except Exception:
                pass  # Verbindung wahrscheinlich schon weg

    def _nachricht_verarbeiten_intern(self, nachricht: dict):
        typ = nachricht.get("typ")
        daten = nachricht.get("daten", {})

        print(f"[DEBUG] Nachricht: {typ}, spieler_id: {self.spieler_id}, charakter_id: {self.aktiver_charakter_id}")

        if typ == VERBINDUNG_HERSTELLEN:
            bestaetigung = Protokoll.nachricht_erstellen(VERBINDUNG_BESTAETIGT, {})
            self.senden(bestaetigung)

        elif typ == REGISTRIEREN:
            benutzername = daten.get(SCHLUESSEL_BENUTZERNAME, "")
            passwort = daten.get(SCHLUESSEL_PASSWORT, "")
            ergebnis = self.authentifizierung.registrieren(benutzername, passwort)
            if ergebnis["erfolg"]:
                antwort = Protokoll.nachricht_erstellen(REGISTRIEREN_ERFOLG, {SCHLUESSEL_NACHRICHT: ergebnis["nachricht"]})
            else:
                antwort = Protokoll.nachricht_erstellen(REGISTRIEREN_FEHLER, {SCHLUESSEL_NACHRICHT: ergebnis["nachricht"]})
            self.senden(antwort)

        elif typ == LOGIN:
            benutzername = daten.get(SCHLUESSEL_BENUTZERNAME, "")
            passwort = daten.get(SCHLUESSEL_PASSWORT, "")
            ergebnis = self.authentifizierung.einloggen(benutzername, passwort)
            if ergebnis["erfolg"]:
                self.spieler_id = ergebnis["spieler_id"]
                letzter_charakter_id = self.datenbank.letzten_charakter_laden(self.spieler_id)
                antwort_daten = {
                    SCHLUESSEL_SPIELER_ID: self.spieler_id,
                    SCHLUESSEL_NACHRICHT: ergebnis["nachricht"]
                }
                if letzter_charakter_id:
                    antwort_daten["letzter_charakter_id"] = letzter_charakter_id
                antwort = Protokoll.nachricht_erstellen(LOGIN_ERFOLG, antwort_daten)
            else:
                antwort = Protokoll.nachricht_erstellen(LOGIN_FEHLER, {SCHLUESSEL_NACHRICHT: ergebnis["nachricht"]})
            self.senden(antwort)

        elif typ == CHARAKTERE_LADEN and self.spieler_id:
            charaktere = self.charakter_verwaltung.charaktere_laden(self.spieler_id)
            antwort = Protokoll.nachricht_erstellen(CHARAKTERE_ANTWORT, {SCHLUESSEL_CHARAKTERE: charaktere})
            self.senden(antwort)

        elif typ == CHARAKTER_ERSTELLEN and self.spieler_id:
            name = daten.get(SCHLUESSEL_CHARAKTER_NAME, "")
            masterie = daten.get(SCHLUESSEL_MASTERIE, "")
            stats = daten.get(SCHLUESSEL_STATS, {})
            ergebnis = self.charakter_verwaltung.charakter_erstellen(self.spieler_id, name, masterie, stats)
            if ergebnis["erfolg"]:
                charakter_id = ergebnis.get("charakter_id")
                if charakter_id:
                    self.skill_verwaltung.charakter_initialisieren(charakter_id, masterie)
                antwort = Protokoll.nachricht_erstellen(CHARAKTER_ERSTELLT, {SCHLUESSEL_NACHRICHT: ergebnis["nachricht"]})
            else:
                antwort = Protokoll.nachricht_erstellen(CHARAKTER_ERSTELLEN_FEHLER, {SCHLUESSEL_NACHRICHT: ergebnis["nachricht"]})
            self.senden(antwort)

        elif typ == CHARAKTER_WAEHLEN and self.spieler_id:
            charakter_id = daten.get(SCHLUESSEL_CHARAKTER_ID)
            if charakter_id:
                charakter = self.charakter_verwaltung.charakter_laden(charakter_id)
                if charakter and charakter["spieler_id"] == self.spieler_id:
                    self.aktiver_charakter_id = charakter_id
                    self.datenbank.letzten_charakter_speichern(self.spieler_id, charakter_id)

                    klassen = self.datenbank.klassen_laden(charakter_id)
                    if not klassen:
                        masterie = charakter.get("masterie_1", "")
                        self.skill_verwaltung.charakter_initialisieren(charakter_id, masterie)

                    self.snapshot.erstellen_und_speichern(charakter_id)
                    antwort = Protokoll.nachricht_erstellen(CHARAKTER_GEWAEHLT, {SCHLUESSEL_CHARAKTER_ID: charakter_id})
                    self.senden(antwort)

        elif typ == CHARAKTER_DETAILS_LADEN and self.spieler_id and self.aktiver_charakter_id:
            charakter = self.charakter_verwaltung.charakter_laden(self.aktiver_charakter_id)
            if charakter and charakter["spieler_id"] == self.spieler_id:
                self.datenbank.abgelaufene_traenke_entfernen(self.aktiver_charakter_id)
                traeanke = self.datenbank.traeanke_laden(self.aktiver_charakter_id)
                abgeleitete_stats = StatBerechnung.stats_mit_traenken(charakter, traeanke)
                charakter_mit_stats = {**charakter, **abgeleitete_stats}
                charakter_mit_stats["traenke_anzahl"] = len(traeanke)
                antwort = Protokoll.nachricht_erstellen(CHARAKTER_DETAILS_ANTWORT, {SCHLUESSEL_CHARAKTER_DATEN: charakter_mit_stats})
                self.senden(antwort)

        elif typ == TESTKAMPF_STARTEN and self.spieler_id and self.aktiver_charakter_id:
            charakter = self.datenbank.snapshot_laden(self.aktiver_charakter_id)
            if charakter:
                level = charakter.get("level", 1)
                gegner = testkampfer_erstellen(level)
                seed = secrets.randbits(32)
                engine = KampfEngine(seed=seed)
                spieler_name = charakter.get("name", "Spieler")
                gegner_name = gegner.get("name", "Gegner")
                ergebnis = engine.kampf_berechnen(charakter, gegner, spieler_name, gegner_name)
                antwort = Protokoll.nachricht_erstellen(KAMPF_ERGEBNIS, {SCHLUESSEL_KAMPF_ERGEBNIS: ergebnis})
                self.senden(antwort)

        elif typ == QUESTS_LADEN and self.spieler_id and self.aktiver_charakter_id:
            try:
                charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
                level = charakter.get("level", 1) if charakter else 1
                print(f"[DEBUG] quests_laden für level {level}")
                quests = self.quest_verwaltung.quests_laden_oder_generieren(
                    self.spieler_id, self.aktiver_charakter_id, level)
                print(f"[DEBUG] quests geladen: {len(quests)}")
                aktive_quest = None
                for q in quests:
                    if q.get("gestartet_am") and not q.get("abgeschlossen"):
                        aktive_quest = q
                        break
                antwort = Protokoll.nachricht_erstellen(QUESTS_ANTWORT, {
                    SCHLUESSEL_QUESTS: quests,
                    "aktive_quest": aktive_quest
                })
                self.senden(antwort)
                print(f"[DEBUG] QUESTS_ANTWORT gesendet")
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[FEHLER] QUESTS_LADEN: {e}")

        elif typ == QUEST_ANNEHMEN and self.spieler_id and self.aktiver_charakter_id:
            quest_id = daten.get(SCHLUESSEL_QUEST_ID)
            if quest_id:
                ergebnis = self.quest_verwaltung.quest_annehmen(quest_id, self.spieler_id)
                antwort = Protokoll.nachricht_erstellen(QUEST_ANGENOMMEN, ergebnis)
                self.senden(antwort)

        elif typ == QUEST_AUFLOESEN and self.spieler_id and self.aktiver_charakter_id:
            quest_id = daten.get(SCHLUESSEL_QUEST_ID)
            if quest_id:
                snapshot = self.datenbank.snapshot_laden(self.aktiver_charakter_id)
                if snapshot:
                    ergebnis = self.quest_verwaltung.quest_aufloesen(quest_id, self.spieler_id, snapshot)
                    print(f"Quest Ergebnis: {ergebnis.get('erfolg')}")
                    print(f"Snapshot vorhanden: {self.datenbank.snapshot_laden(self.aktiver_charakter_id) is not None}")
                    if ergebnis.get("erfolg"):
                        mitglied = self.datenbank.gilde_mitglied_laden(self.aktiver_charakter_id)
                        gold = ergebnis["gold"]
                        xp = ergebnis["xp"]
                        if mitglied:
                            gilde = self.datenbank.gilde_laden(mitglied["gilden_id"])
                            if gilde:
                                gold = int(gold * (1 + gilde["gold_bonus"]))
                                xp = int(xp * (1 + gilde["xp_bonus"]))
                                steuer = self.gilde_verwaltung.steuer_einziehen(self.aktiver_charakter_id, gold)
                                ergebnis["steuer_abgezogen"] = steuer
                                gold -= steuer
                        self.datenbank.gold_hinzufuegen(self.aktiver_charakter_id, gold)
                        ergebnis["gold"] = gold
                        level_ergebnis = self.datenbank.xp_hinzufuegen(self.aktiver_charakter_id, xp)
                        ergebnis["xp"] = xp
                        ergebnis["level_up"] = self.datenbank.level_up_pruefen(self.aktiver_charakter_id)

                        if ergebnis.get("item_drop"):
                            inventar_anzahl = self.datenbank.inventar_anzahl(self.aktiver_charakter_id)
                            if inventar_anzahl < 20:
                                self.datenbank.item_hinzufuegen(
                                    self.aktiver_charakter_id, ergebnis["item_drop"])
                            else:
                                ergebnis["inventar_voll"] = True

                        # FRISCHEN Snapshot erstellen (nach Level-Up, Gold, Items)
                        self.snapshot.aktualisieren(self.aktiver_charakter_id)
                    antwort = Protokoll.nachricht_erstellen(QUEST_ERGEBNIS, {SCHLUESSEL_QUEST_ERGEBNIS: ergebnis})
                    self.senden(antwort)

        elif typ == QUEST_TIMER_REDUZIEREN and self.spieler_id and self.aktiver_charakter_id:
            quest_id = daten.get(SCHLUESSEL_QUEST_ID)
            if quest_id:
                quest = self.datenbank.quest_laden(quest_id)
                if quest and quest["spieler_id"] == self.spieler_id and quest.get("gestartet_am"):
                    timer_sekunden = quest.get("timer_sekunden", 300)
                    neuer_zeitstempel = datetime.now() - timedelta(seconds=timer_sekunden - 3)
                    self.datenbank.quest_starten(quest_id, neuer_zeitstempel.isoformat())
                    antwort = Protokoll.nachricht_erstellen(QUEST_TIMER_REDUZIERT, {
                        "quest_id": quest_id,
                        "gestartet_am": neuer_zeitstempel.isoformat()
                    })
                    self.senden(antwort)

        elif typ == INVENTAR_LADEN and self.spieler_id and self.aktiver_charakter_id:
            daten = self.datenbank.inventar_laden(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(INVENTAR_ANTWORT, daten)
            self.senden(antwort)

        elif typ == ITEM_AUSRUESTEN and self.spieler_id and self.aktiver_charakter_id:
            item_id = daten.get(SCHLUESSEL_ITEM_ID)
            slot = daten.get(SCHLUESSEL_SLOT)
            if item_id and slot:
                success = self.datenbank.item_ausruesten(self.aktiver_charakter_id, item_id, slot)
                if success:
                    self.snapshot.aktualisieren(self.aktiver_charakter_id)
                    daten = self.datenbank.inventar_laden(self.aktiver_charakter_id)
                    antwort = Protokoll.nachricht_erstellen(INVENTAR_ANTWORT, daten)
                    self.senden(antwort)

        elif typ == ITEM_ABLEGEN and self.spieler_id and self.aktiver_charakter_id:
            item_id = daten.get(SCHLUESSEL_ITEM_ID)
            if item_id:
                success = self.datenbank.item_ablegen_by_id(self.aktiver_charakter_id, item_id)
                if success:
                    self.snapshot.aktualisieren(self.aktiver_charakter_id)
                    daten = self.datenbank.inventar_laden(self.aktiver_charakter_id)
                    antwort = Protokoll.nachricht_erstellen(INVENTAR_ANTWORT, daten)
                    self.senden(antwort)

        elif typ == SKILLS_LADEN and self.spieler_id and self.aktiver_charakter_id:
            daten = self.skill_verwaltung.skills_laden(self.aktiver_charakter_id)
            antwort_daten = {
                "klassen": daten.get("klassen", []),
                "nodes": daten.get("nodes", {}),
                "skills": daten.get("skills", []),
                "ausgeruestet": daten.get("ausgeruestet", {"aktiv": [], "passiv": []}),
                "skill_punkte": daten.get("skill_punkte", 0)
            }
            antwort = Protokoll.nachricht_erstellen(SKILLS_ANTWORT, antwort_daten)
            self.senden(antwort)

        elif typ == SKILL_AUSRUESTEN and self.spieler_id and self.aktiver_charakter_id:
            skill_id = daten.get(SCHLUESSEL_SKILL_ID)
            slot_typ = daten.get(SCHLUESSEL_SKILL_SLOT) or daten.get("slot_typ")
            slot_nummer = daten.get("slot_nummer")
            if skill_id and slot_typ and slot_nummer:
                print(f"Skill ausrüsten: {skill_id} in {slot_typ} Slot {slot_nummer}")
                ergebnis = self.skill_verwaltung.skill_ausruesten(self.aktiver_charakter_id, skill_id, slot_typ, slot_nummer)
                print(f"Ergebnis: {ergebnis}")
                antwort = Protokoll.nachricht_erstellen(SKILL_AUSGERUESTET, ergebnis)
                self.senden(antwort)
                self.snapshot.aktualisieren(self.aktiver_charakter_id)

        elif typ == SKILL_ABLEGEN and self.spieler_id and self.aktiver_charakter_id:
            skill_id = daten.get(SCHLUESSEL_SKILL_ID)
            if skill_id:
                ergebnis = self.skill_verwaltung.skill_ablegen(self.aktiver_charakter_id, skill_id)
                antwort = Protokoll.nachricht_erstellen(SKILL_ABGELEGT, ergebnis)
                self.senden(antwort)
                self.snapshot.aktualisieren(self.aktiver_charakter_id)

        elif typ == KLASSEN_LADEN and self.spieler_id and self.aktiver_charakter_id:
            ergebnis = self.skill_verwaltung.skills_laden(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(KLASSEN_ANTWORT, ergebnis)
            self.senden(antwort)

        elif typ == NODE_SKILLEN and self.spieler_id and self.aktiver_charakter_id:
            klassen_id = daten.get(SCHLUESSEL_KLASSEN_ID)
            node_id = daten.get(SCHLUESSEL_NODE_ID)
            if klassen_id and node_id:
                try:
                    ergebnis = self.skill_verwaltung.node_skillen(
                        self.aktiver_charakter_id, klassen_id, node_id)
                    print(f"Node-Skillen Ergebnis: {ergebnis}")
                    antwort = Protokoll.nachricht_erstellen(NODE_GESKILLT, ergebnis)
                    self.senden(antwort)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.senden(Protokoll.nachricht_erstellen(NODE_GESKILLT, {
                        "erfolg": False, "nachricht": str(e)
                    }))

        elif typ == SPEZIALISIERUNG_WAEHLEN and self.spieler_id and self.aktiver_charakter_id:
            spez_id = daten.get("spezialisierung_id")
            if spez_id:
                charakter = self.datenbank.snapshot_laden(self.aktiver_charakter_id)
                if charakter:
                    ergebnis = self.skill_verwaltung.spezialisierung_waehlen(
                        self.aktiver_charakter_id, spez_id, charakter.get("level", 1))
                    antwort = Protokoll.nachricht_erstellen(SPEZIALISIERUNG_GEWAEHLT, ergebnis)
                    self.senden(antwort)
                    if ergebnis.get("erfolg"):
                        self.snapshot.aktualisieren(self.aktiver_charakter_id)

        elif typ == REISE_STARTEN and self.spieler_id and self.aktiver_charakter_id:
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            if charakter:
                max_dauer = daten.get("max_dauer", 4 * 3600)
                ergebnis = self.reise_verwaltung.reise_starten(
                    self.aktiver_charakter_id, charakter.get("level", 1), max_dauer)
                antwort = Protokoll.nachricht_erstellen(REISE_GESTARTET, ergebnis)
                self.senden(antwort)

        elif typ == REISE_STATUS_LADEN and self.spieler_id and self.aktiver_charakter_id:
            status = self.reise_verwaltung.reise_status(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(REISE_STATUS_ANTWORT, status)
            self.senden(antwort)

        elif typ == REISE_BELOHNUNGEN_LADEN and self.spieler_id and self.aktiver_charakter_id:
            snapshot = self.datenbank.snapshot_laden(self.aktiver_charakter_id)
            ergebnisse = self.reise_verwaltung.reise_quests_berechnen(self.aktiver_charakter_id, snapshot)
            offene = self.datenbank.offene_reise_belohnungen(self.aktiver_charakter_id)
            gesamt_gold = sum(q["belohnung_gold"] for q in offene)
            gesamt_xp = sum(q["belohnung_xp"] for q in offene)
            antwort = Protokoll.nachricht_erstellen(REISE_BELOHNUNGEN_ANTWORT, {
                SCHLUESSEL_KAMPF_ERGEBNISSE: ergebnisse,
                SCHLUESSEL_GESAMT_GOLD: gesamt_gold,
                SCHLUESSEL_GESAMT_XP: gesamt_xp,
                SCHLUESSEL_ANZAHL_QUESTS: len(ergebnisse)
            })
            self.senden(antwort)

        elif typ == REISE_BELOHNUNGEN_ABHOLEN and self.spieler_id and self.aktiver_charakter_id:
            belohnung = self.datenbank.reise_belohnungen_abholen(self.aktiver_charakter_id)
            if belohnung["gold"] > 0 or belohnung["xp"] > 0:
                self.snapshot.aktualisieren(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(REISE_BELOHNUNGEN_ABGEHOLT, belohnung)
            self.senden(antwort)

        elif typ == REISE_BEENDEN and self.spieler_id and self.aktiver_charakter_id:
            ergebnis = self.reise_verwaltung.reise_beenden(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(REISE_BEENDET, ergebnis)
            self.senden(antwort)

        elif typ == SHOP_LADEN and self.spieler_id:
            if not self.aktiver_charakter_id:
                self.senden(Protokoll.nachricht_erstellen(
                    "fehler", {"nachricht": "Kein aktiver Charakter"}))
                return
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            level = charakter.get("level", 1) if charakter else 1
            ergebnis = self.shop_verwaltung.shop_daten_laden(self.aktiver_charakter_id, level)
            antwort = Protokoll.nachricht_erstellen(SHOP_ANTWORT, ergebnis)
            self.senden(antwort)

        elif typ == SHOP_REROLL and self.spieler_id and self.aktiver_charakter_id:
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            level = charakter.get("level", 1) if charakter else 1
            gold = charakter.get("gold", 0) if charakter else 0
            ergebnis = self.shop_verwaltung.shop_reroll(self.aktiver_charakter_id, level, gold)
            antwort = Protokoll.nachricht_erstellen(SHOP_REROLL_ANTWORT, ergebnis)
            self.senden(antwort)
            if ergebnis.get("erfolg"):
                self.snapshot.aktualisieren(self.aktiver_charakter_id)

        elif typ == SHOP_KAUFEN and self.spieler_id and self.aktiver_charakter_id:
            slot = daten.get(SCHLUESSEL_SHOP_SLOT)
            if slot is None:
                return
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            gold = charakter.get("gold", 0) if charakter else 0
            ergebnis = self.shop_verwaltung.angebot_kaufen(self.aktiver_charakter_id, slot, gold)
            if ergebnis.get("erfolg"):
                antwort = Protokoll.nachricht_erstellen(SHOP_GEKAUFT, ergebnis)
                self.senden(antwort)
                self.snapshot.aktualisieren(self.aktiver_charakter_id)
            else:
                antwort = Protokoll.nachricht_erstellen(SHOP_KAUFEN_FEHLER, {"nachricht": ergebnis.get("nachricht")})
                self.senden(antwort)

        elif typ == TRANK_KAUFEN and self.spieler_id and self.aktiver_charakter_id:
            slot = daten.get(SCHLUESSEL_SHOP_SLOT)
            if slot is None:
                return
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            gold = charakter.get("gold", 0) if charakter else 0
            ergebnis = self.shop_verwaltung.trank_kaufen(self.aktiver_charakter_id, slot, gold)
            if ergebnis.get("erfolg"):
                antwort = Protokoll.nachricht_erstellen(TRANK_GEKAUFT, ergebnis)
                self.senden(antwort)
                self.snapshot.aktualisieren(self.aktiver_charakter_id)
            else:
                antwort = Protokoll.nachricht_erstellen(TRANK_KAUFEN_FEHLER, {"nachricht": ergebnis.get("nachricht")})
                self.senden(antwort)

        elif typ == TRANK_ENTFERNEN and self.spieler_id and self.aktiver_charakter_id:
            trank_id = daten.get(SCHLUESSEL_TRANK_ID)
            if trank_id is None:
                return
            self.datenbank.trank_entfernen(self.aktiver_charakter_id, trank_id)
            self.snapshot.aktualisieren(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(TRANK_ENTFERNT, {"erfolg": True})
            self.senden(antwort)

        elif typ == ARENA_LADEN and self.spieler_id and self.aktiver_charakter_id:
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            if charakter:
                gegner = self.arena_verwaltung.gegner_laden(self.aktiver_charakter_id, charakter.get("level", 1))
                stats = self.datenbank.arena_stats_laden(self.aktiver_charakter_id)
                rang = rang_berechnen(stats["rang_punkte"])
                antwort = Protokoll.nachricht_erstellen(ARENA_ANTWORT, {
                    "gegner": gegner,
                    "stats": stats,
                    "rang": rang,
                    "arena_shop": ARENA_SHOP
                })
                self.senden(antwort)

        elif typ == ARENA_KAMPF_STARTEN and self.spieler_id and self.aktiver_charakter_id:
            gegner_id = daten.get(SCHLUESSEL_GEGNER_ID)
            if gegner_id:
                ergebnis = self.arena_verwaltung.kampf_starten(self.aktiver_charakter_id, gegner_id)
                if ergebnis.get("erfolg"):
                    gold = ergebnis.get("gold", 0)
                    xp = ergebnis.get("xp", 0)
                    mitglied = self.datenbank.gilde_mitglied_laden(self.aktiver_charakter_id)
                    if mitglied:
                        gilde = self.datenbank.gilde_laden(mitglied["gilden_id"])
                        if gilde:
                            gold = int(gold * (1 + gilde["gold_bonus"]))
                            xp = int(xp * (1 + gilde["xp_bonus"]))
                            steuer = self.gilde_verwaltung.steuer_einziehen(self.aktiver_charakter_id, gold)
                            gold -= steuer
                            ergebnis["steuer_abgezogen"] = steuer
                    ergebnis["gold"] = gold
                    ergebnis["xp"] = xp
                    level_ergebnis = self.datenbank.level_up_pruefen(self.aktiver_charakter_id)
                    ergebnis["level_up"] = level_ergebnis
                antwort = Protokoll.nachricht_erstellen(ARENA_KAMPF_ERGEBNIS, ergebnis)
                self.senden(antwort)
                if ergebnis.get("erfolg"):
                    self.snapshot.aktualisieren(self.aktiver_charakter_id)

        elif typ == ARENA_SHOP_KAUFEN and self.spieler_id and self.aktiver_charakter_id:
            artikel_id = daten.get(SCHLUESSEL_ARTIKEL_ID)
            if artikel_id:
                ergebnis = self.arena_verwaltung.arena_shop_kaufen(self.aktiver_charakter_id, artikel_id)
                antwort = Protokoll.nachricht_erstellen(ARENA_SHOP_GEKAUFT, ergebnis)
                self.senden(antwort)

        elif typ == ARENA_VERZAUBERN and self.spieler_id and self.aktiver_charakter_id:
            item_id = daten.get(SCHLUESSEL_ITEM_ID)
            if item_id:
                ergebnis = self.arena_verwaltung.item_verzaubern(self.aktiver_charakter_id, item_id)
                antwort = Protokoll.nachricht_erstellen(ARENA_VERZAUBERT, ergebnis)
                self.senden(antwort)

        elif typ == GILDE_LADEN and self.spieler_id and self.aktiver_charakter_id:
            daten = self.gilde_verwaltung.gilde_daten_laden(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(GILDE_ANTWORT, daten)
            self.senden(antwort)

        elif typ == GILDE_ERSTELLEN and self.spieler_id and self.aktiver_charakter_id:
            name = daten.get(SCHLUESSEL_GILDEN_NAME)
            beschreibung = daten.get("beschreibung", "")
            ergebnis = self.gilde_verwaltung.gilde_erstellen(self.aktiver_charakter_id, name, beschreibung)
            antwort = Protokoll.nachricht_erstellen(GILDE_ERSTELLT, ergebnis)
            self.senden(antwort)

        elif typ == GILDE_BEITRETEN and self.spieler_id and self.aktiver_charakter_id:
            gilden_id = daten.get(SCHLUESSEL_GILDEN_ID)
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            ergebnis = self.gilde_verwaltung.gilde_beitreten(
                self.aktiver_charakter_id, gilden_id, charakter["name"])
            antwort = Protokoll.nachricht_erstellen(GILDE_BEIGETRETEN, ergebnis)
            self.senden(antwort)

        elif typ == GILDE_VERLASSEN and self.spieler_id and self.aktiver_charakter_id:
            charakter = self.datenbank.charakter_laden(self.aktiver_charakter_id)
            ergebnis = self.gilde_verwaltung.gilde_verlassen(
                self.aktiver_charakter_id, charakter["name"])
            antwort = Protokoll.nachricht_erstellen(GILDE_VERLASSEN_OK, ergebnis)
            self.senden(antwort)

        elif typ == GILDE_STEUER_SETZEN and self.spieler_id and self.aktiver_charakter_id:
            steuer = daten.get(SCHLUESSEL_STEUER)
            ergebnis = self.gilde_verwaltung.steuer_setzen(self.aktiver_charakter_id, steuer)
            antwort = Protokoll.nachricht_erstellen(GILDE_STEUER_OK, ergebnis)
            self.senden(antwort)

        elif typ == GILDE_RANG_SETZEN and self.spieler_id and self.aktiver_charakter_id:
            ziel_id = daten.get(SCHLUESSEL_ZIEL_ID)
            rang = daten.get(SCHLUESSEL_RANG)
            ergebnis = self.gilde_verwaltung.rang_setzen(self.aktiver_charakter_id, ziel_id, rang)
            antwort = Protokoll.nachricht_erstellen(GILDE_RANG_OK, ergebnis)
            self.senden(antwort)

        elif typ == GILDE_KICK and self.spieler_id and self.aktiver_charakter_id:
            ziel_id = daten.get(SCHLUESSEL_ZIEL_ID)
            ergebnis = self.gilde_verwaltung.mitglied_kicken(self.aktiver_charakter_id, ziel_id)
            antwort = Protokoll.nachricht_erstellen(GILDE_KICK_OK, ergebnis)
            self.senden(antwort)

        elif typ == GILDE_AUFSTEIGEN and self.spieler_id and self.aktiver_charakter_id:
            ergebnis = self.gilde_verwaltung.stufe_aufsteigen(self.aktiver_charakter_id)
            antwort = Protokoll.nachricht_erstellen(GILDE_AUFGESTIEGEN, ergebnis)
            self.senden(antwort)

    def senden(self, nachricht: dict):
        try:
            Protokoll.senden(self.socket, nachricht)
        except Exception as e:
            print(f"Senden-Fehler (Verbindung {self.verbindungs_id}): {e}")
            self.trennen()

    def trennen(self):
        self.laufend = False
        if self.server and self.verbindungs_id in self.server.verbindungen:
            del self.server.verbindungen[self.verbindungs_id]
        try:
            self.socket.close()
        except Exception:
            pass
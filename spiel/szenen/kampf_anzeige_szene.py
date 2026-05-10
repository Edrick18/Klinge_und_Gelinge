"""
spiel/szenen/kampf_anzeige_szene.py - Animierte Kampf-Anzeige

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import KAMPF_ERGEBNIS, SCHLUESSEL_KAMPF_ERGEBNIS
from spiel.systeme.kampf_typen import (
    EREIGNIS_ANGRIFF, EREIGNIS_KRIT, EREIGNIS_AUSGEWICHEN,
    EREIGNIS_FAULE, EREIGNIS_KAMPFENDE,
    EREIGNIS_SKILL_AKTIV, EREIGNIS_STATUS_EFFEKT
)
from spiel.systeme.item_typen import ITEM_RARITAET_FARBE


class KampfAnzeigeSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, kampf_ergebnis: dict, spieler_name: str = "Spieler", gegner_name: str = "Gegner"):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.kampf_ergebnis = kampf_ergebnis
        self.spieler_name = spieler_name
        self.gegner_name = gegner_name

        self.ereignisse = kampf_ergebnis.get("ereignisse", [])
        self.aktueller_index = 0
        self.animations_timer = 0.0
        self.geschwindigkeit = 1.0

        erste_ereignisse = kampf_ergebnis.get("ereignisse", [])
        self.hp_max_spieler = erste_ereignisse[0].get("hp_max", 100) if erste_ereignisse else 100
        self.hp_max_gegner = self.hp_max_spieler

        self.hp_spieler_ziel = self.hp_max_spieler
        self.hp_gegner_ziel = self.hp_max_gegner
        self.hp_spieler_angezeigt = self.hp_max_spieler
        self.hp_gegner_angezeigt = self.hp_max_gegner

        self.log_zeilen = []
        self.scroll_offset = 0
        self.kampf_beendet = False

        self.gesamtschaden_spieler = 0
        self.krits_spieler = 0
        self.kampf_dauer = 0.0

        ausgeruestete = kampf_ergebnis.get("ausgeruestete_skills", {})
        self.skill_slots = {
            "aktiv": ausgeruestete.get("aktiv", [None, None, None]),
            "passiv": ausgeruestete.get("passiv", [None, None])
        }
        self.cooldowns = {}
        for slot in self.skill_slots.get("aktiv", []):
            if slot:
                skill_def = slot.get("definition", {})
                cd = skill_def.get("cooldown", 0)
                self.cooldowns[slot["skill_id"]] = [0, cd]

        self.mana_spieler = 0
        self.mana_max_spieler = 0
        for e in self.ereignisse:
            if "mana_danach" in e:
                self.mana_spieler = e.get("mana_danach", 100)
                self.mana_max_spieler = e.get("mana_max", 100)
                break

        self._layout_berechnen()

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(14, int(h * 0.022)))
        self.schrift_normal = pygame.font.Font(None, max(20, int(h * 0.03)))
        self.schrift_gross = pygame.font.Font(None, max(36, int(h * 0.055)))

        self.hp_balken_breite = int(b * 0.25)
        self.hp_balken_hoehe = int(h * 0.04)

        self.hp_bereich_y = 0
        self.hp_bereich_hoehe = int(h * 0.20)

        self.log_rect = pygame.Rect(
            int(b * 0.25),
            int(h * 0.33),
            int(b * 0.50),
            int(h * 0.25)
        )
        self.zeilen_hoehe = int(h * 0.032)

        self.ergebnis_y = int(h * 0.61)
        self.stats_y = int(h * 0.67)

        self.item_header_y = int(h * 0.73)
        self.item_name_y = int(h * 0.78)
        self.affix1_y = int(h * 0.83)
        self.affix2_y = int(h * 0.87)
        self.enter_button_y = int(h * 0.92)
        self.enter_button_ohne_item_y = int(h * 0.75)

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.kampf_beendet:
                    while self.aktueller_index < len(self.ereignisse):
                        self._naechstes_ereignis_verarbeiten()
                    self.kampf_beendet = True
                elif event.key == pygame.K_RETURN and self.kampf_beendet:
                    self._zurueck_zur_uebersicht()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.geschwindigkeit = min(4.0, self.geschwindigkeit + 0.5)
                elif event.key == pygame.K_MINUS:
                    self.geschwindigkeit = max(0.5, self.geschwindigkeit - 0.5)
                elif event.key == pygame.K_UP:
                    max_sichtbar = self.log_rect.height // self.zeilen_hoehe
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.key == pygame.K_DOWN:
                    max_sichtbar = self.log_rect.height // self.zeilen_hoehe
                    self.scroll_offset = min(max(0, len(self.log_zeilen) - max_sichtbar), self.scroll_offset + 1)
            elif event.type == pygame.MOUSEWHEEL:
                max_sichtbar = self.log_rect.height // self.zeilen_hoehe
                if event.y > 0:
                    self.scroll_offset = max(0, self.scroll_offset - 2)
                else:
                    self.scroll_offset = min(max(0, len(self.log_zeilen) - max_sichtbar), self.scroll_offset + 2)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.kampf_beendet:
                    self._zurueck_zur_uebersicht()

    def _zurueck_zur_uebersicht(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        self.szenen_manager.szene_wechseln(CharakterUebersichtSzene(
            self.szenen_manager, self.netzwerk_client, None
        ))

    def _naechstes_ereignis_verarbeiten(self):
        if self.aktueller_index >= len(self.ereignisse):
            return

        ereignis = self.ereignisse[self.aktueller_index]
        self.aktueller_index += 1
        self.kampf_dauer = ereignis.get("zeit", 0)

        typ = ereignis.get("typ")

        if typ == EREIGNIS_FAULE:
            stufe = ereignis.get("stufe", 1)
            self.log_zeilen.append({"text": f"⚠ Fäule Stufe {stufe} — Kampftempo steigt!", "farbe": config.FARBE_WARNUNG})
        elif typ == EREIGNIS_AUSGEWICHEN:
            name = self.spieler_name if ereignis.get("angreifer") == "gegner" else self.gegner_name
            self.log_zeilen.append({"text": f"{name} weicht aus!", "farbe": config.FARBE_TEXT_GEDIMMT})
        elif typ in (EREIGNIS_ANGRIFF, EREIGNIS_KRIT):
            name = ereignis.get("angreifer", "unbekannt")
            schaden = ereignis.get("schaden", 0)
            hp = ereignis.get("hp_danach", 0)
            hp_max = ereignis.get("hp_max", 100)

            if name == "spieler":
                self.hp_gegner_ziel = hp
                self.hp_max_gegner = hp_max
                name_anzeige = self.spieler_name
                if schaden > 0 and typ != EREIGNIS_AUSGEWICHEN:
                    self.gesamtschaden_spieler += schaden
                    if typ == EREIGNIS_KRIT:
                        self.krits_spieler += 1
            else:
                self.hp_spieler_ziel = hp
                self.hp_max_spieler = hp_max
                name_anzeige = self.gegner_name

            if typ == EREIGNIS_KRIT:
                farbe = config.FARBE_AKZENT
                text = f"{name_anzeige} KRITISCHER TREFFER für {schaden}!"
            else:
                farbe = config.FARBE_TEXT
                text = f"{name_anzeige} trifft für {schaden} Schaden"

            self.log_zeilen.append({"text": text, "farbe": farbe})
        elif typ == EREIGNIS_KAMPFENDE:
            self.kampf_beendet = True

        elif typ == EREIGNIS_SKILL_AKTIV:
            skill_id = ereignis.get("skill_id")
            skill_name = ereignis.get("skill_name", "Skill")
            schaden = ereignis.get("schaden", 0)

            if skill_id in self.cooldowns:
                self.cooldowns[skill_id][0] = self.cooldowns[skill_id][1]

            if "mana_danach" in ereignis:
                self.mana_spieler = ereignis["mana_danach"]

            if ereignis.get("angreifer") == "spieler":
                text = f"✦ {skill_name} — {schaden} Schaden!"
                farbe = (180, 100, 220)
            else:
                text = f"✦ Gegner: {skill_name} — {schaden} Schaden!"
                farbe = (220, 80, 80)
            self.log_zeilen.append({"text": text, "farbe": farbe})

            if ereignis.get("angreifer") == "spieler":
                self.hp_gegner_ziel = ereignis.get("hp_danach", self.hp_gegner_ziel)
            else:
                self.hp_spieler_ziel = ereignis.get("hp_danach", self.hp_spieler_ziel)

        elif typ == EREIGNIS_STATUS_EFFEKT:
            effekt_typ = ereignis.get("effekt_typ", "")
            schaden = ereignis.get("schaden", 0)
            ziel = ereignis.get("ziel", "")
            text = f"☠ {effekt_typ.capitalize()}: {schaden} Schaden"
            self.log_zeilen.append({"text": text, "farbe": config.FARBE_WARNUNG})
            if ziel == "spieler":
                self.hp_spieler_ziel = ereignis.get("hp_danach", self.hp_spieler_ziel)
            else:
                self.hp_gegner_ziel = ereignis.get("hp_danach", self.hp_gegner_ziel)

        max_sichtbar = self.log_rect.height // self.zeilen_hoehe
        if len(self.log_zeilen) > max_sichtbar + 5:
            self.log_zeilen = self.log_zeilen[-(max_sichtbar + 5):]
        self.scroll_offset = max(0, len(self.log_zeilen) - max_sichtbar)

    def updaten(self, delta_zeit: float):
        self.hp_spieler_angezeigt += (self.hp_spieler_ziel - self.hp_spieler_angezeigt) * min(1.0, delta_zeit * 8)
        self.hp_gegner_angezeigt += (self.hp_gegner_ziel - self.hp_gegner_angezeigt) * min(1.0, delta_zeit * 8)

        for skill_id in self.cooldowns:
            cd_aktuell, cd_max = self.cooldowns[skill_id]
            if cd_aktuell > 0:
                self.cooldowns[skill_id][0] = max(
                    0,
                    cd_aktuell - delta_zeit * self.geschwindigkeit * cd_max / 2
                )

        if self.kampf_beendet:
            return

        self.animations_timer += delta_zeit
        intervall = 0.5 / self.geschwindigkeit
        if self.animations_timer >= intervall:
            self.animations_timer = 0.0
            self._naechstes_ereignis_verarbeiten()

    def zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        flaeche.fill(config.FARBE_HINTERGRUND)

        pygame.draw.rect(flaeche, config.FARBE_PANEL, (50, self.hp_bereich_y, self.hp_balken_breite, self.hp_bereich_hoehe))
        hp_spieler_balken = int(self.hp_balken_breite * (self.hp_spieler_angezeigt / max(self.hp_max_spieler, 1)))
        pygame.draw.rect(flaeche, config.FARBE_HP, (50, self.hp_bereich_y + 20, hp_spieler_balken, self.hp_balken_hoehe))
        pygame.draw.rect(flaeche, config.FARBE_RAND, (50, self.hp_bereich_y + 20, self.hp_balken_breite, self.hp_balken_hoehe), 2)
        spieler_name = self.schrift_normal.render(self.spieler_name, True, config.FARBE_TEXT)
        flaeche.blit(spieler_name, (50, self.hp_bereich_y))
        hp_spieler_text = self.schrift_klein.render(f"{int(self.hp_spieler_angezeigt)}/{self.hp_max_spieler}", True, config.FARBE_TEXT)
        flaeche.blit(hp_spieler_text, (50, self.hp_bereich_y + self.hp_balken_hoehe + 25))

        pygame.draw.rect(flaeche, config.FARBE_PANEL, (b - 50 - self.hp_balken_breite, self.hp_bereich_y, self.hp_balken_breite, self.hp_bereich_hoehe))
        hp_gegner_balken = int(self.hp_balken_breite * (self.hp_gegner_angezeigt / max(self.hp_max_gegner, 1)))
        pygame.draw.rect(flaeche, config.FARBE_HP, (b - 50 - self.hp_balken_breite, self.hp_bereich_y + 20, hp_gegner_balken, self.hp_balken_hoehe))
        pygame.draw.rect(flaeche, config.FARBE_RAND, (b - 50 - self.hp_balken_breite, self.hp_bereich_y + 20, self.hp_balken_breite, self.hp_balken_hoehe), 2)
        gegner_name = self.schrift_normal.render(self.gegner_name, True, config.FARBE_TEXT)
        gegner_name_rect = gegner_name.get_rect(topright=(b - 50, self.hp_bereich_y))
        flaeche.blit(gegner_name, gegner_name_rect)
        hp_gegner_text = self.schrift_klein.render(f"{int(self.hp_gegner_angezeigt)}/{self.hp_max_gegner}", True, config.FARBE_TEXT)
        hp_gegner_text_rect = hp_gegner_text.get_rect(topright=(b - 50, self.hp_bereich_y + self.hp_balken_hoehe + 25))
        flaeche.blit(hp_gegner_text, hp_gegner_text_rect)

        vs_text = self.schrift_gross.render("VS", True, config.FARBE_AKZENT)
        vs_rect = vs_text.get_rect(center=(b // 2, self.hp_bereich_y + self.hp_bereich_hoehe // 2))
        flaeche.blit(vs_text, vs_rect)

        self._skill_leiste_zeichnen(flaeche)

        log_surface = pygame.Surface((self.log_rect.width, self.log_rect.height))
        log_surface.fill(config.FARBE_PANEL)

        max_sichtbar = self.log_rect.height // self.zeilen_hoehe
        sichtbare_zeilen = self.log_zeilen[self.scroll_offset:self.scroll_offset + max_sichtbar]
        for i, log_eintrag in enumerate(sichtbare_zeilen):
            text = self.schrift_klein.render(log_eintrag["text"], True, log_eintrag["farbe"])
            text_rect = text.get_rect(center=(self.log_rect.width // 2, i * self.zeilen_hoehe + self.zeilen_hoehe // 2))
            log_surface.blit(text, text_rect)

        flaeche.blit(log_surface, self.log_rect.topleft)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.log_rect, 1)

        if not self.kampf_beendet:
            skip_text = self.schrift_klein.render("LEERTASTE: Überspringen | MAUSRAD/PFEILTASTEN: Scrollen", True, config.FARBE_TEXT_GEDIMMT)
            skip_rect = skip_text.get_rect(center=(b // 2, h - 30))
            flaeche.blit(skip_text, skip_rect)

            speed_text = self.schrift_klein.render(f"Geschwindigkeit: {self.geschwindigkeit}x  (+/-)", True, config.FARBE_TEXT_GEDIMMT)
            speed_rect = speed_text.get_rect(center=(b // 2, h - 15))
            flaeche.blit(speed_text, speed_rect)
        else:
            if self.kampf_ergebnis.get("gewonnen", False):
                ergebnis_text = self.schrift_gross.render("SIEG!", True, config.FARBE_ERFOLG)
            else:
                ergebnis_text = self.schrift_gross.render("NIEDERLAGE", True, config.FARBE_HP)
            ergebnis_rect = ergebnis_text.get_rect(center=(b // 2, self.ergebnis_y))
            flaeche.blit(ergebnis_text, ergebnis_rect)

            stats_text = self.schrift_klein.render(f"Schaden: {self.gesamtschaden_spieler} | Krits: {self.krits_spieler} | Dauer: {self.kampf_dauer}s", True, config.FARBE_TEXT_GEDIMMT)
            stats_rect = stats_text.get_rect(center=(b // 2, self.stats_y))
            flaeche.blit(stats_text, stats_rect)

        button_y = self.item_header_y
        gold = self.kampf_ergebnis.get("gold", 0)
        xp = self.kampf_ergebnis.get("xp", 0)
        level_up = self.kampf_ergebnis.get("level_up", {})

        if gold > 0 or xp > 0:
            belohnung_text = ""
            if gold > 0:
                belohnung_text += f"💰 +{gold} Gold"
            if xp > 0:
                if belohnung_text:
                    belohnung_text += " | "
                belohnung_text += f"✨ +{xp} XP"
            belohnung_render = self.schrift_normal.render(belohnung_text, True, config.FARBE_XP)
            belohnung_rect = belohnung_render.get_rect(center=(b // 2, button_y))
            flaeche.blit(belohnung_render, belohnung_rect)
            button_y += 30

        if level_up and level_up.get("level_up", False):
            level_text = self.schrift_gross.render("⬆ LEVEL UP!", True, config.FARBE_AKZENT)
            level_rect = level_text.get_rect(center=(b // 2, button_y))
            flaeche.blit(level_text, level_rect)
            button_y += 40

        button_y = self.enter_button_ohne_item_y

        item_drop = self.kampf_ergebnis.get("item_drop")
        if item_drop:
            raritaet = item_drop.get("raritaet", "normal")
            raritaet_farbe = ITEM_RARITAET_FARBE.get(raritaet, (180, 180, 180))

            item_header = self.schrift_klein.render("📦 ITEM GEFUNDEN!", True, raritaet_farbe)
            item_header_rect = item_header.get_rect(center=(b // 2, self.item_header_y))
            flaeche.blit(item_header, item_header_rect)

            item_name = self.schrift_normal.render(item_drop.get("name", ""), True, raritaet_farbe)
            item_name_rect = item_name.get_rect(center=(b // 2, self.item_name_y))
            flaeche.blit(item_name, item_name_rect)

            prefixe = item_drop.get("prefixe", [])
            suffixe = item_drop.get("suffixe", [])
            alle_affixe = prefixe + suffixe
            if len(alle_affixe) > 0:
                affix1_text = f"+ {alle_affixe[0]['wert']} {alle_affixe[0]['typ'].replace('_', ' ')}"
                affix1 = self.schrift_klein.render(affix1_text, True, config.FARBE_TEXT_GEDIMMT)
                affix1_rect = affix1.get_rect(center=(b // 2, self.affix1_y))
                flaeche.blit(affix1, affix1_rect)
            if len(alle_affixe) > 1:
                affix2_text = f"+ {alle_affixe[1]['wert']}{alle_affixe[1]['einheit']} {alle_affixe[1]['typ'].replace('_bonus', '').replace('_', ' ')}"
                affix2 = self.schrift_klein.render(affix2_text, True, config.FARBE_TEXT_GEDIMMT)
                affix2_rect = affix2.get_rect(center=(b // 2, self.affix2_y))
                flaeche.blit(affix2, affix2_rect)
            elif len(alle_affixe) > 2:
                affix2 = self.schrift_klein.render("...", True, config.FARBE_TEXT_GEDIMMT)
                affix2_rect = affix2.get_rect(center=(b // 2, self.affix2_y))
                flaeche.blit(affix2, affix2_rect)

            button_y = self.enter_button_y

        if self.kampf_ergebnis.get("inventar_voll"):
            voll_text = self.schrift_klein.render("⚠ Inventar voll — Item verloren!", True, config.FARBE_WARNUNG)
            voll_rect = voll_text.get_rect(center=(b // 2, button_y))
            flaeche.blit(voll_text, voll_rect)
            button_y = min(button_y + 25, int(h * 0.95))

        weiter_text = self.schrift_normal.render("ENTER: Weiter", True, config.FARBE_TEXT)
        weiter_rect = weiter_text.get_rect(center=(b // 2, button_y))
        flaeche.blit(weiter_text, weiter_rect)

    def _skill_leiste_zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        icon_breite = int(b * 0.07)
        icon_hoehe = int(h * 0.10)
        abstand = int(b * 0.01)
        leiste_y = int(h * 0.21)

        mana_balken_breite = int(b * 0.25)
        mana_x = (b - mana_balken_breite) // 2
        mana_y = leiste_y - int(h * 0.025)
        pygame.draw.rect(flaeche, config.FARBE_PANEL,
            (mana_x, mana_y, mana_balken_breite, int(h * 0.015)))
        if self.mana_max_spieler > 0:
            mana_fuell = int(mana_balken_breite * (self.mana_spieler / self.mana_max_spieler))
            pygame.draw.rect(flaeche, config.FARBE_MANA,
                (mana_x, mana_y, mana_fuell, int(h * 0.015)))
        pygame.draw.rect(flaeche, config.FARBE_RAND,
            (mana_x, mana_y, mana_balken_breite, int(h * 0.015)), 1)
        mana_text = self.schrift_klein.render(
            f"Mana: {int(self.mana_spieler)}/{self.mana_max_spieler}",
            True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(mana_text, (mana_x, mana_y - 18))

        gesamt_breite = 5 * icon_breite + 4 * abstand + int(b * 0.02)
        start_x = (b - gesamt_breite) // 2

        for i in range(3):
            x = start_x + i * (icon_breite + abstand)
            slot = self.skill_slots["aktiv"][i] if i < len(self.skill_slots["aktiv"]) else None
            self._skill_icon_zeichnen(flaeche, x, leiste_y, icon_breite, icon_hoehe, slot, "aktiv")

        trenner_x = start_x + 3 * (icon_breite + abstand) - abstand // 2
        pygame.draw.line(flaeche, config.FARBE_RAND,
            (trenner_x, leiste_y), (trenner_x, leiste_y + icon_hoehe), 1)

        for i in range(2):
            x = start_x + int(b * 0.02) + (3 + i) * (icon_breite + abstand)
            slot = self.skill_slots["passiv"][i] if i < len(self.skill_slots["passiv"]) else None
            self._skill_icon_zeichnen(flaeche, x, leiste_y, icon_breite, icon_hoehe, slot, "passiv")

    def _skill_icon_zeichnen(self, flaeche: pygame.Surface, x: int, y: int, breite: int, hoehe: int, slot: dict, slot_typ: str):
        rand_farbe = config.FARBE_AKZENT if slot_typ == "aktiv" else config.FARBE_MANA
        pygame.draw.rect(flaeche, config.FARBE_PANEL, (x, y, breite, hoehe))
        pygame.draw.rect(flaeche, rand_farbe if slot else config.FARBE_RAND,
            (x, y, breite, hoehe), 1)

        if not slot:
            leer = self.schrift_klein.render("---", True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(leer, leer.get_rect(center=(x + breite//2, y + hoehe//2)))
            return

        skill_def = slot.get("definition", {})
        skill_id = slot.get("skill_id", "")
        name = skill_def.get("name", "?")[:8]

        name_text = self.schrift_klein.render(name, True, config.FARBE_TEXT)
        flaeche.blit(name_text, name_text.get_rect(center=(x + breite//2, y + int(hoehe * 0.25))))

        typ_text = self.schrift_klein.render(
            "A" if slot_typ == "aktiv" else "P",
            True, rand_farbe)
        flaeche.blit(typ_text, (x + 4, y + 4))

        if slot_typ == "aktiv":
            cd_y = y + hoehe - int(hoehe * 0.20)
            cd_breite = breite - 8
            pygame.draw.rect(flaeche, config.FARBE_RAND, (x + 4, cd_y, cd_breite, int(hoehe * 0.12)))

            cd_aktuell, cd_max = self.cooldowns.get(skill_id, [0, 1])
            if cd_max > 0:
                abgelaufen = cd_max - cd_aktuell
                fuell = int(cd_breite * (abgelaufen / cd_max))
                farbe = config.FARBE_AKZENT if cd_aktuell <= 0 else config.FARBE_MANA
                pygame.draw.rect(flaeche, farbe, (x + 4, cd_y, fuell, int(hoehe * 0.12)))
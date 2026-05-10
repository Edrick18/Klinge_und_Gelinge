"""
spiel/szenen/inventar_szene.py - Inventar-Ansicht

Komplette Implementierung gemäß Aufgabenbeschreibung:
- Equipment-Slots links (6 Slots: Kopf, Brust, Waffe, Beine, Ring, Amulett)
- Grid mitte (4x5 = 20 Items)
- Details rechts
- Anlegen/Ablegen Buttons
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import INVENTAR_LADEN, INVENTAR_ANTWORT, SCHLUESSEL_ITEMS, ITEM_AUSRUESTEN, ITEM_ABLEGEN, ARENA_VERZAUBERN, ARENA_VERZAUBERT, SCHLUESSEL_ITEM_ID
from spiel.systeme.item_typen import ITEM_RARITAET_FARBE


EQUIPMENT_SLOTS = [
    ("helm", "Helm"), ("brust", "Brust"),
    ("handschuhe", "Handschuhe"), ("schuhe", "Schuhe"),
    ("amulett", "Amulett"), ("ring_1", "Ring 1"),
    ("ring_2", "Ring 2"), ("waffe", "Waffe"),
    ("offhand", "Offhand")
]


class InventarSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_daten):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten
        self.items = []
        self.ausgeruestet = {}
        self.selected_index = None
        self.selected_equipment_slot = None
        self.selected_item = None
        self.filter_slot = None
        self.geladen = False
        self.vergleich_item = None  # Item zum Vergleich (ausgeruestetes Item im Slot)

        self._laden_angefordert = False
        self._layout_berechnen()

        self.schrift_gross = pygame.font.Font(None, 48)
        self.schrift_klein = pygame.font.Font(None, 24)
        self.schrift_sehr_klein = pygame.font.Font(None, 18)

    def _layout_berechnen(self):
        self.b = config.AUFLOESUNG_BREITE
        self.h = config.AUFLOESUNG_HOEHE

        verfuegbare_hoehe = int(self.h * 0.75)
        self.eq_slot_h = int(verfuegbare_hoehe / 9) - 4
        self.eq_slot_w = int(self.b * 0.12)
        self.eq_start_x = int(self.b * 0.02)
        self.eq_start_y = int(self.h * 0.12)
        self.eq_abstand_y = int(verfuegbare_hoehe / 9)

        self.eq_slot_rects = {}
        for i, (slot_id, slot_name) in enumerate(EQUIPMENT_SLOTS):
            self.eq_slot_rects[slot_id] = pygame.Rect(
                self.eq_start_x,
                self.eq_start_y + i * self.eq_abstand_y,
                self.eq_slot_w,
                self.eq_slot_h
            )

        # Grid mitte (4x5)
        self.slot_w = int(self.b * 0.08)
        self.slot_h = int(self.b * 0.08)
        self.abstand = int(self.b * 0.01)
        self.grid_cols = 4
        self.grid_rows = 5
        self.grid_start_x = int(self.b * 0.25)
        self.grid_start_y = int(self.h * 0.20)
        self.slot_rects = [
            (self.grid_start_x + c * (self.slot_w + self.abstand),
             self.grid_start_y + r * (self.slot_h + self.abstand))
            for r in range(self.grid_rows) for c in range(self.grid_cols)
        ]

        self.alle_anzeigen_btn = pygame.Rect(
            self.grid_start_x,
            self.grid_start_y - int(self.h * 0.06),
            int(self.b * 0.15),
            int(self.h * 0.04)
        )

        # Details rechts
        self.detail_x = int(self.b * 0.70)
        self.detail_y = 130
        self.detail_w = int(self.b * 0.28)
        self.detail_h = 490
        self.detail_rect = pygame.Rect(self.detail_x, self.detail_y, self.detail_w, self.detail_h)

        # Buttons - drei gleichmäßig nebeneinander
        self.btn_h = 45
        self.btn_breite = (self.detail_w - 30) // 3
        button_y = self.detail_y + self.detail_h + 10
        self.anlegen_btn = pygame.Rect(self.detail_x + 10, button_y, self.btn_breite, self.btn_h)
        self.ablegen_btn = pygame.Rect(self.detail_x + 10 + self.btn_breite + 5, button_y, self.btn_breite, self.btn_h)
        self.verzaubern_btn = pygame.Rect(self.detail_x + 10 + (self.btn_breite + 5) * 2, button_y, self.btn_breite, self.btn_h)
        self.ehrenmarken = 0

        # Zurück
        self.back_button = pygame.Rect(20, self.h - 35, 100, 28)

        self.debug = False

    def _gefilterte_items(self):
        if self.filter_slot is None:
            return [item for item in self.items if not item.get("ausgeruestet", False)]
        return [item for item in self.items
                if item.get("slot") == self.filter_slot
                and not item.get("ausgeruestet", False)]

    def _vergleich_pfeil(self, wert_neu, wert_alt):
        """Gibt ▲ wenn neu besser, ▼ wenn neu schlechter, sonst ''."""
        if wert_alt is None:
            return ""
        try:
            if float(wert_neu) > float(wert_alt):
                return "▲"
            elif float(wert_neu) < float(wert_alt):
                return "▼"
        except (ValueError, TypeError):
            pass
        return ""

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._zurueck_zur_uebersicht()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos

                    # Alle anzeigen Button
                    if self.alle_anzeigen_btn.collidepoint(mx, my):
                        self.filter_slot = None
                        self.selected_index = None
                        self.selected_item = None

                    # Equipment-Slots prüfen
                    for slot_id, rect in self.eq_slot_rects.items():
                        if rect.collidepoint(mx, my):
                            self.filter_slot = slot_id
                            self.selected_index = None
                            self.selected_item = None
                            self.selected_equipment_slot = slot_id
                            break

                    # Grid-Items prüfen
                    gefiltert = self._gefilterte_items()
                    for idx, (x, y) in enumerate(self.slot_rects):
                        rect = pygame.Rect(x, y, self.slot_w, self.slot_h)
                        if rect.collidepoint(mx, my) and idx < len(gefiltert):
                            self.selected_index = idx
                            self.selected_item = gefiltert[idx]
                            self.selected_equipment_slot = None
                            # Vergleich: ist im gleichen Slot schon ein Item?
                            slot = gefiltert[idx].get("slot")
                            self.vergleich_item = self.ausgeruestet.get(slot) if slot else None
                            break

                    # Anlegen-Button
                    if self.anlegen_btn.collidepoint(mx, my) and self.selected_item is not None:
                        self._anlegen()

                    # Ablegen-Button
                    if self.ablegen_btn.collidepoint(mx, my) and self.selected_equipment_slot:
                        self._ablegen()

                    # Verzaubern-Button
                    if self.verzaubern_btn.collidepoint(mx, my) and self._can_verzaubern():
                        if self.ehrenmarken >= 5:
                            item_id = self.selected_item.get("id")
                            if item_id:
                                self.netzwerk_client.nachricht_senden(ARENA_VERZAUBERN, {
                                    SCHLUESSEL_ITEM_ID: item_id
                                })
                        else:
                            self.status_nachricht = "Nicht genug Ehrenmarken!"
                            self.status_farbe = config.FARBE_WARNUNG

                    # Zurück
                    if self.back_button.collidepoint(mx, my):
                        self._zurueck_zur_uebersicht()

    def _anlegen(self):
        item = self.selected_item
        if item is None:
            return
        slot = item.get("slot")
        if not slot:
            return
        self.netzwerk_client.nachricht_senden(ITEM_AUSRUESTEN, {
            "item_id": item.get("id"),
            "slot": slot
        })

    def _ablegen(self):
        if self.selected_equipment_slot is None:
            return

        item = self.ausgeruestet.get(self.selected_equipment_slot)
        if item is None:
            return
        self.netzwerk_client.nachricht_senden(ITEM_ABLEGEN, {
            "item_id": item.get("id")
        })

    def _can_verzaubern(self) -> bool:
        if not self.selected_item:
            return False
        item_typ = self.selected_item.get("typ", "")
        if item_typ in ("verzauberung", "schriftrolle", "trank", "verbrauch"):
            return False
        slot = self.selected_item.get("slot", "")
        if slot not in ("waffe", "helm", "brust", "handschuhe", "schuhe", "ring", "amulett"):
            return False
        if self.selected_item.get("verzaubert", False):
            return False
        return True

    def _zurueck_zur_uebersicht(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        self.szenen_manager.szene_wechseln(CharakterUebersichtSzene(
            self.szenen_manager, self.netzwerk_client, None, self.charakter_daten
        ))

    def updaten(self, delta_zeit: float):
        if not self._laden_angefordert:
            self.netzwerk_client.nachricht_senden(INVENTAR_LADEN, {})
            self._laden_angefordert = True

        while True:
            msg = self.netzwerk_client.nachricht_holen()
            if not msg:
                break
            typ = msg.get("typ")
            daten = msg.get("daten", {})

            if typ == INVENTAR_ANTWORT:
                self.items = daten.get(SCHLUESSEL_ITEMS, [])
                self.ausgeruestet = daten.get("ausgeruestet", {})
                self.geladen = True
                break
            elif typ in ("item_ausgeruestet", "item_abgelegt"):
                self.netzwerk_client.nachricht_senden(INVENTAR_LADEN, {})

            elif typ == ARENA_VERZAUBERT:
                if daten.get("erfolg"):
                    self.status_nachricht = "✓ Verzaubert! +15% Stats"
                    self.status_farbe = config.FARBE_ERFOLG
                    self.ehrenmarken = daten.get("ehrenmarken_rest", 0)
                    self.netzwerk_client.nachricht_senden(INVENTAR_LADEN, {})
                else:
                    self.status_nachricht = daten.get("nachricht", "Verzauberung fehlgeschlagen")
                    self.status_farbe = config.FARBE_WARNUNG

    def zeichnen(self, flaeche: pygame.Surface):
        b = self.b
        h = self.h
        flaeche.fill(config.FARBE_HINTERGRUND)

        title = self.schrift_gross.render("Inventar", True, config.FARBE_TEXT)
        flaeche.blit(title, title.get_rect(center=(b // 2, 50)))

        if not self.geladen:
            loading = self.schrift_gross.render("Lade Inventar…", True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(loading, loading.get_rect(center=(b // 2, h // 2)))
            return

        # === LINKS: Equipment-Slots ===
        for slot_id, slot_name in EQUIPMENT_SLOTS:
            rect = self.eq_slot_rects[slot_id]
            pygame.draw.rect(flaeche, config.FARBE_PANEL, rect)
            pygame.draw.rect(flaeche, config.FARBE_RAND, rect, 2)

            name_txt = self.schrift_sehr_klein.render(slot_name, True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(name_txt, (rect.x + 4, rect.y + 2))

            item = self.ausgeruestet.get(slot_id)
            if item:
                rar = item.get("raritaet", "normal")
                color = ITEM_RARITAET_FARBE.get(rar, (180, 180, 180))
                inner = rect.inflate(-8, -8)
                pygame.draw.rect(flaeche, color, inner, 2)
                item_name = item.get("name", "")[:12]
                txt = self.schrift_sehr_klein.render(item_name, True, color)
                flaeche.blit(txt, (rect.x + 6, rect.y + 20))

        # Filter-Anzeige
        gefiltert = self._gefilterte_items()
        if self.filter_slot:
            slot_name = next((name for sid, name in EQUIPMENT_SLOTS if sid == self.filter_slot), self.filter_slot)
            filter_txt = self.schrift_klein.render(f"Filter: {slot_name} ({len(gefiltert)} Items)", True, config.FARBE_AKZENT)
        else:
            filter_txt = self.schrift_klein.render(f"Alle Items ({len(gefiltert)} Items)", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(filter_txt, (self.grid_start_x, self.grid_start_y - int(self.h * 0.10)))

        # Alle anzeigen Button
        btn_rand = 2 if self.filter_slot else 1
        pygame.draw.rect(flaeche, config.FARBE_PANEL, self.alle_anzeigen_btn)
        pygame.draw.rect(flaeche, config.FARBE_AKZENT if self.filter_slot else config.FARBE_RAND, self.alle_anzeigen_btn, btn_rand)
        btn_text = "Alle anzeigen" if self.filter_slot else "Alle Items"
        btn_txt = self.schrift_sehr_klein.render(btn_text, True, config.FARBE_TEXT)
        flaeche.blit(btn_txt, btn_txt.get_rect(center=self.alle_anzeigen_btn.center))

        # === MITTE: Grid ===
        for idx, (x, y) in enumerate(self.slot_rects):
            rect = pygame.Rect(x, y, self.slot_w, self.slot_h)
            pygame.draw.rect(flaeche, config.FARBE_PANEL, rect)
            pygame.draw.rect(flaeche, config.FARBE_RAND, rect, 1)

            if idx < len(gefiltert):
                item = gefiltert[idx]
                rar = item.get("raritaet", "normal")
                color = ITEM_RARITAET_FARBE.get(rar, (180, 180, 180))
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(flaeche, color, inner, 2)

                item_name = item.get("name", "")[:10]
                txt = self.schrift_sehr_klein.render(item_name, True, color)
                flaeche.blit(txt, (rect.x + 4, rect.y + 4))

                if idx == self.selected_index:
                    pygame.draw.rect(flaeche, (255, 255, 255), rect, 3)

        # === RECHTS: Details ===
        pygame.draw.rect(flaeche, config.FARBE_PANEL, self.detail_rect)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.detail_rect, 2)

        detail_title = self.schrift_klein.render("Details", True, config.FARBE_TEXT)
        flaeche.blit(detail_title, (self.detail_x + 10, self.detail_y + 10))

        aktuelles_item = None
        if self.selected_item is not None:
            aktuelles_item = self.selected_item
        elif self.selected_equipment_slot:
            aktuelles_item = self.ausgeruestet.get(self.selected_equipment_slot)

        if aktuelles_item:
            y_off = self.detail_y + 40
            item_name = aktuelles_item.get("name", "?")
            name_txt = self.schrift_klein.render(item_name, True, config.FARBE_TEXT)
            flaeche.blit(name_txt, (self.detail_x + 10, y_off))
            y_off += 30

            rar = aktuelles_item.get("raritaet", "normal")
            rar_txt = self.schrift_sehr_klein.render(f"Rarität: {rar}", True, ITEM_RARITAET_FARBE.get(rar, (180,180,180)))
            flaeche.blit(rar_txt, (self.detail_x + 10, y_off))
            y_off += 25

            typ = aktuelles_item.get("typ", "?")
            typ_txt = self.schrift_sehr_klein.render(f"Typ: {typ}", True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(typ_txt, (self.detail_x + 10, y_off))
            y_off += 25

            # Vergleich mit ausgeruestetem Item im Slot
            vergleich = self.vergleich_item if self.vergleich_item and self.selected_item is not None else None

            for stat, wert in aktuelles_item.get("basis_stats", {}).items():
                vergleich_wert = None
                if vergleich:
                    vergleich_wert = vergleich.get("basis_stats", {}).get(stat)
                pfeil = self._vergleich_pfeil(wert, vergleich_wert)
                pfeil_farbe = config.FARBE_ERFOLG if pfeil == "▲" else (config.FARBE_HP if pfeil == "▼" else config.FARBE_TEXT_GEDIMMT)
                txt = self.schrift_sehr_klein.render(
                    f"{stat}: {wert} {pfeil}", True, config.FARBE_TEXT if not pfeil else pfeil_farbe)
                flaeche.blit(txt, (self.detail_x + 10, y_off))
                y_off += 20

            for prefix in aktuelles_item.get("prefixe", []):
                typ = prefix['typ']
                vergleich_wert = None
                if vergleich:
                    for v_prefix in vergleich.get("prefixe", []):
                        if v_prefix['typ'] == typ:
                            vergleich_wert = v_prefix['wert']
                            break
                    if vergleich_wert is None:
                        for v_suffix in vergleich.get("suffixe", []):
                            if v_suffix['typ'] == typ:
                                vergleich_wert = v_suffix['wert']
                                break
                pfeil = self._vergleich_pfeil(prefix['wert'], vergleich_wert)
                pfeil_farbe = config.FARBE_ERFOLG if pfeil == "▲" else (config.FARBE_HP if pfeil == "▼" else None)
                txt = self.schrift_sehr_klein.render(
                    f"+ {prefix['wert']}{prefix['einheit']} {prefix['typ'].replace('_', ' ')} {pfeil}",
                    True, pfeil_farbe if pfeil else config.FARBE_ERFOLG)
                flaeche.blit(txt, (self.detail_x + 10, y_off))
                y_off += 20

            for suffix in aktuelles_item.get("suffixe", []):
                typ = suffix['typ']
                vergleich_wert = None
                if vergleich:
                    for v_suffix in vergleich.get("suffixe", []):
                        if v_suffix['typ'] == typ:
                            vergleich_wert = v_suffix['wert']
                            break
                    if vergleich_wert is None:
                        for v_prefix in vergleich.get("prefixe", []):
                            if v_prefix['typ'] == typ:
                                vergleich_wert = v_prefix['wert']
                                break
                pfeil = self._vergleich_pfeil(suffix['wert'], vergleich_wert)
                pfeil_farbe = config.FARBE_ERFOLG if pfeil == "▲" else (config.FARBE_HP if pfeil == "▼" else None)
                txt = self.schrift_sehr_klein.render(
                    f"+ {suffix['wert']}{suffix['einheit']} {suffix['typ'].replace('_bonus','').replace('_',' ')} {pfeil}",
                    True, pfeil_farbe if pfeil else config.FARBE_MANA)
                flaeche.blit(txt, (self.detail_x + 10, y_off))
                y_off += 20
        else:
            leer_txt = self.schrift_sehr_klein.render("Kein Item ausgewählt", True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(leer_txt, (self.detail_x + 10, self.detail_y + 40))

        # Buttons
        pygame.draw.rect(flaeche, config.FARBE_PANEL, self.anlegen_btn)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.anlegen_btn, 1)
        anlegen_txt = self.schrift_klein.render("Anlegen", True, config.FARBE_TEXT)
        flaeche.blit(anlegen_txt, anlegen_txt.get_rect(center=self.anlegen_btn.center))

        pygame.draw.rect(flaeche, config.FARBE_PANEL, self.ablegen_btn)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.ablegen_btn, 1)
        ablegen_txt = self.schrift_klein.render("Ablegen", True, config.FARBE_TEXT)
        flaeche.blit(ablegen_txt, ablegen_txt.get_rect(center=self.ablegen_btn.center))

        verzauberbar = self._can_verzaubern()
        if verzauberbar and self.ehrenmarken >= 5:
            verzauber_farbe = config.FARBE_AKZENT
            text_farbe = config.FARBE_WEISS
        else:
            verzauber_farbe = config.FARBE_DUNKELGRAU
            text_farbe = config.FARBE_TEXT_GEDIMMT
        pygame.draw.rect(flaeche, verzauber_farbe, self.verzaubern_btn)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.verzaubern_btn, 1)
        verzauber_txt = self.schrift_klein.render("✦ Verzaubern (5M)", True, text_farbe)
        flaeche.blit(verzauber_txt, verzauber_txt.get_rect(center=self.verzaubern_btn.center))

        # Zurück
        pygame.draw.rect(flaeche, config.FARBE_PANEL, self.back_button)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.back_button, 1)
        back_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        back_rect = back_text.get_rect(center=self.back_button.center)
        flaeche.blit(back_text, back_rect)
"""
spiel/systeme/skill_definitionen.py - Klassen-Daten laden

Lädt klassen_index.json und einzelne Klassen-Dateien bei Bedarf.
"""

import json
import os


_DATEN_PFAD = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'daten'
)

_INDEX_PFAD = os.path.join(_DATEN_PFAD, 'klassen_index.json')

_index_cache = None


def klassen_index_laden() -> dict:
    """Lädt den Klassen-Index"""
    global _index_cache
    if _index_cache is None:
        with open(_INDEX_PFAD, 'r', encoding='utf-8') as f:
            _index_cache = json.load(f)
    return _index_cache


def _klasse_datei_laden(eintrag: dict) -> dict:
    """Lädt eine einzelne Klassen-Datei"""
    pfad = os.path.join(_DATEN_PFAD, eintrag['datei'])
    with open(pfad, encoding='utf-8') as f:
        return json.load(f)


def basis_klasse_laden(klassen_id: str) -> dict | None:
    """Lädt eine Basis-Klasse nach ID"""
    index = klassen_index_laden()
    eintrag = index['basis_klassen'].get(klassen_id)
    if not eintrag:
        return None
    daten = _klasse_datei_laden(eintrag)
    return daten.get('basis')


def spezialisierung_laden(spez_id: str) -> dict | None:
    """Lädt eine Spezialisierung nach ID"""
    index = klassen_index_laden()
    for klassen_id, eintrag in index['basis_klassen'].items():
        if spez_id in eintrag['spezialisierungen']:
            daten = _klasse_datei_laden(eintrag)
            return daten['spezialisierungen'].get(spez_id)
    return None


def klasse_laden(klassen_id: str) -> dict | None:
    """Lädt eine Klasse (Basis oder Spezialisierung)"""
    return basis_klasse_laden(klassen_id) or spezialisierung_laden(klassen_id)


def skill_laden(klassen_id: str, skill_id: str) -> dict | None:
    """Lädt einen Skill nach Klassen-ID und Skill-ID"""
    if klassen_id:
        klasse = klasse_laden(klassen_id)
        if klasse:
            for skill in klasse.get('skill_baum', {}).get('skills', []):
                if skill.get('id') == skill_id:
                    return skill

    index = klassen_index_laden()
    for basis_id, eintrag in index['basis_klassen'].items():
        try:
            daten = _klasse_datei_laden(eintrag)
            basis = daten.get('basis')
            if basis:
                for skill in basis.get('skill_baum', {}).get('skills', []):
                    if skill.get('id') == skill_id:
                        return skill
            spez = daten.get('spezialisierungen', {})
            for spez_id, spez_daten in spez.items():
                if spez_daten:
                    for skill in spez_daten.get('skill_baum', {}).get('skills', []):
                        if skill.get('id') == skill_id:
                            return skill
        except:
            pass
    return None


def node_laden(klassen_id: str, node_id: str) -> dict | None:
    """Lädt eine Node nach Klassen-ID und Node-ID"""
    klasse = klasse_laden(klassen_id)
    if not klasse:
        return None
    for node in klasse.get('skill_baum', {}).get('nodes', []):
        if node.get('id') == node_id:
            return node
    return None


def verfuegbare_basis_klassen() -> list[str]:
    """Gibt Liste aller verfügbaren Basis-Klassen-IDs zurück"""
    index = klassen_index_laden()
    return list(index['basis_klassen'].keys())


def spezialisierungen_fuer_basis(basis_id: str) -> list[str]:
    """Gibt Liste aller Spezialisierungen für eine Basis-Klasse zurück"""
    index = klassen_index_laden()
    eintrag = index['basis_klassen'].get(basis_id)
    if not eintrag:
        return []
    return eintrag['spezialisierungen']


def alle_klassen() -> dict:
    """Gibt alle Klassen (Basis + Spezialisierungen) zurück"""
    index = klassen_index_laden()
    result = {'basis_klassen': {}, 'spezialisierungen': {}}
    for klassen_id, eintrag in index['basis_klassen'].items():
        daten = _klasse_datei_laden(eintrag)
        result['basis_klassen'][klassen_id] = daten.get('basis', {})
        for spez_id, spez_daten in daten.get('spezialisierungen', {}).items():
            if spez_daten:
                result['spezialisierungen'][spez_id] = spez_daten
    return result


def skill_typ(klassen_id: str, skill_id: str) -> str | None:
    """Gibt den Typ eines Skills zurück (aktiv/passiv)"""
    skill = skill_laden(klassen_id, skill_id)
    return skill.get('typ') if skill else None


def klasse_hat_daten(klassen_id: str) -> bool:
    """Prüft ob eine Klasse vollständige Daten hat (nicht nur Platzhalter)"""
    basis = basis_klasse_laden(klassen_id)
    if basis:
        return bool(basis.get('skill_baum'))
    spez = spezialisierung_laden(klassen_id)
    return bool(spez and spez.get('skill_baum'))


def grundwert_fuer_klasse(klassen_id: str) -> str | None:
    """Gibt den Grundwert für eine Klasse zurück"""
    index = klassen_index_laden()
    if klassen_id in index['basis_klassen']:
        return index['basis_klassen'][klassen_id]['grundwert']
    for klassen_id, eintrag in index['basis_klassen'].items():
        if klassen_id in eintrag['spezialisierungen']:
            return eintrag['grundwert']
    return None


def beschreibung_generieren(eintrag: dict) -> str:
    """
    Generiert Beschreibungstext aus Template und Werten.
    Funktioniert für Skills und Nodes.
    """
    template = eintrag.get("beschreibung_template", "")
    werte = eintrag.get("beschreibung_werte", {})

    if not template:
        return eintrag.get("beschreibung", "Keine Beschreibung")

    try:
        return template.format(**werte)
    except KeyError as e:
        return f"[Fehler in Beschreibung: {e}]"


def skill_beschreibung_mit_level(skill: dict, level: int) -> str:
    """
    Generiert Beschreibung mit level-abhängigen Werten.
    Skaliert Werte basierend auf skill_level.
    """
    template = skill.get("beschreibung_template", "")
    basis_werte = skill.get("beschreibung_werte", {}).copy()
    skalierung = skill.get("skalierung", {})

    pro_level = skalierung.get("pro_level", 0)
    if pro_level > 0 and level > 1:
        for key in basis_werte:
            wert = basis_werte[key]
            if isinstance(wert, (int, float)) and wert > 0:
                skaliert = wert * (1 + (level - 1) * pro_level)
                basis_werte[key] = round(skaliert, 1)
                if isinstance(wert, int):
                    basis_werte[key] = int(basis_werte[key])

    if not template:
        return skill.get("beschreibung", "Keine Beschreibung")

    try:
        return template.format(**basis_werte)
    except KeyError as e:
        return f"[Fehler: {e}]"
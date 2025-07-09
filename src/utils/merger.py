"""
Merger für StoryWeaver
Führt Duplikate zusammen und erkennt ähnliche Entitäten
"""
from typing import Dict, List, Tuple, Set
from fuzzywuzzy import fuzz, process
import re

from ..models import Character, Item, Location, StoryElement


class EntityMerger:
    """Führt ähnliche Entitäten zusammen"""
    
    def __init__(self, similarity_threshold: int = 80):
        """
        Args:
            similarity_threshold: Minimale Ähnlichkeit (0-100) für Zusammenführung
        """
        self.similarity_threshold = similarity_threshold
    
    def merge_characters(self, characters: Dict[str, Character]) -> Dict[str, Character]:
        """Führt ähnliche Charaktere zusammen"""
        merged = {}
        processed = set()
        
        char_names = list(characters.keys())
        
        for name in char_names:
            if name in processed:
                continue
            
            char = characters[name]
            similar_names = self._find_similar_names(name, char_names, processed)
            
            # Führe alle ähnlichen Charaktere zusammen
            for similar_name in similar_names:
                if similar_name != name and similar_name not in processed:
                    similar_char = characters[similar_name]
                    char.merge_with(similar_char)
                    char.add_alias(similar_name)
                    processed.add(similar_name)
            
            # Verwende den längsten/vollständigsten Namen als Hauptnamen
            all_names = [name] + list(char.aliases)
            main_name = self._select_best_name(all_names)
            if main_name != name:
                char.name = main_name
                char.add_alias(name)
            
            merged[char.name] = char
            processed.add(name)
        
        return merged
    
    def merge_items(self, items: Dict[str, Item]) -> Dict[str, Item]:
        """Führt ähnliche Gegenstände zusammen"""
        merged = {}
        processed = set()
        
        item_names = list(items.keys())
        
        for name in item_names:
            if name in processed:
                continue
            
            item = items[name]
            similar_names = self._find_similar_items(name, item_names, processed)
            
            # Führe ähnliche Gegenstände zusammen
            for similar_name in similar_names:
                if similar_name != name and similar_name not in processed:
                    similar_item = items[similar_name]
                    item.merge_with(similar_item)
                    processed.add(similar_name)
            
            # Bereinige den Namen
            clean_name = self._clean_item_name(name)
            if clean_name != name:
                item.name = clean_name
            
            merged[item.name] = item
            processed.add(name)
        
        return merged
    
    def merge_locations(self, locations: Dict[str, Location]) -> Dict[str, Location]:
        """Führt ähnliche Orte zusammen"""
        merged = {}
        processed = set()
        
        location_names = list(locations.keys())
        
        for name in location_names:
            if name in processed:
                continue
            
            location = locations[name]
            similar_names = self._find_similar_locations(name, location_names, processed)
            
            # Führe ähnliche Orte zusammen
            for similar_name in similar_names:
                if similar_name != name and similar_name not in processed:
                    similar_location = locations[similar_name]
                    location.merge_with(similar_location)
                    processed.add(similar_name)
            
            # Verwende den vollständigsten Namen
            if similar_names:
                all_names = [name] + list(similar_names)
                best_name = self._select_best_location_name(all_names)
                if best_name != name:
                    location.name = best_name
            
            merged[location.name] = location
            processed.add(name)
        
        return merged
    
    def _find_similar_names(self, name: str, all_names: List[str], processed: Set[str]) -> List[str]:
        """Findet ähnliche Charakternamen"""
        similar = []
        
        # Normalisiere den Namen für Vergleich
        normalized = self._normalize_character_name(name)
        
        for other_name in all_names:
            if other_name in processed or other_name == name:
                continue
            
            other_normalized = self._normalize_character_name(other_name)
            
            # Prüfe verschiedene Ähnlichkeitskriterien
            
            # 1. Fuzzy String Matching auf normalisierten Namen
            similarity = fuzz.ratio(normalized, other_normalized)
            if similarity >= self.similarity_threshold:
                similar.append(other_name)
                continue
            
            # 2. Teilstring-Matching (z.B. "Lyra" in "Lyra Nightshade")
            if normalized in other_normalized or other_normalized in normalized:
                similar.append(other_name)
                continue
            
            # 3. Gleicher Vorname
            name_parts = normalized.split()
            other_parts = other_normalized.split()
            if name_parts and other_parts and name_parts[0] == other_parts[0]:
                similar.append(other_name)
        
        return similar
    
    def _find_similar_items(self, name: str, all_names: List[str], processed: Set[str]) -> List[str]:
        """Findet ähnliche Gegenstandsnamen"""
        similar = []
        
        # Normalisiere den Namen für Vergleich
        normalized = self._normalize_item_name(name)
        
        for other_name in all_names:
            if other_name in processed or other_name == name:
                continue
            
            other_normalized = self._normalize_item_name(other_name)
            
            # Fuzzy Matching auf normalisierten Namen
            similarity = fuzz.ratio(normalized, other_normalized)
            if similarity >= self.similarity_threshold:
                similar.append(other_name)
                continue
            
            # Prüfe ob es derselbe Gegenstand mit Attributen ist
            # z.B. "schwert" und "magisches schwert"
            base_item = self._extract_base_item(normalized)
            other_base = self._extract_base_item(other_normalized)
            
            if base_item and other_base and base_item == other_base:
                similar.append(other_name)
        
        return similar
    
    def _find_similar_locations(self, name: str, all_names: List[str], processed: Set[str]) -> List[str]:
        """Findet ähnliche Ortsnamen"""
        similar = []
        
        # Normalisiere den Namen für Vergleich
        normalized = self._normalize_location_name(name)
        
        for other_name in all_names:
            if other_name in processed or other_name == name:
                continue
            
            other_normalized = self._normalize_location_name(other_name)
            
            # Fuzzy Matching auf normalisierten Namen
            similarity = fuzz.ratio(normalized, other_normalized)
            if similarity >= self.similarity_threshold:
                similar.append(other_name)
                continue
            
            # Teilstring-Matching für Orte
            # z.B. "Tempel" und "Tempel von Morrakel"
            if self._is_location_subset(name, other_name):
                similar.append(other_name)
            
            # Basis-Orte erkennen (z.B. "Wald" in "Dunkler Wald")
            base_location1 = self._extract_base_location(normalized)
            base_location2 = self._extract_base_location(other_normalized)
            
            if base_location1 and base_location2 and base_location1 == base_location2:
                similar.append(other_name)
        
        return similar
    
    def _extract_base_location(self, name: str) -> str:
        """Extrahiert den Basis-Ort aus einem Namen"""
        # Liste von Orts-Schlüsselwörtern
        location_words = [
            'wald', 'schloss', 'burg', 'turm', 'dorf', 'stadt', 'tempel', 'höhle',
            'taverne', 'palast', 'ruine', 'kirche', 'platz', 'tal', 'berg', 'see',
            'fluss', 'meer', 'insel', 'brücke', 'straße', 'haus', 'hof', 'halle',
            'festung', 'hafen', 'bucht', 'schenke', 'markt', 'garten'
        ]
        
        # Wortgrenzen beachten um false positives zu vermeiden
        for word in location_words:
            if re.search(r'\b' + word + r'\b', name):
                return word
        
        return None
    
    def _normalize_item_name(self, name: str) -> str:
        """Normalisiert einen Gegenstandsnamen für bessere Vergleichbarkeit"""
        # Zu Kleinbuchstaben konvertieren
        name = name.lower()
        
        # Entferne Artikelformen und Präpositionen am Anfang
        name = re.sub(r'^(der|die|das|den|dem|des|ein|eine|einem|einer|eines|durch|mit|von|im|in|am|an)\s+', '', name)
        
        # Entferne Satzzeichen und Sonderzeichen
        name = re.sub(r'[^\w\säöüß]', '', name)
        
        # Entferne überflüssige Leerzeichen
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    def _extract_base_item(self, name: str) -> str:
        """Extrahiert den Basis-Gegenstand aus einem Namen"""
        # Erweiterte Liste von Item-Schlüsselwörtern
        item_words = [
            'schwert', 'dolch', 'stab', 'bogen', 'amulett', 'ring', 'kette', 'mantel',
            'kristall', 'stein', 'schlüssel', 'seil', 'schild', 'robe', 'buch', 'karte',
            'tasche', 'flasche', 'handschellen', 'krone', 'helm', 'rüstung', 'umhang',
            'trank', 'werkzeug', 'waffe', 'schriftrolle'
        ]
        
        # Wortgrenzen beachten um false positives zu vermeiden
        for word in item_words:
            if re.search(r'\b' + word + r'\b', name):
                return word
        
        # Prüfe auf Pluralformen
        plural_mapping = {
            'schwerter': 'schwert', 'dolche': 'dolch', 'stäbe': 'stab', 'bögen': 'bogen',
            'amulette': 'amulett', 'ringe': 'ring', 'ketten': 'kette', 'mäntel': 'mantel',
            'kristalle': 'kristall', 'steine': 'stein', 'schlüssel': 'schlüssel',
            'seile': 'seil', 'schilde': 'schild', 'roben': 'robe'
        }
        
        for plural, singular in plural_mapping.items():
            if re.search(r'\b' + plural + r'\b', name):
                return singular
        
        return None
    
    def _clean_item_name(self, name: str) -> str:
        """Bereinigt einen Gegenstandsnamen"""
        # Entferne führende Artikel
        name = re.sub(r'^(der|die|das|ein|eine)\s+', '', name)
        # Erste Buchstaben groß
        words = name.split()
        if words:
            words[0] = words[0].capitalize()
        return ' '.join(words)
    
    def _select_best_name(self, names: List[str]) -> str:
        """Wählt den besten Namen aus einer Liste (längster/vollständigster)"""
        if not names:
            return ""
        
        # Bevorzuge Namen ohne Sonderzeichen
        clean_names = [n for n in names if not re.search(r'[^\w\s]', n)]
        if clean_names:
            names = clean_names
        
        # Wähle den längsten Namen (vermutlich vollständigster)
        return max(names, key=len)
    
    def _select_best_location_name(self, names: List[str]) -> str:
        """Wählt den besten Ortsnamen"""
        if not names:
            return ""
        
        # Bevorzuge Namen mit "von", "des", etc. (vollständigere Namen)
        descriptive_names = [n for n in names if any(word in n.lower() for word in ['von', 'des', 'der', 'am'])]
        if descriptive_names:
            return max(descriptive_names, key=len)
        
        return max(names, key=len)
    
    def _normalize_character_name(self, name: str) -> str:
        """Normalisiert einen Charakternamen für bessere Vergleichbarkeit"""
        # Zu Kleinbuchstaben konvertieren
        name = name.lower()
        
        # Entferne Titel und Anreden
        name = re.sub(r'^(herr|frau|fräulein|lord|lady|sir|prinz|prinzessin|könig|königin|herzog|herzogin|dr|doktor|professor|prof)\s+', '', name)
        
        # Entferne Satzzeichen und Sonderzeichen
        name = re.sub(r'[^\w\säöüß]', '', name)
        
        # Entferne überflüssige Leerzeichen
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    def _is_location_subset(self, name1: str, name2: str) -> bool:
        """Prüft ob ein Ortsname Teil eines anderen ist"""
        # Normalisiere die Namen
        norm1 = self._normalize_location_name(name1)
        norm2 = self._normalize_location_name(name2)
        
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        # Ignoriere kleine Wörter
        stop_words = {'von', 'der', 'die', 'das', 'am', 'im', 'zur', 'zum', 'in', 'an', 'auf', 'bei'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        # Prüfe ob eine Wortmenge Teilmenge der anderen ist
        return words1.issubset(words2) or words2.issubset(words1)
    
    def _normalize_location_name(self, name: str) -> str:
        """Normalisiert einen Ortsnamen für bessere Vergleichbarkeit"""
        # Zu Kleinbuchstaben konvertieren
        name = name.lower()
        
        # Entferne Artikel und Präpositionen am Anfang
        name = re.sub(r'^(der|die|das|den|dem|des|im|in|am|an|auf|bei|zum|zur)\s+', '', name)
        
        # Entferne Satzzeichen und Sonderzeichen
        name = re.sub(r'[^\w\säöüß]', '', name)
        
        # Entferne überflüssige Leerzeichen
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
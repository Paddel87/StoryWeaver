"""
Entity-Extractor für StoryWeaver
Nutzt spaCy und Heuristiken zur Erkennung von Story-Elementen
"""
import spacy
from typing import List, Dict, Set, Tuple
import re
from pathlib import Path

from ..models import Character, Item, Location
from ..parsers.chat_parser import ChatLine, ChatParser


class EntityExtractor:
    """Extrahiert Charaktere, Gegenstände und Orte aus Chat-Verläufen"""
    
    def __init__(self, spacy_model: str = "de_core_news_sm"):
        """Initialisiert den Extractor mit einem spaCy-Modell"""
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            print(f"SpaCy-Modell '{spacy_model}' nicht gefunden. Installiere es mit:")
            print(f"python -m spacy download {spacy_model}")
            raise
        
        # Listen von Schlüsselwörtern für verschiedene Kategorien
        self.item_keywords = {
            'waffen': ['schwert', 'dolch', 'stab', 'bogen', 'pfeil', 'speer', 'axt', 'klinge'],
            'schmuck': ['amulett', 'ring', 'kette', 'armband', 'krone', 'diadem'],
            'werkzeuge': ['schlüssel', 'seil', 'fackel', 'karte', 'kompass', 'flasche'],
            'magisch': ['kristall', 'stein', 'orb', 'zauberstab', 'runen', 'artefakt'],
            'kleidung': ['mantel', 'umhang', 'robe', 'stiefel', 'handschuhe', 'rüstung']
        }
        
        self.location_keywords = {
            'gebäude': ['tempel', 'turm', 'burg', 'schloss', 'haus', 'hütte', 'palast', 'ruine'],
            'natur': ['wald', 'berg', 'tal', 'see', 'fluss', 'höhle', 'klippe', 'wiese'],
            'siedlung': ['stadt', 'dorf', 'markt', 'hafen', 'straße', 'platz', 'brücke'],
            'räume': ['zimmer', 'saal', 'kammer', 'halle', 'keller', 'gang', 'raum']
        }
        
        # Container für extrahierte Entitäten
        self.characters: Dict[str, Character] = {}
        self.items: Dict[str, Item] = {}
        self.locations: Dict[str, Location] = {}
        
        # Dialog-Daten für SillyTavern-Export
        self.dialog_data: Dict[str, List[Dict]] = {}
    
    def extract_from_file(self, filepath: Path):
        """Extrahiert Entitäten aus einer einzelnen Chat-Datei"""
        parser = ChatParser()
        chat_lines = parser.parse_file(filepath)
        
        # Erst alle Sprecher als potenzielle Charaktere erfassen
        for speaker in parser.get_speakers():
            self._add_character(speaker, f"Spricht in {filepath.name}")
        
        # Sammle Dialog-Daten für jeden Charakter
        for line in chat_lines:
            if line.speaker and line.line_type in ["dialog", "action"]:
                if line.speaker not in self.dialog_data:
                    self.dialog_data[line.speaker] = []
                
                self.dialog_data[line.speaker].append({
                    "speaker": line.speaker,
                    "content": line.content,
                    "line_type": line.line_type,
                    "line_number": line.line_number,
                    "source_file": str(filepath)
                })
        
        # Dann alle Zeilen analysieren
        for line in chat_lines:
            self._analyze_line(line, str(filepath))
    
    def _analyze_line(self, line: ChatLine, source_file: str):
        """Analysiert eine einzelne Chat-Zeile"""
        if not line.content:
            return
        
        # SpaCy-Analyse
        doc = self.nlp(line.content)
        
        # Named Entities verarbeiten
        for ent in doc.ents:
            if ent.label_ == "PER":  # Person
                self._add_character(ent.text, line.raw_text, source_file, line.line_number)
            elif ent.label_ in ["LOC", "GPE"]:  # Location, Geopolitical entity
                self._add_location(ent.text, line.raw_text, source_file, line.line_number)
        
        # Schlüsselwort-basierte Suche für Gegenstände
        self._extract_items_by_keywords(line, source_file)
        
        # Schlüsselwort-basierte Suche für Orte
        self._extract_locations_by_keywords(line, source_file)
        
        # Besitzbeziehungen erkennen
        self._extract_ownership(doc, line, source_file)
        
        # Aktionen analysieren
        if line.is_action():
            self._analyze_action(line, doc, source_file)
    
    def _add_character(self, name: str, context: str, source_file: str = None, line_number: int = None):
        """Fügt einen Charakter hinzu oder aktualisiert ihn"""
        name = name.strip()
        if not name or len(name) < 2:
            return
        
        # Normalisiere den Namen (erste Buchstaben groß)
        name = name.title()
        
        if name not in self.characters:
            self.characters[name] = Character(name=name)
        
        if source_file:
            self.characters[name].add_mention(context, source_file, line_number)
    
    def _add_item(self, name: str, item_type: str, context: str, source_file: str, line_number: int):
        """Fügt einen Gegenstand hinzu oder aktualisiert ihn"""
        name = name.strip().lower()
        if not name:
            return
        
        if name not in self.items:
            self.items[name] = Item(name=name)
            if item_type:
                self.items[name].set_type(item_type)
        
        self.items[name].add_mention(context, source_file, line_number)
    
    def _add_location(self, name: str, context: str, source_file: str, line_number: int):
        """Fügt einen Ort hinzu oder aktualisiert ihn"""
        name = name.strip()
        if not name or len(name) < 2:
            return
        
        # Normalisiere den Namen
        name = name.title()
        
        if name not in self.locations:
            self.locations[name] = Location(name=name)
        
        self.locations[name].add_mention(context, source_file, line_number)
    
    def _extract_items_by_keywords(self, line: ChatLine, source_file: str):
        """Sucht nach Gegenständen basierend auf Schlüsselwörtern"""
        text_lower = line.content.lower()
        
        for category, keywords in self.item_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Versuche, den vollständigen Gegenstandsnamen zu extrahieren
                    patterns = [
                        rf'([\w\s]{{1,20}}?{keyword}[\w\s]{{0,10}})',  # Wörter vor und nach dem Keyword
                        rf'({keyword}[\w\s]{{0,20}})',  # Keyword am Anfang
                        rf'([\w\s]{{1,20}}{keyword})'   # Keyword am Ende
                    ]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, text_lower)
                        for match in matches:
                            item_name = match.group(1).strip()
                            if item_name and len(item_name) > 2:
                                self._add_item(item_name, category, line.raw_text, source_file, line.line_number)
                                break
    
    def _extract_locations_by_keywords(self, line: ChatLine, source_file: str):
        """Sucht nach Orten basierend auf Schlüsselwörtern"""
        text_lower = line.content.lower()
        
        for category, keywords in self.location_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Ähnliche Muster wie bei Gegenständen
                    patterns = [
                        rf'([\w\s]{{1,20}}?{keyword}[\w\s]{{0,10}})',
                        rf'({keyword}[\w\s]{{0,20}})',
                        rf'([\w\s]{{1,20}}{keyword})'
                    ]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, text_lower)
                        for match in matches:
                            location_name = match.group(1).strip()
                            if location_name and len(location_name) > 2:
                                self._add_location(location_name.title(), line.raw_text, source_file, line.line_number)
                                # Setze den Typ
                                if location_name.title() in self.locations:
                                    self.locations[location_name.title()].set_type(category)
                                break
    
    def _extract_ownership(self, doc, line: ChatLine, source_file: str):
        """Erkennt Besitzbeziehungen zwischen Charakteren und Gegenständen"""
        # Muster für Besitz: "sein/ihr [Gegenstand]", "[Name]s [Gegenstand]"
        for token in doc:
            # Possessivpronomen
            if token.pos_ == "DET" and token.tag_ in ["PPOSAT", "PWAT"]:
                # Nächstes Nomen könnte ein Gegenstand sein
                for child in token.children:
                    if child.pos_ == "NOUN":
                        item_name = child.text.lower()
                        # Prüfe ob es ein bekannter Gegenstand ist
                        for item_key in self.items:
                            if item_name in item_key or item_key in item_name:
                                # Verknüpfe mit Sprecher
                                if line.speaker and line.speaker in self.characters:
                                    self.items[item_key].add_owner(line.speaker)
                                    self.characters[line.speaker].add_item(item_key)
    
    def _analyze_action(self, line: ChatLine, doc, source_file: str):
        """Analysiert Aktionszeilen für zusätzliche Informationen"""
        # Suche nach Verben und ihren Objekten
        for token in doc:
            if token.pos_ == "VERB":
                # Objekte des Verbs könnten Gegenstände sein
                for child in token.children:
                    if child.dep_ in ["dobj", "obj"] and child.pos_ == "NOUN":
                        # Könnte ein Gegenstand sein
                        item_text = child.text.lower()
                        for category, keywords in self.item_keywords.items():
                            if any(kw in item_text for kw in keywords):
                                self._add_item(item_text, category, line.raw_text, source_file, line.line_number)
                                # Wenn wir einen Sprecher haben, verknüpfe sie
                                if line.speaker:
                                    self.items[item_text].add_owner(line.speaker)
    
    def get_all_entities(self) -> Dict[str, Dict]:
        """Gibt alle extrahierten Entitäten zurück"""
        return {
            'characters': {name: char.to_dict() for name, char in self.characters.items()},
            'items': {name: item.to_dict() for name, item in self.items.items()},
            'locations': {name: loc.to_dict() for name, loc in self.locations.items()}
        }
    
    def get_dialog_data(self) -> Dict[str, List[Dict]]:
        """Gibt die gesammelten Dialog-Daten zurück"""
        return self.dialog_data 
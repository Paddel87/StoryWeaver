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
            # Erhöhe das Limit für große Texte
            self.nlp.max_length = 2000000  # 2 Millionen Zeichen
            
            # Deaktiviere nicht benötigte Pipeline-Komponenten für bessere Performance
            # Behalte nur NER (Named Entity Recognition)
            disabled_pipes = []
            for pipe in self.nlp.pipe_names:
                if pipe not in ["ner", "tok2vec"]:
                    disabled_pipes.append(pipe)
            
            if disabled_pipes:
                self.nlp.disable_pipes(disabled_pipes)
                print(f"Deaktivierte Pipeline-Komponenten für bessere Performance: {disabled_pipes}")
                
        except OSError:
            print(f"SpaCy-Modell '{spacy_model}' nicht gefunden. Installiere es mit:")
            print(f"python -m spacy download {spacy_model}")
            raise
        
        # Listen von Schlüsselwörtern für verschiedene Kategorien
        # REDUZIERT auf wirklich relevante Story-Gegenstände
        self.item_keywords = {
            'waffen': ['schwert', 'dolch', 'klinge', 'messer'],
            'schmuck': ['halskette', 'armband', 'ring'],
            'werkzeuge': ['schlüssel'],
            'magisch': ['kristall', 'amulett', 'zauberstab'],
            'fesselung': ['seil', 'kette', 'fessel', 'handschellen', 'manschetten']
        }
        
        self.location_keywords = {
            'gebäude': ['schloss', 'turm', 'kerker', 'verlies', 'kammer'],
            'räume': ['dungeon', 'spielzimmer', 'studio']
        }
        
        # Körper- und Handlungsbegriffe, die NICHT als Gegenstände erkannt werden sollen
        self.body_and_action_terms = {
            'hand', 'hände', 'fuß', 'füße', 'arm', 'arme', 'bein', 'beine',
            'kopf', 'hals', 'schulter', 'brust', 'rücken', 'bauch', 'hüfte',
            'handgelenk', 'handgelenke', 'knöchel', 'fußgelenk', 'fußgelenke',
            'finger', 'zehen', 'knie', 'ellbogen', 'position', 'haltung',
            'knoten', 'schlinge', 'schlaufe', 'wicklung', 'bindung', 'fesselung',
            'bewegung', 'druck', 'spannung', 'gefühl', 'berührung', 'griff'
        }
        
        # Erweitere Common Words
        self.common_words = {
            'der', 'die', 'das', 'ein', 'eine', 'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr',
            'mein', 'dein', 'sein', 'unser', 'euer', 'von', 'zu', 'mit', 'auf', 'in', 'an',
            'und', 'oder', 'aber', 'doch', 'wenn', 'dann', 'dass', 'weil', 'als', 'wie',
            'nicht', 'kein', 'keine', 'sehr', 'viel', 'mehr', 'wenig', 'alle', 'jeder',
            'mann', 'frau', 'herr', 'dame', 'person', 'mensch', 'körper',
            'oben', 'unten', 'vorne', 'hinten', 'links', 'rechts', 'mitte',
            'erste', 'zweite', 'dritte', 'letzte', 'nächste'
        }
        
        # Minimale Länge für Entitätsnamen
        self.min_name_length = 3
        
        # Mindesthäufigkeit für finale Aufnahme (wird später in der Merge-Phase angewendet)
        self.min_frequency = 2
        
        # Maximale Textlänge für SpaCy-Verarbeitung
        self.MAX_TEXT_LENGTH = 1000000
        
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
        
        # Verwende Batch-Verarbeitung für große Dateien
        if len(chat_lines) > 1000:
            print(f"Verwende Batch-Verarbeitung für {len(chat_lines)} Zeilen...")
            self._analyze_lines_batch(chat_lines, str(filepath))
        else:
            # Bei kleineren Dateien normale Verarbeitung
            for line in chat_lines:
                self._analyze_line(line, str(filepath))
    
    def _analyze_lines_batch(self, lines: List[ChatLine], source_file: str, batch_size: int = 500):
        """Verarbeitet Zeilen in Batches für bessere Performance bei großen Texten"""
        # Gruppiere Zeilen mit Inhalt
        lines_with_content = [(i, line) for i, line in enumerate(lines) if line.content]
        
        # Verarbeite in Batches
        for i in range(0, len(lines_with_content), batch_size):
            batch = lines_with_content[i:i + batch_size]
            
            # Extrahiere Texte für SpaCy
            texts = [line.content for _, line in batch]
            
            # Nutze pipe() für Batch-Verarbeitung
            docs = list(self.nlp.pipe(texts, batch_size=50, n_process=1))
            
            # Verarbeite Ergebnisse
            for doc, (idx, line) in zip(docs, batch):
                self._analyze_doc_and_line(doc, line, source_file)
                
            # Gib Speicher frei nach jedem Batch
            if i % (batch_size * 10) == 0 and i > 0:
                import gc
                gc.collect()
                print(f"Verarbeitet: {i}/{len(lines_with_content)} Zeilen...")
    
    def _analyze_doc_and_line(self, doc, line: ChatLine, source_file: str):
        """Analysiert ein SpaCy-Doc-Objekt zusammen mit der ChatLine"""
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
    
    def _analyze_line(self, line: ChatLine, source_file: str):
        """Analysiert eine einzelne Chat-Zeile"""
        if not line.content:
            return
        
        # SpaCy-Analyse
        doc = self.nlp(line.content)
        
        # Verwende die gleiche Analyse-Logik
        self._analyze_doc_and_line(doc, line, source_file)
    
    def _add_character(self, name: str, context: str, source_file: str = None, line_number: int = None):
        """Fügt einen Charakter hinzu oder aktualisiert ihn"""
        name = name.strip()
        if not name or len(name) < self.min_name_length:
            return
        
        # Prüfe auf Common Words
        if name.lower() in self.common_words:
            return
        
        # Ignoriere Namen die nur aus Zahlen bestehen
        if name.isdigit():
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
        
        # Verwende die neue Validierungsmethode
        if not self._is_valid_location(name, context):
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
                    # Präzisere Muster - nur direkte Modifikatoren
                    patterns = [
                        rf'\b(\w+\s+{keyword})\b',  # Ein Wort vor dem Keyword
                        rf'\b({keyword}\s+\w+)\b',  # Ein Wort nach dem Keyword
                        rf'\b({keyword})\b'          # Nur das Keyword selbst
                    ]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, text_lower)
                        for match in matches:
                            item_name = match.group(1).strip()
                            # Verwende die neue Validierungsmethode
                            if item_name and self._is_valid_item(item_name, line.content):
                                self._add_item(item_name, category, line.raw_text, source_file, line.line_number)
                                break
    
    def _extract_locations_by_keywords(self, line: ChatLine, source_file: str):
        """Sucht nach Orten basierend auf Schlüsselwörtern"""
        text_lower = line.content.lower()
        
        for category, keywords in self.location_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Präzisere Muster für Orte
                    patterns = [
                        rf'\b(\w+\s+{keyword})\b',  # Ein Wort vor dem Keyword
                        rf'\b({keyword}\s+\w+)\b',  # Ein Wort nach dem Keyword
                        rf'\b({keyword})\b'          # Nur das Keyword selbst
                    ]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, text_lower)
                        for match in matches:
                            location_name = match.group(1).strip()
                            # Verwende die neue Validierungsmethode
                            if location_name and self._is_valid_location(location_name, line.content):
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

    def _is_valid_item(self, name, text):
        """Überprüft, ob ein erkannter Gegenstand valide ist"""
        name_lower = name.lower()
        
        # Zu kurze Namen
        if len(name) < 3:
            return False
            
        # Häufige Wörter
        if name_lower in self.common_words:
            return False
            
        # Körperteile und Handlungsbegriffe ausschließen
        if name_lower in self.body_and_action_terms:
            return False
            
        # Einzelbuchstaben oder nur Zahlen
        if len(name) == 1 or name.isdigit():
            return False
            
        # Prüfe ob es nur eine Richtungsangabe ist
        if name_lower in ['oben', 'unten', 'vorne', 'hinten', 'links', 'rechts']:
            return False
            
        # Prüfe ob es ein generischer Begriff ist
        generic_terms = {'objekt', 'gegenstand', 'ding', 'sache', 'material', 'stück'}
        if name_lower in generic_terms:
            return False
            
        return True
    
    def _is_valid_location(self, name, text):
        """Überprüft, ob ein erkannter Ort valide ist"""
        name_lower = name.lower()
        
        # Zu kurze Namen  
        if len(name) < 3:
            return False
            
        # Häufige Wörter
        if name_lower in self.common_words:
            return False
            
        # Generische Ortsangaben
        generic_locations = {
            'hier', 'dort', 'überall', 'nirgends', 'irgendwo',
            'nähe', 'ferne', 'umgebung', 'gegend', 'bereich',
            'stelle', 'platz', 'ort', 'position', 'lage'
        }
        if name_lower in generic_locations:
            return False
            
        # Körperteile sind keine Orte
        if name_lower in self.body_and_action_terms:
            return False
            
        return True 

    def _looks_like_item(self, text: str, context: str) -> bool:
        """Prüft zusätzlich ob ein Text wirklich ein Gegenstand sein könnte"""
        text_lower = text.lower()
        
        # Prüfe ob es eine Handlung/Aktion beschreibt
        action_indicators = ['en', 'ung', 'tion', 'heit', 'keit', 'schaft']
        for suffix in action_indicators:
            if text_lower.endswith(suffix):
                return False
        
        # Prüfe ob es in einem typischen Gegenstandskontext steht
        item_contexts = ['nutzt', 'verwendet', 'hält', 'nimmt', 'legt', 'bindet mit', 'fesselt mit']
        context_lower = context.lower()
        
        for indicator in item_contexts:
            if indicator in context_lower and text_lower in context_lower:
                return True
        
        # Standardmäßig false für unklare Fälle
        return False 

    def extract_items(self, text: str):
        """Erweiterte Gegenstandsextraktion mit NLP und kontextspezifischer Validierung"""
        items = {}
        
        # Begrenze Textlänge für SpaCy
        text_chunk = text[:self.MAX_TEXT_LENGTH] if hasattr(self, 'MAX_TEXT_LENGTH') else text[:1000000]
        
        # 1. Keyword-basierte Suche (sehr spezifisch)
        for category, keywords in self.item_keywords.items():
            for keyword in keywords:
                pattern = rf'\b(\w*{keyword}\w*)\b'
                matches = re.finditer(pattern, text_chunk, re.IGNORECASE)
                for match in matches:
                    item_name = match.group(1)
                    if self._is_valid_item(item_name, text_chunk):
                        item_key = item_name.lower()
                        if item_key not in items:
                            items[item_key] = {
                                'name': item_name,
                                'category': category,
                                'count': 0,
                                'contexts': []
                            }
                        items[item_key]['count'] += 1
                        
                        # Kontext extrahieren
                        start = max(0, match.start() - 50)
                        end = min(len(text_chunk), match.end() + 50)
                        context = text_chunk[start:end].strip()
                        if context not in items[item_key]['contexts']:
                            items[item_key]['contexts'].append(context)
        
        # 2. NLP-basierte Suche (sehr restriktiv)
        doc = self.nlp(text_chunk)
        for ent in doc.ents:
            if ent.label_ in ['MISC', 'PRODUCT'] and len(ent.text) >= 3:
                # Strenge Validierung
                if (self._is_valid_item(ent.text, text_chunk) and 
                    self._looks_like_item(ent.text, ent.sent.text)):
                    item_key = ent.text.lower()
                    
                    # Skip wenn schon durch Keywords gefunden
                    if item_key not in items:
                        items[item_key] = {
                            'name': ent.text,
                            'category': 'sonstige',
                            'count': 1,
                            'contexts': [ent.sent.text.strip()]
                        }
        
        return items
    
    def extract_locations(self, text: str):
        """Erweiterte Ortsextraktion mit NLP und kontextspezifischer Validierung"""
        locations = {}
        
        # Begrenze Textlänge für SpaCy
        text_chunk = text[:self.MAX_TEXT_LENGTH] if hasattr(self, 'MAX_TEXT_LENGTH') else text[:1000000]
        
        # 1. Keyword-basierte Suche (sehr spezifisch)
        for category, keywords in self.location_keywords.items():
            for keyword in keywords:
                pattern = rf'\b(\w*{keyword}\w*)\b'
                matches = re.finditer(pattern, text_chunk, re.IGNORECASE)
                for match in matches:
                    location_name = match.group(1)
                    if self._is_valid_location(location_name, text_chunk):
                        location_key = location_name.lower()
                        if location_key not in locations:
                            locations[location_key] = {
                                'name': location_name.title(),
                                'category': category,
                                'count': 0,
                                'contexts': []
                            }
                        locations[location_key]['count'] += 1
                        
                        # Kontext extrahieren
                        start = max(0, match.start() - 50)
                        end = min(len(text_chunk), match.end() + 50)
                        context = text_chunk[start:end].strip()
                        if context not in locations[location_key]['contexts']:
                            locations[location_key]['contexts'].append(context)
        
        # 2. NLP-basierte Suche (sehr restriktiv für bekannte Orte)
        doc = self.nlp(text_chunk)
        for ent in doc.ents:
            if ent.label_ in ['LOC', 'GPE'] and len(ent.text) >= 4:
                # Strenge Validierung
                if self._is_valid_location(ent.text, text_chunk):
                    location_key = ent.text.lower()
                    
                    # Skip wenn schon durch Keywords gefunden
                    if location_key not in locations:
                        # Nur sehr spezifische Orte hinzufügen
                        if any(kw in location_key for kw in ['schloss', 'turm', 'kammer', 'verlies']):
                            locations[location_key] = {
                                'name': ent.text.title(),
                                'category': 'sonstige',
                                'count': 1,
                                'contexts': [ent.sent.text.strip()]
                            }
        
        return locations 
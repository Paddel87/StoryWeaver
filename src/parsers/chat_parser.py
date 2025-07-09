"""
Chat-Parser für StoryWeaver
Erkennt verschiedene Formate von Chat-Verläufen (Text und JSON)
"""
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChatLine:
    """Repräsentiert eine einzelne Zeile im Chat"""
    line_number: int
    raw_text: str
    speaker: Optional[str] = None
    content: Optional[str] = None
    line_type: str = "unknown"  # dialog, action, narration, unknown
    
    def is_dialog(self) -> bool:
        return self.line_type == "dialog"
    
    def is_action(self) -> bool:
        return self.line_type == "action"
    
    def is_narration(self) -> bool:
        return self.line_type == "narration"


class ChatParser:
    """Parser für verschiedene Chat-Formate"""
    
    # Regex-Muster für verschiedene Formate
    PATTERNS = {
        # Dialog mit Doppelpunkt (z.B. "Lyra: Ich bin hier")
        'dialog_colon': re.compile(r'^([A-Za-zÄÖÜäöüß\s]+):\s*(.+)$'),
        
        # Dialog mit Bindestrich (z.B. "Lyra - Ich bin hier")
        'dialog_dash': re.compile(r'^([A-Za-zÄÖÜäöüß\s]+)\s*-\s*(.+)$'),
        
        # Aktionen in eckigen Klammern (z.B. "[Lyra öffnet die Tür]")
        'action_brackets': re.compile(r'^\[(.+)\]$'),
        
        # Aktionen in Sternchen (z.B. "*öffnet die Tür*")
        'action_asterisk': re.compile(r'^\*(.+)\*$'),
        
        # Erzähler-Markierung
        'narrator': re.compile(r'^(Erzähler|Narrator|Erzählerin):\s*(.+)$', re.IGNORECASE),
    }
    
    def __init__(self):
        self.lines: List[ChatLine] = []
    
    def parse_file(self, filepath: Path) -> List[ChatLine]:
        """Parst eine einzelne Chat-Datei basierend auf dem Dateityp"""
        self.lines = []
        
        if not filepath.exists():
            logging.error(f"Datei nicht gefunden: {filepath}")
            return []
        
        # Dateiendung überprüfen und entsprechenden Parser aufrufen
        file_extension = filepath.suffix.lower()
        
        if file_extension == '.json':
            return self.parse_json_file(filepath)
        else:
            # Text-Parser für .txt und .md
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_number, raw_line in enumerate(f, 1):
                    line = raw_line.strip()
                    if not line:  # Leere Zeilen überspringen
                        continue
                    
                    chat_line = self._parse_line(line_number, line)
                    self.lines.append(chat_line)
            
            return self.lines
            
    def parse_json_file(self, file_path: Path) -> List[ChatLine]:
        """Parst eine JSON-Datei in ChatLine-Objekte"""
        chat_lines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Verschiedene JSON-Formate erkennen und verarbeiten
                
                # Format 1: Liste von Dialog-Objekten
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    for idx, item in enumerate(data):
                        if 'speaker' in item and 'content' in item:
                            line = ChatLine(
                                line_number=idx+1,
                                speaker=item['speaker'],
                                content=item['content'],
                                raw_text=json.dumps(item),
                                line_type=item.get('type', 'dialog')
                            )
                            chat_lines.append(line)
                
                # Format 2: Charakterobjekt mit Dialog-Array
                elif isinstance(data, dict) and 'dialog' in data and isinstance(data['dialog'], list):
                    for idx, entry in enumerate(data['dialog']):
                        if isinstance(entry, dict) and 'content' in entry:
                            speaker = entry.get('speaker', data.get('name', 'Unknown'))
                            line = ChatLine(
                                line_number=idx+1,
                                speaker=speaker,
                                content=entry['content'],
                                raw_text=json.dumps(entry),
                                line_type=entry.get('type', 'dialog')
                            )
                            chat_lines.append(line)
                
                # Format 3: Einfache Charakter-Beschreibung
                elif isinstance(data, dict) and 'name' in data:
                    # Charakter als einzelne Zeile extrahieren
                    char_name = data['name']
                    # Sammle alle relevanten Felder
                    description_parts = []
                    
                    for key in ['description', 'personality', 'background', 'traits']:
                        if key in data and data[key]:
                            description_parts.append(f"{key.capitalize()}: {data[key]}")
                    
                    content = "\n".join(description_parts)
                    
                    if content:
                        line = ChatLine(
                            line_number=1,
                            speaker=char_name,
                            content=content,
                            raw_text=json.dumps(data),
                            line_type='description'
                        )
                        chat_lines.append(line)
                
                # Charakter-Beziehungen extrahieren, falls vorhanden
                if isinstance(data, dict) and 'relationships' in data and isinstance(data['relationships'], list):
                    char_name = data.get('name', 'Unknown')
                    for rel_idx, rel in enumerate(data['relationships']):
                        if isinstance(rel, dict) and 'name' in rel and 'relationship' in rel:
                            content = f"Beziehung zu {rel['name']}: {rel['relationship']}"
                            line = ChatLine(
                                line_number=len(chat_lines) + rel_idx + 1,
                                speaker=char_name,
                                content=content,
                                raw_text=json.dumps(rel),
                                line_type='relationship'
                            )
                            chat_lines.append(line)
                
                self.lines.extend(chat_lines)
                return chat_lines
                
        except json.JSONDecodeError:
            logging.error(f"Fehler beim Parsen der JSON-Datei: {file_path}")
        except Exception as e:
            logging.error(f"Unerwarteter Fehler beim Parsen von {file_path}: {str(e)}")
            
        return chat_lines
    
    def _parse_line(self, line_number: int, text: str) -> ChatLine:
        """Parst eine einzelne Zeile und erkennt ihren Typ"""
        chat_line = ChatLine(line_number=line_number, raw_text=text)
        
        # Prüfe auf Erzähler
        narrator_match = self.PATTERNS['narrator'].match(text)
        if narrator_match:
            chat_line.speaker = "Erzähler"
            chat_line.content = narrator_match.group(2).strip()
            chat_line.line_type = "narration"
            return chat_line
        
        # Prüfe auf Dialog mit Doppelpunkt
        dialog_match = self.PATTERNS['dialog_colon'].match(text)
        if dialog_match:
            chat_line.speaker = dialog_match.group(1).strip()
            chat_line.content = dialog_match.group(2).strip()
            chat_line.line_type = "dialog"
            return chat_line
        
        # Prüfe auf Dialog mit Bindestrich
        dialog_dash_match = self.PATTERNS['dialog_dash'].match(text)
        if dialog_dash_match:
            chat_line.speaker = dialog_dash_match.group(1).strip()
            chat_line.content = dialog_dash_match.group(2).strip()
            chat_line.line_type = "dialog"
            return chat_line
        
        # Prüfe auf Aktionen in eckigen Klammern
        action_brackets_match = self.PATTERNS['action_brackets'].match(text)
        if action_brackets_match:
            chat_line.content = action_brackets_match.group(1).strip()
            chat_line.line_type = "action"
            # Versuche Sprecher aus Aktion zu extrahieren
            chat_line.speaker = self._extract_actor_from_action(chat_line.content)
            return chat_line
        
        # Prüfe auf Aktionen in Sternchen
        action_asterisk_match = self.PATTERNS['action_asterisk'].match(text)
        if action_asterisk_match:
            chat_line.content = action_asterisk_match.group(1).strip()
            chat_line.line_type = "action"
            chat_line.speaker = self._extract_actor_from_action(chat_line.content)
            return chat_line
        
        # Wenn kein Muster passt, könnte es Erzähltext sein
        # Heuristik: Wenn die Zeile mit einem Großbuchstaben beginnt und einen Punkt endet
        if text and text[0].isupper() and text.endswith('.'):
            chat_line.content = text
            chat_line.line_type = "narration"
        else:
            # Unbekanntes Format
            chat_line.content = text
            chat_line.line_type = "unknown"
        
        return chat_line
    
    def _extract_actor_from_action(self, action_text: str) -> Optional[str]:
        """Versucht, den Handelnden aus einer Aktion zu extrahieren"""
        # Einfache Heuristik: Erstes Wort könnte der Name sein
        words = action_text.split()
        if words:
            # Prüfe ob erstes Wort ein Name sein könnte (Großbuchstabe)
            first_word = words[0]
            if first_word[0].isupper() and len(first_word) > 2:
                return first_word
        
        # Weitere Muster könnten hier ergänzt werden
        return None
    
    def get_speakers(self) -> List[str]:
        """Gibt eine Liste aller erkannten Sprecher zurück"""
        speakers = set()
        for line in self.lines:
            if line.speaker and line.speaker != "Erzähler":
                speakers.add(line.speaker)
        return sorted(list(speakers))
    
    def get_dialog_lines(self) -> List[ChatLine]:
        """Gibt nur Dialog-Zeilen zurück"""
        return [line for line in self.lines if line.is_dialog()]
    
    def get_action_lines(self) -> List[ChatLine]:
        """Gibt nur Aktions-Zeilen zurück"""
        return [line for line in self.lines if line.is_action()]
    
    def get_narration_lines(self) -> List[ChatLine]:
        """Gibt nur Erzähl-Zeilen zurück"""
        return [line for line in self.lines if line.is_narration()] 
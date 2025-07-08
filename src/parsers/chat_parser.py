"""
Chat-Parser für StoryWeaver
Erkennt verschiedene Formate von Chat-Verläufen
"""
import re
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
        """Parst eine einzelne Chat-Datei"""
        self.lines = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_number, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line:  # Leere Zeilen überspringen
                    continue
                
                chat_line = self._parse_line(line_number, line)
                self.lines.append(chat_line)
        
        return self.lines
    
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
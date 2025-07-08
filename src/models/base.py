"""
Basisklassen für StoryWeaver Datenmodelle
"""
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class StoryElement:
    """Basisklasse für alle Story-Elemente"""
    name: str
    description: str = ""
    mentions: List[Dict[str, str]] = field(default_factory=list)  # Quellstellen
    frequency: int = 0
    source_files: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_mention(self, text: str, source_file: str, line_number: Optional[int] = None):
        """Fügt eine Erwähnung aus dem Quelltext hinzu"""
        mention = {
            "text": text,
            "source_file": source_file,
            "line_number": line_number
        }
        self.mentions.append(mention)
        self.source_files.add(source_file)
        self.frequency += 1
        self.updated_at = datetime.now()
    
    def merge_with(self, other: 'StoryElement'):
        """Führt dieses Element mit einem anderen zusammen"""
        # Beschreibungen kombinieren, wenn unterschiedlich
        if other.description and other.description not in self.description:
            if self.description:
                self.description += f" | {other.description}"
            else:
                self.description = other.description
        
        # Erwähnungen und Quellen zusammenführen
        self.mentions.extend(other.mentions)
        self.source_files.update(other.source_files)
        self.frequency += other.frequency
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Konvertiert das Objekt in ein Dictionary für JSON-Export"""
        return {
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "source_files": list(self.source_files),
            "mentions": self.mentions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def save_to_json(self, output_dir: Path):
        """Speichert das Element als JSON-Datei"""
        # Dateiname aus Name generieren (lowercase, Leerzeichen durch Unterstriche ersetzen)
        filename = self.name.lower().replace(" ", "_").replace("/", "_") + ".json"
        filepath = output_dir / filename
        
        # Verzeichnis erstellen, falls nicht vorhanden
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Als JSON speichern
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StoryElement':
        """Erstellt ein Objekt aus einem Dictionary"""
        obj = cls(
            name=data['name'],
            description=data.get('description', ''),
            frequency=data.get('frequency', 0)
        )
        obj.mentions = data.get('mentions', [])
        obj.source_files = set(data.get('source_files', []))
        
        # Datumsfelder konvertieren
        if 'created_at' in data:
            obj.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            obj.updated_at = datetime.fromisoformat(data['updated_at'])
            
        return obj 
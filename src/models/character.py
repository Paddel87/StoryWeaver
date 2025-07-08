"""
Charakter-Modell für StoryWeaver
"""
from typing import List, Set, Dict
from dataclasses import dataclass, field
from .base import StoryElement


@dataclass
class Character(StoryElement):
    """Repräsentiert einen Charakter in der Geschichte"""
    
    # Zusätzliche charakter-spezifische Attribute
    behaviors: List[str] = field(default_factory=list)  # Verhaltensweisen
    items: Set[str] = field(default_factory=set)  # Besessene/genutzte Gegenstände
    relationships: Dict[str, str] = field(default_factory=dict)  # Beziehungen zu anderen Charakteren
    aliases: Set[str] = field(default_factory=set)  # Alternative Namen/Bezeichnungen
    
    def add_behavior(self, behavior: str):
        """Fügt eine Verhaltensweise hinzu"""
        if behavior and behavior not in self.behaviors:
            self.behaviors.append(behavior)
    
    def add_item(self, item_name: str):
        """Fügt einen Gegenstand hinzu"""
        if item_name:
            self.items.add(item_name)
    
    def add_relationship(self, other_character: str, relationship_type: str):
        """Fügt eine Beziehung zu einem anderen Charakter hinzu"""
        if other_character and relationship_type:
            self.relationships[other_character] = relationship_type
    
    def add_alias(self, alias: str):
        """Fügt einen alternativen Namen hinzu"""
        if alias and alias != self.name:
            self.aliases.add(alias)
    
    def merge_with(self, other: 'Character'):
        """Führt diesen Charakter mit einem anderen zusammen"""
        # Basis-Merge aufrufen
        super().merge_with(other)
        
        # Charakter-spezifische Attribute zusammenführen
        for behavior in other.behaviors:
            self.add_behavior(behavior)
        
        self.items.update(other.items)
        self.aliases.update(other.aliases)
        
        # Beziehungen zusammenführen (neuere überschreiben ältere)
        self.relationships.update(other.relationships)
    
    def to_dict(self) -> Dict:
        """Konvertiert den Charakter in ein Dictionary"""
        data = super().to_dict()
        data.update({
            "type": "character",
            "behaviors": self.behaviors,
            "items": list(self.items),
            "relationships": self.relationships,
            "aliases": list(self.aliases)
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        """Erstellt einen Charakter aus einem Dictionary"""
        char = cls(
            name=data['name'],
            description=data.get('description', '')
        )
        
        # Basis-Attribute laden
        char.mentions = data.get('mentions', [])
        char.source_files = set(data.get('source_files', []))
        char.frequency = data.get('frequency', 0)
        
        # Charakter-spezifische Attribute
        char.behaviors = data.get('behaviors', [])
        char.items = set(data.get('items', []))
        char.relationships = data.get('relationships', {})
        char.aliases = set(data.get('aliases', []))
        
        return char 
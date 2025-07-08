"""
Gegenstand-Modell für StoryWeaver
"""
from typing import Set, Dict, Optional
from dataclasses import dataclass, field
from .base import StoryElement


@dataclass
class Item(StoryElement):
    """Repräsentiert einen Gegenstand in der Geschichte"""
    
    # Zusätzliche item-spezifische Attribute
    item_type: Optional[str] = None  # Typ oder Funktion (z.B. Waffe, Werkzeug, Schmuck)
    owners: Set[str] = field(default_factory=set)  # Charaktere, die den Gegenstand besitzen/nutzen
    properties: Dict[str, str] = field(default_factory=dict)  # Eigenschaften (z.B. magisch, verzaubert)
    location: Optional[str] = None  # Wo der Gegenstand sich befindet
    
    def add_owner(self, character_name: str):
        """Fügt einen Besitzer/Nutzer hinzu"""
        if character_name:
            self.owners.add(character_name)
    
    def add_property(self, property_name: str, property_value: str):
        """Fügt eine Eigenschaft hinzu"""
        if property_name and property_value:
            self.properties[property_name] = property_value
    
    def set_type(self, item_type: str):
        """Setzt den Typ des Gegenstands"""
        if item_type:
            self.item_type = item_type
    
    def set_location(self, location: str):
        """Setzt den Ort, wo sich der Gegenstand befindet"""
        if location:
            self.location = location
    
    def merge_with(self, other: 'Item'):
        """Führt diesen Gegenstand mit einem anderen zusammen"""
        # Basis-Merge aufrufen
        super().merge_with(other)
        
        # Item-spezifische Attribute zusammenführen
        if other.item_type and not self.item_type:
            self.item_type = other.item_type
        elif other.item_type and self.item_type != other.item_type:
            # Bei unterschiedlichen Typen beide behalten
            self.item_type = f"{self.item_type} / {other.item_type}"
        
        self.owners.update(other.owners)
        self.properties.update(other.properties)
        
        if other.location:
            self.location = other.location
    
    def to_dict(self) -> Dict:
        """Konvertiert den Gegenstand in ein Dictionary"""
        data = super().to_dict()
        data.update({
            "type": "item",
            "item_type": self.item_type,
            "owners": list(self.owners),
            "properties": self.properties,
            "location": self.location
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Erstellt einen Gegenstand aus einem Dictionary"""
        item = cls(
            name=data['name'],
            description=data.get('description', '')
        )
        
        # Basis-Attribute laden
        item.mentions = data.get('mentions', [])
        item.source_files = set(data.get('source_files', []))
        item.frequency = data.get('frequency', 0)
        
        # Item-spezifische Attribute
        item.item_type = data.get('item_type')
        item.owners = set(data.get('owners', []))
        item.properties = data.get('properties', {})
        item.location = data.get('location')
        
        return item 
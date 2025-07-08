"""
Ort-Modell für StoryWeaver
"""
from typing import List, Set, Dict, Optional
from dataclasses import dataclass, field
from .base import StoryElement


@dataclass
class Location(StoryElement):
    """Repräsentiert einen Ort in der Geschichte"""
    
    # Zusätzliche ort-spezifische Attribute
    location_type: Optional[str] = None  # Art des Orts (Stadt, Ruine, Raum, Planet)
    atmosphere: List[str] = field(default_factory=list)  # Stimmung/Atmosphäre
    significance: Optional[str] = None  # Bedeutung innerhalb der Geschichte
    connected_locations: Set[str] = field(default_factory=set)  # Verbundene Orte
    inhabitants: Set[str] = field(default_factory=set)  # Bewohner/häufige Besucher
    features: List[str] = field(default_factory=list)  # Besondere Merkmale
    
    def set_type(self, location_type: str):
        """Setzt den Typ des Ortes"""
        if location_type:
            self.location_type = location_type
    
    def add_atmosphere(self, mood: str):
        """Fügt eine Stimmung/Atmosphäre hinzu"""
        if mood and mood not in self.atmosphere:
            self.atmosphere.append(mood)
    
    def set_significance(self, significance: str):
        """Setzt die Bedeutung des Ortes"""
        if significance:
            self.significance = significance
    
    def add_connected_location(self, location_name: str):
        """Fügt einen verbundenen Ort hinzu"""
        if location_name:
            self.connected_locations.add(location_name)
    
    def add_inhabitant(self, character_name: str):
        """Fügt einen Bewohner/Besucher hinzu"""
        if character_name:
            self.inhabitants.add(character_name)
    
    def add_feature(self, feature: str):
        """Fügt ein besonderes Merkmal hinzu"""
        if feature and feature not in self.features:
            self.features.append(feature)
    
    def merge_with(self, other: 'Location'):
        """Führt diesen Ort mit einem anderen zusammen"""
        # Basis-Merge aufrufen
        super().merge_with(other)
        
        # Location-spezifische Attribute zusammenführen
        if other.location_type and not self.location_type:
            self.location_type = other.location_type
        elif other.location_type and self.location_type != other.location_type:
            # Bei unterschiedlichen Typen beide behalten
            self.location_type = f"{self.location_type} / {other.location_type}"
        
        # Listen zusammenführen ohne Duplikate
        for mood in other.atmosphere:
            self.add_atmosphere(mood)
        
        for feature in other.features:
            self.add_feature(feature)
        
        # Sets zusammenführen
        self.connected_locations.update(other.connected_locations)
        self.inhabitants.update(other.inhabitants)
        
        # Bedeutung zusammenführen
        if other.significance:
            if self.significance and other.significance not in self.significance:
                self.significance += f" | {other.significance}"
            else:
                self.significance = other.significance
    
    def to_dict(self) -> Dict:
        """Konvertiert den Ort in ein Dictionary"""
        data = super().to_dict()
        data.update({
            "type": "location",
            "location_type": self.location_type,
            "atmosphere": self.atmosphere,
            "significance": self.significance,
            "connected_locations": list(self.connected_locations),
            "inhabitants": list(self.inhabitants),
            "features": self.features
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Erstellt einen Ort aus einem Dictionary"""
        location = cls(
            name=data['name'],
            description=data.get('description', '')
        )
        
        # Basis-Attribute laden
        location.mentions = data.get('mentions', [])
        location.source_files = set(data.get('source_files', []))
        location.frequency = data.get('frequency', 0)
        
        # Location-spezifische Attribute
        location.location_type = data.get('location_type')
        location.atmosphere = data.get('atmosphere', [])
        location.significance = data.get('significance')
        location.connected_locations = set(data.get('connected_locations', []))
        location.inhabitants = set(data.get('inhabitants', []))
        location.features = data.get('features', [])
        
        return location 
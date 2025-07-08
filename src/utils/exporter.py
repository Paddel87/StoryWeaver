"""
JSON-Exporter für StoryWeaver
Exportiert die extrahierten Daten in strukturierte JSON-Dateien
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

from ..models import Character, Item, Location


class JSONExporter:
    """Exportiert Story-Elemente als JSON-Dateien"""
    
    def __init__(self, output_dir: Path = Path("output")):
        """
        Args:
            output_dir: Hauptverzeichnis für die Ausgabe
        """
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Erstelle Ausgabeverzeichnisse
        self._create_output_dirs()
    
    def _create_output_dirs(self):
        """Erstellt die Ausgabeverzeichnisstruktur"""
        dirs = [
            self.output_dir / "characters",
            self.output_dir / "items",
            self.output_dir / "locations"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def export_all(self, characters: Dict[str, Character], 
                   items: Dict[str, Item], 
                   locations: Dict[str, Location]):
        """Exportiert alle Entitäten"""
        self.logger.info("Exportiere alle Entitäten...")
        
        # Exportiere einzelne Entitäten
        char_count = self.export_characters(characters)
        item_count = self.export_items(items)
        loc_count = self.export_locations(locations)
        
        # Erstelle Übersichtsdateien
        self.create_overview_files(characters, items, locations)
        
        # Erstelle Statistik
        self.create_statistics_file(char_count, item_count, loc_count)
        
        self.logger.info(f"Export abgeschlossen: {char_count} Charaktere, {item_count} Gegenstände, {loc_count} Orte")
    
    def export_characters(self, characters: Dict[str, Character]) -> int:
        """Exportiert alle Charaktere als einzelne JSON-Dateien"""
        output_dir = self.output_dir / "characters"
        count = 0
        
        for name, character in characters.items():
            try:
                character.save_to_json(output_dir)
                count += 1
                self.logger.debug(f"Charakter exportiert: {name}")
            except Exception as e:
                self.logger.error(f"Fehler beim Export von Charakter {name}: {e}")
        
        return count
    
    def export_items(self, items: Dict[str, Item]) -> int:
        """Exportiert alle Gegenstände als einzelne JSON-Dateien"""
        output_dir = self.output_dir / "items"
        count = 0
        
        for name, item in items.items():
            try:
                item.save_to_json(output_dir)
                count += 1
                self.logger.debug(f"Gegenstand exportiert: {name}")
            except Exception as e:
                self.logger.error(f"Fehler beim Export von Gegenstand {name}: {e}")
        
        return count
    
    def export_locations(self, locations: Dict[str, Location]) -> int:
        """Exportiert alle Orte als einzelne JSON-Dateien"""
        output_dir = self.output_dir / "locations"
        count = 0
        
        for name, location in locations.items():
            try:
                location.save_to_json(output_dir)
                count += 1
                self.logger.debug(f"Ort exportiert: {name}")
            except Exception as e:
                self.logger.error(f"Fehler beim Export von Ort {name}: {e}")
        
        return count
    
    def create_overview_files(self, characters: Dict[str, Character],
                            items: Dict[str, Item],
                            locations: Dict[str, Location]):
        """Erstellt Übersichtsdateien für alle Entitäten"""
        
        # Charakterübersicht
        char_overview = {
            "total": len(characters),
            "characters": [
                {
                    "name": char.name,
                    "aliases": list(char.aliases),
                    "frequency": char.frequency,
                    "items": list(char.items),
                    "relationships": char.relationships
                }
                for char in characters.values()
            ]
        }
        self._save_json(self.output_dir / "characters_overview.json", char_overview)
        
        # Gegenstandsübersicht
        item_overview = {
            "total": len(items),
            "items": [
                {
                    "name": item.name,
                    "type": item.item_type,
                    "frequency": item.frequency,
                    "owners": list(item.owners),
                    "location": item.location
                }
                for item in items.values()
            ]
        }
        self._save_json(self.output_dir / "items_overview.json", item_overview)
        
        # Ortsübersicht
        location_overview = {
            "total": len(locations),
            "locations": [
                {
                    "name": loc.name,
                    "type": loc.location_type,
                    "frequency": loc.frequency,
                    "inhabitants": list(loc.inhabitants),
                    "connected_locations": list(loc.connected_locations)
                }
                for loc in locations.values()
            ]
        }
        self._save_json(self.output_dir / "locations_overview.json", location_overview)
        
        # Gesamt-Übersicht
        complete_overview = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "version": "1.0",
                "total_entities": len(characters) + len(items) + len(locations)
            },
            "characters": char_overview,
            "items": item_overview,
            "locations": location_overview
        }
        self._save_json(self.output_dir / "complete_overview.json", complete_overview)
    
    def create_statistics_file(self, char_count: int, item_count: int, loc_count: int):
        """Erstellt eine Statistikdatei"""
        stats = {
            "export_timestamp": datetime.now().isoformat(),
            "entity_counts": {
                "characters": char_count,
                "items": item_count,
                "locations": loc_count,
                "total": char_count + item_count + loc_count
            },
            "export_status": "successful"
        }
        
        self._save_json(self.output_dir / "export_statistics.json", stats)
    
    def create_relationship_graph(self, characters: Dict[str, Character],
                                 items: Dict[str, Item],
                                 locations: Dict[str, Location]):
        """Erstellt eine Datei mit allen Beziehungen zwischen Entitäten"""
        relationships = {
            "nodes": [],
            "edges": []
        }
        
        # Knoten hinzufügen
        for char in characters.values():
            relationships["nodes"].append({
                "id": f"char_{char.name}",
                "label": char.name,
                "type": "character"
            })
        
        for item in items.values():
            relationships["nodes"].append({
                "id": f"item_{item.name}",
                "label": item.name,
                "type": "item"
            })
        
        for loc in locations.values():
            relationships["nodes"].append({
                "id": f"loc_{loc.name}",
                "label": loc.name,
                "type": "location"
            })
        
        # Kanten hinzufügen
        
        # Charakter -> Item Beziehungen
        for char in characters.values():
            for item_name in char.items:
                relationships["edges"].append({
                    "source": f"char_{char.name}",
                    "target": f"item_{item_name}",
                    "type": "owns"
                })
        
        # Charakter -> Charakter Beziehungen
        for char in characters.values():
            for other_char, relation in char.relationships.items():
                relationships["edges"].append({
                    "source": f"char_{char.name}",
                    "target": f"char_{other_char}",
                    "type": relation
                })
        
        # Charakter -> Location Beziehungen
        for loc in locations.values():
            for inhabitant in loc.inhabitants:
                relationships["edges"].append({
                    "source": f"char_{inhabitant}",
                    "target": f"loc_{loc.name}",
                    "type": "inhabits"
                })
        
        # Location -> Location Beziehungen
        for loc in locations.values():
            for connected in loc.connected_locations:
                relationships["edges"].append({
                    "source": f"loc_{loc.name}",
                    "target": f"loc_{connected}",
                    "type": "connected"
                })
        
        self._save_json(self.output_dir / "relationship_graph.json", relationships)
    
    def _save_json(self, filepath: Path, data: Any):
        """Speichert Daten als JSON-Datei"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"JSON gespeichert: {filepath}")
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern von {filepath}: {e}")
            raise 
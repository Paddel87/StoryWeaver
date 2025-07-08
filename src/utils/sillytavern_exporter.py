"""
SillyTavern/TavernAI Exporter für StoryWeaver
Exportiert Charaktere im kompatiblen JSON-Format mit PNG-Einbettung
"""
import json
import zlib
import struct
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
from PIL import Image, PngImagePlugin
import base64

from ..models import Character
from .create_default_image import create_default_portrait


class SillyTavernExporter:
    """Exportiert Charaktere im SillyTavern/TavernAI-Format"""
    
    def __init__(self, output_dir: Path = Path("output")):
        """
        Args:
            output_dir: Hauptverzeichnis für die Ausgabe
        """
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Erstelle Ausgabeverzeichnisse
        self.json_dir = self.output_dir / "characters_sillytavern"
        self.png_dir = self.output_dir / "characters_sillytavern_png"
        self._create_output_dirs()
        
        # Stelle sicher, dass das Standardbild existiert
        self.default_portrait_path = Path("assets/images/default_portrait.png")
        if not self.default_portrait_path.exists():
            self.logger.info("Erstelle Standard-Portrait...")
            create_default_portrait()
    
    def _create_output_dirs(self):
        """Erstellt die Ausgabeverzeichnisse"""
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.png_dir.mkdir(parents=True, exist_ok=True)
    
    def export_character(self, character: Character, dialog_lines: List[Dict] = None, 
                        export_png: bool = True) -> Dict[str, Path]:
        """
        Exportiert einen einzelnen Charakter
        
        Args:
            character: Character-Objekt
            dialog_lines: Liste von Dialog-Zeilen für Beispiele
            export_png: Ob auch eine PNG-Datei erstellt werden soll
            
        Returns:
            Dictionary mit Pfaden zu den erstellten Dateien
        """
        # Erstelle TavernAI-JSON
        tavern_data = self._create_tavern_json(character, dialog_lines)
        
        # Speichere JSON
        json_path = self._save_json(character.name, tavern_data)
        
        result = {"json": json_path}
        
        # Erstelle PNG mit eingebetteten Daten
        if export_png:
            png_path = self._create_character_card(character.name, tavern_data)
            result["png"] = png_path
        
        return result
    
    def export_all_characters(self, characters: Dict[str, Character], 
                            dialog_data: Dict[str, List[Dict]] = None,
                            selected_only: List[str] = None) -> Dict[str, List[Path]]:
        """
        Exportiert mehrere Charaktere
        
        Args:
            characters: Dictionary mit allen Charakteren
            dialog_data: Dialog-Daten pro Charakter
            selected_only: Liste von Charakternamen, die exportiert werden sollen
            
        Returns:
            Dictionary mit Listen der erstellten Dateien pro Typ
        """
        if dialog_data is None:
            dialog_data = {}
        
        # Bestimme zu exportierende Charaktere
        to_export = selected_only if selected_only else list(characters.keys())
        
        results = {"json": [], "png": []}
        
        for char_name in to_export:
            if char_name not in characters:
                self.logger.warning(f"Charakter '{char_name}' nicht gefunden, überspringe...")
                continue
            
            character = characters[char_name]
            dialogs = dialog_data.get(char_name, [])
            
            try:
                paths = self.export_character(character, dialogs)
                results["json"].append(paths["json"])
                if "png" in paths:
                    results["png"].append(paths["png"])
                    
                self.logger.info(f"Charakter exportiert: {char_name}")
            except Exception as e:
                self.logger.error(f"Fehler beim Export von {char_name}: {e}")
        
        return results
    
    def _create_tavern_json(self, character: Character, dialog_lines: List[Dict] = None) -> Dict:
        """Erstellt die TavernAI-JSON-Struktur"""
        # Basis-Daten
        tavern_data = {
            "name": character.name,
            "description": self._generate_description(character),
            "personality": self._generate_personality(character),
            "scenario": self._generate_scenario(character),
            "first_mes": self._generate_first_message(character, dialog_lines),
            "mes_example": self._generate_message_examples(character, dialog_lines),
        }
        
        # Optionale Metadaten
        metadata = {
            "tags": self._generate_tags(character),
            "creator": "StoryWeaver",
            "version": "1.0",
            "created_at": datetime.now().isoformat()
        }
        
        if metadata["tags"]:
            tavern_data["metadata"] = metadata
        
        return tavern_data
    
    def _generate_description(self, character: Character) -> str:
        """Generiert eine Charakterbeschreibung"""
        if character.description:
            return character.description
        
        # Fallback: Generiere aus verfügbaren Informationen
        parts = []
        
        if character.aliases:
            parts.append(f"Auch bekannt als: {', '.join(character.aliases)}")
        
        if character.items:
            items_str = ', '.join(list(character.items)[:3])  # Erste 3 Gegenstände
            parts.append(f"Besitzt: {items_str}")
        
        if character.relationships:
            rel_str = ', '.join([f"{k} ({v})" for k, v in list(character.relationships.items())[:2]])
            parts.append(f"Beziehungen: {rel_str}")
        
        return ". ".join(parts) if parts else f"{character.name} ist ein Charakter aus der Geschichte."
    
    def _generate_personality(self, character: Character) -> str:
        """Generiert die Persönlichkeitsbeschreibung"""
        if character.behaviors:
            return ", ".join(character.behaviors)
        
        # Fallback basierend auf Häufigkeit und Kontext
        return "geheimnisvoll, zurückhaltend"
    
    def _generate_scenario(self, character: Character) -> str:
        """Generiert ein Szenario"""
        # Versuche aus Locations zu generieren
        scenario_parts = []
        
        # Suche nach Orten in den Erwähnungen
        for mention in character.mentions[:5]:  # Erste 5 Erwähnungen
            text = mention.get("text", "").lower()
            if any(keyword in text for keyword in ["tempel", "wald", "stadt", "ruine", "berg"]):
                scenario_parts.append(mention["text"])
                break
        
        if scenario_parts:
            return scenario_parts[0]
        
        return "In einer fantastischen Welt voller Geheimnisse und Abenteuer."
    
    def _generate_first_message(self, character: Character, dialog_lines: List[Dict] = None) -> str:
        """Generiert die erste Nachricht"""
        # Versuche aus Dialog-Daten
        if dialog_lines:
            for line in dialog_lines:
                if line.get("speaker") == character.name and line.get("line_type") == "dialog":
                    content = line.get("content", "")
                    if len(content) > 20:  # Sinnvolle Länge
                        return content
        
        # Fallback-Nachrichten
        fallbacks = [
            f"Ah, du bist es. Ich bin {character.name}. Was führt dich hierher?",
            f"*{character.name} blickt dich prüfend an* Wer bist du und was willst du?",
            f"Grüße, Fremder. Man nennt mich {character.name}. Was kann ich für dich tun?"
        ]
        
        import random
        return random.choice(fallbacks)
    
    def _generate_message_examples(self, character: Character, dialog_lines: List[Dict] = None) -> str:
        """Generiert Beispiel-Dialoge im <START>-Format"""
        examples = []
        
        if dialog_lines:
            # Sammle Dialog-Paare
            char_lines = [l for l in dialog_lines if l.get("speaker") == character.name 
                         and l.get("line_type") == "dialog"]
            
            # Versuche Kontext zu finden
            for i, line in enumerate(dialog_lines):
                if (line.get("speaker") == character.name and 
                    line.get("line_type") == "dialog" and 
                    i > 0):
                    
                    # Vorherige Zeile könnte User sein
                    prev_line = dialog_lines[i-1]
                    if prev_line.get("speaker") != character.name:
                        user_text = prev_line.get("content", "").strip()
                        char_text = line.get("content", "").strip()
                        
                        if user_text and char_text:
                            examples.append(f"{{{{user}}}}: {user_text}\n{{{{char}}}}: {char_text}")
                        
                        if len(examples) >= 2:  # Maximal 2 Beispiele
                            break
        
        # Fallback-Beispiele wenn keine gefunden
        if not examples:
            examples = [
                "{{user}}: Wer bist du?",
                f"{{{{char}}}}: Ich bin {character.name}. Und du bist...?",
                "{{user}}: Kannst du mir helfen?",
                "{{char}}: Das kommt darauf an, was du brauchst."
            ]
        
        # Formatiere im <START>-Format
        formatted_examples = []
        for i in range(0, len(examples), 2):
            if i+1 < len(examples):
                formatted_examples.append(f"<START>\n{examples[i]}\n{examples[i+1]}")
        
        return "\n".join(formatted_examples) if formatted_examples else "<START>\n{{user}}: Hallo\n{{char}}: Grüße."
    
    def _generate_tags(self, character: Character) -> List[str]:
        """Generiert Tags für den Charakter"""
        tags = []
        
        # Basis-Tags
        tags.append("fantasy")
        
        # Tags basierend auf Items
        if any(item in str(character.items).lower() for item in ["schwert", "klinge", "dolch"]):
            tags.append("kämpfer")
        if any(item in str(character.items).lower() for item in ["stab", "amulett", "kristall"]):
            tags.append("magier")
        
        # Tags basierend auf Verhalten
        if any(behavior in str(character.behaviors).lower() for behavior in ["mutig", "tapfer"]):
            tags.append("held")
        if any(behavior in str(character.behaviors).lower() for behavior in ["geheimnisvoll", "mysteriös"]):
            tags.append("mysteriös")
        
        return list(set(tags))  # Duplikate entfernen
    
    def _save_json(self, char_name: str, data: Dict) -> Path:
        """Speichert die JSON-Datei"""
        filename = char_name.lower().replace(" ", "_") + ".json"
        filepath = self.json_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _create_character_card(self, char_name: str, tavern_data: Dict) -> Path:
        """Erstellt eine PNG-Charakterkarte mit eingebetteten JSON-Daten"""
        # Lade das Bild
        if self.default_portrait_path.exists():
            img = Image.open(self.default_portrait_path)
        else:
            # Erstelle ein einfaches Fallback-Bild
            img = Image.new('RGB', (400, 600), color=(128, 128, 128))
        
        # Konvertiere JSON zu Bytes
        json_str = json.dumps(tavern_data, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        
        # Komprimiere mit zlib
        compressed_data = zlib.compress(json_bytes)
        
        # Erstelle PNG-Metadaten
        metadata = PngImagePlugin.PngInfo()
        
        # Füge als zTXt-Chunk hinzu (komprimiert)
        # Format: Key als bytes, dann compressed flag (1), dann compression method (0), dann komprimierte Daten
        metadata.add_text("chara", json_str, zip=True)
        
        # Speichere PNG mit Metadaten
        filename = char_name.lower().replace(" ", "_") + ".png"
        filepath = self.png_dir / filename
        
        img.save(filepath, "PNG", pnginfo=metadata)
        
        self.logger.debug(f"PNG-Charakterkarte erstellt: {filepath}")
        return filepath 
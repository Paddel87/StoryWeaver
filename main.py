#!/usr/bin/env python3
"""
StoryWeaver - Hauptprogramm
Lokale Analyse von dialogbasierten Geschichten
"""
import argparse
import logging
from pathlib import Path
import sys
from tqdm import tqdm

from src.extractors.entity_extractor import EntityExtractor
from src.utils.merger import EntityMerger
from src.utils.exporter import JSONExporter
from src.utils.sillytavern_exporter import SillyTavernExporter


class StoryWeaver:
    """Hauptklasse für die Story-Analyse"""
    
    def __init__(self, input_dir: Path, output_dir: Path, 
                 similarity_threshold: int = 80,
                 spacy_model: str = "de_core_news_sm",
                 sillytavern_export: bool = False):
        """
        Args:
            input_dir: Verzeichnis mit Chat-Dateien
            output_dir: Ausgabeverzeichnis für JSON-Dateien
            similarity_threshold: Schwellwert für Ähnlichkeit (0-100)
            spacy_model: SpaCy-Modell für NLP
            sillytavern_export: Ob SillyTavern-Export aktiviert werden soll
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.sillytavern_export = sillytavern_export
        
        # Initialisiere Komponenten
        self.extractor = EntityExtractor(spacy_model)
        self.merger = EntityMerger(similarity_threshold)
        self.exporter = JSONExporter(output_dir)
        
        # SillyTavern-Exporter bei Bedarf
        if self.sillytavern_export:
            self.tavern_exporter = SillyTavernExporter(output_dir)
        
        # Setup Logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Konfiguriert das Logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'storyweaver.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_files(self):
        """Verarbeitet alle Chat-Dateien im Input-Verzeichnis"""
        # Finde alle Text-Dateien
        chat_files = list(self.input_dir.glob("*.txt")) + list(self.input_dir.glob("*.md"))
        
        if not chat_files:
            self.logger.warning(f"Keine Chat-Dateien in {self.input_dir} gefunden!")
            return
        
        self.logger.info(f"Gefunden: {len(chat_files)} Chat-Dateien")
        
        # Verarbeite jede Datei
        for file_path in tqdm(chat_files, desc="Verarbeite Dateien"):
            self.logger.info(f"Analysiere: {file_path.name}")
            try:
                self.extractor.extract_from_file(file_path)
            except Exception as e:
                self.logger.error(f"Fehler bei {file_path.name}: {e}")
                continue
        
        # Hole alle extrahierten Entitäten
        self.logger.info("Extrahierung abgeschlossen. Beginne Zusammenführung...")
        
        # Führe ähnliche Entitäten zusammen
        merged_characters = self.merger.merge_characters(self.extractor.characters)
        merged_items = self.merger.merge_items(self.extractor.items)
        merged_locations = self.merger.merge_locations(self.extractor.locations)
        
        self.logger.info(f"Zusammenführung abgeschlossen:")
        self.logger.info(f"  - {len(merged_characters)} Charaktere")
        self.logger.info(f"  - {len(merged_items)} Gegenstände")
        self.logger.info(f"  - {len(merged_locations)} Orte")
        
        # Exportiere die Ergebnisse
        self.exporter.export_all(merged_characters, merged_items, merged_locations)
        
        # Erstelle Beziehungsgraph
        self.exporter.create_relationship_graph(merged_characters, merged_items, merged_locations)
        
        # SillyTavern-Export wenn aktiviert
        if self.sillytavern_export:
            self.logger.info("Erstelle SillyTavern-kompatible Charakterkarten...")
            
            # Hole Dialog-Daten
            dialog_data = self.extractor.get_dialog_data()
            
            # Exportiere alle Charaktere
            results = self.tavern_exporter.export_all_characters(
                merged_characters, 
                dialog_data
            )
            
            self.logger.info(f"SillyTavern-Export abgeschlossen:")
            self.logger.info(f"  - {len(results['json'])} JSON-Dateien erstellt")
            self.logger.info(f"  - {len(results['png'])} PNG-Charakterkarten erstellt")
        
        self.logger.info(f"Analyse abgeschlossen! Ergebnisse in: {self.output_dir}")
    
    def print_summary(self):
        """Gibt eine Zusammenfassung der Ergebnisse aus"""
        print("\n" + "="*50)
        print("StoryWeaver - Analyse abgeschlossen")
        print("="*50)
        print(f"\nErgebnisse gespeichert in: {self.output_dir.absolute()}")
        print("\nDateistruktur:")
        print("  output/")
        print("  ├── characters/       # Einzelne Charakter-JSONs")
        print("  ├── items/           # Einzelne Gegenstands-JSONs")
        print("  ├── locations/       # Einzelne Orts-JSONs")
        print("  ├── characters_overview.json")
        print("  ├── items_overview.json")
        print("  ├── locations_overview.json")
        print("  ├── complete_overview.json")
        print("  ├── relationship_graph.json")
        print("  ├── export_statistics.json")
        
        if self.sillytavern_export:
            print("  ├── characters_sillytavern/    # SillyTavern JSON-Dateien")
            print("  └── characters_sillytavern_png/ # SillyTavern PNG-Charakterkarten")
        
        print("\n" + "="*50)


def main():
    """Hauptfunktion mit CLI"""
    parser = argparse.ArgumentParser(
        description="StoryWeaver - Lokale Analyse von dialogbasierten Geschichten",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python main.py examples/             # Analysiert alle Dateien im examples-Ordner
  python main.py examples/ -o results/ # Speichert Ergebnisse in results/
  python main.py examples/ -t 70       # Niedrigerer Ähnlichkeitsschwellwert
  python main.py examples/ -m en_core_web_sm  # Englisches SpaCy-Modell
  python main.py examples/ -s          # Mit SillyTavern-Export
  python main.py examples/ -s -v       # SillyTavern-Export mit Details
        """
    )
    
    parser.add_argument(
        'input_dir',
        type=str,
        help='Verzeichnis mit Chat-Dateien (.txt oder .md)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output',
        help='Ausgabeverzeichnis für JSON-Dateien (Standard: output/)'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=80,
        help='Ähnlichkeitsschwellwert für Zusammenführung (0-100, Standard: 80)'
    )
    
    parser.add_argument(
        '-m', '--model',
        type=str,
        default='de_core_news_sm',
        help='SpaCy-Modell für NLP (Standard: de_core_news_sm)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Ausführliche Ausgabe'
    )
    
    parser.add_argument(
        '-s', '--sillytavern',
        action='store_true',
        help='Erstellt zusätzlich SillyTavern-kompatible Charakterkarten (JSON + PNG)'
    )
    
    args = parser.parse_args()
    
    # Setze Logging-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validiere Input-Verzeichnis
    input_dir = Path(args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Fehler: Verzeichnis '{input_dir}' existiert nicht!")
        sys.exit(1)
    
    # Erstelle StoryWeaver-Instanz
    weaver = StoryWeaver(
        input_dir=input_dir,
        output_dir=Path(args.output),
        similarity_threshold=args.threshold,
        spacy_model=args.model,
        sillytavern_export=args.sillytavern
    )
    
    try:
        # Verarbeite Dateien
        weaver.process_files()
        
        # Zeige Zusammenfassung
        weaver.print_summary()
        
    except KeyboardInterrupt:
        print("\n\nVerarbeitung abgebrochen!")
        sys.exit(1)
    except Exception as e:
        print(f"\nFehler: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 
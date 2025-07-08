#!/usr/bin/env python3
"""
Test-Skript für SillyTavern-Export
Demonstriert die Verwendung der neuen Export-Funktionen
"""
from pathlib import Path
from src.models import Character
from src.utils.sillytavern_exporter import SillyTavernExporter

# Erstelle einen Test-Charakter
test_char = Character(name="Test Magier")
test_char.description = "Ein mächtiger Zauberer aus dem Norden"
test_char.behaviors = ["weise", "mysteriös", "hilfsbereit"]
test_char.items.add("Zauberstab")
test_char.items.add("Kristallkugel")
test_char.add_mention("Der alte Magier betrat den Raum.", "test.txt", 1)

# Erstelle Exporter
exporter = SillyTavernExporter(Path("test_output"))

# Beispiel-Dialog-Daten
dialog_data = [
    {
        "speaker": "Test Magier",
        "content": "Willkommen in meinem Turm, Reisender.",
        "line_type": "dialog",
        "line_number": 5
    },
    {
        "speaker": "Held",
        "content": "Ich brauche deine Hilfe, weiser Magier.",
        "line_type": "dialog",
        "line_number": 6
    },
    {
        "speaker": "Test Magier",
        "content": "Ich werde sehen, was ich tun kann. Die alten Schriften sprechen von großer Gefahr.",
        "line_type": "dialog",
        "line_number": 7
    }
]

# Exportiere den Charakter
print("Exportiere Test-Charakter...")
result = exporter.export_character(test_char, dialog_data)

print("\nErstellte Dateien:")
for file_type, path in result.items():
    print(f"  {file_type}: {path}")

print("\nTest abgeschlossen! Prüfe die Dateien in 'test_output/'")
print("\nHinweis: Die PNG-Datei kann direkt in SillyTavern importiert werden.") 
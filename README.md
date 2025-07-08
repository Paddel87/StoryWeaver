# StoryWeaver

StoryWeaver ist ein lokales Python-Tool zur Analyse von dialogbasierten Geschichten aus Chat-Verläufen. Es extrahiert automatisch Charaktere, Gegenstände und Orte aus Textdateien und erstellt strukturierte JSON-Dateien für die weitere Verwendung.

## Features

- **Automatische Extraktion** von Charakteren, Gegenständen und Orten
- **Intelligente Zusammenführung** von Duplikaten über mehrere Dateien
- **Flexible Parser** für verschiedene Chat-Formate
- **NLP-basierte Analyse** mit spaCy
- **Strukturierte JSON-Ausgabe** für einfache Weiterverarbeitung
- **Beziehungsgraphen** zwischen allen Entitäten
- **SillyTavern/TavernAI Export** - Erstellt kompatible Charakterkarten
- **100% lokal** - keine API-Zugriffe erforderlich

## Installation

### 1. Repository klonen
```bash
git clone https://github.com/yourusername/StoryWeaver.git
cd StoryWeaver
```

### 2. Virtuelle Umgebung einrichten

#### Option A: Mit dem Setup-Skript (empfohlen)
```bash
chmod +x setup.sh
./setup.sh
```

#### Option B: Manuell
```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Aktivieren (Windows)
# venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# SpaCy Sprachmodell herunterladen
python -m spacy download de_core_news_sm
```

## Verwendung

### Grundlegende Nutzung
```bash
# Aktiviere virtuelle Umgebung
source venv/bin/activate

# Analysiere Chat-Dateien
python main.py examples/
```

### Erweiterte Optionen
```bash
# Eigenes Ausgabeverzeichnis
python main.py examples/ -o meine_ergebnisse/

# Niedrigerer Ähnlichkeitsschwellwert (mehr Zusammenführungen)
python main.py examples/ -t 70

# Englisches SpaCy-Modell verwenden
python main.py examples/ -m en_core_web_sm

# Ausführliche Ausgabe
python main.py examples/ -v

# Mit SillyTavern-Export
python main.py examples/ -s

# SillyTavern-Export mit Details
python main.py examples/ -s -v
```

### Kommandozeilenoptionen
- `input_dir`: Verzeichnis mit Chat-Dateien (.txt oder .md)
- `-o, --output`: Ausgabeverzeichnis (Standard: output/)
- `-t, --threshold`: Ähnlichkeitsschwellwert 0-100 (Standard: 80)
- `-m, --model`: SpaCy-Modell (Standard: de_core_news_sm)
- `-v, --verbose`: Ausführliche Ausgabe
- `-s, --sillytavern`: Erstellt SillyTavern-kompatible Charakterkarten

## Chat-Format

StoryWeaver erkennt verschiedene Chat-Formate automatisch:

### Dialog mit Doppelpunkt
```
Lyra: Ich habe den Tempel gefunden.
Raenor: Sei vorsichtig dort drin!
```

### Aktionen in eckigen Klammern
```
[Lyra öffnet vorsichtig die Tür]
[Raenor zieht sein Schwert]
```

### Erzählertext
```
Erzähler: Die Nacht war dunkel und stürmisch.
Die alte Burg ragte bedrohlich in den Himmel.
```

### Aktionen mit Sternchen
```
*öffnet die Schatztruhe*
*blickt sich nervös um*
```

## Ausgabestruktur

Nach der Analyse finden Sie folgende Struktur im Ausgabeverzeichnis:

```
output/
├── characters/               # Einzelne JSON-Dateien pro Charakter
│   ├── lyra_nightshade.json
│   └── raenor.json
├── items/                   # Einzelne JSON-Dateien pro Gegenstand
│   ├── kristallamulett.json
│   └── schwert_dämmerlicht.json
├── locations/               # Einzelne JSON-Dateien pro Ort
│   ├── tempel_von_morrakel.json
│   └── schwarzer_pass.json
├── characters_overview.json  # Übersicht aller Charaktere
├── items_overview.json      # Übersicht aller Gegenstände
├── locations_overview.json  # Übersicht aller Orte
├── complete_overview.json   # Gesamtübersicht
├── relationship_graph.json  # Beziehungen zwischen Entitäten
├── export_statistics.json   # Export-Statistiken
├── storyweaver.log         # Log-Datei
│
├── characters_sillytavern/  # (Optional mit -s) TavernAI JSON-Format
│   ├── lyra_nightshade.json
│   └── raenor.json
└── characters_sillytavern_png/  # (Optional mit -s) PNG-Charakterkarten
    ├── lyra_nightshade.png
    └── raenor.png
```

## JSON-Struktur

### Charakter-Beispiel
```json
{
  "name": "Lyra Nightshade",
  "description": "Spricht in chat_example1.txt | Spricht in chat_example2.txt",
  "frequency": 15,
  "behaviors": ["vorsichtig", "entschlossen"],
  "items": ["kristallamulett", "karte"],
  "relationships": {
    "Raenor": "Gefährte",
    "Aelon": "alter Freund"
  },
  "aliases": ["Lyra"],
  "type": "character"
}
```

### Gegenstand-Beispiel
```json
{
  "name": "Kristallamulett",
  "description": "",
  "frequency": 3,
  "item_type": "schmuck / magisch",
  "owners": ["Lyra"],
  "properties": {
    "magisch": "leuchtet bei Magie"
  },
  "type": "item"
}
```

### Ort-Beispiel
```json
{
  "name": "Tempel Von Morrakel",
  "description": "",
  "frequency": 2,
  "location_type": "gebäude",
  "atmosphere": ["verlassen", "magisch", "gefährlich"],
  "significance": "Ort alter Magie",
  "inhabitants": [],
  "connected_locations": ["Dorf"],
  "features": ["alte Inschriften", "bröckelnde Steine"],
  "type": "location"
}
```

## SillyTavern-Export

Mit der Option `-s` erstellt StoryWeaver automatisch SillyTavern/TavernAI-kompatible Charakterkarten:

### Features
- **Automatische JSON-Generierung** im TavernAI-Format
- **PNG-Charakterkarten** mit eingebetteten Metadaten (zTXt-Chunk)
- **Intelligente Feldgenerierung** aus extrahierten Daten
- **Beispiel-Dialoge** aus den Chat-Verläufen

### TavernAI JSON-Format
```json
{
  "name": "Lyra Nightshade",
  "description": "Geheimnisvolle Elfenmagierin mit einem Kristallamulett",
  "personality": "vorsichtig, misstrauisch, loyal",
  "scenario": "Am Rande des alten Tempels von Morrakel",
  "first_mes": "Ich habe den Tempel endlich gefunden. Er ist verlassen, aber voller alter Magie.",
  "mes_example": "<START>\n{{user}}: Wer bist du?\n{{char}}: Ich bin Lyra Nightshade. Und du bist...?",
  "metadata": {
    "tags": ["fantasy", "magier"],
    "creator": "StoryWeaver"
  }
}
```

### Verwendung in SillyTavern
1. Kopiere die PNG-Dateien aus `output/characters_sillytavern_png/`
2. Importiere sie in SillyTavern über "Import Character"
3. Die eingebetteten Daten werden automatisch erkannt

## Erweiterung

### Neue Schlüsselwörter hinzufügen

Bearbeiten Sie `src/extractors/entity_extractor.py`:

```python
self.item_keywords = {
    'waffen': ['schwert', 'dolch', 'stab', ...],
    'neue_kategorie': ['neues_item1', 'neues_item2']
}
```

### Neue Chat-Formate unterstützen

Bearbeiten Sie `src/parsers/chat_parser.py` und fügen Sie neue Regex-Muster hinzu:

```python
PATTERNS = {
    'neues_format': re.compile(r'IHR_REGEX_MUSTER'),
    ...
}
```

## Tests ausführen

```bash
# Einzelne Tests
python tests/test_parser.py

# Mit pytest (wenn installiert)
pytest tests/
```

## Streamlit UI

Eine interaktive Benutzeroberfläche für StoryWeaver ist jetzt verfügbar!

### Features der UI
- **Visuelle Darstellung** aller extrahierten Charaktere, Orte und Gegenstände
- **Interaktive Filter** nach Namen, Gegenständen und Eigenschaften
- **Charakter-Bearbeitung** direkt in der Oberfläche
- **Checkbox-Auswahl** für selektiven Export
- **Live-Vorschau** der generierten JSON-Daten
- **Ein-Klick-Export** als JSON und/oder PNG

### UI starten
```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Streamlit-App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

## Troubleshooting

### SpaCy-Modell nicht gefunden
```bash
python -m spacy download de_core_news_sm
```

### Keine Entitäten gefunden
- Prüfen Sie das Chat-Format
- Verwenden Sie `-v` für ausführliche Ausgabe
- Reduzieren Sie den Threshold mit `-t 60`

### Speicherfehler bei großen Dateien
- Teilen Sie große Chat-Dateien auf
- Verarbeiten Sie Dateien in Batches

## Lizenz

MIT License - siehe LICENSE Datei

## Beitragen

Pull Requests sind willkommen! Für größere Änderungen öffnen Sie bitte zuerst ein Issue.

## Autoren

- Entwickelt für die lokale Analyse von Rollenspielen und Story-basierten Chats 
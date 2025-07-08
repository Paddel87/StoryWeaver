# StoryWeaver

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/Paddel87/StoryWeaver/releases/tag/v1.1.0)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)

StoryWeaver ist ein lokales Python-Tool zur Analyse von dialogbasierten Geschichten aus Chat-Verläufen. Es extrahiert automatisch Charaktere, Gegenstände und Orte aus Textdateien und erstellt strukturierte JSON-Dateien für die weitere Verwendung.

📋 **[Changelog](CHANGELOG.md)** | 🐛 **[Issues](https://github.com/Paddel87/StoryWeaver/issues)** | 💡 **[Discussions](https://github.com/Paddel87/StoryWeaver/discussions)**

## Features

- **Automatische Extraktion** von Charakteren, Gegenständen und Orten
- **Intelligente Zusammenführung** von Duplikaten über mehrere Dateien
- **Flexible Parser** für verschiedene Chat-Formate
- **NLP-basierte Analyse** mit spaCy
- **Strukturierte JSON-Ausgabe** für einfache Weiterverarbeitung
- **Beziehungsgraphen** zwischen allen Entitäten
- **SillyTavern/TavernAI Export** - Erstellt kompatible Charakterkarten
- **100% lokal** - keine API-Zugriffe erforderlich

### Neue UI-Features (v1.1.0)
- **📤 Drag & Drop Upload** - Dateien direkt in die Web-UI hochladen
- **📥 Download-Funktionen** - Alle Ergebnisse als JSON oder ZIP herunterladen
- **🔧 Batch-Bearbeitung** - Mehrere Charaktere gleichzeitig bearbeiten
- **🔍 Erweiterte Filter** - Nach Häufigkeit, Verhalten, Beziehungen filtern
- **🎯 Smart Selection** - Intelligente Auswahl (Top N, mit Item, etc.)
- **👁️ Verbesserte Vorschau** - JSON, lesbare und tabellarische Ansichten
- **⚡ Performance** - Optimiert für große Geschichten (600k-800k Tokens)

## Installation

### 🐳 Docker (Empfohlen)
Die einfachste Installation erfolgt über Docker. Siehe [Docker Setup Guide](README.Docker.md) für detaillierte Anweisungen.

**Option 1: Vorgefertigtes Image von GitHub Container Registry**
```bash
# Image ziehen und starten
docker run -d -p 8501:8501 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  ghcr.io/paddel87/storyweaver:latest
# Öffne http://localhost:8501
```

**Option 2: Selbst bauen mit Docker Compose**
```bash
# Repository klonen
git clone https://github.com/Paddel87/StoryWeaver.git
cd StoryWeaver
docker-compose up -d
# Öffne http://localhost:8501
```

### Manuelle Installation

#### 1. Repository klonen
```bash
git clone https://github.com/Paddel87/StoryWeaver.git
cd StoryWeaver
```

#### 2. Virtuelle Umgebung einrichten

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

### SpaCy-Modell-Konfiguration
StoryWeaver unterstützt alle drei deutschen SpaCy-Modelle:

| Modell | Größe | Genauigkeit | Empfohlen für |
|--------|-------|-------------|---------------|
| `de_core_news_sm` | 15 MB | ~90% | Kleine Texte, schnelle Verarbeitung |
| `de_core_news_md` | 45 MB | ~91% | **Standard** - Beste Balance |
| `de_core_news_lg` | 550 MB | ~92% | Große Geschichten (>100k Tokens) |

```bash
# Modell über Kommandozeile wählen
python main.py examples/ -m de_core_news_lg

# Oder über Umgebungsvariable (Docker)
SPACY_MODEL=de_core_news_lg docker-compose up
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
- **Drag & Drop Upload** - Dateien direkt hochladen ohne Verzeichnis-Setup
- **Visuelle Darstellung** aller extrahierten Charaktere, Orte und Gegenstände
- **Erweiterte Filter** nach Namen, Häufigkeit, Verhalten, Beziehungen
- **Batch-Bearbeitung** - Mehrere Charaktere gleichzeitig bearbeiten
- **Smart Selection** - Intelligente Auswahl nach verschiedenen Kriterien
- **Charakter-Bearbeitung** direkt in der Oberfläche
- **Checkbox-Auswahl** für selektiven Export
- **Live-Vorschau** in JSON, lesbarer und tabellarischer Form
- **Ein-Klick-Export** als JSON und/oder PNG
- **Download-Funktionen** - Alle Ergebnisse direkt herunterladen

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

Pull Requests sind willkommen! Bitte lies unsere [Contributing Guidelines](CONTRIBUTING.md) für Details zum Entwicklungsprozess.

## Autoren

- Entwickelt für die lokale Analyse von Rollenspielen und Story-basierten Chats 
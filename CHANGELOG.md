# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt verwendet [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unveröffentlicht]

### Geplant
- Web-Scraping für Online-Geschichten
- KI-Integration für verbesserte Charakteranalyse
- Export zu World Anvil und Obsidian
- Mehrsprachige Unterstützung (Englisch, Spanisch, Französisch)
- Benutzerdefinierte Charakterportraits Upload

## [1.0.0] - 2025-07-08

### Hinzugefügt
- **Kernfunktionalität**
  - Automatische Extraktion von Charakteren, Gegenständen und Orten aus Chat-Verläufen
  - Intelligente Duplikaterkennung und -zusammenführung
  - NLP-basierte Analyse mit spaCy (Deutsch)
  
- **Parser-Unterstützung**
  - Dialog mit Doppelpunkt (z.B. `Lyra: Text`)
  - Aktionen in eckigen Klammern `[Aktion]`
  - Aktionen mit Sternchen `*Aktion*`
  - Erzählertext-Erkennung
  
- **Export-Funktionen**
  - Strukturierte JSON-Ausgabe für alle Entitäten
  - SillyTavern/TavernAI kompatible Charakterkarten
  - PNG-Export mit eingebetteten Metadaten (zTXt-Chunk)
  - Beziehungsgraphen zwischen Entitäten
  
- **Streamlit UI**
  - Interaktive Web-Oberfläche
  - Charakterkarten mit Bearbeitungsfunktion
  - Filter und Suchfunktionen
  - Checkbox-basierte Export-Auswahl
  - Live-Vorschau der TavernAI JSON-Daten
  
- **Entwickler-Features**
  - Modulare Architektur
  - Umfassende Dokumentation
  - Beispiel-Chatverläufe
  - Setup-Skript für einfache Installation
  - Test-Suite

### Technischer Stack
- Python 3.8+
- spaCy 3.7+ für NLP
- Streamlit 1.28+ für UI
- Pillow für Bildverarbeitung
- fuzzywuzzy für String-Matching

### Bekannte Einschränkungen
- Nur deutsche Sprachmodelle in v1.0
- Standardbild für alle Charaktere
- Keine direkte API-Integration

[Unveröffentlicht]: https://github.com/Paddel87/StoryWeaver/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Paddel87/StoryWeaver/releases/tag/v1.0 
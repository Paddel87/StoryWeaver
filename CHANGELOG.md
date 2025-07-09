# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt verwendet [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unveröffentlicht]

### Hinzugefügt
- **JSON-Unterstützung für strukturierte Daten**
  - Import von Charakteren, Dialogen und Beziehungen als strukturierte JSON-Dateien
  - Verschiedene JSON-Formate werden unterstützt (Charakterlisten, Dialoglisten, etc.)
  - Beispiel-Template `examples/character_template.json` zur Referenz
  - Verbesserte UI mit detaillierten Informationen zu JSON-Formaten
  
- **Verbesserte Entity-Merger-Logik**
  - Intelligentere Normalisierung von Entitätsnamen zur Reduzierung von Duplikaten
  - Erweiterte Erkennung grammatikalischer Variationen (z.B. "Das Seil", "Dem Seil")
  - Verbesserte Basisextraktion für Gegenstände und Pluralformerkennung
  - Optimierte Zusammenführung ähnlicher Orte und Charaktere

### Geplant
- Web-Scraping für Online-Geschichten
- KI-Integration für verbesserte Charakteranalyse
- Export zu World Anvil und Obsidian
- Mehrsprachige Unterstützung (Englisch, Spanisch, Französisch)
- Benutzerdefinierte Charakterportraits Upload

## [1.1.0] - 2025-01-09

### Hinzugefügt
- **Streamlit UI Verbesserungen (Phase 1 + 2)**
  - **Download-Funktionalität**: Direkte Downloads aller Analyseergebnisse als JSON oder ZIP
  - **Drag & Drop File Upload**: Dateien direkt in die Web-UI hochladen ohne Verzeichnis-Setup
  - **Batch-Bearbeitung**: Mehrere Charaktere gleichzeitig bearbeiten (Verhaltensweisen, Beschreibungen, Beziehungen)
  - **Erweiterte Filter**: Nach Häufigkeit, Verhaltensweisen, Beziehungen und Beschreibung filtern
  - **Smart Selection**: Intelligente Charakterauswahl (Top N, mit Item, ohne Beziehungen)
  - **Verbesserte Vorschau**: Tab-basierte Ansichten (JSON, Lesbar, Tabelle)
  - **Batch-Export**: Nur ausgewählte Charaktere exportieren
  - **Bessere Eingabe-Hilfe**: Dropdown-Menü statt Textfeld, kontextuelle Hilfe

- **Performance-Optimierungen für große Texte**
  - Batch-Verarbeitung für Dateien >1000 Zeilen
  - SpaCy-Pipeline-Optimierung (nur benötigte Komponenten)
  - Erhöhtes Textlimit auf 2 Millionen Zeichen
  - Speicher-Management mit Garbage Collection
  - Unterstützung für 600k-800k Token große Geschichten

- **SpaCy-Modell-Flexibilität**
  - Alle drei deutschen Modelle vorinstalliert (sm, md, lg)
  - Konfigurierbar über Umgebungsvariable SPACY_MODEL
  - Standard: de_core_news_md für bessere Balance

- **Docker-Unterstützung**
  - Multi-Stage Dockerfile für optimierte Images
  - Docker Compose Konfigurationen für Entwicklung und Produktion
  - Automatisches Caching von spaCy-Modellen
  - Health Checks und Restart-Policies
  - Volume-Management für persistente Daten
  - Makefile mit praktischen Docker-Shortcuts
  - Ausführliche Docker-Dokumentation (README.Docker.md)
  
- **GitHub Container Registry (GHCR)**
  - Automatisches Build und Push via GitHub Actions
  - Multi-Platform Images (linux/amd64, linux/arm64)
  - Versionierte Tags und latest-Tag
  - Makefile-Integration für lokales Push zu GHCR
  - Dokumentation für GHCR-Nutzung
  
- **Entwickler-Tools**
  - GitHub Actions für CI/CD (Tests auf Python 3.8-3.12)
  - GitHub Actions für Docker Build und Push zu GHCR
  - Issue Templates für Bug Reports und Feature Requests
  - Pull Request Template
  - Contributing Guidelines (CONTRIBUTING.md)
  - Conventional Commits Standard
  
- **Projektstruktur**
  - Versionsdatei (VERSION) für einheitliche Versionsverwaltung
  - Branch-Struktur (main, develop, feature/*)
  - Erweiterte .gitignore für Docker und Uploads

### Geändert
- README.md erweitert um Docker-Installation als empfohlene Methode
- README.md erweitert um GHCR als primäre Docker-Image-Quelle
- Badges für Version, Lizenz und Python-Kompatibilität hinzugefügt

### Geplant
- Web-Scraping für Online-Geschichten
- KI-Integration für verbesserte Charakteranalyse
- Export zu World Anvil und Obsidian
- Mehrsprachige Unterstützung (Englisch, Spanisch, Französisch)
- Benutzerdefinierte Charakterportraits Upload

## [1.0.0] - 2025-01-08

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

[Unveröffentlicht]: https://github.com/Paddel87/StoryWeaver/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Paddel87/StoryWeaver/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Paddel87/StoryWeaver/releases/tag/v1.0 
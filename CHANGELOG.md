# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt verwendet [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unveröffentlicht]

### Hinzugefügt
- **Docker-Unterstützung**
  - Multi-Stage Dockerfile für optimierte Images
  - Docker Compose Konfigurationen für Entwicklung und Produktion
  - Automatisches Caching von spaCy-Modellen
  - Health Checks und Restart-Policies
  - Volume-Management für persistente Daten
  - Makefile mit praktischen Docker-Shortcuts
  - Ausführliche Docker-Dokumentation (README.Docker.md)
  
- **Entwickler-Tools**
  - GitHub Actions für CI/CD (Tests auf Python 3.8-3.12)
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

[Unveröffentlicht]: https://github.com/Paddel87/StoryWeaver/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Paddel87/StoryWeaver/releases/tag/v1.0 
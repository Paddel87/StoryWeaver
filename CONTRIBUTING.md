# Contributing to StoryWeaver

Vielen Dank für dein Interesse, zu StoryWeaver beizutragen! 🎉

## Entwicklungsprozess

Wir verwenden GitHub Flow mit folgender Branch-Struktur:
- `main` - Stabiler Release-Branch
- `develop` - Hauptentwicklungsbranch
- `feature/*` - Feature-Branches
- `hotfix/*` - Dringende Bugfixes

## Wie du beitragen kannst

### 1. Issues melden
- Nutze die [Issue-Templates](https://github.com/Paddel87/StoryWeaver/issues/new/choose)
- Beschreibe Bugs detailliert mit Reproduktionsschritten
- Feature-Requests sollten Use Cases enthalten

### 2. Code beitragen

1. **Fork das Repository**
   ```bash
   git clone https://github.com/[dein-username]/StoryWeaver.git
   cd StoryWeaver
   ```

2. **Erstelle einen Feature-Branch**
   ```bash
   git checkout develop
   git checkout -b feature/deine-feature-beschreibung
   ```

3. **Installiere die Entwicklungsumgebung**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download de_core_news_sm
   ```

4. **Mache deine Änderungen**
   - Folge dem bestehenden Code-Stil
   - Füge Tests für neue Features hinzu
   - Aktualisiere die Dokumentation

5. **Teste deine Änderungen**
   ```bash
   # Führe Tests aus
   python -m pytest tests/
   
   # Teste die Funktionalität
   python main.py examples/
   
   # Teste die UI
   streamlit run app.py
   ```

6. **Committe deine Änderungen**
   ```bash
   git add .
   git commit -m "feat: Beschreibung deiner Änderung"
   ```

   Wir folgen [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` Neue Features
   - `fix:` Bugfixes
   - `docs:` Dokumentation
   - `style:` Formatierung
   - `refactor:` Code-Refactoring
   - `test:` Tests
   - `chore:` Wartungsarbeiten

7. **Push und erstelle einen Pull Request**
   ```bash
   git push origin feature/deine-feature-beschreibung
   ```

### 3. Code-Standards

- **Python**: PEP 8
- **Docstrings**: Google Style
- **Type Hints**: Verwende sie wo möglich
- **Tests**: Mindestens 80% Coverage für neue Features

### 4. Pull Request Prozess

1. PR gegen `develop` Branch erstellen
2. Beschreibe deine Änderungen im PR
3. Verlinke relevante Issues
4. Warte auf Code Review
5. Adressiere Feedback

### 5. Versionierung

- Wir verwenden [Semantic Versioning](https://semver.org/)
- Version in `src/__init__.py` und `VERSION` aktualisieren
- CHANGELOG.md nach [Keep a Changelog](https://keepachangelog.com/) pflegen

## Entwicklungsrichtlinien

### Neue Features
- Diskutiere große Features erst in einem Issue
- Halte Features klein und fokussiert
- Denke an Rückwärtskompatibilität

### Tests
- Schreibe Tests für neue Funktionalität
- Nutze pytest für Unit Tests
- Teste Edge Cases

### Dokumentation
- Aktualisiere README.md bei Bedarf
- Füge Docstrings zu neuen Funktionen hinzu
- Dokumentiere Breaking Changes

## Community

- **Fragen?** Erstelle eine [Discussion](https://github.com/Paddel87/StoryWeaver/discussions)
- **Bugs?** Öffne ein [Issue](https://github.com/Paddel87/StoryWeaver/issues)
- **Ideen?** Teile sie in den Discussions!

## Lizenz

Mit deinem Beitrag stimmst du zu, dass dein Code unter der MIT-Lizenz veröffentlicht wird.

Vielen Dank für deine Unterstützung! 🚀 
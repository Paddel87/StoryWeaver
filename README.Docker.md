# 🐳 StoryWeaver Docker Setup

Diese Anleitung beschreibt die Docker-basierte Installation und Nutzung von StoryWeaver.

## 📋 Voraussetzungen

- Docker Engine 20.10+
- Docker Compose v2.0+
- 4GB freier RAM (für spaCy Modelle)
- 2GB freier Speicherplatz

## 🚀 Schnellstart

### 1. Repository klonen
```bash
git clone https://github.com/Paddel87/StoryWeaver.git
cd StoryWeaver
```

### 2. Umgebungsvariablen konfigurieren
```bash
# Erstelle .env Datei
cat > .env << EOF
STREAMLIT_THEME=Dark
PROJECT_NAME=StoryWeaver
EOF
```

### 3. Container starten

**Entwicklungsmodus** (mit Live-Code-Reload):
```bash
docker-compose up -d
```

**Produktionsmodus**:
```bash
# Image bauen
docker build -t storyweaver:latest .

# Container starten
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Anwendung aufrufen
Öffne http://localhost:8501 im Browser

## 📁 Verzeichnisstruktur

```
StoryWeaver/
├── input/              # Chat-Verläufe hier ablegen
├── output/             # Exportierte Dateien
├── assets/             # Bilder und Ressourcen
├── streamlit_uploads/  # Hochgeladene Dateien (Docker Volume)
└── examples/           # Beispiel-Chatverläufe
```

## 🔧 Konfiguration

### Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `STREAMLIT_THEME` | `Dark` | UI Theme (Dark/Light) |
| `PROJECT_NAME` | `StoryWeaver` | Projektname in der UI |
| `PYTHONUNBUFFERED` | `1` | Direktes Logging |

### Volumes

| Host-Pfad | Container-Pfad | Beschreibung |
|-----------|----------------|--------------|
| `./input` | `/app/input` | Input-Dateien |
| `./output` | `/app/output` | Output-Dateien |
| `./assets` | `/app/assets` | Bilder/Assets |
| `streamlit_uploads` | `/app/streamlit_uploads` | Upload-Verzeichnis |
| `spacy_models` | `/root/.cache/spacy` | spaCy Model Cache |

## 🛠️ Befehle

### Container-Management

```bash
# Status anzeigen
docker-compose ps

# Logs anzeigen
docker-compose logs -f storyweaver

# Container stoppen
docker-compose down

# Container mit Volumes entfernen
docker-compose down -v
```

### CLI im Container nutzen

```bash
# Bash-Shell im Container
docker-compose exec storyweaver bash

# Direkter CLI-Aufruf
docker-compose exec storyweaver python main.py /app/examples -o /app/output
```

### Image neu bauen

```bash
# Nach Code-Änderungen
docker-compose build --no-cache

# Nur bei Dependency-Änderungen
docker-compose build
```

## 🔍 Debugging

### Health Check
```bash
# Health Status prüfen
docker-compose exec storyweaver curl localhost:8501/_stcore/health
```

### Container-Logs
```bash
# Alle Logs
docker-compose logs

# Nur Fehler
docker-compose logs | grep -i error

# Live-Logs
docker-compose logs -f --tail=100
```

### Volumes inspizieren
```bash
# Volume-Liste
docker volume ls | grep storyweaver

# Volume-Details
docker volume inspect storyweaver_uploads
```

## 🚦 Produktions-Setup

### Mit Traefik (empfohlen)

1. Traefik-Netzwerk erstellen:
```bash
docker network create proxy_network
```

2. Domain in `docker-compose.prod.yml` anpassen:
```yaml
labels:
  - "traefik.http.routers.storyweaver.rule=Host(`ihre-domain.de`)"
```

3. Container starten:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Mit Nginx

1. Nginx-Konfiguration erstellen:
```nginx
server {
    listen 80;
    server_name ihre-domain.de;
    
    location / {
        proxy_pass http://storyweaver:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. Nginx-Service in `docker-compose.prod.yml` aktivieren

## 🎯 Performance-Optimierung

### Build-Cache nutzen
```bash
# Docker Buildkit aktivieren
export DOCKER_BUILDKIT=1

# Mit Cache bauen
docker-compose build
```

### Resource Limits anpassen
In `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Mehr CPUs
      memory: 8G     # Mehr RAM
```

### spaCy-Modell wählen
- `de_core_news_sm`: Schnell, weniger genau (43 MB)
- `de_core_news_md`: Ausgewogen (116 MB)
- `de_core_news_lg`: Genau, langsamer (541 MB)

## ❓ Häufige Probleme

### Port bereits belegt
```bash
# Anderen Port verwenden
sed -i 's/8501:8501/8502:8501/g' docker-compose.yml
```

### Speicherprobleme
```bash
# Docker-Speicher aufräumen
docker system prune -a

# Nur ungenutzte Volumes
docker volume prune
```

### spaCy-Download fehlgeschlagen
```bash
# Manuell im Container installieren
docker-compose exec storyweaver python -m spacy download de_core_news_sm
```

## 📊 Monitoring

### Container-Statistiken
```bash
# Live-Statistiken
docker stats storyweaver-dev

# Einmalige Ausgabe
docker-compose top
```

### Disk-Usage
```bash
# Volume-Größen
docker system df -v | grep storyweaver
```

## 🔄 Updates

1. Code aktualisieren:
```bash
git pull origin main
```

2. Container neu bauen:
```bash
docker-compose down
docker-compose build --pull
docker-compose up -d
```

3. Alte Images aufräumen:
```bash
docker image prune -f
```

## 📝 Entwicklung

### Live-Reload aktiviert
Im Entwicklungsmodus werden Code-Änderungen automatisch erkannt:
- `src/`, `app.py`, `main.py` sind als Read-Only gemountet
- Streamlit erkennt Änderungen und lädt neu

### Neue Dependencies
1. `requirements.txt` aktualisieren
2. Container neu bauen:
```bash
docker-compose build
docker-compose up -d
```

### Tests im Container
```bash
# Tests ausführen
docker-compose exec storyweaver python -m pytest tests/

# Mit Coverage
docker-compose exec storyweaver python -m pytest --cov=src tests/
```

## 🆘 Support

Bei Problemen:
1. [GitHub Issues](https://github.com/Paddel87/StoryWeaver/issues)
2. [Discussions](https://github.com/Paddel87/StoryWeaver/discussions)
3. Logs mit `docker-compose logs` prüfen 

## Weitere Ressourcen

- [Docker Dokumentation](https://docs.docker.com/)
- [Docker Compose Dokumentation](https://docs.docker.com/compose/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)

## GitHub Container Registry (GHCR)

StoryWeaver ist auch über die GitHub Container Registry verfügbar. Dies ermöglicht es, vorgefertigte Images zu verwenden, ohne sie lokal bauen zu müssen.

### Image von GHCR verwenden

```bash
# Image ziehen
docker pull ghcr.io/paddel87/storyweaver:latest

# Container starten
docker run -d -p 8501:8501 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  ghcr.io/paddel87/storyweaver:latest
```

### Mit Docker Compose

Erstelle eine `docker-compose.ghcr.yml`:

```yaml
version: '3.8'

services:
  storyweaver:
    image: ghcr.io/paddel87/storyweaver:latest
    ports:
      - "8501:8501"
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./streamlit_uploads:/app/streamlit_uploads
    environment:
      - STREAMLIT_SERVER_PORT=8501
    restart: unless-stopped
```

### Lokale Entwicklung mit GHCR

Das Makefile enthält praktische Befehle für GHCR:

```bash
# Bei GHCR anmelden (benötigt GitHub Token)
make ghcr-login

# Image bauen und taggen
make ghcr-build

# Image zu GHCR pushen
make ghcr-push

# Alles in einem Schritt
make ghcr-all

# Image von GHCR ziehen
make ghcr-pull

# Container von GHCR Image starten
make ghcr-run
```

### Authentifizierung

Für das Pushen von Images zu GHCR benötigst du ein GitHub Personal Access Token:

1. Gehe zu GitHub Settings → Developer settings → Personal access tokens
2. Erstelle ein neues Token mit den Berechtigungen:
   - `write:packages` (zum Pushen von Images)
   - `read:packages` (zum Pullen von Images)
   - `delete:packages` (optional, zum Löschen von Images)

3. Melde dich an:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u DEIN_GITHUB_USERNAME --password-stdin
```

Oder mit GitHub CLI:
```bash
gh auth token | docker login ghcr.io -u DEIN_GITHUB_USERNAME --password-stdin
```

### Verfügbare Tags

- `latest`: Neueste stabile Version vom main Branch
- `develop`: Aktuelle Entwicklungsversion
- `v1.0.0`, `v1.1.0`, etc.: Spezifische Versionen
- `sha-xxxxx`: Commit-spezifische Builds

### CI/CD Integration

Die GitHub Action `.github/workflows/docker-publish.yml` baut und pusht automatisch Images zu GHCR bei:
- Push auf main Branch → `latest` Tag
- Push auf develop Branch → `develop` Tag  
- Neue Version Tags → Versionsspezifische Tags
- Pull Requests → PR-spezifische Tags

Die Images werden automatisch für `linux/amd64` und `linux/arm64` Architekturen gebaut. 
# Multi-Stage Build für StoryWeaver

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# System-Abhängigkeiten für Build
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pip-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# System-Abhängigkeiten für Runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python-Pakete vom Builder kopieren
COPY --from=builder /root/.local /root/.local

# Sicherstellen, dass Scripts im PATH sind
ENV PATH=/root/.local/bin:$PATH

# Anwendungscode kopieren
COPY . .

# spaCy-Modelle herunterladen (wird gecached)
RUN python -m spacy download de_core_news_sm && \
    python -m spacy download de_core_news_md && \
    python -m spacy download de_core_news_lg

# Setze Standard-SpaCy-Modell (kann überschrieben werden)
ENV SPACY_MODEL=de_core_news_md

# Verzeichnisse für Volumes erstellen
RUN mkdir -p /app/input /app/output /app/assets /app/streamlit_uploads

# Streamlit-Konfiguration
RUN mkdir -p ~/.streamlit && \
    echo "[general]" > ~/.streamlit/credentials.toml && \
    echo "email = \"\"" >> ~/.streamlit/credentials.toml && \
    echo "[server]" > ~/.streamlit/config.toml && \
    echo "headless = true" >> ~/.streamlit/config.toml && \
    echo "enableCORS = false" >> ~/.streamlit/config.toml && \
    echo "port = 8501" >> ~/.streamlit/config.toml

# Port exponieren
EXPOSE 8501

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Streamlit starten
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"] 
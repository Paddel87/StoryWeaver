#!/bin/bash

# StoryWeaver Setup Script

echo "=== StoryWeaver Setup ==="
echo "Erstelle virtuelle Umgebung..."

# Virtuelle Umgebung erstellen
python3 -m venv venv

# Aktiviere virtuelle Umgebung
source venv/bin/activate

echo "Installiere Abhängigkeiten..."

# Pip aktualisieren
pip install --upgrade pip

# Requirements installieren
pip install -r requirements.txt

# SpaCy Sprachmodell herunterladen
echo "Lade deutsches SpaCy-Modell herunter..."
python -m spacy download de_core_news_sm

echo ""
echo "Setup abgeschlossen!"
echo "Aktiviere die virtuelle Umgebung mit: source venv/bin/activate"
echo "Starte das Programm mit: python main.py" 
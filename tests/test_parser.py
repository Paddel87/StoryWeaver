#!/usr/bin/env python3
"""
Tests für den Chat-Parser
"""
import pytest
from pathlib import Path
import sys

# Füge src zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.chat_parser import ChatParser, ChatLine


def test_parse_dialog_colon():
    """Test: Dialog mit Doppelpunkt"""
    parser = ChatParser()
    line = parser._parse_line(1, "Lyra: Ich bin hier")
    
    assert line.speaker == "Lyra"
    assert line.content == "Ich bin hier"
    assert line.line_type == "dialog"


def test_parse_action_brackets():
    """Test: Aktion in eckigen Klammern"""
    parser = ChatParser()
    line = parser._parse_line(1, "[Lyra öffnet die Tür]")
    
    assert line.content == "Lyra öffnet die Tür"
    assert line.line_type == "action"
    assert line.speaker == "Lyra"


def test_parse_narrator():
    """Test: Erzähler-Text"""
    parser = ChatParser()
    line = parser._parse_line(1, "Erzähler: Die Nacht war dunkel.")
    
    assert line.speaker == "Erzähler"
    assert line.content == "Die Nacht war dunkel."
    assert line.line_type == "narration"


def test_parse_file():
    """Test: Komplette Datei parsen"""
    # Erstelle temporäre Test-Datei
    test_content = """Lyra: Hallo Raenor!
Raenor: Grüße, Lyra.
[Lyra lächelt]
Erzähler: Die beiden trafen sich am Marktplatz."""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)
    
    try:
        parser = ChatParser()
        lines = parser.parse_file(temp_path)
        
        assert len(lines) == 4
        assert lines[0].speaker == "Lyra"
        assert lines[1].speaker == "Raenor"
        assert lines[2].line_type == "action"
        assert lines[3].speaker == "Erzähler"
        
        # Test get_speakers
        speakers = parser.get_speakers()
        assert "Lyra" in speakers
        assert "Raenor" in speakers
        assert "Erzähler" not in speakers  # Erzähler wird ausgeschlossen
        
    finally:
        # Aufräumen
        temp_path.unlink()


if __name__ == "__main__":
    # Führe Tests aus
    test_parse_dialog_colon()
    test_parse_action_brackets()
    test_parse_narrator()
    test_parse_file()
    
    print("Alle Tests erfolgreich!") 
"""
StoryWeaver - Lokale Analyse von dialogbasierten Geschichten

Ein Python-Tool zur automatischen Extraktion von Charakteren, 
Gegenständen und Orten aus Chat-Verläufen.
"""

__version__ = "1.0.0"
__author__ = "StoryWeaver Team"

from .models import Character, Item, Location
from .parsers import ChatParser
from .extractors import EntityExtractor
from .utils import EntityMerger, JSONExporter

__all__ = [
    'Character', 
    'Item', 
    'Location',
    'ChatParser',
    'EntityExtractor',
    'EntityMerger',
    'JSONExporter'
]

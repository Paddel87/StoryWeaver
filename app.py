#!/usr/bin/env python3
"""
StoryWeaver - Streamlit UI
Benutzeroberfläche für die Analyse und den Export von Story-Elementen
"""
import streamlit as st
from pathlib import Path
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
from PIL import Image

# Import der Backend-Komponenten
from src.extractors.entity_extractor import EntityExtractor
from src.utils.merger import EntityMerger
from src.utils.exporter import JSONExporter
from src.utils.sillytavern_exporter import SillyTavernExporter
from src.models import Character, Item, Location

# Konfiguration
st.set_page_config(
    page_title="StoryWeaver",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für besseres Styling
st.markdown("""
<style>
    .character-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }
    .property-tag {
        display: inline-block;
        background-color: #e0e0e0;
        padding: 3px 8px;
        margin: 2px;
        border-radius: 15px;
        font-size: 0.9em;
    }
    .export-checkbox {
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State initialisieren
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'characters' not in st.session_state:
    st.session_state.characters = {}
if 'items' not in st.session_state:
    st.session_state.items = {}
if 'locations' not in st.session_state:
    st.session_state.locations = {}
if 'dialog_data' not in st.session_state:
    st.session_state.dialog_data = {}
if 'selected_characters' not in st.session_state:
    st.session_state.selected_characters = set()
if 'character_images' not in st.session_state:
    st.session_state.character_images = {}


def analyze_stories(input_dir: Path, similarity_threshold: int = 80):
    """Analysiert die Story-Dateien und speichert Ergebnisse im Session State"""
    with st.spinner("Analysiere Geschichten..."):
        try:
            # Initialisiere Komponenten
            extractor = EntityExtractor()
            merger = EntityMerger(similarity_threshold)
            
            # Finde alle Text-Dateien
            chat_files = list(input_dir.glob("*.txt")) + list(input_dir.glob("*.md"))
            
            if not chat_files:
                st.error(f"Keine Chat-Dateien in {input_dir} gefunden!")
                return False
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Verarbeite jede Datei
            for i, file_path in enumerate(chat_files):
                status_text.text(f"Analysiere: {file_path.name}")
                extractor.extract_from_file(file_path)
                progress_bar.progress((i + 1) / len(chat_files))
            
            # Führe ähnliche Entitäten zusammen
            status_text.text("Führe ähnliche Elemente zusammen...")
            merged_characters = merger.merge_characters(extractor.characters)
            merged_items = merger.merge_items(extractor.items)
            merged_locations = merger.merge_locations(extractor.locations)
            
            # Speichere im Session State
            st.session_state.characters = merged_characters
            st.session_state.items = merged_items
            st.session_state.locations = merged_locations
            st.session_state.dialog_data = extractor.get_dialog_data()
            st.session_state.analyzed = True
            
            progress_bar.empty()
            status_text.empty()
            
            return True
            
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {str(e)}")
            return False


def display_character_card(char_name: str, character: Character, col):
    """Zeigt eine Charakter-Karte an"""
    with col:
        # Container für die Karte
        with st.container():
            # Checkbox für Export-Auswahl
            export_selected = st.checkbox(
                "Für Export auswählen",
                key=f"export_{char_name}",
                value=char_name in st.session_state.selected_characters
            )
            
            if export_selected:
                st.session_state.selected_characters.add(char_name)
            else:
                st.session_state.selected_characters.discard(char_name)
            
            # Charakter-Bild
            image_path = st.session_state.character_images.get(
                char_name, 
                Path("assets/images/default_portrait.png")
            )
            
            if image_path and Path(image_path).exists():
                try:
                    img = Image.open(image_path)
                    st.image(img, width=200, caption=char_name)
                except:
                    st.image("assets/images/default_portrait.png", width=200, caption=char_name)
            else:
                # Fallback wenn kein Bild existiert
                st.info("📷 Kein Bild verfügbar")
            
            # Charakter-Details
            st.markdown(f"### {char_name}")
            
            # Aliase
            if character.aliases:
                st.markdown(f"**Auch bekannt als:** {', '.join(character.aliases)}")
            
            # Beschreibung
            if character.description:
                with st.expander("Beschreibung", expanded=True):
                    st.write(character.description)
            
            # Verhaltensweisen
            if character.behaviors:
                st.markdown("**Verhalten:**")
                behavior_html = " ".join([
                    f'<span class="property-tag">{b}</span>' 
                    for b in character.behaviors
                ])
                st.markdown(behavior_html, unsafe_allow_html=True)
            
            # Gegenstände
            if character.items:
                st.markdown("**Gegenstände:**")
                items_html = " ".join([
                    f'<span class="property-tag">🗡️ {item}</span>' 
                    for item in list(character.items)[:5]
                ])
                st.markdown(items_html, unsafe_allow_html=True)
            
            # Beziehungen
            if character.relationships:
                with st.expander("Beziehungen"):
                    for other, relation in character.relationships.items():
                        st.write(f"- **{other}**: {relation}")
            
            # Häufigkeit
            st.markdown(f"**Erwähnungen:** {character.frequency}")
            
            # Bearbeiten-Button
            if st.button(f"✏️ Bearbeiten", key=f"edit_{char_name}"):
                st.session_state[f"editing_{char_name}"] = True
            
            # Bearbeitungsmodus
            if st.session_state.get(f"editing_{char_name}", False):
                with st.form(key=f"edit_form_{char_name}"):
                    st.markdown("#### Charakter bearbeiten")
                    
                    new_description = st.text_area(
                        "Beschreibung",
                        value=character.description,
                        key=f"desc_{char_name}"
                    )
                    
                    new_behaviors = st.text_input(
                        "Verhaltensweisen (kommagetrennt)",
                        value=", ".join(character.behaviors),
                        key=f"behav_{char_name}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Speichern"):
                            character.description = new_description
                            character.behaviors = [b.strip() for b in new_behaviors.split(",") if b.strip()]
                            st.session_state[f"editing_{char_name}"] = False
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Abbrechen"):
                            st.session_state[f"editing_{char_name}"] = False
                            st.rerun()


def display_characters_tab():
    """Zeigt den Charaktere-Tab an"""
    st.header("📚 Charaktere")
    
    if not st.session_state.characters:
        st.info("Keine Charaktere gefunden. Bitte analysiere zuerst Story-Dateien.")
        return
    
    # Filter-Optionen
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Suche nach Name", "")
    
    with col2:
        # Filter nach Gegenständen
        all_items = set()
        for char in st.session_state.characters.values():
            all_items.update(char.items)
        
        filter_items = st.multiselect(
            "Nach Gegenständen filtern",
            options=sorted(list(all_items))
        )
    
    with col3:
        # Sortierung
        sort_by = st.selectbox(
            "Sortieren nach",
            ["Name", "Häufigkeit"]
        )
    
    # Gefilterte Charaktere
    filtered_chars = {}
    for name, char in st.session_state.characters.items():
        # Name-Filter
        if search_term and search_term.lower() not in name.lower():
            continue
        
        # Item-Filter
        if filter_items and not any(item in char.items for item in filter_items):
            continue
        
        filtered_chars[name] = char
    
    # Sortierung anwenden
    if sort_by == "Name":
        sorted_chars = sorted(filtered_chars.items())
    else:  # Häufigkeit
        sorted_chars = sorted(filtered_chars.items(), key=lambda x: x[1].frequency, reverse=True)
    
    # Anzeige-Optionen
    st.markdown("---")
    
    # Massenaktionen
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("✅ Alle auswählen"):
            st.session_state.selected_characters = set(filtered_chars.keys())
            st.rerun()
    
    with col2:
        if st.button("❌ Auswahl aufheben"):
            st.session_state.selected_characters = set()
            st.rerun()
    
    # Status-Anzeige
    st.info(f"**{len(st.session_state.selected_characters)}** von {len(filtered_chars)} Charakteren ausgewählt")
    
    # Charaktere in Spalten anzeigen
    if sorted_chars:
        # 3 Spalten für Charakterkarten
        cols = st.columns(3)
        
        for idx, (char_name, character) in enumerate(sorted_chars):
            col_idx = idx % 3
            display_character_card(char_name, character, cols[col_idx])
    else:
        st.warning("Keine Charaktere entsprechen den Filterkriterien.")


def display_locations_tab():
    """Zeigt den Orte-Tab an"""
    st.header("🗺️ Orte")
    
    if not st.session_state.locations:
        st.info("Keine Orte gefunden.")
        return
    
    # Orte als Tabelle anzeigen
    location_data = []
    for name, location in st.session_state.locations.items():
        location_data.append({
            "Name": name,
            "Typ": location.location_type or "Unbekannt",
            "Atmosphäre": ", ".join(location.atmosphere[:3]) if location.atmosphere else "-",
            "Bewohner": len(location.inhabitants),
            "Erwähnungen": location.frequency
        })
    
    st.dataframe(location_data, use_container_width=True)
    
    # Details-Ansicht
    st.markdown("---")
    selected_location = st.selectbox(
        "Ort für Details auswählen:",
        options=[""] + list(st.session_state.locations.keys())
    )
    
    if selected_location:
        location = st.session_state.locations[selected_location]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {selected_location}")
            if location.description:
                st.write(f"**Beschreibung:** {location.description}")
            if location.significance:
                st.write(f"**Bedeutung:** {location.significance}")
            if location.atmosphere:
                st.write(f"**Atmosphäre:** {', '.join(location.atmosphere)}")
        
        with col2:
            if location.inhabitants:
                st.write("**Bewohner:**")
                for inhabitant in location.inhabitants:
                    st.write(f"- {inhabitant}")
            
            if location.connected_locations:
                st.write("**Verbundene Orte:**")
                for connected in location.connected_locations:
                    st.write(f"- {connected}")


def display_items_tab():
    """Zeigt den Gegenstände-Tab an"""
    st.header("⚔️ Gegenstände")
    
    if not st.session_state.items:
        st.info("Keine Gegenstände gefunden.")
        return
    
    # Gruppiere nach Typ
    items_by_type = {}
    for name, item in st.session_state.items.items():
        item_type = item.item_type or "Sonstige"
        if item_type not in items_by_type:
            items_by_type[item_type] = []
        items_by_type[item_type].append((name, item))
    
    # Zeige nach Typ gruppiert
    for item_type, items in sorted(items_by_type.items()):
        with st.expander(f"{item_type} ({len(items)} Gegenstände)", expanded=True):
            for name, item in sorted(items):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{name.title()}**")
                    if item.description:
                        st.caption(item.description)
                
                with col2:
                    if item.owners:
                        st.write(f"Besitzer: {', '.join(list(item.owners)[:3])}")
                
                with col3:
                    st.write(f"Erwähnungen: {item.frequency}")


def display_export_tab():
    """Zeigt den Export-Tab an"""
    st.header("📤 Vorschau & Export")
    
    if not st.session_state.selected_characters:
        st.warning("Keine Charaktere für den Export ausgewählt.")
        st.info("Wechsle zum Charaktere-Tab und wähle mindestens einen Charakter aus.")
        return
    
    st.success(f"**{len(st.session_state.selected_characters)}** Charaktere für Export ausgewählt:")
    
    # Zeige ausgewählte Charaktere
    selected_names = sorted(list(st.session_state.selected_characters))
    cols = st.columns(min(len(selected_names), 4))
    
    for idx, char_name in enumerate(selected_names):
        col_idx = idx % len(cols)
        with cols[col_idx]:
            character = st.session_state.characters.get(char_name)
            if character:
                st.write(f"✅ **{char_name}**")
                if character.behaviors:
                    st.caption(f"{', '.join(character.behaviors[:3])}")
    
    st.markdown("---")
    
    # Export-Optionen
    st.markdown("### Export-Einstellungen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.radio(
            "Export-Format",
            ["Beide (JSON + PNG)", "Nur JSON", "Nur PNG"],
            help="PNG-Dateien enthalten die JSON-Daten eingebettet"
        )
    
    with col2:
        output_dir = st.text_input(
            "Ausgabeverzeichnis",
            value="export",
            help="Relativ zum Arbeitsverzeichnis"
        )
    
    # Vorschau
    if st.checkbox("Vorschau der JSON-Daten anzeigen"):
        preview_char = st.selectbox(
            "Charakter für Vorschau:",
            options=selected_names
        )
        
        if preview_char:
            character = st.session_state.characters[preview_char]
            dialog_data = st.session_state.dialog_data.get(preview_char, [])
            
            # Erstelle temporären Exporter für Vorschau
            temp_exporter = SillyTavernExporter(Path("temp"))
            tavern_data = temp_exporter._create_tavern_json(character, dialog_data)
            
            st.json(tavern_data)
    
    # Export-Button
    st.markdown("---")
    
    if st.button("🚀 Export starten", type="primary", use_container_width=True):
        export_characters(
            selected_names,
            Path(output_dir),
            export_json=(export_format in ["Beide (JSON + PNG)", "Nur JSON"]),
            export_png=(export_format in ["Beide (JSON + PNG)", "Nur PNG"])
        )


def export_characters(selected_names: List[str], output_dir: Path, 
                     export_json: bool = True, export_png: bool = True):
    """Exportiert die ausgewählten Charaktere"""
    with st.spinner("Exportiere Charaktere..."):
        try:
            # Erstelle Exporter
            exporter = SillyTavernExporter(output_dir)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            exported_files = {"json": [], "png": []}
            
            for idx, char_name in enumerate(selected_names):
                status_text.text(f"Exportiere {char_name}...")
                
                character = st.session_state.characters.get(char_name)
                if not character:
                    continue
                
                dialog_data = st.session_state.dialog_data.get(char_name, [])
                
                # Exportiere
                result = exporter.export_character(
                    character, 
                    dialog_data,
                    export_png=export_png
                )
                
                if export_json and "json" in result:
                    exported_files["json"].append(result["json"])
                if export_png and "png" in result:
                    exported_files["png"].append(result["png"])
                
                progress_bar.progress((idx + 1) / len(selected_names))
            
            progress_bar.empty()
            status_text.empty()
            
            # Erfolgsmeldung
            st.success("✅ Export erfolgreich abgeschlossen!")
            
            # Zeige exportierte Dateien
            col1, col2 = st.columns(2)
            
            with col1:
                if exported_files["json"]:
                    st.markdown(f"**📄 {len(exported_files['json'])} JSON-Dateien erstellt:**")
                    for file_path in exported_files["json"]:
                        st.caption(f"✓ {file_path.name}")
            
            with col2:
                if exported_files["png"]:
                    st.markdown(f"**🖼️ {len(exported_files['png'])} PNG-Dateien erstellt:**")
                    for file_path in exported_files["png"]:
                        st.caption(f"✓ {file_path.name}")
            
            # Hinweis
            st.info(f"Die Dateien wurden in '{output_dir.absolute()}' gespeichert.")
            
        except Exception as e:
            st.error(f"Fehler beim Export: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def main():
    """Hauptfunktion der Streamlit-App"""
    # Titel und Beschreibung
    st.title("📚 StoryWeaver")
    st.markdown("**Analysiere und exportiere Charaktere aus deinen Geschichten**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Einstellungen")
        
        # Input-Verzeichnis
        input_dir = st.text_input(
            "📁 Story-Verzeichnis",
            value="examples",
            help="Verzeichnis mit .txt oder .md Dateien"
        )
        
        # Ähnlichkeitsschwellwert
        similarity_threshold = st.slider(
            "Ähnlichkeitsschwellwert",
            min_value=50,
            max_value=100,
            value=80,
            help="Niedrigere Werte führen zu mehr Zusammenführungen"
        )
        
        # Analyse-Button
        if st.button("🔍 Geschichten analysieren", type="primary", use_container_width=True):
            if analyze_stories(Path(input_dir), similarity_threshold):
                st.success("✅ Analyse erfolgreich!")
                st.balloons()
            else:
                st.error("❌ Analyse fehlgeschlagen")
        
        # Status
        if st.session_state.analyzed:
            st.success("✅ Daten geladen")
            st.metric("Charaktere", len(st.session_state.characters))
            st.metric("Orte", len(st.session_state.locations))
            st.metric("Gegenstände", len(st.session_state.items))
        else:
            st.info("Bitte analysiere zuerst Story-Dateien")
        
        st.markdown("---")
        
        # Bild-Upload (Platzhalter für spätere Funktion)
        st.markdown("### 🖼️ Standard-Portrait")
        default_img_path = Path("assets/images/default_portrait.png")
        if default_img_path.exists():
            st.image(str(default_img_path), width=150)
        
        # Info
        st.markdown("---")
        st.caption("StoryWeaver v1.0")
        st.caption("Erstellt mit ❤️ und Python")
    
    # Hauptbereich mit Tabs
    if st.session_state.analyzed:
        tab1, tab2, tab3, tab4 = st.tabs(["📚 Charaktere", "🗺️ Orte", "⚔️ Gegenstände", "📤 Export"])
        
        with tab1:
            display_characters_tab()
        
        with tab2:
            display_locations_tab()
        
        with tab3:
            display_items_tab()
        
        with tab4:
            display_export_tab()
    else:
        # Willkommensbildschirm
        st.info("👈 Bitte wähle ein Verzeichnis in der Seitenleiste und klicke auf 'Geschichten analysieren'")
        
        # Beispiel-Anleitung
        with st.expander("📖 Kurzanleitung"):
            st.markdown("""
            1. **Verzeichnis wählen:** Gib den Pfad zu deinen Story-Dateien an
            2. **Analysieren:** Klicke auf 'Geschichten analysieren'
            3. **Charaktere durchsuchen:** Wechsle zum Charaktere-Tab
            4. **Auswählen:** Wähle Charaktere für den Export aus
            5. **Exportieren:** Gehe zum Export-Tab und erstelle deine Charakterkarten
            
            **Unterstützte Formate:**
            - Dialog mit Doppelpunkt: `Lyra: Hallo!`
            - Aktionen in Klammern: `[Lyra öffnet die Tür]`
            - Erzählertext
            """)


if __name__ == "__main__":
    main() 
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
import zipfile
import io
import tempfile

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
if 'story_items' not in st.session_state:
    st.session_state.story_items = {}
if 'locations' not in st.session_state:
    st.session_state.locations = {}
if 'dialog_data' not in st.session_state:
    st.session_state.dialog_data = {}
if 'selected_characters' not in st.session_state:
    st.session_state.selected_characters = set()
if 'character_images' not in st.session_state:
    st.session_state.character_images = {}

# Filter-States initialisieren
if 'filter_search' not in st.session_state:
    st.session_state.filter_search = ""
if 'filter_items' not in st.session_state:
    st.session_state.filter_items = []
if 'filter_behaviors' not in st.session_state:
    st.session_state.filter_behaviors = []
if 'filter_has_relationships' not in st.session_state:
    st.session_state.filter_has_relationships = False
if 'filter_has_description' not in st.session_state:
    st.session_state.filter_has_description = False
if 'filter_sort_by' not in st.session_state:
    st.session_state.filter_sort_by = "Name"


def analyze_stories(input_dir: Path, similarity_threshold: int = 80):
    """Analysiert die Story-Dateien und speichert Ergebnisse im Session State"""
    with st.spinner("Analysiere Geschichten..."):
        try:
            # Initialisiere Komponenten
            extractor = EntityExtractor()
            merger = EntityMerger(similarity_threshold)
            
            # Finde alle unterstützten Dateien (inkl. JSON)
            chat_files = list(input_dir.glob("*.txt")) + list(input_dir.glob("*.md")) + list(input_dir.glob("*.json"))
            
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
            st.session_state.story_items = merged_items
            st.session_state.locations = merged_locations
            st.session_state.dialog_data = extractor.get_dialog_data()
            st.session_state.analyzed = True
            
            progress_bar.empty()
            status_text.empty()
            
            return True
            
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {str(e)}")
            return False


def process_uploaded_files(uploaded_files, similarity_threshold: int = 80):
    """Verarbeitet hochgeladene Story-Dateien"""
    if not uploaded_files:
        return False
    
    with st.spinner(f"Verarbeite {len(uploaded_files)} hochgeladene Dateien..."):
        try:
            # Initialisiere Komponenten
            extractor = EntityExtractor()
            merger = EntityMerger(similarity_threshold)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Verarbeite jede hochgeladene Datei
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Analysiere: {uploaded_file.name}")
                
                # Zeige Dateityp an
                if uploaded_file.name.lower().endswith('.json'):
                    status_text.text(f"Analysiere JSON: {uploaded_file.name}")
                else:
                    status_text.text(f"Analysiere Text: {uploaded_file.name}")
                
                # Erstelle temporäre Datei
                with tempfile.NamedTemporaryFile(mode='w', suffix=uploaded_file.name, delete=False, encoding='utf-8') as tmp_file:
                    # Lese Inhalt und schreibe in temporäre Datei
                    content = uploaded_file.read().decode('utf-8')
                    tmp_file.write(content)
                    tmp_path = tmp_file.name
                
                # Verarbeite die temporäre Datei
                try:
                    # Extrahiere Entitäten
                    extractor.extract_from_file(Path(tmp_path))
                finally:
                    # Lösche temporäre Datei
                    Path(tmp_path).unlink(missing_ok=True)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Führe ähnliche Entitäten zusammen
            status_text.text("Führe ähnliche Elemente zusammen...")
            merged_characters = merger.merge_characters(extractor.characters)
            merged_items = merger.merge_items(extractor.items)
            merged_locations = merger.merge_locations(extractor.locations)
            
            # Speichere im Session State
            st.session_state.characters = merged_characters
            st.session_state.story_items = merged_items
            st.session_state.locations = merged_locations
            st.session_state.dialog_data = extractor.get_dialog_data()
            st.session_state.analyzed = True
            
            progress_bar.empty()
            status_text.empty()
            
            return True
            
        except Exception as e:
            st.error(f"Fehler bei der Verarbeitung: {str(e)}")
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


def display_batch_edit_modal():
    """Zeigt ein Modal für Batch-Bearbeitung ausgewählter Charaktere"""
    if not st.session_state.selected_characters:
        return
    
    with st.expander("🔧 Batch-Bearbeitung", expanded=False):
        st.markdown(f"### Bearbeite {len(st.session_state.selected_characters)} ausgewählte Charaktere")
        
        # Batch-Bearbeitungsoptionen
        col1, col2 = st.columns(2)
        
        with col1:
            # Verhaltensweisen hinzufügen
            add_behaviors = st.text_input(
                "➕ Verhaltensweisen hinzufügen (kommagetrennt)",
                placeholder="z.B. mutig, loyal, weise",
                help="Diese werden zu allen ausgewählten Charakteren hinzugefügt"
            )
            
            # Verhaltensweisen entfernen
            all_behaviors = set()
            for char_name in st.session_state.selected_characters:
                if char_name in st.session_state.characters:
                    all_behaviors.update(st.session_state.characters[char_name].behaviors)
            
            if all_behaviors:
                remove_behaviors = st.multiselect(
                    "➖ Verhaltensweisen entfernen",
                    options=sorted(list(all_behaviors)),
                    help="Diese werden von allen ausgewählten Charakteren entfernt"
                )
            else:
                remove_behaviors = []
        
        with col2:
            # Beschreibung anhängen
            append_description = st.text_area(
                "📝 Text an Beschreibung anhängen",
                placeholder="Dieser Text wird an alle Beschreibungen angehängt...",
                height=100
            )
            
            # Präfix/Suffix für Namen
            name_prefix = st.text_input(
                "🏷️ Präfix für Namen",
                placeholder="z.B. 'Lord' oder 'Lady'"
            )
        
        # Beziehungen batch-editieren
        st.markdown("#### 🤝 Beziehungen bearbeiten")
        
        col3, col4, col5 = st.columns([2, 2, 1])
        with col3:
            # Alle Charakternamen als Optionen
            all_char_names = list(st.session_state.characters.keys())
            target_character = st.selectbox(
                "Ziel-Charakter",
                options=[""] + all_char_names,
                help="Zu wem soll die Beziehung erstellt werden?"
            )
        
        with col4:
            relationship_type = st.text_input(
                "Beziehungstyp",
                placeholder="z.B. Freund, Feind, Mentor"
            )
        
        with col5:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacer
            bidirectional = st.checkbox("↔️ Beidseitig", help="Beziehung in beide Richtungen")
        
        # Vorschau der Änderungen
        if any([add_behaviors, remove_behaviors, append_description, name_prefix, target_character and relationship_type]):
            with st.expander("👁️ Vorschau der Änderungen", expanded=True):
                st.info(f"Änderungen werden auf {len(st.session_state.selected_characters)} Charaktere angewendet:")
                
                if add_behaviors:
                    st.write(f"✅ **Füge hinzu:** {add_behaviors}")
                if remove_behaviors:
                    st.write(f"❌ **Entferne:** {', '.join(remove_behaviors)}")
                if append_description:
                    st.write(f"📝 **Hänge an Beschreibung:** '{append_description[:50]}...'")
                if name_prefix:
                    st.write(f"🏷️ **Name-Präfix:** '{name_prefix}'")
                if target_character and relationship_type:
                    rel_text = f"🤝 **Beziehung:** → {target_character}: {relationship_type}"
                    if bidirectional:
                        rel_text += " (beidseitig)"
                    st.write(rel_text)
        
        # Anwenden-Button
        col_apply, col_cancel = st.columns([1, 1])
        
        with col_apply:
            if st.button("✅ Änderungen anwenden", type="primary", use_container_width=True):
                apply_batch_changes(
                    add_behaviors=add_behaviors,
                    remove_behaviors=remove_behaviors,
                    append_description=append_description,
                    name_prefix=name_prefix,
                    target_character=target_character,
                    relationship_type=relationship_type,
                    bidirectional=bidirectional
                )
                st.success("✅ Batch-Änderungen angewendet!")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ Abbrechen", use_container_width=True):
                st.rerun()


def apply_batch_changes(add_behaviors=None, remove_behaviors=None, 
                       append_description=None, name_prefix=None,
                       target_character=None, relationship_type=None, 
                       bidirectional=False):
    """Wendet Batch-Änderungen auf ausgewählte Charaktere an"""
    
    for char_name in st.session_state.selected_characters:
        if char_name not in st.session_state.characters:
            continue
            
        character = st.session_state.characters[char_name]
        
        # Verhaltensweisen hinzufügen
        if add_behaviors:
            new_behaviors = [b.strip() for b in add_behaviors.split(",") if b.strip()]
            character.behaviors.extend(new_behaviors)
            character.behaviors = list(set(character.behaviors))  # Duplikate entfernen
        
        # Verhaltensweisen entfernen
        if remove_behaviors:
            character.behaviors = [b for b in character.behaviors if b not in remove_behaviors]
        
        # Beschreibung anhängen
        if append_description:
            if character.description:
                character.description += f" {append_description}"
            else:
                character.description = append_description
        
        # Name-Präfix (nur wenn noch nicht vorhanden)
        if name_prefix and not character.name.startswith(name_prefix):
            # Aktualisiere den Schlüssel im Dictionary
            new_name = f"{name_prefix} {character.name}"
            character.name = new_name
            st.session_state.characters[new_name] = character
            del st.session_state.characters[char_name]
            # Update selected characters
            st.session_state.selected_characters.discard(char_name)
            st.session_state.selected_characters.add(new_name)
        
        # Beziehung hinzufügen
        if target_character and relationship_type and target_character != char_name:
            if not hasattr(character, 'relationships'):
                character.relationships = {}
            character.relationships[target_character] = relationship_type
            
            # Beidseitige Beziehung
            if bidirectional and target_character in st.session_state.characters:
                target_char = st.session_state.characters[target_character]
                if not hasattr(target_char, 'relationships'):
                    target_char.relationships = {}
                target_char.relationships[character.name] = relationship_type


def display_characters_tab():
    """Zeigt den Charaktere-Tab an"""
    st.header("📚 Charaktere")
    
    if not st.session_state.characters:
        st.info("Keine Charaktere gefunden. Bitte analysiere zuerst Story-Dateien.")
        return
    
    # Filter-Optionen
    with st.expander("🔍 Erweiterte Filter", expanded=False):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            search_term = st.text_input("🔍 Suche nach Name", "")
            
            # Filter nach Häufigkeit
            all_frequencies = [char.frequency for char in st.session_state.characters.values()]
            if all_frequencies:
                min_freq, max_freq = st.slider(
                    "📊 Erwähnungen (Min-Max)",
                    min_value=min(all_frequencies),
                    max_value=max(all_frequencies),
                    value=(min(all_frequencies), max(all_frequencies))
                )
            else:
                min_freq, max_freq = 0, 100
        
        with col2:
            # Filter nach Gegenständen
            all_items = set()
            for char in st.session_state.characters.values():
                all_items.update(char.items)
            
            filter_items = st.multiselect(
                "🗡️ Nach Gegenständen filtern",
                options=sorted(list(all_items))
            )
            
            # Filter nach Verhaltensweisen
            all_behaviors = set()
            for char in st.session_state.characters.values():
                all_behaviors.update(char.behaviors)
            
            if all_behaviors:
                filter_behaviors = st.multiselect(
                    "🎭 Nach Verhalten filtern",
                    options=sorted(list(all_behaviors))
                )
            else:
                filter_behaviors = []
        
        with col3:
            # Filter nach Beziehungen
            has_relationships = st.checkbox("🤝 Nur mit Beziehungen")
            
            # Filter nach Beschreibung
            has_description = st.checkbox("📝 Nur mit Beschreibung")
        
        with col4:
            # Sortierung
            sort_by = st.selectbox(
                "📑 Sortieren nach",
                ["Name", "Häufigkeit", "Anzahl Items", "Anzahl Beziehungen"]
            )
    
    # Gefilterte Charaktere
    filtered_chars = {}
    for name, char in st.session_state.characters.items():
        # Name-Filter
        if search_term and search_term.lower() not in name.lower():
            continue
        
        # Häufigkeits-Filter
        if not (min_freq <= char.frequency <= max_freq):
            continue
        
        # Item-Filter
        if filter_items and not any(item in char.items for item in filter_items):
            continue
        
        # Verhaltens-Filter
        if filter_behaviors and not any(behavior in char.behaviors for behavior in filter_behaviors):
            continue
        
        # Beziehungs-Filter
        if has_relationships and (not hasattr(char, 'relationships') or not char.relationships):
            continue
        
        # Beschreibungs-Filter
        if has_description and not char.description:
            continue
        
        filtered_chars[name] = char
    
    # Sortierung anwenden
    if sort_by == "Name":
        sorted_chars = sorted(filtered_chars.items())
    elif sort_by == "Häufigkeit":
        sorted_chars = sorted(filtered_chars.items(), key=lambda x: x[1].frequency, reverse=True)
    elif sort_by == "Anzahl Items":
        sorted_chars = sorted(filtered_chars.items(), key=lambda x: len(x[1].items), reverse=True)
    else:  # Anzahl Beziehungen
        sorted_chars = sorted(filtered_chars.items(), 
                            key=lambda x: len(getattr(x[1], 'relationships', {})), reverse=True)
    
    # Anzeige-Optionen
    st.markdown("---")
    
    # Massenaktionen
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        if st.button("✅ Alle auswählen"):
            st.session_state.selected_characters = set(filtered_chars.keys())
            st.rerun()
    
    with col2:
        if st.button("❌ Auswahl aufheben"):
            st.session_state.selected_characters = set()
            st.rerun()
    
    with col3:
        if st.button("🔄 Auswahl umkehren"):
            current_selected = st.session_state.selected_characters
            all_filtered = set(filtered_chars.keys())
            st.session_state.selected_characters = all_filtered - current_selected
            st.rerun()
    
    with col4:
        # Smart Selection
        with st.popover("🎯 Smart Selection"):
            st.markdown("#### Charaktere intelligent auswählen")
            
            smart_option = st.radio(
                "Auswahl-Kriterium:",
                ["Top N nach Häufigkeit", "Mit bestimmtem Item", "Ohne Beziehungen"]
            )
            
            if smart_option == "Top N nach Häufigkeit":
                top_n = st.number_input("Anzahl:", min_value=1, max_value=len(filtered_chars), value=5)
                if st.button("Auswählen", key="smart_top_n"):
                    sorted_by_freq = sorted(filtered_chars.items(), 
                                          key=lambda x: x[1].frequency, reverse=True)
                    st.session_state.selected_characters = set(
                        name for name, _ in sorted_by_freq[:top_n]
                    )
                    st.rerun()
            
            elif smart_option == "Mit bestimmtem Item":
                all_items = set()
                for char in filtered_chars.values():
                    all_items.update(char.items)
                
                if all_items:
                    selected_item = st.selectbox("Item:", sorted(list(all_items)))
                    if st.button("Auswählen", key="smart_item"):
                        st.session_state.selected_characters = set(
                            name for name, char in filtered_chars.items() 
                            if selected_item in char.items
                        )
                        st.rerun()
                else:
                    st.info("Keine Items gefunden")
            
            else:  # Ohne Beziehungen
                if st.button("Auswählen", key="smart_no_rel"):
                    st.session_state.selected_characters = set(
                        name for name, char in filtered_chars.items() 
                        if not hasattr(char, 'relationships') or not char.relationships
                    )
                    st.rerun()
    
    # Status-Anzeige
    st.info(f"**{len(st.session_state.selected_characters)}** von {len(filtered_chars)} Charakteren ausgewählt")
    
    # Batch-Bearbeitung (nur wenn Charaktere ausgewählt sind)
    if st.session_state.selected_characters:
        display_batch_edit_modal()
    
    # Charaktere in Spalten anzeigen
    if sorted_chars:
        # 3 Spalten für Charakterkarten
        cols = st.columns(3)
        
        for idx, (char_name, character) in enumerate(sorted_chars):
            col_idx = idx % 3
            display_character_card(char_name, character, cols[col_idx])
    else:
        st.warning("Keine Charaktere entsprechen den Filterkriterien.")
    
    # Download-Sektion
    if st.session_state.characters:
        st.markdown("---")
        st.subheader("📥 Download-Optionen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Alle Charaktere als JSON
            all_chars_data = {name: char.to_dict() for name, char in st.session_state.characters.items()}
            create_json_download(all_chars_data, "alle_charaktere.json")
        
        with col2:
            # Gefilterte Charaktere als JSON
            if filtered_chars:
                filtered_data = {name: char.to_dict() for name, char in filtered_chars.items()}
                create_json_download(filtered_data, "gefilterte_charaktere.json")
        
        with col3:
            # Kompletter Export als ZIP
            if st.button("📦 Alles als ZIP herunterladen", use_container_width=True):
                zip_data = create_zip_download(
                    st.session_state.characters,
                    st.session_state.story_items,
                    st.session_state.locations
                )
                st.download_button(
                    label="💾 StoryWeaver_Export.zip",
                    data=zip_data,
                    file_name=f"StoryWeaver_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        
        # Batch-Export für ausgewählte Charaktere
        if st.session_state.selected_characters:
            st.markdown("#### 🎯 Ausgewählte Charaktere exportieren")
            
            col_batch1, col_batch2 = st.columns(2)
            
            with col_batch1:
                # Nur ausgewählte als JSON
                selected_chars_data = {
                    name: char.to_dict() 
                    for name, char in st.session_state.characters.items() 
                    if name in st.session_state.selected_characters
                }
                
                if selected_chars_data:
                    create_json_download(
                        selected_chars_data, 
                        f"ausgewaehlte_charaktere_{len(selected_chars_data)}.json"
                    )
            
            with col_batch2:
                # Nur ausgewählte als ZIP
                if st.button("📦 Ausgewählte als ZIP", use_container_width=True):
                    batch_zip = io.BytesIO()
                    
                    with zipfile.ZipFile(batch_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for char_name in st.session_state.selected_characters:
                            if char_name in st.session_state.characters:
                                char = st.session_state.characters[char_name]
                                json_data = json.dumps(char.to_dict(), indent=2, ensure_ascii=False)
                                safe_name = char_name.replace(' ', '_').lower()
                                zf.writestr(f"selected_characters/{safe_name}.json", json_data)
                        
                        # Übersichtsdatei
                        summary = {
                            "export_timestamp": datetime.now().isoformat(),
                            "selected_count": len(st.session_state.selected_characters),
                            "character_names": sorted(list(st.session_state.selected_characters))
                        }
                        zf.writestr("selected_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))
                    
                    batch_zip.seek(0)
                    
                    st.download_button(
                        label=f"💾 Ausgewählte_{len(st.session_state.selected_characters)}_Charaktere.zip",
                        data=batch_zip.getvalue(),
                        file_name=f"Selected_Characters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )


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
    
    # Download-Option
    if st.session_state.locations:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            locations_data = {name: loc.to_dict() for name, loc in st.session_state.locations.items()}
            create_json_download(locations_data, "alle_orte.json")


def display_items_tab():
    """Zeigt den Gegenstände-Tab an"""
    st.header("⚔️ Gegenstände")
    
    if not st.session_state.story_items:
        st.info("Keine Gegenstände gefunden.")
        return
    
    # Gruppiere nach Typ
    items_by_type = {}
    for name, item in st.session_state.story_items.items():
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
    
    # Download-Option
    if st.session_state.story_items:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            items_data = {name: item.to_dict() for name, item in st.session_state.story_items.items()}
            create_json_download(items_data, "alle_gegenstaende.json")


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
    if st.checkbox("Vorschau der Export-Daten anzeigen"):
        preview_char = st.selectbox(
            "Charakter für Vorschau:",
            options=selected_names
        )
        
        if preview_char:
            character = st.session_state.characters[preview_char]
            dialog_data = st.session_state.dialog_data.get(preview_char, [])
            
            # Tabs für verschiedene Vorschau-Modi
            preview_tab1, preview_tab2, preview_tab3 = st.tabs(["📄 JSON", "📖 Lesbar", "📊 Tabelle"])
            
            with preview_tab1:
                # JSON-Vorschau
                temp_exporter = SillyTavernExporter(Path("temp"))
                tavern_data = temp_exporter._create_tavern_json(character, dialog_data)
                st.json(tavern_data)
            
            with preview_tab2:
                # Lesbare Vorschau
                st.markdown(f"### {character.name}")
                st.markdown(f"**Beschreibung:** {character.description}")
                
                if character.aliases:
                    st.markdown(f"**Aliase:** {', '.join(character.aliases)}")
                
                if character.behaviors:
                    st.markdown(f"**Verhalten:** {', '.join(character.behaviors)}")
                
                if character.items:
                    st.markdown("**Gegenstände:**")
                    for item in list(character.items)[:10]:
                        st.markdown(f"- {item}")
                
                if character.relationships:
                    st.markdown("**Beziehungen:**")
                    for other, relation in list(character.relationships.items())[:10]:
                        st.markdown(f"- **{other}**: {relation}")
            
            with preview_tab3:
                # Tabellarische Vorschau
                char_info = {
                    "Eigenschaft": ["Name", "Erwähnungen", "Anzahl Aliase", 
                                   "Anzahl Gegenstände", "Anzahl Beziehungen"],
                    "Wert": [character.name, character.frequency, 
                            len(character.aliases), len(character.items), 
                            len(character.relationships)]
                }
                st.table(char_info)
    
    # Export-Button
    st.markdown("---")
    
    if st.button("🚀 Export starten", type="primary", use_container_width=True):
        export_characters(
            selected_names,
            Path(output_dir),
            export_json=(export_format in ["Beide (JSON + PNG)", "Nur JSON"]),
            export_png=(export_format in ["Beide (JSON + PNG)", "Nur PNG"])
        )


def create_json_download(data: Dict, filename: str):
    """Erstellt einen Download-Button für JSON-Daten"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        label=f"📥 {filename} herunterladen",
        data=json_str,
        file_name=filename,
        mime="application/json",
        use_container_width=True
    )


def create_zip_download(characters: Dict, items: Dict, locations: Dict):
    """Erstellt einen ZIP-Download mit allen Analyseergebnissen"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Charaktere
        for name, char in characters.items():
            json_data = json.dumps(char.to_dict() if hasattr(char, 'to_dict') else char, 
                                   indent=2, ensure_ascii=False)
            zf.writestr(f"characters/{name.replace(' ', '_').lower()}.json", json_data)
        
        # Gegenstände
        for name, item in items.items():
            json_data = json.dumps(item.to_dict() if hasattr(item, 'to_dict') else item, 
                                   indent=2, ensure_ascii=False)
            zf.writestr(f"items/{name.replace(' ', '_').lower()}.json", json_data)
        
        # Orte
        for name, location in locations.items():
            json_data = json.dumps(location.to_dict() if hasattr(location, 'to_dict') else location, 
                                   indent=2, ensure_ascii=False)
            zf.writestr(f"locations/{name.replace(' ', '_').lower()}.json", json_data)
        
        # Übersichtsdateien
        overview = {
            "export_timestamp": datetime.now().isoformat(),
            "statistics": {
                "characters": len(characters),
                "items": len(items),
                "locations": len(locations)
            },
            "characters": {name: char.to_dict() if hasattr(char, 'to_dict') else char 
                          for name, char in characters.items()},
            "items": {name: item.to_dict() if hasattr(item, 'to_dict') else item 
                     for name, item in items.items()},
            "locations": {name: loc.to_dict() if hasattr(loc, 'to_dict') else loc 
                         for name, loc in locations.items()}
        }
        zf.writestr("complete_overview.json", json.dumps(overview, indent=2, ensure_ascii=False))
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


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
            
            # Download-Optionen
            st.markdown("---")
            st.subheader("📥 Dateien herunterladen")
            
            # Erstelle ZIP mit exportierten Dateien
            export_zip = io.BytesIO()
            with zipfile.ZipFile(export_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                # JSON-Dateien
                for file_path in exported_files.get("json", []):
                    if file_path.exists():
                        zf.write(file_path, f"json/{file_path.name}")
                
                # PNG-Dateien
                for file_path in exported_files.get("png", []):
                    if file_path.exists():
                        zf.write(file_path, f"png/{file_path.name}")
            
            export_zip.seek(0)
            
            # Download-Button
            st.download_button(
                label="📦 Alle exportierten Dateien als ZIP herunterladen",
                data=export_zip.getvalue(),
                file_name=f"SillyTavern_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
            
            # Hinweis
            st.info(f"Die Dateien wurden auch lokal in '{output_dir.absolute()}' gespeichert.")
            
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
        
        # Tabs für verschiedene Input-Methoden
        input_tab1, input_tab2 = st.tabs(["📁 Verzeichnis", "📤 Upload"])
        
        with input_tab1:
            # Verbesserte Input-Sektion
            st.subheader("📁 Story-Verzeichnis")
            
            # Vordefinierte Optionen
            predefined_dirs = ["examples", "input", "Eigenes Verzeichnis..."]
            selected_option = st.selectbox(
                "Wähle ein Verzeichnis:",
                options=predefined_dirs,
                help="Wähle ein vordefiniertes Verzeichnis oder gib ein eigenes an"
            )
            
            # Zeige Eingabefeld nur wenn "Eigenes Verzeichnis" gewählt
            if selected_option == "Eigenes Verzeichnis...":
                input_dir = st.text_input(
                    "Verzeichnispfad eingeben:",
                    value="",
                    placeholder="z.B. meine_geschichten/",
                    help="Gib den relativen Pfad zu deinen Story-Dateien an"
                )
            else:
                input_dir = selected_option
            
            # Hilfetext
            with st.expander("ℹ️ Hilfe zu Verzeichnissen"):
                st.markdown("""
                **Wo müssen die Dateien liegen?**
                - Im `input/` Ordner des Projekts
                - Oder im `examples/` Ordner (Beispieldateien)
                - Unterstützte Formate: `.txt`, `.md` und `.json`
                
                **Beispielstruktur:**
                ```
                input/
                ├── geschichte1.txt
                ├── kapitel2.md
                ├── charakter.json
                └── epilog.txt
                ```
                
                **JSON-Format:**
                JSON-Dateien können strukturierte Charakterdaten enthalten:
                ```json
                {
                  "name": "Lyra",
                  "description": "Eine mutige Kämpferin mit roten Haaren",
                  "dialog": [
                    {"speaker": "Lyra", "content": "Wir müssen den Wald durchqueren."}
                  ],
                  "relationships": [
                    {"name": "Elias", "relationship": "Freund und Reisegefährte"}
                  ]
                }
                ```
                """)
        
        with input_tab2:
            # Upload-Sektion
            st.subheader("📤 Dateien hochladen")
            
            uploaded_files = st.file_uploader(
                "Story-Dateien auswählen",
                type=['txt', 'md', 'json'],
                accept_multiple_files=True,
                help="Ziehe Dateien hierher oder klicke zum Auswählen"
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} Datei(en) ausgewählt")
                
                # Zeige hochgeladene Dateien
                with st.expander("📄 Hochgeladene Dateien", expanded=True):
                    for file in uploaded_files:
                        file_size = len(file.read()) / 1024  # KB
                        file.seek(0)  # Reset file pointer
                        st.caption(f"• {file.name} ({file_size:.1f} KB)")
            
            st.info("""
            💡 **Tipp:** Du kannst mehrere Dateien gleichzeitig hochladen!
            
            Unterstützte Formate:
            - `.txt` - Textdateien
            - `.md` - Markdown-Dateien
            - `.json` - JSON-Strukturierte Daten mit Charakteren, Dialog und Beziehungen
            
            **JSON-Vorteile:**
            JSON-Dateien können strukturierte Daten enthalten und werden direkt interpretiert,
            ohne die Notwendigkeit einer NLP-basierten Extraktion. Dies reduziert das Problem
            grammatikalischer Variationen und doppelter Entitäten erheblich.
            """)
        
        # Gemeinsame Einstellungen
        st.markdown("---")
        
        # Ähnlichkeitsschwellwert
        similarity_threshold = st.slider(
            "Ähnlichkeitsschwellwert",
            min_value=50,
            max_value=100,
            value=80,
            help="Niedrigere Werte führen zu mehr Zusammenführungen"
        )
        
        # Analyse-Button (kontextabhängig)
        st.markdown("---")
        
        # Analyse-Buttons werden kontextabhängig angezeigt
        # Button für Verzeichnis-Analyse (nur wenn Verzeichnis ausgewählt)
        if input_dir:
            if st.button("🔍 Verzeichnis analysieren", type="primary", use_container_width=True, key="analyze_dir"):
                if analyze_stories(Path(input_dir), similarity_threshold):
                    st.success("✅ Analyse erfolgreich!")
                    st.balloons()
                else:
                    st.error("❌ Analyse fehlgeschlagen")
        
        # Button für Upload-Analyse (nur wenn Dateien hochgeladen)
        if uploaded_files:
            if st.button("🚀 Uploads analysieren", type="primary", use_container_width=True, key="analyze_upload"):
                if process_uploaded_files(uploaded_files, similarity_threshold):
                    st.success("✅ Analyse erfolgreich!")
                    st.balloons()
                else:
                    st.error("❌ Analyse fehlgeschlagen")
        
        # Info wenn nichts ausgewählt
        if not input_dir and not uploaded_files:
            st.info("👆 Wähle ein Verzeichnis oder lade Dateien hoch")
        
        # Status
        if st.session_state.analyzed:
            st.success("✅ Daten geladen")
            st.metric("Charaktere", len(st.session_state.characters))
            st.metric("Orte", len(st.session_state.locations))
            st.metric("Gegenstände", len(st.session_state.story_items))
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
            
            **Unterstützte Textformate:**
            - Dialog mit Doppelpunkt: `Lyra: Hallo!`
            - Dialog mit Bindestrich: `Lyra - Hallo!`
            - Aktionen in Klammern: `[Lyra öffnet die Tür]`
            - Aktionen mit Sternchen: `*Lyra öffnet die Tür*`
            - Erzählertext
            
            **JSON-Format:**
            Alternativ kannst du strukturierte JSON-Dateien verwenden:
            ```json
            {
              "name": "Lyra",
              "description": "Mutige Abenteurerin",
              "dialog": [
                {"speaker": "Lyra", "content": "Lasst uns aufbrechen!"}
              ]
            }
            ```
            """)


if __name__ == "__main__":
    main() 
"""
Erstellt ein Standard-Platzhalterbild für Charaktere ohne eigenes Portrait
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os


def create_default_portrait():
    """Erstellt ein 400x600 Pixel großes Platzhalterbild"""
    # Bildgröße und Farben
    width, height = 400, 600
    background_color = (128, 128, 128)  # Grau
    text_color = (255, 255, 255)  # Weiß
    
    # Erstelle neues Bild
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Text
    text = "No Image"
    
    # Versuche eine Schriftart zu laden, falls nicht verfügbar, nutze Standard
    try:
        # Versuche System-Schriftart
        font_size = 48
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        try:
            # Alternative Windows-Schriftart
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            # Fallback auf Standard-Schriftart
            font = ImageFont.load_default()
    
    # Berechne Text-Position (zentriert)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Zeichne Text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Zeichne einen Rahmen
    border_width = 10
    draw.rectangle(
        [(border_width, border_width), 
         (width - border_width, height - border_width)],
        outline=text_color,
        width=3
    )
    
    # Speichere das Bild
    output_path = Path("assets/images/default_portrait.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    
    print(f"Standardbild erstellt: {output_path}")
    return output_path


if __name__ == "__main__":
    create_default_portrait() 
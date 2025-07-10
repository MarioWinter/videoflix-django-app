from PIL import Image
import os
from django_rq import job

@job
def resize_thumbnail(path: str):
    if not os.path.exists(path):
        return

    with Image.open(path) as img:
        img = img.convert("RGB")

        # Erst zentriert beschneiden (crop)
        width, height = img.size
        target_ratio = 341 / 192
        current_ratio = width / height

        if current_ratio > target_ratio:
            # Bild ist zu breit -> Seiten abschneiden
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img = img.crop((left, 0, left + new_width, height))
        else:
            # Bild ist zu hoch -> oben/unten abschneiden
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img = img.crop((0, top, width, top + new_height))

        # Dann auf Zielgröße skalieren
        img = img.resize((341, 192))
        img.save(path)
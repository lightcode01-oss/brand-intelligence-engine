import hashlib
from pydantic import BaseModel
from typing import List

class VisualRecommendation(BaseModel):
    primary_hue: int
    secondary_hue: int
    heading_font: str
    body_font: str
    brand_personality: List[str]
    icon_style: str
    design_direction: str
    mood: str

class LogoRecommendationEngine:
    """Generates typographic, palette, and style suggestions based on candidate strings."""
    
    def generate_recommendation(self, name: str, style: str) -> VisualRecommendation:
        """Determines typography pairs, HSL hues, and icon traits based on candidate hashes."""
        # Create deterministic hash from word to ensure stable suggestions
        hashed = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
        
        # Select palette base on hash
        primary_hue = hashed % 360
        secondary_hue = (primary_hue + 120) % 360
        
        # Fonts mappings based on style
        font_pairings = [
            ("Outfit", "Inter", "Modern, Clean, Tech-forward"),
            ("Playfair Display", "Lora", "Sophisticated, Premium, Traditional"),
            ("Montserrat", "Roboto", "Bold, Energetic, Direct"),
            ("Fira Code", "Source Sans 3", "Developer-centric, Technical")
        ]
        pairing = font_pairings[hashed % len(font_pairings)]
        
        # Mappings based on style category
        style_details = {
            "Compound": ("Abstract geometric badge", "Constructed, bold alignments", "Synergetic"),
            "Abstract": ("Minimalist line art icon", "Subtle letter spacing tweaks", "Avant-garde"),
            "Tech": ("Digital node system", "Hexagonal frame constraints", "Innovative")
        }
        icon, direction, mood = style_details.get(style, ("Abstract geometric badge", "Standard grid alignment", "Modern"))
        
        return VisualRecommendation(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            heading_font=pairing[0],
            body_font=pairing[1],
            brand_personality=[pairing[2], "Trustworthy", "Innovative"],
            icon_style=icon,
            design_direction=direction,
            mood=mood
        )

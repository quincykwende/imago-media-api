from app.config import settings

def generate_thumbnail_path(db: str, bildnummer: str) -> str:
    """Generate image URL with zero-padded bildnummer"""
    return f"{settings.image_base_url}/bild/{db}/{bildnummer.zfill(10)}/s.jpg"

def extract_copyright(text: str) -> str:
    """Extract the first word after Copyright: marker"""
    copyright_marker = "Copyright:"
    if copyright_marker in text:
        parts = text.split(copyright_marker, 1)
        copyright_words = parts[1].strip().split()
        return copyright_words[0] if copyright_words else ""
    return ""

from app.config import settings

def generate_thumbnail_path(db: str, bildnummer: str) -> str:
    """Generate image URL with zero-padded bildnummer"""
    return f"{settings.image_base_url}/bild/{db}/{bildnummer.zfill(10)}/s.jpg"

def extract_copyright(text: str) -> str:
    """Extract copyright information from suchtext"""
    print(text)
    copyright_marker = "Copyright:"
    if copyright_marker in text:
        copyright_part = text.split(copyright_marker)[-1]
        return copyright_part.split("ABACAPRESS")[0].strip()
    return ""

from app.config import settings

def generate_thumbnail_path(db: str, image_number: str) -> str:
    """
    Generate consistent thumbnail URLs
    Format: https://www.imago-images.de/bild/{db}/{padded_bildnummer}/s.jpg
    """
    padded_num = image_number.zfill(10)
    return f"{settings.image_base_url}/bild/{db}/{padded_num}/s.jpg"

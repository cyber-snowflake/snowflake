import re

IMGUR_EXTENSIONS = re.compile(r"\.(gif|jpe?g|tiff?|a?png|webp|bmp)$", re.IGNORECASE)
IMAGE_EXTENSIONS = re.compile(r"\.(jpe?g|png|webp)$", re.IGNORECASE)

import io

from wand.image import Image


def img_to_buffer(img: Image):
    """Saves image object as BytesIO"""
    _buffer = io.BytesIO()
    img.save(file=_buffer)
    _buffer.seek(0)

    return _buffer

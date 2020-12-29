import io

from wand.image import Image


class WandImage(Image):
    def clone(self):
        return WandImage(image=self)

    def convert(self, format):
        cloned = self.clone()
        cloned.format = format
        return cloned

    def to_bin_stream(self):
        """Saves image object as BytesIO object"""
        fp = io.BytesIO()
        self.save(file=fp)
        fp.seek(0)
        return fp

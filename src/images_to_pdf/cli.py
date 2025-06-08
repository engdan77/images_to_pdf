from pathlib import Path
from cyclopts import App
from images_to_pdf.image import create_collage_from_images, ImageFormat
from loguru import logger

app = App()


@app.default
def test():
    logger.info('Running test')
    files = [
        Path('~/tmp/pdf/convert/1.png').expanduser(),
        Path('~/tmp/pdf/convert/2.png').expanduser(),
        Path('~/tmp/pdf/convert/3.png').expanduser(),
        Path('~/tmp/pdf/convert/4.png').expanduser(),
        Path('~/tmp/pdf/convert/5.png').expanduser(),
    ]

    output_image = create_collage_from_images(images=files,
                                              collage_type='grid',
                                              image_format=ImageFormat.JPG,
                                              size=(1754, 1240),
                                              bg_color='#000000',
                                              )
    Path('~/tmp/pdf/out.jpg').expanduser().write_bytes(output_image)


def main():
    app()

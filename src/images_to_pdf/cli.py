import itertools
import tempfile
from pathlib import Path
from typing import Annotated, Literal
from cyclopts import App, Parameter
from cyclopts.types import ExistingDirectory, ResolvedFile
from images_to_pdf.image import create_collage_from_images, ImageFormat
from loguru import logger

from images_to_pdf.pdf import create_pdf_from_images

app = App()


@app.default
def create_pdf(image_path: ExistingDirectory,
               output_pdf: ResolvedFile,
               images_per_page: int = 10,
               max_pages_per_pdf: int = 20,
               layout: Literal['grid', 'auto', 'lane'] = "grid",
               resolution: tuple[int, int] = (1754, 1240),
):
    logger.info("Start conversion")
    files = list(itertools.chain.from_iterable(image_path.rglob(p) for p in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']))

    orientation: Literal["landscape", "portrait"] = "landscape"
    if layout == 'lane':
        resolution = (resolution[1], resolution[0])
        orientation = "portrait"

    for f in files:
        logger.info(f"Found file {f} {f.stat().st_size / 1000:.0f} KB")

    with tempfile.TemporaryDirectory() as tmpdir:
        page_image_files = []
        for page_number, batch_of_image_files in enumerate(itertools.batched(files, images_per_page), start=1):
            logger.info(f"Creating page {page_number}")
            output_image_bytes = create_collage_from_images(
                images=batch_of_image_files,
                collage_type=layout,
                image_format=ImageFormat.JPG,
                size=resolution,
                bg_color="#000000",
            )
            merged_image_file = (Path(tmpdir) / Path(f"page_{page_number}.jpg")).expanduser()
            merged_image_file.write_bytes(output_image_bytes)
            page_image_files.append(merged_image_file)

        logger.info("Creating PDF")
        create_pdf_from_images(
            images=page_image_files,
            output_pdf_path=output_pdf,
            page_format="a4",
            orientation=orientation
        )


def main():
    app()

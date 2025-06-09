from pathlib import Path
from typing import Literal
from fpdf import FPDF
from PIL import Image
from loguru import logger

from images_to_pdf.image import resize_image


def create_pdf_from_images(
    images: list[Path],
    output_pdf_path: Path,
    page_format: Literal["a4"],
    orientation: Literal["portrait", "landscape"] = "landscape",
    shrink_to_resolution: None | tuple[int, int] = None,
):
    pdf = FPDF(orientation=orientation, format=page_format)
    for image in images:
        pdf.add_page()
        img = Image.open(image.as_posix())
        # img = add_text_to_image(img, 'FOO\nBAR')
        if shrink_to_resolution:
            img = resize_image(img, shrink_to_resolution)
            pdf.image(img, x=0, y=0, w=210, type="", link="")
        else:
            pdf.image(img, x=0, y=0, w=300, type="", link="")

    pdf.output(output_pdf_path.as_posix())
    logger.info(f"Created PDF at {output_pdf_path.as_posix()}")

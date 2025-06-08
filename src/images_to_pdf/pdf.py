from pathlib import Path
from typing import Literal
from fpdf import FPDF
from PIL import Image
from loguru import logger


def create_pdf_from_images(
    images: list[Path],
    output_pdf_path: Path,
    page_format: Literal["a4"],
    orientation: Literal["portrait", "landscape"] = "landscape",
):
    pdf = FPDF(orientation=orientation, format=page_format)
    for image in images:
        pdf.add_page()
        img = Image.open(image.as_posix())
        # img = img.crop((10, 10, 490, 490)).resize((96, 96), resample=Image.NEAREST)
        pdf.image(img, x=0, y=0, w=300, type="", link="")
    pdf.output(output_pdf_path.as_posix())
    logger.info(f"Created PDF at {output_pdf_path.as_posix()}")

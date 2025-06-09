from pathlib import Path
from typing import Literal
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from loguru import logger


def add_text_to_image(image: Image, text: str) -> Image:
    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Define the text properties
    # font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    text_color = (255, 255, 255)

    # Calculate the position to center the text
    text_length = draw.textlength(text)
    x = (image.width - text_length) / 2
    y = image.height / 2
    # Add text to the image
    draw.text((x, y), text, fill=text_color)
    return image


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
        img = add_text_to_image(img, 'FOOO')
        # img = img.crop((10, 10, 490, 490)).resize((96, 96), resample=Image.NEAREST)
        pdf.image(img, x=0, y=0, w=300, type="", link="")
    pdf.output(output_pdf_path.as_posix())
    logger.info(f"Created PDF at {output_pdf_path.as_posix()}")

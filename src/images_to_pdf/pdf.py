from pathlib import Path
from typing import Literal
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from loguru import logger


def add_text_to_image(image: Image, text: str) -> Image:
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(40)
    text_color = (255, 255, 255)
    x = image.width / 4
    y = 20
    position = (x / 2, y)
    left, top, right, bottom = draw.textbbox(position, text, font=font)
    draw.rectangle((left - 5, top - 5, right + 5, bottom + 5), fill="black")
    draw.text(position, text, font=font, fill=text_color)
    return image


def resize_image(image: Image, size: tuple[int, int]) -> Image:
    width = size[0]
    width_percent = (width / float(image.size[0]))
    logger.info(f"Resizing image to {width}x{int(width_percent * float(image.size[1]))}")
    hsize = int((float(image.size[1]) * float(width_percent)))
    img = image.resize((width, hsize), resample=Image.Resampling.BILINEAR)
    return img


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
        img = add_text_to_image(img, 'FOO\nBAR')
        if shrink_to_resolution:
            img = resize_image(img, shrink_to_resolution)
            pdf.image(img, x=0, y=0, w=210, type="", link="")
        else:
            pdf.image(img, x=0, y=0, w=300, type="", link="")

    pdf.output(output_pdf_path.as_posix())
    logger.info(f"Created PDF at {output_pdf_path.as_posix()}")

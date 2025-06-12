from pathlib import Path

from pywebio.output import put_progressbar, set_progressbar, put_text, put_html

from images_to_pdf.cli import create_pdf
from . import runmode, __email__
from pywebio.input import input_group, input, NUMBER, select, checkbox, TEXT
from pywebio_battery import file_picker, put_logbox
from userpaths import get_my_pictures, get_desktop
from . import logger
from . import __version__
import sys


def validate_path(path: str):
    if not Path(path).is_dir():
        return "Input path for images does not exist"
    return None


def validate_output_file(path: str):
    if not Path(path).parent.is_dir():
        return "Directory for output file does not exist"
    if Path(path).suffix != ".pdf":
        return "Output file must be PDF"
    return None


def update_progress_gui(outer: float, inner: float):
    set_progressbar('outer', outer)
    set_progressbar("inner", inner)


def main():
    runmode.set_runmode("gui")

    put_html('<h1>Images to PDF</h1>')
    put_html(f'Author: <a href="mailto:{__email__}">{__email__}</a><br/>')

    put_logbox("log")

    logger.info(f"Start {__package__} {__version__}")
    input_path = sys.argv[1] if len(sys.argv) > 1 else get_desktop()

    params = input_group(
        "Parameters",
        [
            input(
                "Image folder",
                type=TEXT,
                name="image_path",
                value=input_path,
                validate=validate_path,
            ),
            input(
                "Output PDF",
                type=TEXT,
                name="output_pdf",
                value=(Path(get_desktop()) / "output.pdf").as_posix(),
                validate=validate_output_file,
            ),
            select("Page format: ", options=["a4"], name="page_format", value="a4"),
            select(
                label="Orientation",
                options=["landscape", "portrait"],
                name="orientation",
                value="landscape",
                help_text="Landscape found best unless document",
            ),
            input("Images per page: ", type=NUMBER, name="images_per_page", value=10),
            input(
                "Max pages per PDF: ", type=NUMBER, name="max_pages_per_pdf", value=20
            ),
            select(
                label="Layout",
                options=["grid", "auto", "lane", "document"],
                name="layout",
                value="grid",
                help_text="Document for single page per image",
            ),
            select(
                label="Resolution",
                options=[
                    {"label": "big", "value": (1754, 1240), "selected": True},
                    {"label": "medium", "value": (877, 620)},
                    {"label": "small", "value": (584, 413)},
                ],
                name="resolution",
                help_text="Smaller result in smaller file",
            ),
            checkbox(
                label="Annotate images",
                options=["filename"],
                name="annotate_images",
                value=[],
                help_text="Add filename as part of the image, initial digits removed (could be kept for ordering), single underscores replaced by spaces, double underscores replaces by newlines",
            ),
        ],
    )

    logger.info(f"Parameters: {params}")
    put_progressbar("outer", label='PDF creation progress:')
    put_progressbar("inner", label='Imageset progress:')

    create_pdf(
        image_path=Path(params["image_path"]),
        output_pdf=Path(params["output_pdf"]),
        images_per_page=params["images_per_page"],
        max_pages_per_pdf=params["max_pages_per_pdf"],
        layout=params["layout"],
        resolution=params["resolution"],
        annotate_images=params["annotate_images"],
        progress_func=update_progress_gui,
    )

    put_text(f'✅ PDF created successfully to {Path(params["output_pdf"]).parent.as_posix()} ...')




if __name__ == "__main__":
    main()

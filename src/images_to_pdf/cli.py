import itertools
import tempfile
from pathlib import Path
from typing import Annotated, Literal, Callable
from cyclopts import App, Parameter
from cyclopts.types import ExistingDirectory, ResolvedFile
from images_to_pdf.image import (
    create_collage_from_images,
    ImageFormat,
    add_text_to_image,
)
from . import logger
from . import __version__

from images_to_pdf.pdf import create_pdf_from_images
from images_to_pdf.text import filename_to_annotation

app = App()

SUPPORTED_IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"]


def perform_annotate_images(image_files, tmpdir_annotated_images):
    """Annotate images with filenames and return a list of annotated file paths."""
    annotated_files = []
    for image_file in image_files:
        annotated_file = (Path(tmpdir_annotated_images) / image_file.name).expanduser()
        logger.info(f"Annotating {annotated_file.as_posix()}")
        annotated_file.write_bytes(image_file.read_bytes())
        add_text_to_image(annotated_file, text=filename_to_annotation(annotated_file))
        annotated_files.append(annotated_file)
    return annotated_files


def create_pages(
    image_batches,
    layout,
    resolution,
    tmpdir_final_images,
    progress_func,
    progress_pdf_files,
):
    """Create page images from batches and return a list of page file paths."""
    page_files = []
    for page_number, image_batch in enumerate(image_batches, start=1):
        logger.info(f"Creating page {page_number}")
        if layout == "document":  # Use images directly for 'document' layout.
            page_files.extend(image_batch)
            continue
        output_image_bytes = create_collage_from_images(
            images=image_batch,
            collage_type=layout,
            image_format=ImageFormat.JPG,
            size=resolution,
            bg_color="#000000",
        )
        page_file = (Path(tmpdir_final_images) / f"page_{page_number}.jpg").expanduser()
        page_file.write_bytes(output_image_bytes)
        page_files.append(page_file)
        progress_func(progress_pdf_files, page_number / len(image_batches))
    return page_files


def generate_pdf(
    page_files, output_pdf, pdf_number, total_pdfs, orientation, shrink_to_resolution
):
    """Generate a single PDF from the given page files."""
    if total_pdfs > 1:
        pad_size = len(str(total_pdfs))
        output_pdf = (
            output_pdf.parent
            / f"{output_pdf.stem}_{str(pdf_number).zfill(pad_size)}{output_pdf.suffix}"
        )
    logger.info(f"Creating PDF {output_pdf.as_posix()}")
    create_pdf_from_images(
        images=page_files,
        output_pdf_path=output_pdf,
        page_format="a4",
        orientation=orientation,
        shrink_to_resolution=shrink_to_resolution,
    )


@app.default
def create_pdf(
    image_path: ExistingDirectory,
    output_pdf: ResolvedFile,
    images_per_page: int = 10,
    max_pages_per_pdf: int = 20,
    layout: Literal["grid", "auto", "lane", "document"] = "grid",
    resolution: tuple[int, int] = (1754, 1240),
    annotate_images: Annotated[
        bool, Parameter(help="Add filename as part of the image")
    ] = False,
    progress_func: Annotated[
        Callable[[float, float], None],
        Parameter(
            show=False,
            help="Callable with argument progress between 0 and 1 for outer and inner loop",
        ),
    ] = lambda outer, inner: logger.info(
        f"Progress outer: {outer * 100:.0f}% inner: {inner * 100:.0f}%"
    ),
):
    logger.info(f"Start {__package__} {__version__}")

    # Gather and log all image files.
    all_image_files = list(
        itertools.chain.from_iterable(
            image_path.rglob(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS
        )
    )
    for img_file in all_image_files:
        logger.info(f"Found file {img_file} {img_file.stat().st_size / 1000:.0f} KB")

    # Determine orientation and shrink resolution based on layout.
    orientation = "portrait" if layout in ("lane", "document") else "landscape"
    shrink_to_resolution = resolution if layout == "document" else None
    if layout in ("lane", "document"):
        resolution = (
            resolution[1],
            resolution[0],
        )  # Swap resolution for portrait layouts.

    # Calculate number of final PDFs.
    total_pdfs = (len(all_image_files) + max_pages_per_pdf - 1) // max_pages_per_pdf
    logger.info(f"Creating {total_pdfs} PDF files")

    # Process each batch of images for separate PDFs.
    for pdf_number, image_batch in enumerate(
        itertools.batched(all_image_files, max_pages_per_pdf), start=1
    ):
        progress_pdf_files = pdf_number / total_pdfs
        with tempfile.TemporaryDirectory() as tmpdir_annotated_images:
            # Annotate images if required.
            final_images = (
                perform_annotate_images(image_batch, tmpdir_annotated_images)
                if annotate_images
                else image_batch
            )

            # Create pages for the PDF.
            with tempfile.TemporaryDirectory() as tmpdir_final_images:
                image_batches = list(itertools.batched(final_images, images_per_page))
                page_files = create_pages(
                    image_batches,
                    layout,
                    resolution,
                    tmpdir_final_images,
                    progress_func,
                    progress_pdf_files,
                )

                # Generate the PDF from the page images.
                generate_pdf(
                    page_files,
                    output_pdf,
                    pdf_number,
                    total_pdfs,
                    orientation,
                    shrink_to_resolution,
                )

        progress_func(progress_pdf_files, 1.0)


def main():
    app()


if __name__ == "__main__":
    main()

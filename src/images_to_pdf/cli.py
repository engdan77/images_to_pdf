import itertools
import tempfile
from pathlib import Path
from typing import Annotated, Literal
from cyclopts import App, Parameter
from cyclopts.types import ExistingDirectory, ResolvedFile
from images_to_pdf.image import create_collage_from_images, ImageFormat, add_text_to_image
from . import logger

from images_to_pdf.pdf import create_pdf_from_images
from images_to_pdf.text import filename_to_annotation

app = App()


@app.default
def create_pdf(image_path: ExistingDirectory,
               output_pdf: ResolvedFile,
               images_per_page: int = 10,
               max_pages_per_pdf: int = 20,
               layout: Literal['grid', 'auto', 'lane', 'document'] = "grid",
               resolution: tuple[int, int] = (1754, 1240),
               annotate_images: Annotated[bool, Parameter(help='Add filename as part of the image')] = False,
):
    logger.info("Start conversion")
    all_image_files = list(itertools.chain.from_iterable(image_path.rglob(p) for p in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']))

    orientation: Literal["landscape", "portrait"] = "landscape"
    if layout in ('lane', 'document'):
        resolution = (resolution[1], resolution[0])
        orientation = "portrait"

    if layout == 'document':
        shrink_to_resolution = resolution
    else:
        shrink_to_resolution = None

    for f in all_image_files:
        logger.info(f"Found file {f} {f.stat().st_size / 1000:.0f} KB")

    count_of_final_pdf_files = (len(all_image_files) // max_pages_per_pdf) + 1
    logger.info(f"Creating {count_of_final_pdf_files} PDF files")

    for pdf_number, batch_of_image_files_for_pdf in enumerate(
            itertools.batched(all_image_files, max_pages_per_pdf), start=1):

        with tempfile.TemporaryDirectory() as tmpdir_annotated_images:
            final_image_files = []
            if not annotate_images:
                logger.info("Skipping annotation")
                final_image_files = batch_of_image_files_for_pdf
            else:
                logger.info("Annotating images")
                for f in batch_of_image_files_for_pdf:
                    annotated_image_file = (Path(tmpdir_annotated_images) / Path(f.name)).expanduser()
                    logger.info(f"Annotating {annotated_image_file.as_posix()}")
                    annotated_image_file.write_bytes(f.read_bytes())
                    add_text_to_image(annotated_image_file, text=filename_to_annotation(annotated_image_file))
                    final_image_files.append(annotated_image_file)

            with tempfile.TemporaryDirectory() as tmpdir_final_images:
                page_image_files = []
                for page_number, batch_of_image_files_for_page in enumerate(itertools.batched(final_image_files, images_per_page), start=1):
                    logger.info(f"Creating page {page_number}")
                    if layout == 'document':
                        page_image_files.extend(batch_of_image_files_for_page)
                        continue
                    output_image_bytes = create_collage_from_images(
                        images=batch_of_image_files_for_page,
                        collage_type=layout,
                        image_format=ImageFormat.JPG,
                        size=resolution,
                        bg_color="#000000",
                    )
                    merged_image_file = (Path(tmpdir_final_images) / Path(f"page_{page_number}.jpg")).expanduser()
                    merged_image_file.write_bytes(output_image_bytes)
                    page_image_files.append(merged_image_file)

                if count_of_final_pdf_files > 1:
                    pad_size = len(str(count_of_final_pdf_files))
                    output_pdf_final = output_pdf.parent / f"{output_pdf.stem}_{str(pdf_number).zfill(pad_size)}{output_pdf.suffix}"
                else:
                    output_pdf_final = output_pdf.parent / f"{output_pdf.stem}{output_pdf.suffix}"

                logger.info(f"Creating PDF {output_pdf.as_posix()}")
                create_pdf_from_images(
                    images=page_image_files,
                    output_pdf_path=output_pdf_final,
                    page_format="a4",
                    orientation=orientation,
                    shrink_to_resolution=shrink_to_resolution,
                )


def main():
    app()

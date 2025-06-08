from enum import StrEnum

from PIL import Image
import io
from pathlib import Path
from typing import Literal, Annotated
from PIL import Image, ImageOps
import math
import random


GOLDEN_RATIO = (1 + math.sqrt(5)) / 2  # Define the golden ratio


class ImageFormat(StrEnum):
    JPG = 'JPEG'
    PNG = 'PNG'

def golden_ratio_collage(images, collage, padding, randomization):
    """
    Create a golden ratio-based collage from the provided images.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.

    Notes:
        - Images are dynamically resized based on the golden ratio and remaining working area.
    """
    # Initialize the working area for placing images
    working_area = {
        "x": 0,
        "y": 0,
        "width": collage.width,
        "height": collage.height,
    }

    # Determine the initial layout orders
    horizontal_order = "right-to-left"
    vertical_order = "bottom-to-top"

    # Determine the initial layout orders
    if randomization:
        horizontal_order = random.choice(["right-to-left", "left-to-right"])
        vertical_order = random.choice(["bottom-to-top", "top-to-bottom"])
        random.shuffle(images)

    x, y = 0, 0  # Starting position
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        # Decide whether to split horizontally or vertically based on working area dimensions
        if working_area["width"] > working_area["height"]:  # Horizontal split
            img = ImageOps.fit(
                img,
                (int(working_area["width"] / GOLDEN_RATIO), working_area["height"]),
                method=Image.Resampling.LANCZOS,
            )
            # Adjust position and update working area
            if horizontal_order == "right-to-left":
                horizontal_order = "left-to-right"
                working_area["x"] += img.width + padding
            else:
                x = x + working_area["width"] - img.width
                horizontal_order = "right-to-left"
            working_area["width"] -= img.width + padding
        else:  # Vertical split
            img = ImageOps.fit(
                img,
                (working_area["width"], int(working_area["height"] / GOLDEN_RATIO)),
                method=Image.Resampling.LANCZOS,
            )
            # Adjust position and update working area
            if vertical_order == "bottom-to-top":
                working_area["y"] += img.height + padding
                vertical_order = "top-to-bottom"
            else:
                y = y + working_area["height"] - img.height
                vertical_order = "bottom-to-top"
            working_area["height"] -= img.height + padding

        # Paste the image onto the canvas
        collage.paste(img, (x, y))
        x, y = (
            working_area["x"],
            working_area["y"],
        )  # Update position for the next image

        # Stop if the working area becomes too small
        if working_area["width"] <= 0 or working_area["height"] <= 0:
            print("Working area exhausted. Stopping collage creation.")
            break

    return collage


def lane_collage(
    images, collage, padding, randomization, centered, orientation="horizontal"
):
    """
    Create a lane-based collage.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.
        centered (bool): Whether to center the grid if the canvas is not square.
        orientation (str): Orientation of the grid: "horizontal" or "vertical".
    """
    canvas_width, canvas_height = collage.size

    images_num = len(images)

    if randomization:
        random.shuffle(images)

    # Determine block size based on orientation
    if orientation == "horizontal":
        block_height = (canvas_height - (images_num + 1) * padding) // images_num
        block_width = canvas_width
    elif orientation == "vertical":
        block_width = (canvas_width - (images_num + 1) * padding) // images_num
        block_height = canvas_height
    else:
        raise ValueError("Orientation must be 'horizontal' or 'vertical'.")

    # Centering offsets
    offset_x, offset_y = 0, 0
    if centered:
        if (
            orientation == "horizontal"
            and images_num * (block_height + padding) < canvas_height
        ):
            offset_y = (canvas_height - (images_num * (block_height + padding))) // 2
        if (
            orientation == "vertical"
            and images_num * (block_width + padding) < canvas_width
        ):
            offset_x = (canvas_width - (images_num * (block_width + padding))) // 2

    # Resize and paste images
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        img = ImageOps.fit(
            img, (block_width, block_height), method=Image.Resampling.LANCZOS
        )

        # Calculate position
        x, y = 0, 0
        if orientation == "horizontal":
            y = idx * (block_height + padding) + padding + offset_y
        elif orientation == "vertical":
            x = idx * (block_width + padding) + padding + offset_x

        collage.paste(img, (x, y))

    return collage



def auto_layout(images, collage, padding, randomization, centered):
    """
    Create an auto layout.

    Args:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.
        centered (bool): Whether to center the grid if the canvas is not square (default: False).
    """
    canvas_width, canvas_height = collage.size
    images_num = len(images)
    image_objects_list = []
    squares = 0
    horizontal_rectangles = 0
    vertical_rectangles = 0
    total_area = 0
    aspect_ratio_sum_width = aspect_ratio_sum_height = 0
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        image_objects_list.append({"image": img})
        total_area += img.width * img.height
        if img.height == img.width:
            squares += 1
            aspect_ratio_sum_width += 1
            aspect_ratio_sum_height += 1

        elif img.height > img.width:
            vertical_rectangles += 1
            aspect_ratio_sum_height += img.height / img.width
            aspect_ratio_sum_width += 1

        else:
            horizontal_rectangles += 1
            aspect_ratio_sum_width += img.width / img.height
            aspect_ratio_sum_height += 1

    if squares == images_num:
        return grid_collage(images, collage, padding, randomization, centered)

    elif horizontal_rectangles == images_num:
        return lane_collage(
            images, collage, padding, randomization, centered, orientation="horizontal"
        )

    elif vertical_rectangles == images_num:
        return lane_collage(
            images, collage, padding, randomization, centered, orientation="vertical"
        )

    else:
        canvas_area = canvas_width * canvas_height
        scaling_factor = math.sqrt(canvas_area / total_area)
        rows = 0
        cols = 0
        aspect_sum_diff = abs(aspect_ratio_sum_width - aspect_ratio_sum_height)
        return golden_ratio_collage(images, collage, padding, randomization)


def grid_collage(images, collage, padding, randomization, centered):
    """
    Create a grid-based collage.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.
        centered (bool): Whether to center the grid if the canvas is not square.
    """
    images_num = len(images)
    if randomization:
        random.shuffle(images)
    canvas_width, canvas_height = collage.size
    if canvas_width == canvas_height:
        # Square canvas: Determine grid dimensions for a square layout
        grid_size = math.ceil(math.sqrt(images_num))
        cell_size = (canvas_width - (grid_size + 1) * padding) // grid_size

        for idx, img_path in enumerate(images):
            img = Image.open(img_path)
            img = ImageOps.fit(
                img, (cell_size, cell_size), method=Image.Resampling.LANCZOS
            )

            # Calculate position in the grid
            x = (idx % grid_size) * (cell_size + padding) + padding
            y = (idx // grid_size) * (cell_size + padding) + padding

            collage.paste(img, (x, y))

    else:
        # Non-square canvas: Determine grid dimensions for the closest layout
        cols = math.ceil(math.sqrt(images_num))
        rows = math.ceil(images_num / cols)
        offset_x, offset_y = 0, 0

        # Adjust grid dimensions and offsets based on canvas proportions
        if canvas_width > canvas_height:
            if cols < rows:
                cols, rows = rows, cols
            if centered:
                offset_x = (canvas_width - (rows * (canvas_height // rows))) // 2
        elif canvas_width < canvas_height:
            if cols > rows:
                cols, rows = rows, cols
            if centered:
                offset_y = (canvas_height - (cols * (canvas_width // cols))) // 2

        # Calculate cell dimensions
        cell_width = (canvas_width - (cols + 1) * padding) // cols
        cell_height = (canvas_height - (rows + 1) * padding) // rows

        # Use the smaller dimension if centering is enabled
        if centered:
            cell_width = cell_height = min(cell_width, cell_height)

        for idx, img_path in enumerate(images):
            img = Image.open(img_path)
            img = ImageOps.fit(
                img, (cell_width, cell_height), method=Image.Resampling.LANCZOS
            )

            # Calculate position in the grid
            x = (idx % cols) * (cell_width + padding) + padding + offset_x
            y = (idx // cols) * (cell_height + padding) + padding + offset_y

            collage.paste(img, (x, y))

    return collage


def create_collage_from_images(images: list[Path], collage_type: Literal['grid', 'auto'], size = (2560, 1440), bg_color: str = '#000000', image_format: ImageFormat = ImageFormat.PNG) -> Annotated[bytes, "Image bytes"]:
    new_collage = Image.new(
        "RGB",
        size=size,
        color=bg_color,
    )

    t = {'grid': grid_collage, 'auto': auto_layout}

    new_collage: Image = t[collage_type](
        images=images,
        collage=new_collage,
        padding=0,
        randomization=False,
        centered=False,
    )
    image_bytes = io.BytesIO()
    new_collage.save(
        image_bytes, format=image_format.value
    )
    return image_bytes.getvalue()
from pathlib import Path
import re
import unicodedata


def filename_to_annotation(file: Path, newline_delimiter="__") -> str:
    t = file.stem.lower()
    t = t.replace(newline_delimiter, "\n")
    t = re.sub(r"^\d+", "", t)
    t = t.replace("_", " ").strip()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("utf-8")
    return t.capitalize()

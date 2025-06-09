from pathlib import Path
import re
import unicodedata


def filename_to_annotation(file: Path, newline_delimiter='##') -> str:
    t = file.stem.lower()
    t = re.sub(r"^\d+", "", t)
    t = t.replace("_", " ").strip()
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('utf-8')
    t.replace(newline_delimiter, '\n')
    return t.capitalize()
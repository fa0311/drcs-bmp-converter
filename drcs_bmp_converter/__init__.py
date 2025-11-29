"""DRCS BMP Converter package."""

from .cli import main
from .drcs_converter import parse_drcs_bmp

__version__ = "1.0.0"
__all__ = ["parse_drcs_bmp", "main"]

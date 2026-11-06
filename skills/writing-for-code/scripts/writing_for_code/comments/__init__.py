"""Extract, flag, and lint the comment blocks in source files."""

from .extract import analyze, scan, source_files  # noqa: F401
from .languages import style_for  # noqa: F401

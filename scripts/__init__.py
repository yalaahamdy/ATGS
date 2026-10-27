# -*- coding: utf-8 -*-
"""
ATGS - Arabic Translate Game Skill
Package initialization.
"""

from .atgs_reshaper import process_arabic_text, has_arabic
from .atgs_extract import extract_from_file, build_batches
from .atgs_import import rebuild_game_files

__version__ = "1.0.0"
__author__ = "ATGS Team"

# -*- coding: utf-8 -*-
"""
Personal Website Manager - Configuration
"""

import os
from pathlib import Path

APP_NAME = "Personal Website Manager"
APP_VERSION = "1.0.0"

DEFAULT_REPO_URL = "https://github.com/6chHenry/6chHenry.github.io.git" # Alter it to your GitHub repository URL
DEFAULT_LOCAL_REPO = r"F:\EECS498\6ch"   # Alter it to your local path where you want to clone the repo
DEFAULT_DOCS_PATH = os.path.join(DEFAULT_LOCAL_REPO, "docs")

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 280

TAB_SIZE = 4
AUTO_SAVE_INTERVAL = 30000

FONT_FAMILY_CN = "霞鹜文楷, Inter, Microsoft YaHei, sans-serif"
FONT_FAMILY_EN = "JetBrains Mono, Consolas, monospace"
FONT_SIZE = 14
EDITOR_FONT_SIZE = 15
SIDEBAR_FONT_SIZE = 13

SIDEBAR_ICON_SIZE = 18

COLORS = {
    "background": "#09090b",
    "surface": "#18181b",
    "surface_light": "#1f1f23",
    "surface_hover": "#27272a",
    "surface_active": "#3f3f46",
    "border": "#27272a",
    "border_focus": "#52525b",

    "text_primary": "#f4f4f5",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",

    "accent": "#22d3ee",
    "accent_hover": "#67e8f9",
    "accent_pressed": "#06b6d4",

    "success": "#22c55e",
    "warning": "#eab308",
    "error": "#ef4444",
    "info": "#3b82f6",

    "sidebar_bg": "#09090b",
    "sidebar_header": "#18181b",
    "sidebar_item_hover": "#27272a",
    "sidebar_item_active": "#3f3f46",

    "editor_bg": "#09090b",
    "preview_bg": "#18181b",

    "selection": "#3f3f46",
    "line_highlight": "#27272a",

    "btn_primary": "#22d3ee",
    "btn_primary_hover": "#67e8f9",
    "btn_primary_text": "#09090b",
    "btn_secondary": "#27272a",
    "btn_secondary_hover": "#3f3f46",
    "btn_danger": "#ef4444",
    "btn_danger_hover": "#f87171",

    "gradient_start": "#18181b",
    "gradient_end": "#27272a",
}


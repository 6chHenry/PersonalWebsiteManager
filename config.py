# -*- coding: utf-8 -*-
"""
Personal Website Manager - Configuration
"""

import os
from pathlib import Path

# Application name
APP_NAME = "Personal Website Manager"
APP_VERSION = "1.0.0"

# Default paths
DEFAULT_REPO_URL = "https://github.com/..." # Use your own github repo here
DEFAULT_LOCAL_REPO = r"C:\Users\YourUsername\Documents\PersonalWebsiteRepo" # Change this to your local path    
DEFAULT_DOCS_PATH = os.path.join(DEFAULT_LOCAL_REPO, "docs")

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 280

# Editor Settings
TAB_SIZE = 4
AUTO_SAVE_INTERVAL = 30000  # milliseconds
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 14

# Sidebar Settings
SIDEBAR_FONT_SIZE = 14
SIDEBAR_ICON_SIZE = 18

# Colors (Modern dark theme palette - inspired by VS Code Dark+)
COLORS = {
    # Background colors
    "background": "#1a1a2e",
    "surface": "#16213e",
    "surface_light": "#1f3460",
    "surface_hover": "#253a5c",
    "border": "#2d4a6f",
    
    # Text colors
    "text_primary": "#e8e8e8",
    "text_secondary": "#9ba4b4",
    "text_muted": "#6b7280",
    
    # Accent colors
    "accent": "#0f969c",
    "accent_hover": "#0db5bc",
    "accent_light": "#12a4aa",
    
    # Status colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    
    # Special colors
    "sidebar_bg": "#0f0f23",
    "sidebar_header": "#16213e",
    "editor_bg": "#1a1a2e",
    "preview_bg": "#1a1a2e",
    "selection": "#264f78",
    "line_highlight": "#1f2937",
    
    # Button colors
    "btn_primary": "#0f969c",
    "btn_primary_hover": "#0db5bc",
    "btn_secondary": "#16213e",
    "btn_secondary_hover": "#1f3460",
    "btn_danger": "#dc2626",
    "btn_danger_hover": "#ef4444",
    
    # Gradient colors
    "gradient_start": "#0f969c",
    "gradient_end": "#0db5bc",
}

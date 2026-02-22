# -*- coding: utf-8 -*-
"""
Markdown Preview Widget
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QStackedWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QImage, QImageReader, QPalette, QColor
from config import COLORS
from core.markdown_renderer import MarkdownRenderer


class MarkdownPreview(QWidget):
    """Markdown preview widget using WebEngine"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.renderer = MarkdownRenderer()
        self.current_html = ""
        self.current_image_path = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title = QLabel("预览")
        self.title.setStyleSheet(f"""
            font-size: 12px; 
            font-weight: 600; 
            color: {COLORS['text_secondary']};
            padding: 8px 12px;
            background-color: {COLORS['surface']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        self.title.setFixedHeight(32)
        layout.addWidget(self.title)
        
        self.stack = QStackedWidget()
        
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(f"""
            QWebEngineView {{
                background-color: {COLORS["preview_bg"]};
            }}
        """)
        
        palette = self.web_view.palette()
        palette.setBrush(QPalette.ColorRole.Base, QColor(COLORS["preview_bg"]))
        self.web_view.setPalette(palette)
        
        self.stack.addWidget(self.web_view)
        
        self.image_scroll = QScrollArea()
        self.image_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS["preview_bg"]};
            }}
        """)
        self.image_scroll.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(f"padding: 20px; background-color: {COLORS['preview_bg']}; color: {COLORS['text_secondary']};")
        self.image_scroll.setWidget(self.image_label)
        self.stack.addWidget(self.image_scroll)
        
        layout.addWidget(self.stack)
        
        self.update_preview("")
    
    def update_preview(self, markdown_text, base_path=None):
        """Update the preview with new markdown text"""
        self.title.setText("预览")
        self.current_image_path = None
        self.stack.setCurrentIndex(0)
        html = self.renderer.render(markdown_text, base_path)
        
        if base_path:
            base_url = QUrl.fromLocalFile(base_path + '/')
        else:
            base_url = QUrl()
        
        self.web_view.setHtml(html, base_url)
    
    def show_image(self, image_path):
        """Show an image in the preview area"""
        self.title.setText(f"图片: {os.path.basename(image_path)}")
        self.current_image_path = image_path
        
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                1200, 800,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            reader = QImageReader(image_path)
            if reader.canRead():
                image = reader.read()
                if not image.isNull():
                    self.image_label.setPixmap(QPixmap.fromImage(image))
                else:
                    self.image_label.setText(f"无法加载图片:\n{image_path}")
            else:
                self.image_label.setText(f"无法加载图片:\n{image_path}")
        
        self.stack.setCurrentIndex(1)
    
    def reload(self):
        """Reload current content"""
        if self.current_image_path:
            self.show_image(self.current_image_path)
        else:
            self.web_view.reload()

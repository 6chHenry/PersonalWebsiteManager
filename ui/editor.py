# -*- coding: utf-8 -*-
"""
Markdown Editor Widget
"""

import re
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from config import COLORS


class MarkdownEditor(QPlainTextEdit):
    """Markdown editor with syntax highlighting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        
    # Preview-matched font settings
    EDITOR_FONT_FAMILY = '"霞鹜文楷", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    EDITOR_FONT_SIZE_PX = 15
    EDITOR_LINE_HEIGHT = 1.8

    def init_ui(self):
        """Initialize UI"""
        font = QFont()
        font.setFamily("霞鹜文楷")
        font.setPointSize(self.EDITOR_FONT_SIZE_PX)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font)

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {COLORS["editor_bg"]};
                color: {COLORS["text_primary"]};
                border: none;
                border-left: 1px solid {COLORS["border"]};
                padding: 24px 32px;
                selection-background-color: {COLORS["selection"]};
                selection-color: {COLORS["text_primary"]};
                font-family: {self.EDITOR_FONT_FAMILY};
                font-size: {self.EDITOR_FONT_SIZE_PX}px;
                line-height: {self.EDITOR_LINE_HEIGHT};
            }}
            
            QPlainTextEdit:focus {{
                border-left: 2px solid {COLORS["accent"]};
            }}
            
            QPlainTextEdit::selection {{
                background-color: {COLORS["selection"]};
            }}
        """)
        
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        self.setTabStopDistance(40)
        
        self.setPlaceholderText("开始编写您的Markdown文档...")
        
        self.setUndoRedoEnabled(True)
        
        self.setCursorWidth(2)
    
    def keyPressEvent(self, e):
        """Handle key press events"""
        if e.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            
            if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                
                for _ in range(4):
                    cursor.deleteChar()
                
                self.setTextCursor(cursor)
            else:
                cursor.insertText("    ")
            
            e.accept()
            return
        
        cursor = self.textCursor()
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
            line_text = cursor.selectedText()
            
            match = re.match(r'^(\s*)([-*+])\s+', line_text)
            if match:
                indent, bullet = match.groups()
                cursor.insertText("\n" + indent + bullet + " ")
                e.accept()
                return
            
            match = re.match(r'^(\s*)(\d+)\.\s+', line_text)
            if match:
                indent, number = match.groups()
                next_num = int(number) + 1
                cursor.insertText("\n" + indent + str(next_num) + ". ")
                e.accept()
                return
            
            match = re.match(r'^(\s*)[-*+]\s+\[ \]\s+', line_text)
            if match:
                indent = match.group(1)
                cursor.insertText("\n" + indent + "- [ ] ")
                e.accept()
                return
            
            match = re.match(r'^(\s*)[-*+]\s+\[x\]\s+', line_text)
            if match:
                indent = match.group(1)
                cursor.insertText("\n" + indent + "- [ ] ")
                e.accept()
                return
        
        super().keyPressEvent(e)

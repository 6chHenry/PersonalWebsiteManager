# -*- coding: utf-8 -*-
"""
Markdown Editor Widget
"""

import re
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from config import COLORS, FONT_FAMILY, FONT_SIZE


class MarkdownEditor(QPlainTextEdit):
    """Markdown editor with syntax highlighting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        # Set font - use larger size and better Chinese font
        font = QFont("Microsoft YaHei", 16)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font)
        
        # Set colors
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {COLORS["editor_bg"]};
                color: {COLORS["text_primary"]};
                border: none;
                border-left: 1px solid {COLORS["border"]};
                padding: 15px 20px;
                selection-background-color: {COLORS["selection"]};
                selection-color: white;
                font-family: "Microsoft YaHei", "Segoe UI", "PingFang SC", sans-serif;
                font-size: 16px;
                line-height: 1.6;
            }}
            
            QPlainTextEdit:focus {{
                border-left: 2px solid {COLORS["accent"]};
            }}
        """)
        
        # Line wrapping
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # Tab size
        self.setTabStopDistance(40)
        
        # Placeholder text
        self.setPlaceholderText("✏️ 开始编写您的Markdown文档...")
        
        # Enable undo/redo
        self.setUndoRedoEnabled(True)
        
        # Set cursor width
        self.setCursorWidth(2)
    
    def keyPressEvent(self, e):
        """Handle key press events"""
        # Handle Tab key for indentation
        if e.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            
            if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+Tab: dedent
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                
                # Remove up to 4 spaces at start of line
                for _ in range(4):
                    cursor.deleteChar()
                
                self.setTextCursor(cursor)
            else:
                # Tab: insert spaces
                cursor.insertText("    ")
            
            e.accept()
            return
        
        # Handle Enter for list continuation
        cursor = self.textCursor()
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            # Get current line text
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
            line_text = cursor.selectedText()
            
            # Unordered list
            match = re.match(r'^(\s*)([-*+])\s+', line_text)
            if match:
                indent, bullet = match.groups()
                cursor.insertText("\n" + indent + bullet + " ")
                e.accept()
                return
            
            # Ordered list
            match = re.match(r'^(\s*)(\d+)\.\s+', line_text)
            if match:
                indent, number = match.groups()
                next_num = int(number) + 1
                cursor.insertText("\n" + indent + str(next_num) + ". ")
                e.accept()
                return
            
            # Checkbox
            match = re.match(r'^(\s*)[-*+]\s+\[ \]\s+', line_text)
            if match:
                indent = match.group(1)
                cursor.insertText("\n" + indent + "- [ ] ")
                e.accept()
                return
            
            # Checked checkbox
            match = re.match(r'^(\s*)[-*+]\s+\[x\]\s+', line_text)
            if match:
                indent = match.group(1)
                cursor.insertText("\n" + indent + "- [ ] ")
                e.accept()
                return
        
        super().keyPressEvent(e)

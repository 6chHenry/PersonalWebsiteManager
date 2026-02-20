# -*- coding: utf-8 -*-
"""
Clone Repository Dialog
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from config import COLORS, DEFAULT_REPO_URL, DEFAULT_LOCAL_REPO


class CloneDialog(QDialog):
    """Dialog for cloning a GitHub repository"""
    
    repo_url_changed = pyqtSignal(str)
    clone_requested = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("克隆仓库")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("克隆 GitHub 仓库")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("请输入您的GitHub仓库地址，或选择本地已有的仓库")
        desc.setStyleSheet("color: #858585;")
        layout.addWidget(desc)
        
        # Repository URL
        url_layout = QVBoxLayout()
        url_label = QLabel("仓库地址 (URL):")
        url_label.setStyleSheet("color: #CCCCCC;")
        url_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://github.com/username/repo.git")
        self.url_input.setText(DEFAULT_REPO_URL)
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["surface"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                padding: 8px;
                border-radius: 4px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS["accent"]};
            }}
        """)
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Local path
        path_layout = QVBoxLayout()
        path_label = QLabel("本地保存路径:")
        path_label.setStyleSheet("color: #CCCCCC;")
        path_layout.addWidget(path_label)
        
        path_input_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setText(DEFAULT_LOCAL_REPO)
        self.path_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["surface"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                padding: 8px;
                border-radius: 4px;
            }}
        """)
        path_input_layout.addWidget(self.path_input, 1)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedWidth(80)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self.browse_folder)
        path_input_layout.addWidget(browse_btn)
        
        path_layout.addLayout(path_input_layout)
        layout.addLayout(path_layout)
        
        # Check if local repo exists
        if os.path.exists(DEFAULT_LOCAL_REPO):
            existing_label = QLabel(f"✓ 发现本地仓库: {DEFAULT_LOCAL_REPO}")
            existing_label.setStyleSheet("color: #4EC9B0;")
            layout.addWidget(existing_label)
            
            use_local_btn = QPushButton("使用本地仓库")
            use_local_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            use_local_btn.clicked.connect(self.use_local_repo)
            layout.addWidget(use_local_btn)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.clone_btn = QPushButton("克隆仓库")
        self.clone_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clone_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_hover"]};
            }}
        """)
        self.clone_btn.clicked.connect(self.on_clone_clicked)
        button_layout.addWidget(self.clone_btn)
        
        layout.addLayout(button_layout)
    
    def on_url_changed(self, url):
        """Handle URL change"""
        self.repo_url_changed.emit(url)
    
    def browse_folder(self):
        """Browse for folder"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择文件夹", os.path.expanduser("~")
        )
        
        if folder:
            self.path_input.setText(folder)
    
    def use_local_repo(self):
        """Use existing local repository"""
        self.accept()
    
    def on_clone_clicked(self):
        """Handle clone button click"""
        url = self.url_input.text().strip()
        path = self.path_input.text().strip()
        
        if not url:
            self.url_input.setFocus()
            return
        
        if not path:
            self.path_input.setFocus()
            return
        
        if os.path.exists(path):
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "目录已存在",
                "该目录已存在，是否使用现有仓库？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.accept()
            return
        
        # Emit clone signal
        self.clone_requested.emit(url, path)
        
        # Close dialog (parent will handle actual cloning)
        self.accept()

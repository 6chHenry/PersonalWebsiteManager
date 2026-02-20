# -*- coding: utf-8 -*-
"""
Search Dialog - Search content in markdown files
"""

import os
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QWidget, QScrollArea, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor
from config import COLORS


class SearchDialog(QDialog):
    """Dialog for searching content in markdown files"""
    
    jump_to_file = pyqtSignal(str, int)  # file_path, line_number
    
    def __init__(self, root_path, parent=None):
        super().__init__(parent)
        
        self.root_path = root_path
        self.search_results = []
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🔍 内容搜索")
        self.setMinimumSize(800, 600)
        self.setModal(False)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔍 在文档中搜索内容")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; padding: 10px;")
        layout.addWidget(title)
        
        # Search input area
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search input
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入要搜索的内容...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                padding: 8px 12px;
                font-size: 14px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #007ACC;
            }
        """)
        self.search_input.returnPressed.connect(self.do_search)
        input_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
        """)
        self.search_btn.clicked.connect(self.do_search)
        input_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(input_layout)
        
        # Options
        options_layout = HBoxLayout()
        options_layout.setSpacing(20)
        
        self.case_sensitive = QCheckBox("区分大小写")
        self.case_sensitive.setStyleSheet("color: #CCCCCC;")
        options_layout.addWidget(self.case_sensitive)
        
        self.search_in_content = QCheckBox("搜索文件内容")
        self.search_in_content.setChecked(True)
        self.search_in_content.setStyleSheet("color: #CCCCCC;")
        options_layout.addWidget(self.search_in_content)
        
        self.search_in_filename = QCheckBox("搜索文件名")
        self.search_in_filename.setChecked(True)
        self.search_in_filename.setStyleSheet("color: #CCCCCC;")
        options_layout.addWidget(self.search_in_filename)
        
        options_layout.addStretch()
        
        search_layout.addLayout(options_layout)
        
        layout.addWidget(search_widget)
        
        # Results count
        self.results_label = QLabel("请输入搜索内容")
        self.results_label.setStyleSheet("color: #8B949E; font-size: 13px; padding: 5px;")
        layout.addWidget(self.results_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3E3E42;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #2A2D2E;
            }
        """)
        self.results_list.itemDoubleClicked.connect(self.on_result_clicked)
        layout.addWidget(self.results_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        buttons_layout.addStretch()
        
        self.jump_btn = QPushButton("跳转到选中项")
        self.jump_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
        """)
        self.jump_btn.clicked.connect(self.on_jump_clicked)
        buttons_layout.addWidget(self.jump_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4E4E4E;
            }
        """)
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def do_search(self):
        """Perform search"""
        keyword = self.search_input.text().strip()
        
        if not keyword:
            self.results_label.setText("请输入搜索内容")
            self.results_list.clear()
            return
        
        self.search_results = []
        self.results_list.clear()
        
        flags = 0 if self.case_sensitive.isChecked() else re.IGNORECASE
        
        md_files = self.get_all_md_files()
        
        for file_path in md_files:
            try:
                # Search in filename
                if self.search_in_filename.isChecked():
                    if re.search(keyword, os.path.basename(file_path), flags):
                        rel_path = os.path.relpath(file_path, self.root_path)
                        self.search_results.append({
                            'file': file_path,
                            'line': 0,
                            'content': f"文件名匹配: {os.path.basename(file_path)}",
                            'type': 'filename'
                        })
                
                # Search in content
                if self.search_in_content.isChecked():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(keyword, line, flags):
                                rel_path = os.path.relpath(file_path, self.root_path)
                                # Get context (surrounding text)
                                context = line.strip()
                                if len(context) > 80:
                                    context = context[:80] + "..."
                                
                                self.search_results.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'content': f"第 {line_num} 行: {context}",
                                    'type': 'content'
                                })
                                
                                # Limit results per file for performance
                                if len([r for r in self.search_results if r['file'] == file_path]) > 50:
                                    break
                                    
            except Exception as e:
                continue
        
        # Display results
        for result in self.search_results:
            rel_path = os.path.relpath(result['file'], self.root_path)
            item_text = f"{rel_path} - {result['content']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
        
        # Update results count
        count = len(self.search_results)
        if count == 0:
            self.results_label.setText(f"未找到匹配 '{keyword}' 的结果")
        else:
            self.results_label.setText(f"找到 {count} 个匹配结果")
    
    def get_all_md_files(self):
        """Get all markdown files in the root path"""
        md_files = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip .git directory
            if '.git' in root:
                continue
            
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        return md_files
    
    def on_result_clicked(self, item):
        """Handle result item clicked"""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            self.jump_to_file.emit(result['file'], result['line'])
            self.close()
    
    def on_jump_clicked(self):
        """Handle jump button clicked"""
        current_item = self.results_list.currentItem()
        if current_item:
            self.on_result_clicked(current_item)


class HBoxLayout(QHBoxLayout):
    """Custom HBoxLayout for clean code"""
    pass

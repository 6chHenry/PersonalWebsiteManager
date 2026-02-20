# -*- coding: utf-8 -*-
"""
Git Commit Dialog - Selective commit with file checklist
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
    QPushButton, QLabel, QLineEdit, QTextEdit, 
    QListWidget, QListWidgetItem, QScrollArea, QWidget,
    QMessageBox, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt
from config import COLORS


class GitCommitDialog(QDialog):
    """Dialog for selective git commit and push"""
    
    def __init__(self, git_manager, file_manager, parent=None):
        super().__init__(parent)
        
        self.git_manager = git_manager
        self.file_manager = file_manager
        self.selected_files = []
        
        self.init_ui()
        self.load_modified_files()
    
    def init_ui(self):
        self.setWindowTitle("📝 Git 提交")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📝 Git 提交管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; padding: 10px;")
        layout.addWidget(title)
        
        # Splitter for files and message
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Files section
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        files_layout.setContentsMargins(0, 0, 0, 0)
        
        files_label = QLabel("📁 修改的文件（勾选要提交的文件）：")
        files_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CCCCCC;")
        files_layout.addWidget(files_label)
        
        # Select all checkbox
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all)
        files_layout.addWidget(self.select_all_checkbox)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
            }}
        """)
        files_layout.addWidget(self.file_list)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 刷新文件列表")
        refresh_btn.clicked.connect(self.load_modified_files)
        files_layout.addWidget(refresh_btn)
        
        splitter.addWidget(files_widget)
        
        # Commit message section
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        message_label = QLabel("✏️ 提交信息：")
        message_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CCCCCC;")
        message_layout.addWidget(message_label)
        
        # Quick commit message buttons
        quick_layout = QHBoxLayout()
        
        quick_messages = [
            ("📝 更新文档", "更新文档"),
            ("✨ 添加新内容", "添加新内容"),
            ("🔧 修复问题", "修复问题"),
            ("🎨 优化格式", "优化格式"),
        ]
        
        for btn_text, msg_text in quick_messages:
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, m=msg_text: self.set_commit_message(m))
            quick_layout.addWidget(btn)
        
        message_layout.addLayout(quick_layout)
        
        # Commit message input
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("请输入提交信息...")
        self.message_edit.setMaximumHeight(100)
        self.message_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        message_layout.addWidget(self.message_edit)
        
        # Push options
        push_group = QGroupBox("推送选项")
        push_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        push_layout = QVBoxLayout(push_group)
        
        self.push_checkbox = QCheckBox("推送到远程仓库 (origin/main)")
        self.push_checkbox.setChecked(True)
        push_layout.addWidget(self.push_checkbox)
        
        self.force_checkbox = QCheckBox("强制推送 (--force)")
        self.force_checkbox.setChecked(False)
        push_layout.addWidget(self.force_checkbox)
        
        message_layout.addWidget(push_group)
        
        splitter.addWidget(message_widget)
        splitter.setSizes([300, 200])
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        commit_btn = QPushButton("✅ 提交")
        commit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }}
        """)
        commit_btn.clicked.connect(self.commit)
        button_layout.addWidget(commit_btn)
        
        commit_push_btn = QPushButton("🚀 提交并推送")
        commit_push_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6C5CE7;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }}
        """)
        commit_push_btn.clicked.connect(self.commit_and_push)
        button_layout.addWidget(commit_push_btn)
        
        layout.addLayout(button_layout)
    
    def load_modified_files(self):
        """Load modified files from git status"""
        self.file_list.clear()
        
        if not self.git_manager.is_repo_valid():
            return
        
        try:
            # Get modified and untracked files
            modified = self.git_manager.get_modified_files()
            
            for file_path in modified:
                item = QListWidgetItem()
                checkbox = QCheckBox(file_path)
                checkbox.setStyleSheet("color: #CCCCCC; padding: 3px;")
                
                # Determine file status
                try:
                    full_path = os.path.join(self.git_manager.repo_path, file_path)
                    if os.path.exists(full_path):
                        # Check if it's modified or new
                        if file_path in self.git_manager.repo.untracked_files:
                            checkbox.setText(f"[新] {file_path}")
                            checkbox.setStyleSheet("color: #4EC9B0; padding: 3px;")  # Green for new
                        else:
                            checkbox.setText(f"[改] {file_path}")
                            checkbox.setStyleSheet("color: #DCDCAA; padding: 3px;")  # Yellow for modified
                except:
                    pass
                
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, checkbox)
            
            if not modified:
                item = QListWidgetItem("没有修改的文件")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.file_list.addItem(item)
        
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法获取文件列表: {str(e)}")
    
    def on_select_all(self, state):
        """Select or deselect all files"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            checkbox = self.file_list.itemWidget(item)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(state == Qt.CheckState.Checked.value)
    
    def set_commit_message(self, message):
        """Set commit message from quick button"""
        self.message_edit.setText(message)
    
    def get_selected_files(self):
        """Get list of selected files"""
        selected = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            checkbox = self.file_list.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                # Remove status prefix [新] or [改]
                text = checkbox.text()
                if text.startswith("["):
                    text = text[4:]  # Remove "[X] " prefix
                selected.append(text)
        return selected
    
    def commit(self):
        """Commit selected files"""
        self._do_commit(push=False)
    
    def commit_and_push(self):
        """Commit and push selected files"""
        should_push = self.push_checkbox.isChecked()
        self._do_commit(push=should_push)
    
    def _do_commit(self, push=False):
        """Execute commit (and optionally push)"""
        selected_files = self.get_selected_files()
        
        if not selected_files:
            QMessageBox.warning(self, "错误", "请至少选择一个文件")
            return
        
        message = self.message_edit.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "错误", "请输入提交信息")
            return
        
        try:
            # Stage selected files
            for file_path in selected_files:
                full_path = os.path.join(self.git_manager.repo_path, file_path)
                if os.path.exists(full_path):
                    self.git_manager.repo.git.add(file_path)
            
            # Commit
            self.git_manager.repo.index.commit(message)
            
            if push:
                force = self.force_checkbox.isChecked()
                success, msg = self.git_manager.push_to_remote("origin", "main", force=force)
                
                if success:
                    QMessageBox.information(self, "成功", f"已提交 {len(selected_files)} 个文件并推送到 origin/main")
                    self.accept()
                else:
                    QMessageBox.warning(self, "推送失败", msg)
            else:
                QMessageBox.information(self, "成功", f"已提交 {len(selected_files)} 个文件")
                self.accept()
        
        except Exception as e:
            QMessageBox.warning(self, "错误", f"提交失败: {str(e)}")

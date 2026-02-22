# -*- coding: utf-8 -*-
"""
Directory Tree Widget - Shows file/folder hierarchy
"""

import os
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, 
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from config import COLORS, SIDEBAR_FONT_SIZE


class DirectoryTree(QTreeWidget):
    """Directory tree widget for file browsing"""
    
    file_selected = pyqtSignal(str)
    directory_changed = pyqtSignal(str)
    image_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.root_path = None
        self.current_path = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setHeaderHidden(True)
        self.setIndentation(16)
        self.setAnimated(True)
        
        font = QFont()
        font.setPointSize(SIDEBAR_FONT_SIZE)
        font.setFamily("霞鹜文楷, Inter, Microsoft YaHei, sans-serif")
        self.setFont(font)
        
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {COLORS["sidebar_bg"]};
                color: {COLORS["text_primary"]};
                border: none;
                outline: none;
                padding: 4px;
            }}
            
            QTreeWidget::item {{
                padding: 5px 8px;
                border-radius: 4px;
                margin: 1px 0px;
            }}
            
            QTreeWidget::item:hover {{
                background-color: {COLORS["sidebar_item_hover"]};
            }}
            
            QTreeWidget::item:selected {{
                background-color: {COLORS["accent"]};
                color: {COLORS["btn_primary_text"]};
            }}
            
            QTreeWidget::item:selected:!active {{
                background-color: {COLORS["sidebar_item_active"]};
            }}
            
            QTreeWidget::branch {{
                background-color: transparent;
            }}
            
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM3MTcxN2EiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTkgMThsNi02LTYtNiIvPjwvc3ZnPg==);
            }}
            
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM3MTcxN2EiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTYgOWw2IDYgNi02Ii8+PC9zdmc+);
            }}
            
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {COLORS["border"]};
                border-radius: 3px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {COLORS["accent"]};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.itemClicked.connect(self.on_item_clicked)
    
    def set_root_path(self, path):
        """Set the root path for the tree"""
        self.root_path = path
        self.current_path = path
        self.refresh()
    
    def refresh(self):
        """Refresh the tree - expand to level 2 by default (3 levels total)"""
        self.clear()

        if not self.root_path or not os.path.exists(self.root_path):
            return

        root_name = os.path.basename(self.root_path)
        root_item = QTreeWidgetItem([root_name])
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_path)
        root_item.setData(0, Qt.ItemDataRole.UserRole + 1, True)

        self.addTopLevelItem(root_item)
        root_item.setExpanded(True)

        self.populate_item(root_item, self.root_path, current_level=0, max_expand_level=1)
    
    def populate_item(self, parent_item, parent_path, current_level=0, max_expand_level=2):
        """Populate tree items with depth control"""
        try:
            items = []
            for item_name in os.listdir(parent_path):
                if item_name == '.git':
                    continue

                item_path = os.path.join(parent_path, item_name)
                is_dir = os.path.isdir(item_path)

                image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')

                if not is_dir and not item_name.endswith('.md') and not item_name.lower().endswith(image_extensions):
                    continue

                if is_dir and not item_name.endswith('.assets'):
                    has_content = any(
                        f.endswith('.md') or f.endswith('.assets') or f.lower().endswith(image_extensions)
                        for f in os.listdir(item_path)
                    )
                    if not has_content and item_name != 'docs':
                        continue

                item = QTreeWidgetItem([item_name])
                item.setData(0, Qt.ItemDataRole.UserRole, item_path)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, is_dir)

                items.append((item, item_path, is_dir, item_name))

            items.sort(key=lambda x: (not x[2], x[1].lower()))

            for item, item_path, is_dir, name in items:
                parent_item.addChild(item)

                if is_dir:
                    # Only expand if within the depth limit (levels 0, 1, 2)
                    if current_level < max_expand_level and not name.endswith('.assets'):
                        item.setExpanded(True)
                    self.populate_item(item, item_path, current_level + 1, max_expand_level)

        except PermissionError:
            pass
    
    def on_item_clicked(self, item, column):
        """Handle item click"""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        is_dir = item.data(0, Qt.ItemDataRole.UserRole + 1)
        
        if is_dir:
            self.current_path = path
            self.directory_changed.emit(path)
        else:
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')
            if path.lower().endswith(image_extensions):
                self.image_selected.emit(path)
            else:
                self.file_selected.emit(path)
    
    def get_current_path(self):
        """Get current selected path"""
        current_item = self.currentItem()
        
        if current_item:
            path = current_item.data(0, Qt.ItemDataRole.UserRole)
            is_dir = current_item.data(0, Qt.ItemDataRole.UserRole + 1)
            
            if is_dir:
                return path
            else:
                return os.path.dirname(path)
        
        return self.root_path or ""
    
    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        item = self.itemAt(position)
        if not item:
            return
        
        path = item.data(0, Qt.ItemDataRole.UserRole)
        is_dir = item.data(0, Qt.ItemDataRole.UserRole + 1)
        
        if is_dir:
            new_file_action = QAction("新建文件", self)
            new_file_action.triggered.connect(lambda: self.create_file_in_dir(path))
            menu.addAction(new_file_action)
            
            new_folder_action = QAction("新建文件夹", self)
            new_folder_action.triggered.connect(lambda: self.create_folder_in_dir(path))
            menu.addAction(new_folder_action)
            
            menu.addSeparator()
        
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self.rename_item(item))
        menu.addAction(rename_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_item(item))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def create_file_in_dir(self, dir_path):
        """Create a new file in the directory"""
        file_name, ok = QInputDialog.getText(
            self, "新建文件", "请输入文件名（不含扩展名）:"
        )
        
        if ok and file_name:
            if not file_name.endswith('.md'):
                file_name += '.md'
            
            file_path = os.path.join(dir_path, file_name)
            
            if os.path.exists(file_path):
                QMessageBox.warning(self, "文件已存在", "该文件已存在！")
                return
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("# " + file_name[:-3] + "\n\n")
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "创建失败", str(e))
    
    def create_folder_in_dir(self, dir_path):
        """Create a new folder in the directory"""
        folder_name, ok = QInputDialog.getText(
            self, "新建文件夹", "请输入文件夹名称:"
        )
        
        if ok and folder_name:
            folder_path = os.path.join(dir_path, folder_name)
            
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "创建失败", str(e))
    
    def rename_item(self, item):
        """Rename an item"""
        old_name = item.text(0)
        new_name, ok = QInputDialog.getText(
            self, "重命名", "请输入新名称:", text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            old_path = item.data(0, Qt.ItemDataRole.UserRole)
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            try:
                os.rename(old_path, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "重命名失败", str(e))
    
    def delete_item(self, item):
        """Delete an item"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个文件/文件夹吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    import shutil
                    shutil.rmtree(path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "删除失败", str(e))

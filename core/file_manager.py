# -*- coding: utf-8 -*-
"""
File Manager - Handles file operations
"""

import os
import shutil
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class FileManager(QObject):
    """Manages file operations"""
    
    file_saved = pyqtSignal(str)
    file_created = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_path = None
    
    def set_root_path(self, path):
        """Set the root path for file operations"""
        self.root_path = path
    
    def list_directory(self, path=None):
        """List contents of a directory"""
        if path is None:
            path = self.root_path
        
        if not path or not os.path.exists(path):
            return []
        
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                # Skip .git directory
                if item == ".git":
                    continue
                
                # Handle .assets folders (Typora style)
                if is_dir and item.endswith(".assets"):
                    items.append({
                        "name": item,
                        "path": item_path,
                        "is_dir": True,
                        "is_assets": True
                    })
                elif is_dir:
                    items.append({
                        "name": item,
                        "path": item_path,
                        "is_dir": True,
                        "is_assets": False
                    })
                elif item.endswith((".md", ".markdown")):
                    items.append({
                        "name": item,
                        "path": item_path,
                        "is_dir": False,
                        "is_assets": False
                    })
            
            # Sort: directories first, then files, alphabetically
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            return items
        except Exception as e:
            self.error_occurred.emit(f"Error listing directory: {str(e)}")
            return []
    
    def read_file(self, file_path):
        """Read content of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.error_occurred.emit(f"Error reading file: {str(e)}")
            return ""
    
    def write_file(self, file_path, content):
        """Write content to a file"""
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(file_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.file_saved.emit(file_path)
            return True, "File saved successfully"
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def create_file(self, file_path, content=""):
        """Create a new file"""
        try:
            parent_dir = os.path.dirname(file_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.file_created.emit(file_path)
            return True, "File created successfully"
        except Exception as e:
            error_msg = f"Error creating file: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def create_directory(self, dir_path):
        """Create a new directory"""
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            return True, "Directory created successfully"
        except Exception as e:
            error_msg = f"Error creating directory: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def delete_file(self, file_path):
        """Delete a file"""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            return True, "Deleted successfully"
        except Exception as e:
            error_msg = f"Error deleting: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def rename_file(self, old_path, new_path):
        """Rename a file or directory"""
        try:
            os.rename(old_path, new_path)
            return True, "Renamed successfully"
        except Exception as e:
            error_msg = f"Error renaming: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def create_assets_folder(self, md_file_path):
        """Create a .assets folder next to the markdown file"""
        base_path = md_file_path.rsplit('.', 1)[0]
        assets_path = base_path + ".assets"
        
        if not os.path.exists(assets_path):
            return self.create_directory(assets_path)
        return True, "Assets folder already exists"
    
    def get_relative_path(self, absolute_path):
        """Get path relative to root"""
        if not self.root_path:
            return absolute_path
        
        try:
            return os.path.relpath(absolute_path, self.root_path)
        except ValueError:
            return absolute_path
    
    def get_absolute_path(self, relative_path):
        """Get absolute path from relative"""
        if not self.root_path:
            return relative_path
        return os.path.join(self.root_path, relative_path)

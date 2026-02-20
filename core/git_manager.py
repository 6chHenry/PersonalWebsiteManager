# -*- coding: utf-8 -*-
"""
Git Manager - Handles all Git operations
"""

import os
from pathlib import Path
from git import Repo, GitCommandError
from PyQt6.QtCore import QObject, pyqtSignal


class GitManager(QObject):
    """Manages Git operations for the repository"""
    
    status_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = None
        self.repo_path = None
    
    def clone_repository(self, url, path):
        """Clone a GitHub repository to local path"""
        try:
            self.status_changed.emit("Cloning repository...")
            self.repo = Repo.clone_from(url, path)
            self.repo_path = path
            self.status_changed.emit("Repository cloned successfully")
            return True, "Repository cloned successfully"
        except GitCommandError as e:
            error_msg = f"Failed to clone repository: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def open_repository(self, path):
        """Open an existing local repository"""
        try:
            if not os.path.exists(path):
                return False, f"Path does not exist: {path}"
            
            self.repo = Repo(path)
            self.repo_path = path
            return True, "Repository opened successfully"
        except Exception as e:
            return False, f"Failed to open repository: {str(e)}"
    
    def get_status(self):
        """Get current repository status"""
        if not self.repo:
            return None
        
        try:
            status = self.repo.git.status()
            return status
        except Exception as e:
            return f"Error getting status: {str(e)}"
    
    def get_modified_files(self):
        """Get list of modified files"""
        if not self.repo:
            return []
        
        modified = []
        try:
            # Get modified files in working tree (not staged)
            # Use None to compare working tree with index
            for item in self.repo.index.diff(None):
                modified.append(item.a_path)
            
            # Get untracked files
            for item in self.repo.untracked_files:
                modified.append(item)
            
            return modified
        except Exception as e:
            print(f"Error getting modified files: {e}")
            return []
    
    def commit_changes(self, message):
        """Commit all changes"""
        if not self.repo:
            return False, "No repository opened"
        
        try:
            self.status_changed.emit("Staging changes...")
            self.repo.git.add(A=True)
            
            self.status_changed.emit("Committing changes...")
            self.repo.index.commit(message)
            
            self.status_changed.emit("Changes committed successfully")
            return True, "Changes committed successfully"
        except Exception as e:
            error_msg = f"Failed to commit: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def push_to_remote(self, remote_name="origin", branch="main", force=False):
        """Push changes to remote repository"""
        if not self.repo:
            return False, "No repository opened"
        
        try:
            self.status_changed.emit(f"Pushing to {remote_name}/{branch}...")
            origin = self.repo.remote(remote_name)
            
            # Fix: use refspec instead of branch parameter
            refspec = f"HEAD:{branch}"
            if force:
                origin.push(refspec, force=True)
            else:
                origin.push(refspec)
            
            self.status_changed.emit("Pushed successfully")
            return True, "Pushed successfully"
        except GitCommandError as e:
            error_msg = f"Failed to push: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error pushing: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def pull_from_remote(self, remote_name="origin", branch="main"):
        """Pull changes from remote repository"""
        if not self.repo:
            return False, "No repository opened"
        
        try:
            self.status_changed.emit(f"Pulling from {remote_name}/{branch}...")
            origin = self.repo.remote(remote_name)
            origin.pull(branch=branch)
            
            self.status_changed.emit("Pulled successfully")
            return True, "Pulled successfully"
        except Exception as e:
            error_msg = f"Failed to pull: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False, error_msg
    
    def get_current_branch(self):
        """Get current branch name"""
        if not self.repo:
            return None
        return self.repo.active_branch.name
    
    def is_repo_valid(self):
        """Check if repository is valid"""
        return self.repo is not None and self.repo_path is not None

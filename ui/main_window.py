# -*- coding: utf-8 -*-
"""
Main Window - Primary application window
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QMessageBox, QFileDialog, QInputDialog, QDialog,
    QMenuBar, QMenu, QStatusBar, QToolButton, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QTextCursor, QIcon

from ui.directory_tree import DirectoryTree
from ui.editor import MarkdownEditor
from ui.preview import MarkdownPreview
from ui.clone_dialog import CloneDialog
from ui.mind_map import MindMapWidget
from config import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT,
    SIDEBAR_WIDTH, COLORS, DEFAULT_REPO_URL, DEFAULT_LOCAL_REPO,
    FONT_FAMILY_CN, FONT_FAMILY_EN, EDITOR_FONT_SIZE, SIDEBAR_FONT_SIZE
)
from core.git_manager import GitManager
from core.file_manager import FileManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.git_manager = GitManager()
        self.file_manager = FileManager()
        
        self.git_manager.status_changed.connect(self.on_git_status_changed)
        self.git_manager.error_occurred.connect(self.on_git_error)
        
        self.current_file_path = None
        self.current_file_modified = False
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)

        self.mind_map_in_sidebar = False
        
        self.init_ui()
        self.apply_styles()
        self.load_config()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.sidebar = self.create_sidebar()
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.setSizes([SIDEBAR_WIDTH, WINDOW_WIDTH - SIDEBAR_WIDTH])
        
        self.content_container = self.create_content_area()
        self.main_splitter.addWidget(self.content_container)
        
        main_layout.addWidget(self.main_splitter, 1)
        
        self.setCentralWidget(central_widget)
        
        self.create_menu_bar()
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                border-top: 1px solid {COLORS['border']};
                padding: 4px 10px;
            }}
        """)
        self.setStatusBar(self.status_bar)
    
    def create_content_area(self):
        """Create content area with editor and preview"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = self.create_content_header()
        layout.addWidget(header)
        
        self.content_stack = QStackedWidget()
        
        self.editor_preview_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.editor = MarkdownEditor()
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor_preview_splitter.addWidget(self.editor)
        
        self.preview = MarkdownPreview()
        self.editor_preview_splitter.addWidget(self.preview)
        
        half_width = WINDOW_WIDTH - SIDEBAR_WIDTH
        self.editor_preview_splitter.setSizes([half_width // 2, half_width // 2])
        
        self.content_stack.addWidget(self.editor_preview_splitter)
        
        from ui.mind_map import MindMapWidget
        self.mind_map_full = MindMapWidget()
        self.mind_map_full.file_selected.connect(self.on_mind_map_file_selected)
        self.mind_map_full.directory_changed.connect(self.on_directory_changed)
        self.mind_map_full.expand_requested.connect(self.show_mind_map_view)
        self.content_stack.addWidget(self.mind_map_full)
        
        layout.addWidget(self.content_stack, 1)
        
        return container
    
    def create_content_header(self):
        """Create content area header"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)
        header_layout.setSpacing(8)
        
        from PyQt6.QtWidgets import QLabel
        
        self.file_name_label = QLabel("未选择文件")
        self.file_name_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        header_layout.addWidget(self.file_name_label)
        
        header_layout.addStretch()

        return header
    
    def create_menu_bar(self):
        """Create menu bar"""
        menu_bar = QMenuBar()
        menu_bar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                border-bottom: 1px solid {COLORS['border']};
                font-size: 13px;
                padding: 2px;
            }}
            QMenuBar::item {{
                padding: 6px 12px;
                background-color: transparent;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['text_primary']};
            }}
            QMenu {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                font-size: 13px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 30px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['accent']};
                color: {COLORS['btn_primary_text']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {COLORS['border']};
                margin: 4px 8px;
            }}
        """)
        
        file_menu = QMenu("文件", self)
        
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        open_repo_action = QAction("打开本地仓库...", self)
        open_repo_action.triggered.connect(self.open_repository)
        file_menu.addAction(open_repo_action)
        
        clone_action = QAction("克隆仓库...", self)
        clone_action.triggered.connect(self.show_clone_dialog)
        file_menu.addAction(clone_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        menu_bar.addMenu(file_menu)
        
        edit_menu = QMenu("编辑", self)
        
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("剪切", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        search_action = QAction("搜索文档内容...", self)
        search_action.setShortcut(QKeySequence("Ctrl+Shift+F"))
        search_action.triggered.connect(self.show_search_dialog)
        edit_menu.addAction(search_action)
        
        menu_bar.addMenu(edit_menu)
        
        git_menu = QMenu("Git", self)
        
        commit_action = QAction("提交更改", self)
        commit_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        commit_action.triggered.connect(self.commit_changes)
        git_menu.addAction(commit_action)
        
        push_action = QAction("推送到远程", self)
        push_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        push_action.triggered.connect(self.push_to_remote)
        git_menu.addAction(push_action)
        
        pull_action = QAction("从远程拉取", self)
        pull_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        pull_action.triggered.connect(self.pull_from_remote)
        git_menu.addAction(pull_action)
        
        git_menu.addSeparator()
        
        view_status_action = QAction("查看状态", self)
        view_status_action.triggered.connect(self.view_git_status)
        git_menu.addAction(view_status_action)
        
        menu_bar.addMenu(git_menu)
        
        mkdocs_menu = QMenu("MkDocs", self)
        
        edit_config_action = QAction("编辑 mkdocs.yml 配置", self)
        edit_config_action.triggered.connect(self.edit_mkdocs_config)
        mkdocs_menu.addAction(edit_config_action)
        
        open_docs_action = QAction("打开 docs 文件夹", self)
        open_docs_action.triggered.connect(self.open_docs_folder)
        mkdocs_menu.addAction(open_docs_action)
        
        mkdocs_menu.addSeparator()
        
        build_action = QAction("构建网站", self)
        build_action.triggered.connect(self.build_site)
        mkdocs_menu.addAction(build_action)
        
        serve_action = QAction("本地预览", self)
        serve_action.triggered.connect(self.serve_site)
        mkdocs_menu.addAction(serve_action)
        
        deploy_action = QAction("部署到GitHub", self)
        deploy_action.triggered.connect(self.deploy_site)
        mkdocs_menu.addAction(deploy_action)
        
        menu_bar.addMenu(mkdocs_menu)

        self.setMenuBar(menu_bar)

    def create_sidebar(self):
        """Create the sidebar with directory tree and actions"""
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {COLORS["sidebar_bg"]};
                border-right: 1px solid {COLORS["border"]};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["sidebar_header"]};
                border-bottom: 1px solid {COLORS["border"]};
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 10)
        
        from PyQt6.QtWidgets import QLabel
        title = QLabel("文件目录")
        title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        header_layout.addWidget(title)
        
        sidebar_layout.addWidget(header)
        
        self.view_toggle_container = QWidget()
        self.view_toggle_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['sidebar_header']};
                padding: 4px 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        toggle_layout = QHBoxLayout(self.view_toggle_container)
        toggle_layout.setContentsMargins(8, 4, 8, 4)
        
        self.tree_view_btn = QToolButton()
        self.tree_view_btn.setText("目录")
        self.tree_view_btn.setCheckable(True)
        self.tree_view_btn.setChecked(True)
        self.tree_view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.mind_map_btn = QToolButton()
        self.mind_map_btn.setText("导图")
        self.mind_map_btn.setCheckable(True)
        self.mind_map_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        toggle_style = f"""
            QToolButton {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }}
            QToolButton:checked {{
                background-color: {COLORS['surface_active']};
                color: {COLORS['accent']};
            }}
            QToolButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['text_primary']};
            }}
        """
        self.tree_view_btn.setStyleSheet(toggle_style)
        self.mind_map_btn.setStyleSheet(toggle_style)
        
        toggle_layout.addWidget(self.tree_view_btn)
        toggle_layout.addWidget(self.mind_map_btn)
        toggle_layout.addStretch()
        
        sidebar_layout.addWidget(self.view_toggle_container)
        
        self.stacked_view = QStackedWidget()
        self.stacked_view.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['sidebar_bg']};
            }}
        """)
        
        tree_container = QWidget()
        tree_container.setStyleSheet(f"""
            background-color: {COLORS['sidebar_bg']};
        """)
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(8, 8, 8, 8)
        
        self.directory_tree = DirectoryTree()
        self.directory_tree.file_selected.connect(self.on_file_selected)
        self.directory_tree.directory_changed.connect(self.on_directory_changed)
        self.directory_tree.image_selected.connect(self.on_image_selected)
        tree_layout.addWidget(self.directory_tree, 1)
        
        self.mind_map = MindMapWidget()
        self.mind_map.file_selected.connect(self.on_file_selected)
        self.mind_map.directory_changed.connect(self.on_directory_changed)
        self.mind_map.expand_requested.connect(self.show_mind_map_view)
        
        self.stacked_view.addWidget(tree_container)
        self.stacked_view.addWidget(self.mind_map)
        
        sidebar_layout.addWidget(self.stacked_view, 1)
        
        self.tree_view_btn.clicked.connect(self.show_tree_view)
        self.mind_map_btn.clicked.connect(self.show_mind_map_view)
        
        buttons_container = QWidget()
        buttons_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["sidebar_bg"]};
                padding: 8px;
                border-top: 1px solid {COLORS["border"]};
            }}
        """)
        button_layout = QVBoxLayout(buttons_container)
        button_layout.setSpacing(4)
        
        from PyQt6.QtWidgets import QPushButton
        
        self.new_file_btn = QPushButton("新建文件")
        self.new_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.new_file_btn)
        
        self.new_folder_btn = QPushButton("新建文件夹")
        self.new_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.new_folder_btn)
        
        self.search_btn = QPushButton("搜索内容")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.search_btn)
        
        self.add_assets_btn = QPushButton("添加资源文件夹")
        self.add_assets_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.add_assets_btn)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 4px 0;")
        button_layout.addWidget(separator)
        
        self.git_push_btn = QPushButton("Git 提交")
        self.git_push_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.git_push_btn)
        
        self.ai_chat_btn = QPushButton("AI 助手")
        self.ai_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.ai_chat_btn)
        
        sidebar_layout.addWidget(buttons_container)
        
        self.new_file_btn.clicked.connect(self.create_new_file)
        self.new_folder_btn.clicked.connect(self.create_new_folder)
        self.search_btn.clicked.connect(self.show_search_dialog)
        self.add_assets_btn.clicked.connect(self.create_assets_folder)
        self.git_push_btn.clicked.connect(self.show_git_commit_dialog)
        self.ai_chat_btn.clicked.connect(self.show_ai_chat)
        
        return sidebar_widget
    
    def show_tree_view(self):
        """Switch to tree view"""
        self.tree_view_btn.setChecked(True)
        self.mind_map_btn.setChecked(False)
        self.stacked_view.setCurrentIndex(0)
        self.content_stack.setCurrentIndex(0)
        self.mind_map_in_sidebar = False
    
    def show_mind_map_view(self):
        """Switch to mind map full screen view - takes over editor+preview area"""
        self.tree_view_btn.setChecked(False)
        self.mind_map_btn.setChecked(True)
        self.stacked_view.setCurrentIndex(1)
        self.content_stack.setCurrentIndex(1)  # Show full-screen mind map in content area
        self.mind_map_in_sidebar = False
        # Refresh mind map to ensure it's up to date
        self.mind_map_full.refresh()
    
    def show_sidebar_mind_map(self):
        """Show mind map in sidebar with editor"""
        self.mind_map_in_sidebar = True
        self.content_stack.setCurrentIndex(0)
        self.stacked_view.setCurrentIndex(1)
        self.tree_view_btn.setChecked(False)
        self.mind_map_btn.setChecked(True)
    
    def hide_sidebar_mind_map(self):
        """Hide mind map from sidebar and go back to editor only"""
        self.mind_map_in_sidebar = False
        self.stacked_view.setCurrentIndex(0)
    
    def apply_styles(self):
        """Apply custom styles to the application"""
        style = f"""
        QWidget {{
            background-color: {COLORS["background"]};
            color: {COLORS["text_primary"]};
            font-family: {FONT_FAMILY_CN};
            font-size: 13px;
        }}
        
        QMainWindow {{
            background-color: {COLORS["background"]};
        }}
        
        QPushButton {{
            background-color: {COLORS["btn_secondary"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            padding: 8px 12px;
            border-radius: 6px;
            text-align: left;
            font-size: 13px;
            font-family: {FONT_FAMILY_CN};
        }}
        
        QPushButton:hover {{
            background-color: {COLORS["btn_secondary_hover"]};
        }}
        
        QPushButton:pressed {{
            background-color: {COLORS["surface_active"]};
        }}
        
        QSplitter::handle {{
            background-color: {COLORS["border"]};
            width: 1px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {COLORS["accent"]};
        }}
        
        QScrollBar:vertical {{
            background: {COLORS["surface"]};
            width: 10px;
            border: none;
            border-radius: 5px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {COLORS["border"]};
            border-radius: 4px;
            min-height: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {COLORS["accent"]};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background: {COLORS["surface"]};
            height: 10px;
            border: none;
            border-radius: 5px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {COLORS["border"]};
            border-radius: 4px;
            min-width: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS["accent"]};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}
        
        QMenu {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 25px;
            border-radius: 4px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background-color: {COLORS["accent"]};
            color: {COLORS["btn_primary_text"]};
        }}
        
        QMenu::separator {{
            height: 1px;
            background: {COLORS["border"]};
            margin: 4px 10px;
        }}
        
        QMenuBar {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_secondary"]};
            border-bottom: 1px solid {COLORS["border"]};
            padding: 2px;
        }}
        
        QMenuBar::item {{
            padding: 6px 10px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {COLORS["surface_hover"]};
            color: {COLORS["text_primary"]};
        }}
        
        QStatusBar {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_secondary"]};
            border-top: 1px solid {COLORS["border"]};
            padding: 4px 10px;
        }}
        
        QToolTip {{
            background-color: {COLORS["surface_active"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 12px;
        }}
        
        QLineEdit {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 13px;
        }}
        
        QLineEdit:focus {{
            border-color: {COLORS["accent"]};
        }}
        
        QTextEdit {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 8px;
        }}
        
        QComboBox {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
        }}
        
        QComboBox:hover {{
            border-color: {COLORS["accent"]};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]};
            selection-background-color: {COLORS["accent"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 2px;
        }}
        """
        self.setStyleSheet(style)
    
    def load_config(self):
        """Load configuration and initialize repository"""
        if os.path.exists(DEFAULT_LOCAL_REPO):
            self.open_local_repository(DEFAULT_LOCAL_REPO)
        else:
            self.show_clone_dialog()
    
    def show_clone_dialog(self):
        """Show dialog to clone repository"""
        dialog = CloneDialog(self)
        dialog.repo_url_changed.connect(self.on_repo_url_changed)
        dialog.clone_requested.connect(self.on_clone_requested)
        dialog.exec()
    
    def on_repo_url_changed(self, url):
        """Handle repository URL change"""
        pass
    
    def on_clone_requested(self, url, path):
        """Handle clone request"""
        success, message = self.git_manager.clone_repository(url, path)
        
        if success:
            self.open_local_repository(path)
        else:
            QMessageBox.warning(self, "克隆失败", message)
    
    def open_local_repository(self, path):
        """Open a local repository"""
        success, message = self.git_manager.open_repository(path)
        
        if success:
            self.file_manager.set_root_path(path)
            self.directory_tree.set_root_path(path)
            self.mind_map.set_root_path(path)
            self.mind_map_full.set_root_path(path)
            self.setWindowTitle(f"{APP_NAME} - {path}")
        else:
            QMessageBox.warning(self, "打开失败", message)
    
    def on_file_selected(self, file_path):
        """Handle file selection"""
        if self.current_file_modified:
            reply = QMessageBox.question(
                self, "保存更改",
                "当前文件有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.load_file(file_path)
    
    def on_mind_map_file_selected(self, file_path):
        """Handle file selection from mind map - switch to hybrid layout"""
        if self.current_file_modified:
            reply = QMessageBox.question(
                self, "保存更改",
                "当前文件有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.load_file(file_path)
        self.show_sidebar_mind_map()
    
    def load_file(self, file_path):
        """Load a file into the editor"""
        if not os.path.exists(file_path):
            return
        
        content = self.file_manager.read_file(file_path)
        self.editor.setPlainText(content)
        self.current_file_path = file_path
        self.current_file_modified = False
        
        base_path = os.path.dirname(file_path)
        self.preview.update_preview(content, base_path)
        
        file_name = os.path.basename(file_path)
        self.file_name_label.setText(file_name)
        
        self.auto_save_timer.start(30000)
    
    def on_text_changed(self):
        """Handle text changes in editor"""
        self.current_file_modified = True
        content = self.editor.toPlainText()
        base_path = os.path.dirname(self.current_file_path) if self.current_file_path else None
        self.preview.update_preview(content, base_path)
        
        if self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            if self.current_file_modified:
                self.file_name_label.setText(f"{file_name} •")
            else:
                self.file_name_label.setText(file_name)
    
    def on_directory_changed(self, directory_path):
        """Handle directory change"""
        pass
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        self.preview.show_image(image_path)
    
    def create_new_file(self):
        """Create a new markdown file"""
        current_path = self.directory_tree.get_current_path()
        
        file_name, ok = QInputDialog.getText(
            self, "新建文件", "请输入文件名（不含扩展名）:"
        )
        
        if ok and file_name:
            if not file_name.endswith('.md'):
                file_name += '.md'
            
            file_path = os.path.join(current_path, file_name)
            
            if os.path.exists(file_path):
                QMessageBox.warning(self, "文件已存在", "该文件已存在！")
                return
            
            success, message = self.file_manager.create_file(file_path, "# " + file_name[:-3] + "\n\n")
            
            if success:
                self.directory_tree.refresh()
                self.load_file(file_path)
            else:
                QMessageBox.warning(self, "创建失败", message)
    
    def create_new_folder(self):
        """Create a new folder"""
        current_path = self.directory_tree.get_current_path()
        
        folder_name, ok = QInputDialog.getText(
            self, "新建文件夹", "请输入文件夹名称:"
        )
        
        if ok and folder_name:
            folder_path = os.path.join(current_path, folder_name)
            
            success, message = self.file_manager.create_directory(folder_path)
            
            if success:
                self.directory_tree.refresh()
            else:
                QMessageBox.warning(self, "创建失败", message)
    
    def create_assets_folder(self):
        """Create a .assets folder for the current file"""
        if not self.current_file_path:
            QMessageBox.information(self, "提示", "请先选择一个Markdown文件")
            return
        
        success, message = self.file_manager.create_assets_folder(self.current_file_path)
        
        if success:
            self.directory_tree.refresh()
            QMessageBox.information(self, "成功", "资源文件夹已创建")
        else:
            QMessageBox.warning(self, "失败", message)
    
    def save_current_file(self):
        """Save the current file"""
        if not self.current_file_path:
            return
        
        content = self.editor.toPlainText()
        success, message = self.file_manager.write_file(self.current_file_path, content)
        
        if success:
            self.current_file_modified = False
            if self.current_file_path:
                file_name = os.path.basename(self.current_file_path)
                self.file_name_label.setText(file_name)
        else:
            QMessageBox.warning(self, "保存失败", message)
    
    def auto_save(self):
        """Auto-save current file"""
        if self.current_file_path and self.current_file_modified:
            self.save_current_file()
    
    def closeEvent(self, a0):
        """Handle window close event"""
        if self.current_file_modified:
            reply = QMessageBox.question(
                self, "保存更改",
                "当前文件有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
                a0.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                a0.accept()
            else:
                a0.ignore()
        else:
            a0.accept()
    
    def on_git_status_changed(self, message):
        """Handle Git status change"""
        self.status_bar.showMessage(message)
    
    def on_git_error(self, error):
        """Handle Git error"""
        QMessageBox.warning(self, "Git错误", error)
    
    def save_as(self):
        """Save file with a new name"""
        if not self.current_file_path:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", self.current_file_path, "Markdown Files (*.md)"
        )
        
        if file_path:
            content = self.editor.toPlainText()
            success, message = self.file_manager.write_file(file_path, content)
            
            if success:
                self.current_file_path = file_path
                self.current_file_modified = False
                self.directory_tree.refresh()
            else:
                QMessageBox.warning(self, "保存失败", message)
    
    def open_repository(self):
        """Open a local repository"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择仓库文件夹", os.path.expanduser("~")
        )
        
        if folder:
            self.open_local_repository(folder)
    
    def commit_changes(self):
        """Commit changes to Git"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        if self.current_file_modified:
            self.save_current_file()
        
        message, ok = QInputDialog.getText(
            self, "提交更改", "请输入提交信息:"
        )
        
        if ok and message:
            success, result = self.git_manager.commit_changes(message)
            
            if success:
                QMessageBox.information(self, "成功", "更改已提交")
            else:
                QMessageBox.warning(self, "提交失败", result)
    
    def push_to_remote(self):
        """Push changes to remote repository"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        reply = QMessageBox.question(
            self, "推送确认",
            "确定要推送到远程仓库吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, result = self.git_manager.push_to_remote()
            
            if success:
                QMessageBox.information(self, "成功", "已推送到远程仓库")
            else:
                QMessageBox.warning(self, "推送失败", result)
    
    def pull_from_remote(self):
        """Pull changes from remote repository"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        success, result = self.git_manager.pull_from_remote()
        
        if success:
            QMessageBox.information(self, "成功", "已从远程仓库拉取")
            self.directory_tree.refresh()
        else:
            QMessageBox.warning(self, "拉取失败", result)
    
    def view_git_status(self):
        """View Git status"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        status = self.git_manager.get_status()
        modified = self.git_manager.get_modified_files()
        
        if status:
            msg = f"当前分支: {self.git_manager.get_current_branch()}\n\n"
            
            if modified:
                msg += "已修改的文件:\n"
                for f in modified:
                    msg += f"  - {f}\n"
            else:
                msg += "没有修改的文件"
            
            QMessageBox.information(self, "Git状态", msg)
        else:
            QMessageBox.warning(self, "错误", "无法获取Git状态")
    
    def build_site(self):
        """Build MkDocs site"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        import subprocess
        import sys
        
        repo_path = self.git_manager.repo_path
        self.status_bar.showMessage("正在构建网站...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mkdocs", "build"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", "网站构建完成！")
            else:
                QMessageBox.warning(self, "构建失败", result.stderr)
            
            self.status_bar.showMessage("")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))
            self.status_bar.showMessage("")
    
    def serve_site(self):
        """Serve MkDocs site locally"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        QMessageBox.information(
            self, "本地预览", 
            "请在终端中运行: mkdocs serve\n"
            "然后访问 http://localhost:8000"
        )
    
    def deploy_site(self):
        """Deploy site to GitHub Pages"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        reply = QMessageBox.question(
            self, "部署确认",
            "这将构建网站并推送到gh-pages分支。\n"
            "确定要继续吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.build_site()
            
            success, result = self.git_manager.commit_changes("Build and deploy to GitHub Pages")
            
            if success:
                success, result = self.git_manager.push_to_remote()
                
                if success:
                    QMessageBox.information(
                        self, "成功", 
                        "网站已部署！\n"
                        "请等待几分钟后访问"
                    )
                else:
                    QMessageBox.warning(self, "推送失败", result)
            else:
                QMessageBox.warning(self, "提交失败", result)
    
    def edit_mkdocs_config(self):
        """Edit mkdocs.yml configuration file"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        repo_path = self.git_manager.repo_path
        config_path = os.path.join(repo_path, "mkdocs.yml")
        
        if os.path.exists(config_path):
            self.load_file(config_path)
            
            content = self.editor.toPlainText()
            lines = content.split('\n')
            nav_line = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('nav:'):
                    nav_line = i
                    break
            
            if nav_line >= 0:
                cursor = self.editor.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                for _ in range(nav_line):
                    cursor.movePosition(QTextCursor.MoveOperation.Down)
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                self.editor.setTextCursor(cursor)
                self.editor.ensureCursorVisible()
        else:
            QMessageBox.warning(self, "错误", "mkdocs.yml 文件不存在")
    
    def open_docs_folder(self):
        """Open docs folder in the directory tree"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        repo_path = self.git_manager.repo_path
        docs_path = os.path.join(repo_path, "docs")
        
        if os.path.exists(docs_path):
            self.file_manager.set_root_path(docs_path)
            self.directory_tree.set_root_path(docs_path)
            self.setWindowTitle(f"{APP_NAME} - {docs_path}")
        else:
            QMessageBox.warning(self, "错误", "docs 文件夹不存在")
    
    def show_git_commit_dialog(self):
        """Show Git commit dialog with file selection"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        if self.current_file_modified:
            self.save_current_file()
        
        from ui.git_commit_dialog import GitCommitDialog
        
        dialog = GitCommitDialog(self.git_manager, self.file_manager, self)
        dialog.exec()
    
    def show_ai_chat(self):
        """Show AI chat dialog"""
        from ui.ai_chat_dialog import AIDialog
        
        if not hasattr(self, 'ai_dialog') or self.ai_dialog is None:
            self.ai_dialog = AIDialog(self)
        
        self.ai_dialog.show()
        self.ai_dialog.raise_()
        self.ai_dialog.activateWindow()
    
    def show_search_dialog(self):
        """Show search dialog to search content in markdown files"""
        if not self.git_manager.is_repo_valid():
            QMessageBox.warning(self, "错误", "请先打开一个Git仓库")
            return
        
        from ui.search_dialog import SearchDialog
        
        if not hasattr(self, 'search_dialog') or self.search_dialog is None:
            self.search_dialog = SearchDialog(self.git_manager.repo_path, self)
            self.search_dialog.jump_to_file.connect(self.jump_to_search_result)
        
        self.search_dialog.show()
        self.search_dialog.raise_()
        self.search_dialog.activateWindow()
    
    def jump_to_search_result(self, file_path, line_number):
        """Jump to search result"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", f"文件不存在: {file_path}")
            return
        
        if self.current_file_modified:
            reply = QMessageBox.question(
                self, "保存更改",
                "当前文件有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.load_file(file_path)
        
        if line_number > 0:
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(line_number - 1):
                cursor.movePosition(QTextCursor.MoveOperation.Down)
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()

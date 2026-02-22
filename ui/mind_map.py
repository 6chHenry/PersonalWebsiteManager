# -*- coding: utf-8 -*-
"""
Mind Map Widget - Visual directory structure as mind map
"""

import os
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, 
    QGraphicsTextItem, QGraphicsLineItem, QGraphicsProxyWidget,
    QWidget, QVBoxLayout, QScrollArea, QLabel, QToolButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QPen, QBrush, QPainter, QCursor, QMouseEvent, QWheelEvent
from config import COLORS


class MindMapNode(QGraphicsItem):
    """Mind map node item"""
    
    scene = None
    
    def __init__(self, text, path, is_dir=True, parent=None, level=0):
        super().__init__(parent)
        
        self.text = text
        self.path = path
        self.is_dir = is_dir
        self.is_expanded = False
        self.child_nodes = []
        self.parent_node = None
        self.level = level
        self._width = 140
        self._height = 32
        self._hovered = False
        self._selected = False
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setAcceptHoverEvents(True)
        
        if parent:
            self.level = parent.level + 1
    
    def add_child(self, node):
        node.parent_node = self
        self.child_nodes.append(node)
    
    def set_expanded(self, expanded):
        was_expanded = self.is_expanded
        self.is_expanded = expanded
        
        for child in self.child_nodes:
            child.setVisible(expanded)
            if child.is_dir and child.is_expanded:
                child.update_children_visibility()
    
    def update_children_visibility(self):
        for child in self.child_nodes:
            child.setVisible(self.is_expanded)
            if child.is_dir and child.is_expanded:
                child.update_children_visibility()
    
    def get_visible_children_count(self):
        """Get count of hidden children (for badges)"""
        if not self.is_dir:
            return 0
        count = 0
        for child in self.child_nodes:
            if not child.isVisible():
                count += 1
            if child.is_dir:
                count += child.get_visible_children_count()
        return count
    
    def boundingRect(self):
        return QRectF(-self._width // 2, -self._height // 2, self._width, self._height)
    
    def paint(self, painter, option, widget=None):
        bg_color = COLORS["accent"] if self._selected else (
            COLORS["sidebar_item_hover"] if self._hovered else COLORS["surface"]
        )
        text_color = COLORS["btn_primary_text"] if self._selected else COLORS["text_primary"]
        
        if self.is_dir:
            border_color = COLORS["accent"] if self._selected else COLORS["border"]
        else:
            border_color = COLORS["accent_pressed"] if self._selected else COLORS["text_muted"]
        
        painter.setPen(QPen(QColor(border_color), 1))
        painter.setBrush(QBrush(QColor(bg_color)))
        
        rect = self.boundingRect()
        radius = 6
        painter.drawRoundedRect(rect, radius, radius)
        
        font = QFont()
        font.setPointSize(11)
        font.setFamily("霞鹜文楷, Inter, Microsoft YaHei, sans-serif")
        painter.setFont(font)
        painter.setPen(QColor(text_color))
        
        text_rect = QRectF(-self._width // 2 + 8, -self._height // 2, self._width - 30, self._height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 
                        self.text[:12] + "..." if len(self.text) > 12 else self.text)
        
        if self.is_dir:
            hidden_count = self.get_visible_children_count()
            if hidden_count > 0:
                badge_rect = QRectF(self._width // 2 - 28, -8, 24, 16)
                painter.setBrush(QBrush(QColor(COLORS["accent"])))
                painter.setPen(QPen(QColor(COLORS["accent"]), 1))
                painter.drawRoundedRect(badge_rect, 8, 8)
                painter.setPen(QColor(COLORS["btn_primary_text"]))
                font_badge = QFont()
                font_badge.setPointSize(9)
                painter.setFont(font_badge)
                painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, str(hidden_count))
            
            indicator = "▼" if self.is_expanded else "▶"
            indicator_rect = QRectF(self._width // 2 - 18, -8, 16, 16)
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, indicator)
    
    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.update()
        super().hoverLeaveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        self._selected = True
        self.update()
        super().mouseDoubleClickEvent(event)
    
    def itemChange(self, change, value):
        return super().itemChange(change, value)


class MindMapScene(QGraphicsScene):
    """Mind map graphics scene"""
    
    node_double_clicked = pyqtSignal(str)
    node_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setSceneRect(-3000, -3000, 6000, 6000)
        self.setBackgroundBrush(QColor(COLORS["sidebar_bg"]))
        
        self.root_node = None
        self.node_map = {}
        self._last_center = QPointF(0, 0)
        
    def build_tree(self, root_path, max_depth=2):
        """Build mind map from directory structure"""
        self.clear()
        self.node_map.clear()
        
        if not root_path or not os.path.exists(root_path):
            return
        
        MindMapNode.scene = self
        
        root_name = os.path.basename(root_path)
        self.root_node = MindMapNode(root_name, root_path, is_dir=True, level=0)
        self.root_node.setPos(0, 0)
        self.addItem(self.root_node)
        self.node_map[root_path] = self.root_node
        
        self._populate_node(self.root_node, root_path, 0, max_depth)
        
        self.root_node.set_expanded(True)
        
        self._layout_tree()
    
    def _populate_node(self, parent_node, parent_path, current_depth, max_depth=2):
        """Populate child nodes"""
        try:
            items = []
            for item_name in os.listdir(parent_path):
                if item_name == '.git':
                    continue

                if item_name.endswith('.assets'):
                    continue

                item_path = os.path.join(parent_path, item_name)
                is_dir = os.path.isdir(item_path)

                image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')

                if not is_dir and not item_name.endswith('.md') and not item_name.lower().endswith(image_extensions):
                    continue

                if is_dir:
                    has_content = any(
                        f.endswith('.md') or f.lower().endswith(image_extensions)
                        for f in os.listdir(item_path)
                        if not f.endswith('.assets')
                    )
                    if not has_content and item_name != 'docs':
                        continue

                items.append((item_name, item_path, is_dir))

            items.sort(key=lambda x: (not x[2], x[0].lower()))

            for item_name, item_path, is_dir in items:
                node_level = parent_node.level + 1
                node = MindMapNode(item_name, item_path, is_dir, level=node_level)
                parent_node.add_child(node)
                self.addItem(node)
                self.node_map[item_path] = node

                node.setVisible(False)

                if is_dir:
                    self._populate_node(node, item_path, current_depth + 1, max_depth)
                    if node_level < max_depth:
                        node.set_expanded(True)

        except PermissionError:
            pass
    
    def _layout_tree(self, keep_viewport=True):
        """Layout the tree nodes with increased spacing"""
        if not self.root_node:
            return
        
        saved_center = None
        if keep_viewport and self.views():
            view = self.views()[0]
            saved_center = view.mapToScene(view.viewport().rect().center())
        
        horizontal_spacing = 220
        vertical_spacing = 60
        
        self._layout_level(self.root_node, 0, 0, horizontal_spacing, vertical_spacing)
        
        self._draw_connections(self.root_node)
        
        if saved_center:
            self.views()[0].centerOn(saved_center)
        elif self.views():
            self.views()[0].centerOn(self.root_node)
    
    def _layout_level(self, node, x, y, h_spacing, v_spacing):
        """Recursively layout nodes - top-down layout to prevent parent movement"""
        node.setPos(x, y)

        visible_children = [c for c in node.child_nodes if c.isVisible()]

        if not visible_children:
            return

        total_height = len(visible_children) * v_spacing
        start_y = y - total_height // 2 + v_spacing // 2

        for i, child in enumerate(visible_children):
            child_x = x + h_spacing
            child_y = start_y + i * v_spacing
            self._layout_level(child, child_x, child_y, h_spacing, v_spacing)
    
    def _draw_connections(self, node):
        """Draw connection lines between nodes"""
        for child in node.child_nodes:
            if not child.isVisible():
                continue
            
            line = QGraphicsLineItem()
            line.setPen(QPen(QColor(COLORS["border"]), 2))
            
            start = node.pos()
            end = child.pos()
            
            line.setLine(start.x() + 70, start.y(), end.x() - 70, end.y())
            line.setZValue(-1)
            self.addItem(line)
            
            self._draw_connections(child)
    
    def save_viewport(self):
        """Save current viewport center"""
        if self.views():
            view = self.views()[0]
            self._last_center = view.mapToScene(view.viewport().rect().center())
    
    def restore_viewport(self):
        """Restore viewport to saved center"""
        if self.views() and self._last_center:
            self.views()[0].centerOn(self._last_center)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click - keep viewport center stable during expand/collapse"""
        items = self.items(event.scenePos())
        for item in items:
            if isinstance(item, MindMapNode):
                if item.is_dir:
                    # Save current viewport center before expanding/collapsing
                    saved_center = None
                    if self.views():
                        view = self.views()[0]
                        saved_center = view.mapToScene(view.viewport().rect().center())
                    item.set_expanded(not item.is_expanded)
                    self._relayout(saved_center=saved_center)
                else:
                    self.node_double_clicked.emit(item.path)
                break
        super().mouseDoubleClickEvent(event)
    
    def mousePressEvent(self, event):
        """Handle single click"""
        items = self.items(event.scenePos())
        for item in items:
            if isinstance(item, MindMapNode):
                item._selected = True
                item.update()
                self.node_clicked.emit(item.path)
            else:
                if isinstance(item, MindMapNode):
                    item._selected = False
                    item.update()
        super().mousePressEvent(event)
    
    def _relayout(self, saved_center=None):
        """Relayout the tree after expand/collapse"""
        self._layout_tree(keep_viewport=False)

        for item in self.items():
            if isinstance(item, QGraphicsLineItem):
                self.removeItem(item)

        self._draw_connections(self.root_node)

        # Restore viewport to saved center point
        if saved_center and self.views():
            self.views()[0].centerOn(saved_center)
    
    def refresh(self):
        """Refresh the mind map"""
        if self.root_node:
            self.build_tree(self.root_node.path)


class MindMapGraphicsView(QGraphicsView):
    """Custom graphics view with pan navigation"""
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        
        self._dragging = False
        self._last_pos = QPoint()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.setStyleSheet(f"""
            QGraphicsView {{
                background-color: {COLORS['sidebar_bg']};
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['accent']};
            }}
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_pos = event.pos()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = event.pos() - self._last_pos
            self._last_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)
    
    def wheelEvent(self, event):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)
        event.accept()


class MindMapWidget(QWidget):
    """Mind map widget wrapper"""
    
    file_selected = pyqtSignal(str)
    directory_changed = pyqtSignal(str)
    expand_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.root_path = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)
        
        title = QLabel("思维导图")
        title.setStyleSheet(f"""
            font-size: 12px; 
            font-weight: 600; 
            color: {COLORS['text_secondary']};
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.expand_btn = QToolButton()
        self.expand_btn.setText("全屏")
        self.expand_btn.setToolTip("全屏查看思维导图")
        self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 11px;
            }}
            QToolButton:hover {{
                background-color: {COLORS['surface_active']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.expand_btn.clicked.connect(self.expand_requested.emit)
        header_layout.addWidget(self.expand_btn)
        
        layout.addWidget(header)
        
        self.scene = MindMapScene()
        self.view = MindMapGraphicsView(self.scene)
        
        layout.addWidget(self.view, 1)
        
        self.scene.node_double_clicked.connect(self.on_node_double_clicked)
        self.scene.node_clicked.connect(self.on_node_clicked)
    
    def set_root_path(self, path):
        """Set root path"""
        self.root_path = path
        self.scene.build_tree(path, max_depth=2)
    
    def on_node_double_clicked(self, path):
        """Handle node double click"""
        if os.path.isfile(path) and path.endswith('.md'):
            self.file_selected.emit(path)
        elif os.path.isdir(path):
            self.directory_changed.emit(path)
    
    def on_node_clicked(self, path):
        """Handle node single click"""
        if os.path.isdir(path):
            self.directory_changed.emit(path)
    
    def refresh(self):
        """Refresh the mind map"""
        if self.root_path:
            self.scene.build_tree(self.root_path, max_depth=2)
    
    def expand_all(self):
        """Expand all nodes"""
        def expand(node):
            if node.is_dir:
                node.set_expanded(True)
            for child in node.child_nodes:
                expand(child)
        
        if self.scene.root_node:
            expand(self.scene.root_node)
            self.scene._relayout()
    
    def collapse_all(self):
        """Collapse all nodes except root"""
        def collapse(node):
            for child in node.child_nodes:
                if child.is_dir:
                    child.set_expanded(False)
                collapse(child)
        
        if self.scene.root_node:
            collapse(self.scene.root_node)
            self.scene._relayout()

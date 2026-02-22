# -*- coding: utf-8 -*-
"""
AI Chat Dialog - Chat with AI to assist writing
"""

import os
import json
import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from config import COLORS


class AIChatWorker(QThread):
    """Worker thread for AI API calls with streaming support"""
    
    chunk_received = pyqtSignal(str)  # For streaming
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, api_base, model, messages):
        super().__init__()
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.messages = messages
    
    def run(self):
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": self.messages,
                "stream": True,  # Enable streaming
                "max_tokens": 2048
            }
            
            # Use stream=True for streaming response
            response = requests.post(url, headers=headers, json=data, timeout=120, stream=True)
            
            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"].get("message", response.text)
                except:
                    pass
                self.error_occurred.emit(f"API错误: {response.status_code} - {error_msg}")
                return
            
            full_content = ""
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_content += content
                                self.chunk_received.emit(content)
                        except json.JSONDecodeError:
                            continue
            
            self.response_ready.emit(full_content)
        
        except requests.exceptions.Timeout:
            self.error_occurred.emit("请求超时(120秒)，请检查网络连接或稍后重试")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("网络连接失败，请检查网络")
        except Exception as e:
            self.error_occurred.emit(f"错误: {str(e)}")


class ChatMessage(QWidget):
    """Chat message bubble with markdown support"""
    
    def __init__(self, text, is_user=True):
        super().__init__()
        self.is_user = is_user
        self.text_edit = None
        self.init_ui(text, is_user)
    
    def init_ui(self, text, is_user):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Convert markdown to HTML for AI messages
        if not is_user:
            text = self.markdown_to_html(text)
        
        # Use QTextEdit for selectable text
        self.text_edit = QTextEdit()
        self.text_edit.setHtml(text)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFrameStyle(QTextEdit.Shape.NoFrame)
        
        # Fix: prevent QTextEdit from expanding too much
        from PyQt6.QtWidgets import QSizePolicy
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.text_edit.setMaximumHeight(400)
        self.text_edit.setMinimumHeight(40)
        
        # Auto-adjust height based on content (simplified)
        doc = self.text_edit.document()
        doc.setTextWidth(500)  # Assume reasonable width
        doc_height = doc.size().height()
        # Estimate: roughly 20px per line + padding
        self.text_edit.setFixedHeight(int(min(doc_height + 30, 400)))
        
        if is_user:
            self.text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {COLORS['surface_active']};
                    color: {COLORS['text_primary']};
                    padding: 10px;
                    border-radius: 10px;
                    border: none;
                }}
            """)
        else:
            self.text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {COLORS['surface_light']};
                    color: {COLORS['text_primary']};
                    padding: 10px;
                    border-radius: 10px;
                    border: none;
                }}
            """)
        
        # Enable text selection
        self.text_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        layout.addWidget(self.text_edit)
    
    def append_text(self, text):
        """Append text to the message (for streaming)"""
        if self.is_user:
            return
        
        # Get current plain text and append
        current = self.text_edit.toPlainText()
        new_text = current + text
        
        # Convert to HTML and update
        html = self.markdown_to_html(new_text)
        self.text_edit.setHtml(html)
        
        # Adjust height
        doc = self.text_edit.document()
        doc.setTextWidth(500)
        doc_height = doc.size().height()
        self.text_edit.setFixedHeight(int(min(doc_height + 30, 400)))
    
    def markdown_to_html(self, md_text):
        """Simple markdown to HTML conversion"""
        import re
        
        html = md_text
        
        # Escape HTML entities first (but preserve existing HTML)
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        
        # Code blocks (must be first)
        html = re.sub(r'```(\w*)\n(.*?)```', r'<pre style="background-color: #16213e; padding: 10px; border-radius: 5px; overflow-x: auto;"><code>\2</code></pre>', html, flags=re.DOTALL)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code style="background-color: #2d2d30; padding: 2px 4px; border-radius: 3px;">\1</code>', html)
        
        # Bold
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h4 style="margin: 10px 0 5px 0; color: #0db5bc;">\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h3 style="margin: 10px 0 5px 0; color: #0db5bc;">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h2 style="margin: 10px 0 5px 0; color: #0db5bc;">\1</h2>', html, flags=re.MULTILINE)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color: #0db5bc;">\1</a>', html)
        
        # Lists
        html = re.sub(r'^- (.+)$', r'<li style="margin-left: 20px;">\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^\d+\. (.+)$', r'<li style="margin-left: 20px;">\1</li>', html, flags=re.MULTILINE)
        
        # Line breaks
        html = html.replace('\n', '<br>')
        
        return html


class AIDialog(QDialog):
    """AI Chat Dialog"""

    # API configurations for different providers
    API_CONFIGS = {
        "siliconflow": {
            "api_key": "sk-duaxzsivkjivevzobuyfhaoknmvezxicgpagbmfpevawrogz",
            "api_base": "https://api.siliconflow.cn/v1"
        },
        "moonshot": {
            "api_key": "sk-QzCKljCIrZevTxc5LF0nTiWIm0JxCqOCRMqEHRWFRW3l2vfl",
            "api_base": "https://api.moonshot.cn/v1"
        }
    }

    # Available models (provider, model_id, display_name)
    # free models marked with ★
    MODELS = [
        ("siliconflow", "deepseek-ai/DeepSeek-V3", "★ DeepSeek V3 (推荐)"),
        ("siliconflow", "deepseek-ai/DeepSeek-R1", "DeepSeek R1 (推理)"),
        ("siliconflow", "Qwen/Qwen3-8B", "★ Qwen3-8B"),
        ("siliconflow", "Qwen/Qwen2.5-7B-Instruct", "Qwen2.5-7B"),
        ("siliconflow", "Qwen/Qwen2.5-14B-Instruct", "Qwen2.5-14B"),
        ("siliconflow", "Qwen/Qwen2.5-32B-Instruct", "Qwen2.5-32B"),
        ("siliconflow", "Qwen/Qwen2.5-Coder-7B-Instruct", "Qwen2.5-Coder-7B"),
        ("siliconflow", "THUDM/glm-4-9b-chat", "GLM-4-9B"),
        ("siliconflow", "THUDM/GLM-Z1-9B-0414", "GLM-Z1-9B"),
        ("moonshot", "kimi-k2.5", "🌙 Kimi K2.5"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize with first model (siliconflow)
        self.current_provider = self.MODELS[0][0]
        config = self.API_CONFIGS[self.current_provider]
        self.api_key = config["api_key"]
        self.api_base = config["api_base"]
        self.model = self.MODELS[0][1]
        
        self.messages = [
            {"role": "system", "content": "你是一个有帮助的写作助手，帮助用户写作、修改文章、解答问题。请用中文回复。"}
        ]
        
        self.worker = None
        self.current_ai_message = None  # For streaming
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🤖 AI 写作助手")
        self.setMinimumSize(600, 550)
        self.setModal(False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title and model selector
        top_layout = QHBoxLayout()
        
        title = QLabel("🤖 AI 写作助手")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; padding: 5px;")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        # Model selector
        from PyQt6.QtWidgets import QComboBox
        model_label = QLabel("模型:")
        model_label.setStyleSheet("color: #CCCCCC;")
        top_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        for provider, model_id, model_name in self.MODELS:
            self.model_combo.addItem(model_name, (provider, model_id))
        self.model_combo.setFixedWidth(180)
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        top_layout.addWidget(self.model_combo)
        
        layout.addLayout(top_layout)
        
        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
            }}
        """)
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.addStretch()
        
        self.messages_scroll_content = ""  # For copying
        
        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入你的问题或请求 AI 帮你写作...")
        self.input_edit.setMaximumHeight(80)
        self.input_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                padding: 8px;
            }}
        """)
        input_layout.addWidget(self.input_edit, 1)
        
        # Send button
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedWidth(80)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['btn_secondary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['btn_secondary_hover']};
                border-color: {COLORS['border_focus']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
            }}
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        
        improve_btn = QPushButton("✏️ 改进写作")
        improve_btn.clicked.connect(lambda: self.quick_action("请帮我改进以下文章的写作质量："))
        quick_layout.addWidget(improve_btn)
        
        translate_btn = QPushButton("🌐 翻译")
        translate_btn.clicked.connect(lambda: self.quick_action("请翻译以下内容为英文："))
        quick_layout.addWidget(translate_btn)
        
        summary_btn = QPushButton("📝 总结")
        summary_btn.clicked.connect(lambda: self.quick_action("请帮我总结以下内容的要点："))
        quick_layout.addWidget(summary_btn)
        
        quick_layout.addStretch()
        
        # Copy button
        copy_btn = QPushButton("📋 复制对话")
        copy_btn.clicked.connect(self.copy_conversation)
        quick_layout.addWidget(copy_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑 清空")
        clear_btn.clicked.connect(self.clear_conversation)
        quick_layout.addWidget(clear_btn)
        
        layout.addLayout(quick_layout)
    
    def on_model_changed(self, index):
        """Handle model change - switch API config based on provider"""
        data = self.model_combo.currentData()
        if data:
            provider, model_id = data
            self.current_provider = provider
            self.model = model_id
            # Update API config for the selected provider
            config = self.API_CONFIGS[provider]
            self.api_key = config["api_key"]
            self.api_base = config["api_base"]
    
    def copy_conversation(self):
        """Copy all conversation text to clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        
        text = ""
        for msg in self.messages:
            role = "用户" if msg["role"] == "user" else "AI"
            text += f"{role}: {msg['content']}\n\n"
        
        clipboard.setText(text)
        
        # Show feedback
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "已复制", "对话内容已复制到剪贴板！")
    
    def clear_conversation(self):
        """Clear conversation history"""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空对话历史吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.messages = [
                {"role": "system", "content": "你是一个有帮助的写作助手，帮助用户写作、修改文章、解答问题。请用中文回复。"}
            ]
            # Clear UI
            while self.messages_layout.count() > 1:
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.messages_layout.insertStretch(0)
            self.messages_layout.addStretch()
    
    def quick_action(self, prefix):
        """Quick action with current editor content"""
        # Get current text from parent editor if available
        parent = self.parent()
        if parent and hasattr(parent, 'editor'):
            current_text = parent.editor.toPlainText()
            if current_text:
                self.input_edit.setText(prefix + "\n\n" + current_text[:500])
                return
        
        self.input_edit.setText(prefix)
    
    def send_message(self):
        message = self.input_edit.toPlainText().strip()
        if not message:
            return
        
        if not self.api_key:
            self.add_message("API 密钥未配置", False)
            return
        
        # Add user message
        self.messages.append({"role": "user", "content": message})
        self.add_message(message, True)
        self.input_edit.clear()
        
        # Disable send button
        self.send_btn.setEnabled(False)
        self.send_btn.setText("...")
        
        # Create placeholder for AI response (for streaming)
        self.current_ai_message = self.add_message("", False)
        
        # Start worker
        self.worker = AIChatWorker(self.api_key, self.api_base, self.model, self.messages)
        self.worker.chunk_received.connect(self.on_chunk_received)
        self.worker.response_ready.connect(self.on_response)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def on_chunk_received(self, chunk):
        """Handle streaming chunk"""
        if self.current_ai_message:
            self.current_ai_message.append_text(chunk)
            # Scroll to bottom
            sb = self.scroll_area.verticalScrollBar()
            if sb:
                sb.setValue(sb.maximum())
    
    def on_response(self, response):
        """Handle AI response complete"""
        self.messages.append({"role": "assistant", "content": response})
        self.current_ai_message = None
        
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送")
    
    def on_error(self, error):
        """Handle error"""
        if self.current_ai_message:
            self.current_ai_message.text_edit.setHtml(f"<p style='color: #ef4444;'>❌ {error}</p>")
        else:
            self.add_message(f"❌ {error}", False)
        
        self.current_ai_message = None
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送")
    
    def add_message(self, text, is_user):
        """Add message to chat"""
        # Remove stretch before adding
        self.messages_layout.removeItem(self.messages_layout.takeAt(self.messages_layout.count() - 1))
        
        msg = ChatMessage(text, is_user)
        self.messages_layout.addWidget(msg)
        
        # Add stretch back
        self.messages_layout.addStretch()
        
        # Scroll to bottom
        sb = self.scroll_area.verticalScrollBar()
        if sb:
            QTimer.singleShot(100, lambda: sb.setValue(sb.maximum()))
        
        return msg

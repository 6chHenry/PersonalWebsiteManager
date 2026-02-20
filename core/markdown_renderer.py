# -*- coding: utf-8 -*-
"""
Markdown Renderer - Converts Markdown to HTML
"""

import markdown2
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
import re
import os
import html as html_module


class MarkdownRenderer:
    """Renders Markdown to HTML"""
    
    def __init__(self):
        # Configure markdown2 with extras
        self.markdown = markdown2.Markdown(
            extras=[
                'fenced-code-blocks',
                'code-friendly',
                'tables',
                'strikeout',
                'task_list',
                'metadata',
                'nl2br',
                'smarty-pants',
                'underline',
                'header-ids',
            ]
        )
        
        # Custom CSS for syntax highlighting
        self.pygments_css = self._get_pygment_css()
        
        # Check if katex module is available
        self.katex_module = None
        try:
            import katex
            self.katex_module = katex
        except ImportError:
            pass
    
    def _get_pygment_css(self):
        """Get Pygments CSS for syntax highlighting"""
        formatter = HtmlFormatter(style='monokai')
        return formatter.get_style_defs('.highlight')
    
    def _render_latex(self, formula, display_mode=False):
        """Render LaTeX formula to HTML using KaTeX"""
        if self.katex_module:
            try:
                result = self.katex_module.render(formula, displayMode=display_mode)
                return result
            except Exception as e:
                pass
        
        # Fallback: use MathJax CDN for rendering (will be slow but works)
        escaped = html_module.escape(formula)
        if display_mode:
            return f'<div class="math-display">\\[{escaped}\\]</div>'
        return f'<span class="math-inline">\\({escaped}\\)</span>'
    
    def _process_math(self, text):
        """Process math formulas in text"""
        # Protect code blocks from math processing
        code_blocks = []
        def save_code(match):
            code_blocks.append(match.group(0))
            return f'___CODE_BLOCK_{len(code_blocks)-1}___'
        
        text = re.sub(r'```[\s\S]*?```', save_code, text)
        text = re.sub(r'`[^`]+`', save_code, text)
        
        # Process display math ($$...$$) first - handle multiline
        def replace_display(match):
            formula = match.group(1)
            return self._render_latex(formula, display_mode=True)
        
        text = re.sub(r'\$\$([\s\S]+?)\$\$', replace_display, text)
        
        # Process inline math ($...$)
        def replace_inline(match):
            formula = match.group(1)
            return self._render_latex(formula, display_mode=False)
        
        # Match $...$ but not $$...$$ and not escaped \$
        text = re.sub(r'(?<![\\$])\$(?!\$)([^\$\n]+?)\$(?!\$)', replace_inline, text)
        
        # Restore code blocks
        for i, code in enumerate(code_blocks):
            text = text.replace(f'___CODE_BLOCK_{i}___', code)
        
        return text
    
    def render(self, markdown_text, base_path=None):
        """Render Markdown text to full HTML"""
        try:
            # Process image paths before rendering
            if base_path:
                markdown_text = self._process_image_paths(markdown_text, base_path)
            
            # Process math formulas before markdown conversion
            markdown_text = self._process_math(markdown_text)
            
            # Convert markdown to HTML
            html_content = self.markdown.convert(markdown_text)
            
            # Build full HTML
            return self._build_html(html_content, base_path)
        except Exception as e:
            return self._build_html(f"<p>Error rendering markdown: {str(e)}</p>", base_path)
    
    def render_content(self, markdown_text, base_path=None):
        """Render only markdown content to HTML (body part)"""
        try:
            if base_path:
                markdown_text = self._process_image_paths(markdown_text, base_path)
            markdown_text = self._process_math(markdown_text)
            return self.markdown.convert(markdown_text)
        except Exception as e:
            return f"<p>Error rendering markdown: {str(e)}</p>"
    
    def _build_html(self, content, base_path=None):
        """Build full HTML document"""
        # KaTeX CSS for fallback MathJax rendering
        katex_css = ""
        mathjax_script = ""
        
        # Base tag for relative paths
        base_tag = ""
        if base_path:
            base_tag = f'    <base href="file:///{base_path.replace(chr(92), "/")}/" />\n'
        
        if not self.katex_module:
            # Include MathJax for rendering if katex not available
            mathjax_script = """
    <script>
        MathJax = {
            tex: {
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['\\\\[', '\\\\]']]
            }
        };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
"""
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
{base_tag}    <style>
        {self.pygments_css}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            font-size: 15px;
            line-height: 1.8;
            color: #e8e8e8;
            background-color: #1a1a2e;
            padding: 25px 40px;
            max-width: 900px;
            margin: 0 auto;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff;
            margin-top: 28px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.3;
        }}
        h1 {{ 
            font-size: 2.2em; 
            padding-bottom: 0.4em; 
            border-bottom: 2px solid #0f969c;
            background: linear-gradient(90deg, #0f969c, transparent);
            background-size: 100% 2px;
            background-position: bottom;
            background-repeat: no-repeat;
        }}
        h2 {{ 
            font-size: 1.6em; 
            padding-bottom: 0.3em; 
            border-bottom: 1px solid #2d4a6f;
        }}
        h3 {{ font-size: 1.3em; color: #0db5bc; }}
        p {{ margin-bottom: 16px; }}
        a {{ color: #0db5bc; text-decoration: none; transition: color 0.2s; }}
        a:hover {{ color: #12a4aa; text-decoration: underline; }}
        code {{
            background-color: #16213e;
            padding: 0.25em 0.5em;
            border-radius: 4px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 90%;
            border: 1px solid #2d4a6f;
        }}
        pre {{
            background-color: #16213e;
            padding: 18px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #2d4a6f;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        pre code {{ background-color: transparent; padding: 0; border: none; }}
        blockquote {{
            margin: 16px 0;
            padding: 12px 20px;
            color: #9ba4b4;
            border-left: 4px solid #0f969c;
            background-color: #16213e;
            border-radius: 0 8px 8px 0;
        }}
        ul, ol {{ padding-left: 2em; margin-bottom: 16px; }}
        li {{ margin-bottom: 6px; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-bottom: 16px;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{ border: 1px solid #2d4a6f; padding: 10px 14px; text-align: left; }}
        th {{ background-color: #16213e; font-weight: 600; }}
        tr:hover {{ background-color: #1f3460; }}
        hr {{ height: 2px; padding: 0; margin: 28px 0; background: linear-gradient(90deg, #0f969c, transparent); border: 0; }}
        img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.3); }}
        .task-list-item {{ list-style-type: none; margin-left: -1.5em; }}
        .task-list-item input {{ margin-right: 0.5em; }}
        .katex {{ color: #e8e8e8; }}
        .math-display {{ text-align: center; margin: 1.5em 0; font-size: 1.1em; }}
        .math-inline {{ }}
    </style>
    {mathjax_script}
</head>
<body>
{content}
</body>
</html>"""
    
    def _process_image_paths(self, markdown_text, base_path):
        """Convert relative image paths to absolute file:// URLs"""
        if not base_path:
            return markdown_text
            
        def replace_image_path(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            
            # Skip URLs that are already absolute
            if img_path.startswith(('http://', 'https://', 'file://', 'data:')):
                return match.group(0)
            
            # Convert relative path to absolute
            if not os.path.isabs(img_path):
                abs_path = os.path.normpath(os.path.join(base_path, img_path))
                # Use forward slashes for file:// URL
                file_url = 'file:///' + abs_path.replace('\\', '/')
                return f'![{alt_text}]({file_url})'
            
            return match.group(0)
        
        processed = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_path, markdown_text)
        return processed

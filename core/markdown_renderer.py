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
        
        self.pygments_css = self._get_pygment_css()
        
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
        
        escaped = html_module.escape(formula)
        if display_mode:
            return f'<div class="math-display">\\[{escaped}\\]</div>'
        return f'<span class="math-inline">\\({escaped}\\)</span>'
    
    def _process_math(self, text):
        """Process math formulas in text"""
        code_blocks = []
        def save_code(match):
            code_blocks.append(match.group(0))
            return f'___CODE_BLOCK_{len(code_blocks)-1}___'
        
        text = re.sub(r'```[\s\S]*?```', save_code, text)
        text = re.sub(r'`[^`]+`', save_code, text)
        
        def replace_display(match):
            formula = match.group(1)
            return self._render_latex(formula, display_mode=True)
        
        text = re.sub(r'\$\$([\s\S]+?)\$\$', replace_display, text)
        
        def replace_inline(match):
            formula = match.group(1)
            return self._render_latex(formula, display_mode=False)
        
        text = re.sub(r'(?<![\\$])\$(?!\$)([^\$\n]+?)\$(?!\$)', replace_inline, text)
        
        for i, code in enumerate(code_blocks):
            text = text.replace(f'___CODE_BLOCK_{i}___', code)
        
        return text
    
    def render(self, markdown_text, base_path=None):
        """Render Markdown text to full HTML"""
        try:
            if base_path:
                markdown_text = self._process_image_paths(markdown_text, base_path)
            
            markdown_text = self._process_math(markdown_text)
            
            html_content = self.markdown.convert(markdown_text)
            
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
        katex_css = ""
        mathjax_script = ""
        
        base_tag = ""
        if base_path:
            base_tag = f'    <base href="file:///{base_path.replace(chr(92), "/")}/" />\n'
        
        if not self.katex_module:
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
            font-family: "霞鹜文楷", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 15px;
            line-height: 1.8;
            color: #f4f4f5;
            background-color: #18181b;
            padding: 24px 32px;
            max-width: 900px;
            margin: 0 auto;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #f4f4f5;
            margin-top: 24px;
            margin-bottom: 14px;
            font-weight: 600;
            line-height: 1.3;
        }}
        h1 {{ 
            font-size: 2em; 
            padding-bottom: 0.3em; 
            border-bottom: 1px solid #27272a;
        }}
        h2 {{ 
            font-size: 1.5em; 
            padding-bottom: 0.25em; 
            border-bottom: 1px solid #27272a;
        }}
        h3 {{ font-size: 1.25em; color: #22d3ee; }}
        h4 {{ font-size: 1.1em; color: #a1a1aa; }}
        p {{ margin-bottom: 14px; }}
        a {{ color: #22d3ee; text-decoration: none; transition: color 0.2s; }}
        a:hover {{ color: #67e8f9; text-decoration: underline; }}
        code {{
            background-color: #27272a;
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-family: "JetBrains Mono", "Consolas", "Monaco", monospace;
            font-size: 0.9em;
            color: #fbbf24;
        }}
        pre {{
            background-color: #09090b;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #27272a;
            margin: 16px 0;
        }}
        pre code {{ 
            background-color: transparent; 
            padding: 0; 
            border: none; 
            color: #e8e8e8;
        }}
        blockquote {{
            margin: 14px 0;
            padding: 10px 16px;
            color: #a1a1aa;
            border-left: 3px solid #22d3ee;
            background-color: #18181b;
            border-radius: 0 6px 6px 0;
        }}
        blockquote p {{ margin: 0; }}
        ul, ol {{ padding-left: 1.8em; margin-bottom: 14px; }}
        li {{ margin-bottom: 4px; }}
        li::marker {{ color: #22d3ee; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-bottom: 14px;
            border-radius: 6px;
            overflow: hidden;
        }}
        th, td {{ border: 1px solid #27272a; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #27272a; font-weight: 600; color: #f4f4f5; }}
        tr:hover {{ background-color: #27272a; }}
        hr {{ height: 1px; padding: 0; margin: 24px 0; background: #27272a; border: 0; }}
        img {{ max-width: 100%; border-radius: 6px; margin: 12px 0; }}
        .task-list-item {{ list-style-type: none; margin-left: -1.5em; }}
        .task-list-item input {{ margin-right: 0.5em; accent-color: #22d3ee; }}
        .katex {{ color: #f4f4f5; }}
        .math-display {{ text-align: center; margin: 1.5em 0; }}
        .math-inline {{ }}
        
        ::selection {{
            background-color: #3f3f46;
            color: #f4f4f5;
        }}
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
            
            if img_path.startswith(('http://', 'https://', 'file://', 'data:')):
                return match.group(0)
            
            if not os.path.isabs(img_path):
                abs_path = os.path.normpath(os.path.join(base_path, img_path))
                file_url = 'file:///' + abs_path.replace('\\', '/')
                return f'![{alt_text}]({file_url})'
            
            return match.group(0)
        
        processed = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_path, markdown_text)
        return processed

from langchain_community.document_loaders.confluence import ConfluenceLoader, ContentFormat
from typing import (
    Any,
    List,
)
from markdownify import markdownify, MarkdownConverter

from langchain_core.documents import Document

class BankGPTConfluenceLoader(ConfluenceLoader):
    def __init__(self, keep_html: bool = False, **kwargs: Any):
        """Load confluence pages"""
        super().__init__(**kwargs)
        self._keep_html = keep_html
    
    def process_page(
        self, 
        page: dict, 
        include_attachments: bool, 
        include_comments: bool, 
        content_format: ContentFormat, 
        ocr_languages: str | None = None, 
        keep_markdown_format: bool | None = False,
        keep_newlines: bool = False
    ) -> Document:
        
        content = content_format.get_content(page)
        text = MarkdownConverter(content, heading_style="atx")

        return text
        
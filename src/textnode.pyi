from enum import Enum
from typing import Optional
from htmlnode import ParentNode

class TextType(Enum):
    TEXT: str
    BOLD: str
    ITALIC: str
    CODE: str
    LINK: str
    IMAGE: str

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: Optional[str] = None) -> None: ...

def markdown_to_html_node(markdown: str) -> ParentNode: ... 
from enum import Enum
from htmlnode import LeafNode, ParentNode
import re

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)

    def __repr__(self):
        return f"TextNode({self.text!r}, {self.text_type}, {self.url!r})"

def text_to_textnodes(text):
    """Convert text to TextNode objects, handling markdown inline formatting"""
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Handle images first since they use ![ which includes the [ character
    nodes = split_nodes_image(nodes)
    
    # Handle other delimiters
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    # Handle links last since they depend on having text nodes to wrap
    nodes = split_nodes_link(nodes)
    
    return nodes

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """Split nodes by delimiter and create new nodes with the specified text type"""
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        splits = old_node.text.split(delimiter)
        if len(splits) % 2 == 0:  # Unmatched delimiter
            new_nodes.append(old_node)
            continue
            
        for i in range(len(splits)):
            if splits[i] == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(splits[i], TextType.TEXT))
            else:
                new_nodes.append(TextNode(splits[i], text_type))
                
    return new_nodes

def extract_markdown_links(text):
    """Extract all markdown links from text. Returns list of (text, url) tuples."""
    pattern = r'\[(.*?)\]\((.*?)\)'
    return re.findall(pattern, text)

def extract_markdown_images(text):
    """Extract all markdown images from text. Returns list of (alt_text, url) tuples."""
    pattern = r'!\[(.*?)\]\((.*?)\)'
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    """Split nodes by image markdown and create image nodes"""
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        images = extract_markdown_images(old_node.text)
        if not images:
            new_nodes.append(old_node)
            continue
            
        # Split text by images and create appropriate nodes
        current_text = old_node.text
        for alt_text, url in images:
            parts = current_text.split(f"![{alt_text}]({url})", 1)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            current_text = parts[1] if len(parts) > 1 else ""
            
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
            
    return new_nodes

def split_nodes_link(old_nodes):
    """Split nodes by link markdown and create link nodes"""
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        links = extract_markdown_links(old_node.text)
        if not links:
            new_nodes.append(old_node)
            continue
            
        # Split text by links and create appropriate nodes
        current_text = old_node.text
        for text, url in links:
            parts = current_text.split(f"[{text}]({url})", 1)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            new_nodes.append(TextNode(text, TextType.LINK, url))
            current_text = parts[1] if len(parts) > 1 else ""
            
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
            
    return new_nodes

def text_node_to_html_node(text_node):
    """Convert a TextNode to its corresponding HTML node"""
    # Ensure we have a valid text value
    text = text_node.text if text_node.text is not None else ""
    
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text)
    elif text_node.text_type == TextType.BOLD:
        return ParentNode("b", [LeafNode(None, text)])  # Changed back to b
    elif text_node.text_type == TextType.ITALIC:
        return ParentNode("i", [LeafNode(None, text)])  # Changed back to i
    elif text_node.text_type == TextType.CODE:
        return ParentNode("code", [LeafNode(None, text)])
    elif text_node.text_type == TextType.LINK:
        return ParentNode("a", [LeafNode(None, text)], {"href": text_node.url or "#"})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", " ", {"src": text_node.url or "", "alt": text})
    else:
        raise ValueError(f"Invalid text type: {text_node.text_type}")

def markdown_to_html_node(markdown):
    """Convert a markdown string to an HTML node"""
    block_nodes = []
    current_nodes = []
    
    lines = markdown.split('\n')
    in_code_block = False
    code_content = []
    
    for line in lines:
        if line.startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_content)
                if not code_text:
                    code_text = ""
                block_nodes.append(ParentNode("pre", [ParentNode("code", [LeafNode(None, code_text)])]))
                code_content = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            continue
            
        if in_code_block:
            code_content.append(line)
            continue
            
        if line.strip() == "":
            if current_nodes:
                block_nodes.append(ParentNode("p", current_nodes))
                current_nodes = []
            continue
            
        # Handle headers
        if line.startswith('#'):
            count = 0
            while count < len(line) and line[count] == '#':
                count += 1
            text = line[count:].strip()
            # Simpler header handling that was working before
            node = ParentNode(f"h{count}", [LeafNode(None, text or "")])  # Ensure empty string if text is empty
            block_nodes.append(node)
            continue
            
        # Handle unordered lists
        if line.strip().startswith('* '):
            text = line.strip()[2:]
            text_nodes = text_to_textnodes(text)
            html_nodes = [text_node_to_html_node(node) for node in text_nodes]
            block_nodes.append(ParentNode("li", html_nodes))
            continue
            
        # Handle ordered lists
        if re.match(r'^\d+\. ', line.strip()):
            text = line.strip().split('. ', 1)[1]
            text_nodes = text_to_textnodes(text)
            html_nodes = [text_node_to_html_node(node) for node in text_nodes]
            block_nodes.append(ParentNode("li", html_nodes))
            continue
            
        # Handle blockquotes
        if line.strip().startswith('> '):
            text = line.strip()[2:]
            text_nodes = text_to_textnodes(text)
            html_nodes = [text_node_to_html_node(node) for node in text_nodes]
            block_nodes.append(ParentNode("blockquote", html_nodes))
            continue
            
        # Regular paragraph text
        text_nodes = text_to_textnodes(line)
        html_nodes = [text_node_to_html_node(node) for node in text_nodes]
        current_nodes.extend(html_nodes)
    
    # Handle any remaining nodes
    if current_nodes:
        block_nodes.append(ParentNode("p", current_nodes))
    
    return ParentNode("div", block_nodes)

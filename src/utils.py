import re
from textnode import TextNode, TextType
from htmlnode import ParentNode, LeafNode

def text_node_to_html_node(text_node):
    if not isinstance(text_node, TextNode):
        raise ValueError("Input must be a TextNode")

    if text_node.text_type == TextType.NORMAL_TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD_TEXT:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC_TEXT:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE_TEXT:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINKS:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGES:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Unsupported TextType: {text_node.text_type}")
    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.NORMAL_TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.NORMAL_TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images(text):
    """
    Extracts markdown image references from text and returns a list of (alt_text, url) tuples.
    
    Markdown image syntax: ![alt text](url)
    
    Args:
        text (str): The markdown text to parse
        
    Returns:
        list[tuple[str, str]]: List of tuples containing (alt_text, url) pairs
        
    Example:
        >>> text = "![cat](cat.jpg) and ![dog](dog.png)"
        >>> extract_markdown_images(text)
        [('cat', 'cat.jpg'), ('dog', 'dog.png')]
    """
    # The regex pattern breaks down as:
    # \!           - Match the literal '!' that precedes markdown images
    # \[([^\]]+)\] - Capture the alt text between square brackets
    # \(([^\)]+)\) - Capture the URL between parentheses
    pattern = r'\!\[([^\]]+)\]\(([^\)]+)\)'
    
    # findall() returns a list of tuples where each tuple contains the captured groups
    return re.findall(pattern, text)

def extract_markdown_links(text):
    """
    Extracts markdown links from text and returns a list of (anchor_text, url) tuples.
    
    Markdown link syntax: [anchor text](url)
    
    Args:
        text (str): The markdown text to parse
        
    Returns:
        list[tuple[str, str]]: List of tuples containing (anchor_text, url) pairs
        
    Example:
        >>> text = "[Google](https://google.com) and [Bing](https://bing.com)"
        >>> extract_markdown_links(text)
        [('Google', 'https://google.com'), ('Bing', 'https://bing.com')]
    """
    # The regex pattern breaks down as:
    """
    \[     # Match an opening square bracket (escaped because [ has special meaning)
    (.*?)  # First capturing group - match any characters (non-greedy)
    \]     # Match a closing square bracket (escaped)
    \(     # Match an opening parenthesis (escaped)
    ([^\)]+)  # Second capturing group - match one or more non-) characters
    \)     # Match a closing parenthesis (escaped)
    """
    pattern = r'\[(.*?)\]\(([^\)]+)\)'
    
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    """
    Splits TextNodes containing markdown images into multiple TextNodes.
    
    Example:
        Input: TextNode("Hello ![alt](url) world", TextType.NORMAL_TEXT)
        Output: [
            TextNode("Hello ", TextType.NORMAL_TEXT),
            TextNode("alt", TextType.IMAGE, "url"),
            TextNode(" world", TextType.NORMAL_TEXT)
        ]
    
    Args:
        old_nodes (list[TextNode]): List of nodes to process
        
    Returns:
        list[TextNode]: New list of nodes with images split out
    """
    new_nodes = []
    for old_node in old_nodes:
        # Skip nodes that aren't normal text
        if old_node.text_type != TextType.NORMAL_TEXT:
            new_nodes.append(old_node)
            continue
            
        # Process the node's text
        current_text = old_node.text
        current_index = 0
        image_matches = extract_markdown_images(current_text)
        
        # Handle each image match and the text between matches
        for alt_text, url in image_matches:
            # Find the full image markdown in the text
            image_markdown = f"![{alt_text}]({url})"
            image_index = current_text.find(image_markdown, current_index)
            
            # Add any text that comes before the image
            if image_index > current_index:
                new_nodes.append(
                    TextNode(
                        current_text[current_index:image_index],
                        TextType.NORMAL_TEXT
                    )
                )
            
            # Add the image node
            new_nodes.append(TextNode(alt_text, TextType.IMAGES, url))
            
            # Update the current index for the next iteration
            current_index = image_index + len(image_markdown)
        
        # Add any remaining text after the last image
        if current_index < len(current_text):
            new_nodes.append(
                TextNode(
                    current_text[current_index:],
                    TextType.NORMAL_TEXT
                )
            )
            
    return new_nodes

def split_nodes_link(old_nodes):
    """
    Splits TextNodes containing markdown links into multiple TextNodes.
    Now properly handles links containing brackets in their text.
    
    Args:
        old_nodes (list[TextNode]): List of nodes to process
        
    Returns:
        list[TextNode]: New list of nodes with links split out
    """
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.NORMAL_TEXT:
            new_nodes.append(old_node)
            continue
            
        current_text = old_node.text
        current_index = 0
        link_matches = extract_markdown_links(current_text)
        
        for anchor_text, url in link_matches:
            # We need to handle the case where anchor_text might contain brackets
            link_markdown = f"[{anchor_text}]({url})"
            link_index = current_text.find(link_markdown, current_index)
            
            if link_index > current_index:
                new_nodes.append(
                    TextNode(
                        current_text[current_index:link_index],
                        TextType.NORMAL_TEXT
                    )
                )
            
            # Create the link node with the proper anchor text
            new_nodes.append(TextNode(anchor_text, TextType.LINKS, url))
            
            current_index = link_index + len(link_markdown)
        
        if current_index < len(current_text):
            new_nodes.append(
                TextNode(
                    current_text[current_index:],
                    TextType.NORMAL_TEXT
                )
            )
            
    return new_nodes

def text_to_textnodes(text):
    """
    Converts markdown text into a list of TextNode objects by applying
    a series of splitting functions to process different markdown elements.
    
    The function processes elements in this order:
    1. Images (![alt](url))
    2. Links ([text](url))
    3. Bold text (**text**)
    4. Italic text (*text*)
    5. Code blocks (`text`)
    
    Args:
        text (str): The markdown text to process
        
    Returns:
        list[TextNode]: A list of TextNode objects representing the processed text
        
    Example:
        text = "Hello **world** with ![alt](url)"
        result = text_to_textnodes(text)
        # Returns [
        #     TextNode("Hello ", TextType.TEXT),
        #     TextNode("world", TextType.BOLD),
        #     TextNode(" with ", TextType.TEXT),
        #     TextNode("alt", TextType.IMAGE, "url")
        # ]
    """
    # Start with a single text node containing the entire text
    nodes = [TextNode(text, TextType.NORMAL_TEXT)]
    
    # Process images first since they contain brackets that could interfere
    # with link processing if done later
    nodes = split_nodes_image(nodes)
    
    # Process links next for the same reason - they contain brackets
    nodes = split_nodes_link(nodes)
    
    # Process bold text with double asterisks
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD_TEXT)
    
    # Process italic text with single asterisks
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC_TEXT)
    
    # Finally process code blocks
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE_TEXT)
    
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks

block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_olist = "ordered_list"
block_type_ulist = "unordered_list"

def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return block_type_heading
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return block_type_code
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return block_type_paragraph
        return block_type_quote
    if block.startswith("* "):
        for line in lines:
            if not line.startswith("* "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return block_type_paragraph
            i += 1
        return block_type_olist
    return block_type_paragraph

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"Invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode("code", children)
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)
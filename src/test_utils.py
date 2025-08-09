import unittest

from utils import (
    text_node_to_html_node, 
    split_nodes_delimiter, 
    extract_markdown_images, 
    extract_markdown_links, 
    split_nodes_image, 
    split_nodes_link, 
    text_to_textnodes, 
    markdown_to_blocks, 
    block_to_block_type, 
    markdown_to_html_node,
    block_type_paragraph,
    block_type_heading,
    block_type_code,
    block_type_olist,
    block_type_ulist,
    block_type_quote,)
from textnode import TextNode, TextType

class TestTextNodeToHtmlNode(unittest.TestCase):

    def test_text_node(self):
        text_node = TextNode("Hello, world!", TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "Hello, world!")

    def test_bold_node(self):
        text_node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic_node(self):
        text_node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code_node(self):
        text_node = TextNode("print('Hello')", TextType.CODE)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('Hello')")

    def test_link_node(self):
        text_node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image_node(self):
        text_node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.jpg")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.jpg", "alt": "Alt text"})

    def test_invalid_type(self):
        text_node = TextNode("Invalid", "INVALID_TYPE")
        with self.assertRaises(ValueError):
            text_node_to_html_node(text_node)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            text_node_to_html_node("Not a TextNode")

class TestInlineMarkdown(unittest.TestCase):
    def test_delim_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded word", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an *italic* word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and *italic*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

class TestMarkdownExtractors(unittest.TestCase):
    """Test suite for markdown image and link extraction functions.
    
    This class contains comprehensive tests for both extract_markdown_images() and 
    extract_markdown_links() functions, ensuring they correctly handle various cases 
    including empty text, single items, multiple items, and special characters.
    """
    
    def setUp(self):
        """Set up test cases that will be used across multiple tests.
        
        We define our test inputs and expected outputs here so they can be reused
        across different test methods, making the code more maintainable.
        """
        # Test cases for images - each tuple contains (input_text, expected_output)
        self.image_cases = {
            'basic': (
                "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
                [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), 
                 ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
            ),
            'empty': (
                "No images here",
                []
            ),
            'single': (
                "![single image](single.jpg)",
                [("single image", "single.jpg")]
            ),
            'spaces': (
                "![image with spaces in alt](https://example.com/pic.jpg)",
                [("image with spaces in alt", "https://example.com/pic.jpg")]
            ),
            'adjacent': (
                "![image1](url1.jpg)![image2](url2.jpg)",
                [("image1", "url1.jpg"), ("image2", "url2.jpg")]
            )
        }
        
        # Test cases for links - each tuple contains (input_text, expected_output)
        self.link_cases = {
            'basic': (
                "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
                [("to boot dev", "https://www.boot.dev"), 
                 ("to youtube", "https://www.youtube.com/@bootdotdev")]
            ),
            'empty': (
                "No links here",
                []
            ),
            'single': (
                "[single link](https://example.com)",
                [("single link", "https://example.com")]
            ),
            'spaces': (
                "[text with spaces](https://example.com/page)",
                [("text with spaces", "https://example.com/page")]
            ),
            'adjacent': (
                "[link1](url1)[link2](url2)",
                [("link1", "url1"), ("link2", "url2")]
            )
        }

    def test_extract_markdown_images_basic(self):
        """Test basic functionality of image extraction with multiple images."""
        input_text, expected = self.image_cases['basic']
        result = extract_markdown_images(input_text)
        self.assertEqual(result, expected, 
                        "Failed to extract multiple images correctly")

    def test_extract_markdown_images_empty(self):
        """Test image extraction with text containing no images."""
        input_text, expected = self.image_cases['empty']
        result = extract_markdown_images(input_text)
        self.assertEqual(result, expected, 
                        "Should return empty list when no images present")

    def test_extract_markdown_images_single(self):
        """Test image extraction with a single image."""
        input_text, expected = self.image_cases['single']
        result = extract_markdown_images(input_text)
        self.assertEqual(result, expected, 
                        "Failed to extract single image correctly")

    def test_extract_markdown_images_spaces(self):
        """Test image extraction with spaces in alt text."""
        input_text, expected = self.image_cases['spaces']
        result = extract_markdown_images(input_text)
        self.assertEqual(result, expected, 
                        "Failed to handle spaces in alt text correctly")

    def test_extract_markdown_images_adjacent(self):
        """Test image extraction with adjacent images (no spacing between them)."""
        input_text, expected = self.image_cases['adjacent']
        result = extract_markdown_images(input_text)
        self.assertEqual(result, expected, 
                        "Failed to extract adjacent images correctly")

    def test_extract_markdown_links_basic(self):
        """Test basic functionality of link extraction with multiple links."""
        input_text, expected = self.link_cases['basic']
        result = extract_markdown_links(input_text)
        self.assertEqual(result, expected, 
                        "Failed to extract multiple links correctly")

    def test_extract_markdown_links_empty(self):
        """Test link extraction with text containing no links."""
        input_text, expected = self.link_cases['empty']
        result = extract_markdown_links(input_text)
        self.assertEqual(result, expected, 
                        "Should return empty list when no links present")

    def test_extract_markdown_links_single(self):
        """Test link extraction with a single link."""
        input_text, expected = self.link_cases['single']
        result = extract_markdown_links(input_text)
        self.assertEqual(result, expected, 
                        "Failed to extract single link correctly")

    def test_extract_markdown_links_spaces(self):
        """Test link extraction with spaces in anchor text."""
        input_text, expected = self.link_cases['spaces']
        result = extract_markdown_links(input_text)
        self.assertEqual(result, expected, 
                        "Failed to handle spaces in anchor text correctly")

    def test_extract_markdown_links_adjacent(self):
        """Test link extraction with adjacent links (no spacing between them)."""
        input_text, expected = self.link_cases['adjacent']
        result = extract_markdown_links(input_text)
        self.assertEqual(result, expected, 
                        "Failed to extract adjacent links correctly")

class TestMarkdownNodeSplitting(unittest.TestCase):
    """Test suite for markdown node splitting functions."""
    
    def test_split_nodes_image_basic(self):
        """Test basic image splitting with a single image."""
        node = TextNode(
            "Hello ![alt text](url) world",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "Hello ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "alt text")
        self.assertEqual(new_nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].url, "url")
        self.assertEqual(new_nodes[2].text, " world")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_split_nodes_image_multiple(self):
        """Test splitting with multiple images."""
        node = TextNode(
            "![img1](url1)middle![img2](url2)",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "img1")
        self.assertEqual(new_nodes[0].url, "url1")
        self.assertEqual(new_nodes[1].text, "middle")
        self.assertEqual(new_nodes[2].text, "img2")
        self.assertEqual(new_nodes[2].url, "url2")

    def test_split_nodes_image_no_images(self):
        """Test with text containing no images."""
        node = TextNode("Plain text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Plain text")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)

    def test_split_nodes_image_non_text_node(self):
        """Test with a non-text node (should be returned unchanged)."""
        node = TextNode("![img](url)", TextType.LINK, "url")
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0], node)

    def test_split_nodes_link_basic(self):
        """Test basic link splitting with a single link."""
        node = TextNode(
            "Hello [anchor](url) world",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "Hello ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "anchor")
        self.assertEqual(new_nodes[1].text_type, TextType.LINK)
        self.assertEqual(new_nodes[1].url, "url")
        self.assertEqual(new_nodes[2].text, " world")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_split_nodes_link_multiple(self):
        """Test splitting with multiple links."""
        node = TextNode(
            "[link1](url1)middle[link2](url2)",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "link1")
        self.assertEqual(new_nodes[0].url, "url1")
        self.assertEqual(new_nodes[1].text, "middle")
        self.assertEqual(new_nodes[2].text, "link2")
        self.assertEqual(new_nodes[2].url, "url2")

    def test_split_nodes_link_no_links(self):
        """Test with text containing no links."""
        node = TextNode("Plain text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Plain text")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)

    def test_split_nodes_link_non_text_node(self):
        """Test with a non-text node (should be returned unchanged)."""
        node = TextNode("[text](url)", TextType.IMAGE, "url")
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0], node)

    def test_split_nodes_complex_cases(self):
        """Test more complex cases for both functions."""
        # Test nested-looking brackets that aren't actually nested
        node = TextNode(
            "[[text]](url)",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "[text]")
        self.assertEqual(new_nodes[0].url, "url")

        # Test links with special characters in URL
        node = TextNode(
            "[text](https://example.com/path?param=value)",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].url, "https://example.com/path?param=value")

    def test_split_nodes_link_advanced_cases(self):
        """Test advanced cases for link parsing."""
        test_cases = [
            (
                "[[text]](url)",
                [TextNode("[text]", TextType.LINK, "url")]
            ),
            (
                "[a[b]c](url)",
                [TextNode("a[b]c", TextType.LINK, "url")]
            ),
            (
                "Before [[text]](url) after",
                [
                    TextNode("Before ", TextType.TEXT),
                    TextNode("[text]", TextType.LINK, "url"),
                    TextNode(" after", TextType.TEXT)
                ]
            )
        ]
        
        for input_text, expected_nodes in test_cases:
            node = TextNode(input_text, TextType.TEXT)
            result = split_nodes_link([node])
            self.assertEqual(len(result), len(expected_nodes))
            for res_node, exp_node in zip(result, expected_nodes):
                self.assertEqual(res_node.text, exp_node.text)
                self.assertEqual(res_node.text_type, exp_node.text_type)
                self.assertEqual(res_node.url, exp_node.url)

class TestTextToTextNodes(unittest.TestCase):
    def test_single_text(self):
        """Test with plain text, no markdown."""
        nodes = text_to_textnodes("Hello world")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "Hello world")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        
    def test_bold_text(self):
        """Test text with bold markdown."""
        nodes = text_to_textnodes("Hello **world**")
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].text, "Hello ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "world")
        self.assertEqual(nodes[1].text_type, TextType.BOLD)
        
    def test_italic_text(self):
        """Test text with italic markdown."""
        nodes = text_to_textnodes("Hello *world*")
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].text, "Hello ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "world")
        self.assertEqual(nodes[1].text_type, TextType.ITALIC)
        
    def test_code_block(self):
        """Test text with code block."""
        nodes = text_to_textnodes("Hello `world`")
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].text, "Hello ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "world")
        self.assertEqual(nodes[1].text_type, TextType.CODE)
        
    def test_link(self):
        """Test text with a link."""
        nodes = text_to_textnodes("Hello [world](https://example.com)")
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].text, "Hello ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "world")
        self.assertEqual(nodes[1].text_type, TextType.LINK)
        self.assertEqual(nodes[1].url, "https://example.com")
        
    def test_image(self):
        """Test text with an image."""
        nodes = text_to_textnodes("Hello ![world](image.jpg)")
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].text, "Hello ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "world")
        self.assertEqual(nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(nodes[1].url, "image.jpg")
        
    def test_multiple_elements(self):
        """Test text with multiple markdown elements."""
        text = "This is **text** with an *italic* word and a `code block` and an ![image](img.jpg) and a [link](url)"
        nodes = text_to_textnodes(text)
        
        # Verify the sequence of nodes
        expected = [
            ("This is ", TextType.TEXT, None),
            ("text", TextType.BOLD, None),
            (" with an ", TextType.TEXT, None),
            ("italic", TextType.ITALIC, None),
            (" word and a ", TextType.TEXT, None),
            ("code block", TextType.CODE, None),
            (" and an ", TextType.TEXT, None),
            ("image", TextType.IMAGE, "img.jpg"),
            (" and a ", TextType.TEXT, None),
            ("link", TextType.LINK, "url"),
        ]
        
        self.assertEqual(len(nodes), len(expected))
        for node, (text, text_type, url) in zip(nodes, expected):
            self.assertEqual(node.text, text)
            self.assertEqual(node.text_type, text_type)
            if url:
                self.assertEqual(node.url, url)
                
    def test_nested_formatting(self):
        """Test handling of nested formatting attempts."""
        text = "This **has *nested* formatting**"
        nodes = text_to_textnodes(text)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].text, "This ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "has *nested* formatting")
        self.assertEqual(nodes[1].text_type, TextType.BOLD)

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
                "* This is a list\n* with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph




This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
                "* This is a list\n* with items",
            ],
        )

class TestBlockToBlockType(unittest.TestCase):
    """Test cases for the block_to_block_type function."""
    
    def test_block_to_block_types(self):
        block = "# heading"
        self.assertEqual(block_to_block_type(block), block_type_heading)
        block = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block), block_type_code)
        block = "> quote\n> more quote"
        self.assertEqual(block_to_block_type(block), block_type_quote)
        block = "* list\n* items"
        self.assertEqual(block_to_block_type(block), block_type_ulist)
        block = "1. list\n2. items"
        self.assertEqual(block_to_block_type(block), block_type_olist)
        block = "paragraph"
        self.assertEqual(block_to_block_type(block), block_type_paragraph)

class TestMarkdownToHTML(unittest.TestCase):
    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with *italic* text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and *more* items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )
if __name__ == "__main__":
    unittest.main()
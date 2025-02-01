import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):

    def test_initialization(self):
        # Test 1: Initialization with all parameters
        node = HTMLNode("div", "Hello", [HTMLNode("p", "World")], {"class": "container"})
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.props, {"class": "container"})

    def test_props_to_html(self):
        # Test 2: props_to_html method
        node1 = HTMLNode(props={"class": "btn", "id": "submit-btn"})
        self.assertIn('class="btn"', node1.props_to_html())
        self.assertIn('id="submit-btn"', node1.props_to_html())
        self.assertEqual(len(node1.props_to_html().split()), 2)

        node2 = HTMLNode()
        self.assertEqual(node2.props_to_html(), "")

    def test_repr(self):
        # Test 3: __repr__ method
        node = HTMLNode("a", "Click me", props={"href": "https://example.com"})
        expected_repr = "HTMLNode('a', 'Click me', None, {'href': 'https://example.com'})"
        self.assertEqual(repr(node), expected_repr)

class TestLeafNode(unittest.TestCase):

    def test_initialization(self):
        # Test initialization with tag and value
        node = LeafNode("p", "Hello, World!")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello, World!")
        self.assertIsNone(node.children)
        self.assertEqual(node.props, None)

        # Test initialization with tag, value, and props
        node = LeafNode("a", "Click me", {"href": "https://example.com"})
        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "Click me")
        self.assertEqual(node.props, {"href": "https://example.com"})

    def test_to_html_with_tag_and_value(self):
        node = LeafNode("span", "Text")
        self.assertEqual(node.to_html(), "<span>Text</span>")

    def test_to_html_with_tag_value_and_props(self):
        node = LeafNode("a", "Link", {"href": "https://example.com", "class": "btn"})
        html = node.to_html()
        self.assertIn("<a", html)
        self.assertIn(">Link</a>", html)
        self.assertIn('href="https://example.com"', html)
        self.assertIn('class="btn"', html)

    def test_to_html_without_tag(self):
        node = LeafNode(None, "Plain text")
        self.assertEqual(node.to_html(), "Plain text")

    def test_to_html_without_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

class TestParentNode(unittest.TestCase):

    def test_to_html_basic(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), expected)

    def test_to_html_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "p",
                    [
                        LeafNode("b", "Bold text"),
                        LeafNode(None, "Normal text"),
                    ]
                ),
                LeafNode("a", "Link", {"href": "https://example.com"}),
            ],
            {"class": "container"}
        )
        expected = '<div class="container"><p><b>Bold text</b>Normal text</p><a href="https://example.com">Link</a></div>'
        self.assertEqual(node.to_html(), expected)

    def test_to_html_no_tag(self):
        node = ParentNode(None, [LeafNode("p", "Text")])
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertTrue("all parent nodes must have a tag" in str(context.exception))

    def test_to_html_no_children(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertTrue("all parent nodes must have children" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
import pytest
from src.markdown_parser import extract_title

def test_extract_title_basic():
    assert extract_title("# Hello") == "Hello"
    
def test_extract_title_with_spaces():
    assert extract_title("# Hello World  ") == "Hello World"
    assert extract_title("#    Spaced    Title    ") == "Spaced    Title"

def test_extract_title_multiline():
    markdown = """# Main Title
    ## Subtitle
    Some content
    """
    assert extract_title(markdown) == "Main Title"

def test_extract_title_no_h1():
    with pytest.raises(ValueError):
        extract_title("## Secondary Header")
        
def test_extract_title_empty():
    with pytest.raises(ValueError):
        extract_title("") 
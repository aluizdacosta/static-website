def extract_title(markdown):
    """Extract the H1 header from markdown text"""
    if not markdown:
        raise ValueError("Markdown content cannot be empty")
        
    lines = markdown.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
            
    raise ValueError("No H1 header (# title) found in markdown") 
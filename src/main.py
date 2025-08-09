import os
import shutil
import sys
from markdown_parser import extract_title  
from textnode import markdown_to_html_node 

def generate_page(from_path, template_path, dest_path, basepath="/"):
    """Generate an HTML page from markdown and template"""
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Read template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Convert markdown to HTML and extract title
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Replace basepath in href and src attributes
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')
    
    # Create destination directory if it doesn't exist
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Write the final HTML to destination
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """
    Recursively generate HTML pages from markdown files in content directory
    """
    # Ensure destination directory exists
    os.makedirs(dest_dir_path, exist_ok=True)
    
    # Walk through content directory
    for entry in os.listdir(dir_path_content):
        entry_path = os.path.join(dir_path_content, entry)
        
        if os.path.isfile(entry_path) and entry.endswith('.md'):
            # Generate HTML file path with same structure
            rel_path = os.path.relpath(entry_path, dir_path_content)
            dest_path = os.path.join(dest_dir_path, rel_path.replace('.md', '.html'))
            
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Generate the page
            generate_page(entry_path, template_path, dest_path, basepath)
            
        elif os.path.isdir(entry_path):
            # Recursively process subdirectories
            sub_dest_dir = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(entry_path, template_path, sub_dest_dir, basepath)

def main():
    # Get basepath from command line arguments, default to "/"
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    
    # Clean docs directory
    if os.path.exists("docs"):
        shutil.rmtree("docs")
    os.makedirs("docs")
    
    # Copy static files if they exist
    if os.path.exists("static"):
        shutil.copytree("static", "docs", dirs_exist_ok=True)
    
    # Generate all pages recursively
    generate_pages_recursive("content", "template.html", "docs", basepath)

if __name__ == "__main__":
    main()


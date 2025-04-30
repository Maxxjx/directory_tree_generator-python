import os
import re
import argparse
from pathlib import Path

def parse_tree_line(line):
    """Parse a single line from the tree representation."""
    # Count the indentation level (number of spaces before the symbol)
    indent = len(line) - len(line.lstrip())
    # Get the level by dividing by spaces per level (assuming 4 spaces per level)
    level = indent // 4
    
    # Extract the name by finding what's after the last '── ' in the line
    if '── ' in line:
        name = line.split('── ')[-1].strip()
    else:
        name = line.strip()
    
    # Determine if it's a file or directory
    # Assuming directories don't have file extensions (a simplified approach)
    is_file = '.' in name and not name.endswith('/')
    
    # If name ends with '/', remove it
    if name.endswith('/'):
        name = name[:-1]
        is_file = False
        
    return {
        'level': level,
        'name': name,
        'is_file': is_file
    }

def create_file_structure(tree_text, base_path="./output"):
    """Create directories and files based on the parsed tree text."""
    lines = [line for line in tree_text.strip().split('\n') if line.strip()]
    
    # Parse all lines
    parsed_lines = [parse_tree_line(line) for line in lines]
    
    # Create the base directory
    base_dir = Path(base_path)
    base_dir.mkdir(exist_ok=True, parents=True)
    
    # Keep track of the current path at each level
    path_stack = [base_dir]
    
    # Process each line to create the structure
    for item in parsed_lines:
        # If we're at a new level, update the path stack
        while len(path_stack) > item['level'] + 1:
            path_stack.pop()
        
        # Get the current path
        current_path = path_stack[-1]
        
        # Create the new path
        new_path = current_path / item['name']
        
        if item['is_file']:
            # Create an empty file
            new_path.touch()
            print(f"Created file: {new_path}")
        else:
            # Create a directory
            new_path.mkdir(exist_ok=True)
            print(f"Created directory: {new_path}")
            # Add this directory to the path stack for potential children
            path_stack.append(new_path)
    
    return base_dir

def main():
    parser = argparse.ArgumentParser(description='Generate a file structure from a textual tree representation.')
    parser.add_argument('--input', '-i', type=str, help='Input file containing the tree representation')
    parser.add_argument('--text', '-t', type=str, help='Tree representation as text')
    parser.add_argument('--output', '-o', default='./output', type=str, help='Base directory to create the structure in')
    
    args = parser.parse_args()
    
    if args.input:
        with open(args.input, 'r') as f:
            tree_text = f.read()
    elif args.text:
        tree_text = args.text
    else:
        # Interactive mode: allow user to paste tree text
        print("Please enter your tree representation. Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:")
        tree_lines = []
        try:
            while True:
                line = input()
                tree_lines.append(line)
        except EOFError:
            tree_text = "\n".join(tree_lines)
    
    output_dir = create_file_structure(tree_text, args.output)
    print(f"\nFile structure created successfully in: {output_dir}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import os
import re
import sys
import argparse
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import shutil

# Set up logging
logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger('dirtree')

class FileSystemItem:
    """Represents an item (file or directory) in the file system."""
    def __init__(self, name: str, is_file: bool, content: Optional[str] = None):
        self.name = name
        self.is_file = is_file
        self.content = content
    
    def __str__(self):
        item_type = "File" if self.is_file else "Directory"
        return f"{item_type}: {self.name}"

def parse_tree_line(line: str) -> Dict:
    """Parse a single line from the tree representation.
    
    Args:
        line: A single line from the tree text representation
        
    Returns:
        Dict containing level, name, is_file status, and optional content
    """
    # Count the indentation level (number of spaces before the symbol)
    indent = len(line) - len(line.lstrip())
    
    # Handle different indentation styles (spaces or │   style indentation)
    if '│' in line[:indent]:
        # Count the number of '│' characters to determine level
        level = line[:indent].count('│')
    else:
        # Get the level by dividing by spaces per level (assuming 4 spaces per level)
        level = indent // 4
    
    # Extract the name by finding what's after the last '── ' in the line
    name = ""
    content = None
    
    if '── ' in line:
        rest = line.split('── ')[-1].strip()
        
        # Check if content is specified inside square brackets
        content_match = re.search(r'(.*?)\s+\[(.*?)\]
, rest)
        if content_match:
            name = content_match.group(1).strip()
            content = content_match.group(2)
        else:
            name = rest
    else:
        name = line.strip()
    
    # Improved file/directory detection
    is_file = False
    
    # Explicit directory indication with trailing slash
    if name.endswith('/'):
        name = name[:-1]
        is_file = False
    # Files with extensions (but check for exceptions like .git directories)
    elif '.' in name.split('/')[-1] and not any(name.endswith(d) for d in ['.git', '.github', '.vscode']):
        is_file = True
    # Explicit file indication with special symbols
    elif any(name.startswith(prefix) for prefix in ['file:', 'f:']):
        name = name.split(':', 1)[1].strip()
        is_file = True
    # Explicit directory indication with special symbols
    elif any(name.startswith(prefix) for prefix in ['dir:', 'd:']):
        name = name.split(':', 1)[1].strip()
        is_file = False
        
    return {
        'level': level,
        'name': name,
        'is_file': is_file,
        'content': content
    }

def plan_file_structure(tree_text: str, base_path: str = "./output") -> List[Tuple[Path, bool, Optional[str]]]:
    """Plan the file structure without creating it.
    
    Args:
        tree_text: Text representation of the directory tree
        base_path: Base directory to create the structure in
        
    Returns:
        List of tuples (path, is_file, content) for all items to be created
    """
    lines = [line for line in tree_text.strip().split('\n') if line.strip()]
    
    # Parse all lines
    parsed_lines = [parse_tree_line(line) for line in lines]
    
    base_dir = Path(base_path)
    path_stack = [base_dir]
    planned_items = []
    
    # Process each line to plan the structure
    for item in parsed_lines:
        # If we're at a new level, update the path stack
        while len(path_stack) > item['level'] + 1:
            path_stack.pop()
        
        # Get the current path
        current_path = path_stack[-1]
        
        # Create the new path
        new_path = current_path / item['name']
        
        # Add to planned items
        planned_items.append((new_path, item['is_file'], item['content']))
        
        if not item['is_file']:
            # Add this directory to the path stack for potential children
            path_stack.append(new_path)
    
    return planned_items

def create_file_structure(planned_items: List[Tuple[Path, bool, Optional[str]]], dry_run: bool = False, force: bool = False) -> None:
    """Create directories and files based on the planned structure.
    
    Args:
        planned_items: List of (path, is_file, content) tuples
        dry_run: If True, only show what would be created without actual creation
        force: If True, overwrite existing files without confirmation
    """
    # Check for existing paths first
    existing_paths = []
    for path, is_file, _ in planned_items:
        if path.exists():
            existing_paths.append(path)
    
    # Ask for confirmation if paths exist and not in force mode
    if existing_paths and not force and not dry_run:
        print("The following paths already exist:")
        for path in existing_paths:
            print(f"  {path}")
        
        choice = input("\nOverwrite existing files/directories? [y/N]: ").lower()
        if choice != 'y':
            logger.warning("Operation cancelled by user")
            return
    
    # Create the structure
    for path, is_file, content in planned_items:
        if dry_run:
            action = "Would create"
            item_type = "file" if is_file else "directory"
            print(f"{action} {item_type}: {path}")
            if content and is_file:
                print(f"  with content: {content[:30]}{'...' if len(content) > 30 else ''}")
        else:
            try:
                if is_file:
                    # Ensure parent directory exists
                    path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create the file with content if provided
                    with open(path, 'w') as f:
                        if content:
                            f.write(content)
                    logger.info(f"Created file: {path}")
                else:
                    # Create the directory
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {path}")
            except Exception as e:
                logger.error(f"Failed to create {path}: {str(e)}")

def reverse_engineer_tree(directory_path: str, max_depth: int = None) -> str:
    """Generate a tree representation from an existing directory structure.
    
    Args:
        directory_path: Path to the directory to analyze
        max_depth: Maximum depth to traverse
        
    Returns:
        String representation of the directory tree
    """
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"'{directory_path}' is not a valid directory")
    
    output_lines = [path.name + "/"]
    
    def _add_directory(dir_path, prefix="", depth=1):
        if max_depth is not None and depth > max_depth:
            return
        
        # Get all items in the directory
        items = list(dir_path.iterdir())
        items.sort(key=lambda p: (p.is_file(), p.name))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            
            # Add the current item
            if item.is_dir():
                output_lines.append(f"{prefix}{connector}{item.name}/")
                
                # Update prefix for children
                new_prefix = prefix + ("    " if is_last else "│   ")
                _add_directory(item, new_prefix, depth + 1)
            else:
                output_lines.append(f"{prefix}{connector}{item.name}")
    
    _add_directory(path)
    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(
        description='Generate a file structure from a textual tree representation.',
        epilog='Example: directory_tree_generator.py --input tree.txt --output ./my_project'
    )
    parser.add_argument('--input', '-i', type=str, help='Input file containing the tree representation')
    parser.add_argument('--text', '-t', type=str, help='Tree representation as text')
    parser.add_argument('--output', '-o', default='./output', type=str, help='Base directory to create the structure in')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Show what would be created without making changes')
    parser.add_argument('--force', '-f', action='store_true', help='Force creation without confirmation prompts')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--reverse', '-r', type=str, help='Generate tree representation from existing directory')
    parser.add_argument('--max-depth', type=int, help='Maximum depth for reverse engineering')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    logger.setLevel(logging.INFO if args.verbose else logging.WARNING)
    
    # Handle reverse engineering mode
    if args.reverse:
        try:
            tree_text = reverse_engineer_tree(args.reverse, args.max_depth)
            print(tree_text)
            return
        except Exception as e:
            logger.error(f"Error in reverse engineering: {str(e)}")
            return
    
    # Get the tree text
    tree_text = None
    if args.input:
        try:
            with open(args.input, 'r') as f:
                tree_text = f.read()
        except FileNotFoundError:
            logger.error(f"Input file not found: {args.input}")
            return
        except Exception as e:
            logger.error(f"Error reading input file: {str(e)}")
            return
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
    
    if not tree_text:
        logger.error("No tree text provided")
        return
    
    try:
        # Plan the structure
        planned_items = plan_file_structure(tree_text, args.output)
        
        # Create or simulate creation
        create_file_structure(planned_items, args.dry_run, args.force)
        
        if args.dry_run:
            print("\nDry run completed. No files were created.")
        else:
            print(f"\nFile structure created successfully in: {args.output}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

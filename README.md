# Directory Tree Generator

A Python utility that transforms textual directory tree representations into actual file systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Directory Tree Generator parses text-based directory tree structures (with indentation and branch symbols like `├──` and `└──`) and creates the corresponding directories and files on your file system. This is particularly useful for quickly setting up project structures or recreating directory hierarchies from documentation.

## Features

- Creates directories and files from indented tree text
- Supports both file input and direct text input
- Interactive mode for pasting tree structures directly
- Customizable output location
- Safe execution with preview capabilities

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/directory-tree-generator.git
cd directory-tree-generator
```

No additional dependencies required - the script uses only Python standard libraries.

## Usage

### Basic Usage

```bash
python directory_tree_generator.py [options]
```

### Options

- `--input`, `-i`: Input file containing the tree representation
- `--text`, `-t`: Tree representation as text directly in the command
- `--output`, `-o`: Base directory to create the structure in (default: `./output`)

### Interactive Mode

Run the script without arguments to enter interactive mode:

```bash
python directory_tree_generator.py
```

Then paste your tree structure and press Ctrl+D (Unix) or Ctrl+Z followed by Enter (Windows) when done.

### Examples

1. **Using a File**

   Create a file `my_tree.txt` with your structure:

   ```
   project/
   ├── src/
   │   ├── main.py
   │   └── utils.py
   ├── tests/
   │   └── test_main.py
   └── README.md
   ```

   Then run:

   ```bash
   python directory_tree_generator.py --input my_tree.txt --output ./my_new_project
   ```

2. **Using Direct Text Input**

   ```bash
   python directory_tree_generator.py --text "project/\n├── src/\n│   ├── main.py\n│   └── utils.py\n└── README.md" --output ./quick_project
   ```

## Safe Testing

To safely test the tool without risking existing files:

1. Always use a dedicated test directory:
   ```bash
   python directory_tree_generator.py --output ./safe_test_area
   ```

2. Review the output before using it for important projects:
   ```bash
   ls -R ./safe_test_area
   ```

## Customization

### Symbol Customization

The parser currently recognizes standard tree symbols (`├──`, `└──`). If you need to support different symbols or formats, modify the `parse_tree_line` function:

```python
def parse_tree_line(line):
    # Customize regex patterns here to match your specific tree format
    # ...
```

### Extension Detection

The script uses a simple extension check to determine if an item is a file or directory. To customize this behavior, modify the relevant section in `parse_tree_line`:

```python
# Current simple approach
is_file = '.' in name and not name.endswith('/')

# More sophisticated approach could check against known directory markers
# or use regex patterns specific to your naming conventions
```

### Empty File Handling

By default, the script creates empty files. To automatically populate certain files with content:

```python
# In the create_file_structure function
if item['is_file']:
    with open(new_path, 'w') as f:
        if item['name'].endswith('.py'):
            f.write('#!/usr/bin/env python3\n\n"""\nAuto-generated file\n"""\n\n')
        elif item['name'] == 'README.md':
            f.write('# ' + os.path.basename(current_path) + '\n\n')
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

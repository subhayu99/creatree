# creatree

![PyPI version](https://img.shields.io/pypi/v/creatree)
![License](https://img.shields.io/github/license/subhayu99/creatree)
[![Downloads](https://pepy.tech/badge/creatree)](https://pepy.tech/project/creatree)

A Python package and CLI tool for creating directory structures from a tree-like string.

## Overview

`creatree` is a simple yet powerful tool that allows you to define directory structures using a human-readable text format and then create those structures automatically in your filesystem. This is particularly useful for quickly setting up project templates, scaffolding applications, or sharing directory structures in documentation.

## Motivation

This project was born out of a major pain point I faced repeatedly—manually creating project structures whenever I started a new project. Since I mostly adhere to the same structure unless there’s a specific need to modify it, I wanted a simple and efficient way to automate this process. Unfortunately, I couldn't find any good tools that fit my workflow.

Additionally, I often write proof-of-concept (POC) functionalities in a Jupyter notebook and later ask ChatGPT to break them down into a structured project format, including a tree with comments. `creatree` bridges this gap by allowing me to quickly generate well-organized project directories without unnecessary manual effort.

## Installation

### Using [`uv`](https://docs.astral.sh/uv)

To install `creatree` as a `uv` tool, run:

```bash
uv tool install creatree
```

### Using `pip`

Alternatively, install `creatree` via `pip`:

```bash
pip install creatree
```

## Usage

### As a Python Library

You can use `creatree` programmatically to generate directory structures.

#### Example Usage

```python
from creatree import creatree, tree_to_dict

# Define a directory tree as a string
tree = '''
example_project/ # Project root
├── main.py # Main entry point
├── config.yaml # Configuration file
├── src/ # Source code directory (Not empty)
│   ├── app.py # Application logic
│   └── utils.py # Utility functions
├── empty_directory/ # Empty directory (This will be created as it ends with /)
└── xyz_file # This will be created as a file as it doesn't end with /
'''

# Convert the tree string to a dictionary
tree_dict = tree_to_dict(tree, include_comments=False)
print(tree_dict)

# Create the directory structure in the current directory
# For each file that has a comment, it will be added to the file as a comment (Think of it like a TODO, except it's not explicit)
creatree(tree, where_to_create=".")
```

### As a CLI Tool

#### Create a directory tree from a file

If you have a text file (for example, `tree.txt`) containing the directory structure, you can create it using:

```bash
creatree tree.txt -w .
```

#### Use pipe to create directory trees

You can also define a directory tree inline using pipes:

```bash
echo "root1/
├── a # This comment will not be present in the a directory :(
│   ├── b.py # This comment will be added to b.py as a comment :)
│   └── c.py
├── d/
└── e.py" | creatree -w .
```

#### Generate a directory tree from an existing structure

You can capture an existing directory structure and replicate it elsewhere using `tree` and `creatree`:

```bash
tree /path/to/existing/directory | creatree -w /path/to/new/location
```

## Comparison with Other Tools

While there are other tools available for scaffolding projects, `creatree` offers a unique approach by allowing users to define directory structures in a simple, tree-like string format. This method provides a clear and concise way to visualize and create complex directory hierarchies without the need for extensive configuration files or templates.

## Features

- Convert a tree string to a structured dictionary.
- Generate directory structures automatically.
- Supports both Python API and CLI usage.
- Works with standard input (`stdin`) for flexible scripting.
- Useful for setting up project templates and scaffolding.
- Supports nested directory structures with file placeholders.
- Lightweight and easy to use.

## How to Contribute

We welcome contributions from the community! Here's how you can get involved:

1. **Fork the Repository**: Click on the 'Fork' button at the top right of the repository page to create a copy of the repository on your GitHub account.

2. **Clone the Forked Repository**: On your local machine, clone the forked repository using:

   ```bash
   git clone https://github.com/[yourusername]/creatree.git
   cd creatree
   ```

3. **Create a New Branch**: Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature-name
   ```

4. **Make Your Changes**: Implement your feature or fix the bug in your branch.

5. **Commit Your Changes**: Commit your changes with a descriptive commit message:

   ```bash
   git commit -m "Description of the feature or fix"
   ```

6. **Push to GitHub**: Push your changes to your forked repository:

   ```bash
   git push origin feature-name
   ```

7. **Create a Pull Request**: Go to the original repository and create a pull request from your forked repository. Provide a clear description of your changes and the motivation behind them.

Before contributing, please ensure that your code adheres to the project's coding standards and that all tests pass. If you're adding a new feature, consider including tests to cover the new functionality.

## License

`creatree` is released under the MIT License, allowing free use, modification, and distribution.

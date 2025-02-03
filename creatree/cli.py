"""
A command-line interface (CLI) for the creatree package.

This module provides a command-line entry point for the creatree package.
It allows users to create directory trees from a tree string. Also works with stdin (pipe).

Example:
    $ # Create directory trees from a tree string using pipe
    $ echo "root1/\n├── a\n│   ├── b.py\n│   └── c.py\n├── d/\n└── e.py\nroot2/\n├── f/\n└── g.py" | creatree -w .
    Created trees in root1, root2
    $ # Create a directory tree from a file
    $ echo "root3/\n├── h.py\n└── i.py" > tree.txt
    $ creatree tree.txt -w .
    Created tree in root3
"""

import os
from pathlib import Path
import sys
import argparse

from creatree.core import creatree


def format_paths(paths: list[Path]):
    return "'" + "', '".join(map(lambda x: x.absolute().as_posix(), paths)) + "'"

def creatree_cli(tree_string: str, where: str = "."):
    # Create the directory tree
    tree_dict = creatree(tree_string, where)
    roots = list(tree_dict.keys())

    print(f"Created tree{'s' if len(roots) > 1 else ''} in {', '.join(format_paths(roots))}")


def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Create directory structures from a tree string."
    )
    parser.add_argument(
        "tree",
        type=str,
        nargs="?",
        help="Path to a file containing the directory tree string",
    )
    parser.add_argument(
        "-w",
        "--where",
        type=str,
        default=".",
        help="Where to create the directory tree",
    )
    args = parser.parse_args()

    tree_file = args.tree
    
    # Handle input from pipe or file
    if tree_file:
        if not os.path.exists(tree_file):
            raise FileNotFoundError(f"File {tree_file} does not exist")
        
        if not os.path.isfile(tree_file):
            raise Exception(f"{tree_file} is not a file")
        
        # Read from file
        with open(tree_file, "r", encoding="utf-8") as f:
            tree_string = f.read()
    else:
        # Read from stdin (pipe)
        tree_string = sys.stdin.read()

    creatree_cli(tree_string=tree_string, where=args.where)


if __name__ == "__main__":
    main()

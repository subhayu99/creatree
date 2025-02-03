"""
The core module for the creatree package.

This module contains the `creatree` function along with supporting functions.
"""

import re
from pathlib import Path
from typing import NamedTuple

from creatree.config import (
    COMMENT_FINDER_REGEX,
    COMMENT_KEY,
    COMMENT_START_CHAR,
    PREFIXES,
)
from creatree.utils import (
    build_or_regex,
    is_root,
    remove_comments,
    replace_empty_dict_with_none,
)


class FileMetadata(NamedTuple):
    """
    A class to represent metadata for a file in a directory tree.

    Attributes:
        name (str): The name of the file or directory.
        index (int): The indentation level or index in the line.
        line_no (int): The line number where the file or directory is located.
        comment (str): Any comment associated with the file or directory.
    """

    name: str
    index: int
    line_no: int
    comment: str

    def __str__(self):
        return f"{' ' * self.index} {self.name}"


def _build_metadata_list(
    tree: str, prefixes: list[str] = PREFIXES
) -> list[FileMetadata]:
    """
    Build a list of file metadata from a tree string.

    Args:
        tree (str): The tree string to be parsed.
        prefixes (list[str], optional): The list of prefixes
            to be used to identify file names. Defaults to PREFIXES.

    Returns:
        list[FileMetadata]: The list of file metadata.
    """

    # Regular expression to find the name of a file or directory
    name_finder_regex = re.compile(f"(?:{build_or_regex(prefixes)})\s*(\S+)")

    datalist: list[FileMetadata] = []
    lines = tree.strip().splitlines()

    for lno, line in enumerate(lines):
        # Find any comment associated with the file or directory
        comment = (COMMENT_FINDER_REGEX.findall(line) or [""])[0]

        # Remove the comment from the line
        if comment:
            line = line.split(COMMENT_START_CHAR)[0].strip()

        # Find the name of the file or directory
        name: str = (name_finder_regex.findall(line) or [""])[0]

        if not name:
            # If the line is a root, assign the whole line as the name
            if not is_root(line):
                continue
            name = line

        index = line.find(name)
        datalist.append(FileMetadata(name, index, lno, comment))

    return datalist


def _build_tree_dict(
    datalist: list[FileMetadata], include_comments: bool = True
) -> dict[str, dict]:
    """
    Build a dictionary from the list of file metadata.

    Args:
        datalist (list[FileMetadata]): The list of file metadata.
        include_comments (bool, optional): Whether to include comments in the dictionary. Defaults to True.

    Returns:
        dict[str, dict]: The dictionary representing the directory tree.
    """
    tree = {}
    path_stack = []  # Stack to maintain the hierarchy

    for item in datalist:
        name = item.name
        index = item.index

        # Find the parent based on indentation
        while path_stack and path_stack[-1][1] >= index:
            path_stack.pop()

        # Get the current working dictionary level
        parent = tree if not path_stack else path_stack[-1][0]
        parent[name] = {COMMENT_KEY: item.comment}  # Initialize directory/file

        # If it's a directory, push it to the stack
        path_stack.append((parent[name], index))

    if not include_comments:
        tree = remove_comments(tree, COMMENT_KEY)
        tree = replace_empty_dict_with_none(tree)

    return tree


def tree_to_dict(
    tree: str, include_comments: bool = True, prefixes: list[str] = PREFIXES
):
    """
    Convert a tree string to a dictionary representation.

    Args:
        tree (str): The tree string to be converted.
        include_comments (bool, optional): Whether to include comments in the tree dictionary. Defaults to True.
        prefixes (list[str], optional): The list of prefixes used to identify file names. Defaults to PREFIXES.

    Returns:
        dict[str, dict]: A dictionary representing the directory tree.

    Example:
        >>> from creatree import tree_to_dict
        >>> tree = '''
        ...     example_project/ # Project root
        ...     │── main.py # Main entry point
        ...     │── config.yaml # Configuration file
        ...     │── src # Source code directory (Not empty)
        ...     │   │── app.py
        ...     │   │── utils.py
        ...     │── empty_directory/ # Empty directory (this will be created as it ends with /)
        ... '''
        >>> tree_dict = tree_to_dict(tree, include_comments=False)
        {
            'example_project/': {
                'main.py': None,
                'config.yaml': None,
                'src': {
                    'app.py': None,
                    'utils.py': None
                },
                'empty_directory/': {}
            }
        }
        >>> # Notice that the 'empty_directory/' directory has an empty dictionary indicating it is a directory
    """
    # Build a list of file metadata from the tree string
    metadata_list = _build_metadata_list(tree, prefixes)

    # Build and return the tree dictionary from the metadata list
    return _build_tree_dict(metadata_list, include_comments)


def create_tree(tree_dict: dict[str, dict], root: Path = Path(".")) -> None:
    """
    Recursively create the directory tree (in the local filesystem) based on the given tree dictionary.

    Args:
        tree_dict (dict[str, dict]): The dictionary representing the directory tree.
        root (Path, optional): The root directory to start creating the directory tree from.
            Defaults to the current working directory.
    """
    _tree_dict = tree_dict.copy()
    for key, value in _tree_dict.items():
        path = Path(root, key) if key != "." else Path(root)

        # Extract the comment associated with the file or directory
        comment = (value or {}).pop(COMMENT_KEY, "")
        # If the comment is not empty, add the comment to the file
        comment = f"# {comment}" if comment else ""
        if value or key.endswith("/"):
            path.mkdir(parents=True, exist_ok=True)
            # Recursively create the subtree
            create_tree(value, path)
        else:
            if path.exists():
                # If the file already exists, skip it
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(comment)


def creatree(
    tree: str,
    where_to_create: str = ".",
    prefixes: list[str] = PREFIXES,
) -> dict[Path, dict]:
    """
    Parse a directory tree string and create the directory tree accordingly.

    Args:
        tree (str): The directory tree string to be parsed.
        where_to_create (str, optional): The directory to create the directory tree from.
            Defaults to the current working directory.
        prefixes (list[str], optional): The list of prefixes to be used to identify file names.
            Defaults to PREFIXES.

    Returns:
        dict[Path, dict]: The dictionary representing the directory tree.
            Keys are the root directories and values are the tree dictionaries.

    Example:
        >>> from creatree import creatree
        >>> tree = '''
        ...     example_project/ # Project root
        ...     │── main.py # Main entry point
        ...     │── config.yaml # Configuration file
        ...     │── src # Source code directory (Not empty)
        ...     │   │── app.py
        ...     │   │── utils.py
        ...     │── empty_directory/ # Empty directory (this will be created as it ends with /)
        ... '''
        >>> tree_dict = creatree(tree, where_to_create=".") # Create the tree in the current directory
        >>> exit()
        $ ls
        example_project/
        $ tree ./example_project/
        .
        │── main.py
        │── config.yaml
        │── src
        │   │── app.py
        │   │── utils.py
        │── empty_directory/
    """
    where_to_create: Path = Path(where_to_create)
    tree_dict = tree_to_dict(tree, prefixes)
    create_tree(tree_dict, where_to_create)
    tree_dict = {(where_to_create / k): v for k, v in tree_dict.items()}
    return tree_dict

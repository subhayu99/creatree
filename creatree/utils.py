import re


def is_root(line: str):
    """Determine if a given line of a directory tree string represents the root."""
    return line == "." or len(line.strip()) > 1

def build_or_regex(options: list[str]):
    """
    Build a regular expression pattern that matches any of the given options.

    Args:
        options (list[str]): A list of strings to be matched.

    Returns:
        str: A regular expression string that matches any of the provided options.
    """
    return "|".join(re.escape(option) for option in (options))


def remove_comments(tree_dict: dict[str, dict], comment_key: str) -> dict[str, dict]:
    """
    Remove comments from the tree dictionary.

    Args:
        tree_dict (dict[str, dict]): The dictionary representing the directory tree.
        comment_key (str): The key in the dictionary that contains comments.

    Returns:
        dict[str, dict]: The dictionary without comments.
    """
    for key, value in tree_dict.items():
        if comment_key in value:
            value.pop(comment_key)
        if value:
            remove_comments(value, comment_key)
    return tree_dict

def replace_empty_dict_with_none(tree_dict: dict[str, dict]) -> dict[str, dict | None]:
    """
    Replace empty directories in the tree dictionary with None.

    Args:
        tree_dict (dict[str, dict]): The dictionary representing the directory tree.

    Returns:
        dict[str, dict | None]: The dictionary with empty directories replaced with None.
    """
    for key, value in tree_dict.items():
        # Replace empty directories with None if they don't end with /
        if not value and not key.endswith("/"):
            tree_dict[key] = None
        
        # Recursively replace empty directories    
        if value:
            replace_empty_dict_with_none(value)
    return tree_dict

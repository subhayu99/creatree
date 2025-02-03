import re


COMMENT_START_CHAR = "#"
"""
Character used to indicate the start of a comment.
"""

COMMENT_FINDER_REGEX = re.compile(f"{COMMENT_START_CHAR}\s+(.*)")
"""
Regular expression to find the comment associated with a file or directory.
"""

COMMENT_KEY = "___comment___"
"""
Key used to store comments in the tree dictionary.
"""

PREFIXES = ["├──", "└──", "├─", "└─", "│──", "│─", "|-", "|--", "+- ", "→ "]
"""
List of prefixes used to identify file names. These prefixes are taken from common tree representations.
"""

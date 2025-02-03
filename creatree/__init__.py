"""
The main module for the creatree package.

This module exports the `creatree` and `tree_to_dict` functions from the `main` module.

Example Usage:
    >>> # import the creatree and tree_to_dict functions
    >>> from creatree import creatree, tree_to_dict
    >>>
    >>> # define a directory tree
    >>> tree = '''
    ...     example_project/ # Project root
    ...     │── main.py # Main entry point
    ...     │── config.yaml # Configuration file
    ...     │── src # Source code directory (Not empty)
    ...     │   │── app.py
    ...     │   │── utils.py
    ...     │── empty_directory/ # Empty directory (this will be created as it ends with /)
    ... '''
    >>>
    >>> # convert the tree string to a dictionary (by default each file or directory will have a dictionary value with comment in the `COMMENT_KEY` key)
    >>> tree_dict = tree_to_dict(tree, include_comments=False)
    >>> # verify the tree dictionary
    >>> tree_dict
    {'example_project/': {'main.py': None, 'config.yaml': None, 'src': {'app.py': None, 'utils.py': None}, 'empty_directory/': {}}}
    >>> 
    >>> # create the directory tree in the current directory (also supports absolute path)
    >>> creatree(tree_dict)
    >>> tree_dict = creatree(tree, where_to_create=".") # Create the tree in the current directory
    >>> exit()
    $ ls
    example_project/
    $ tree ./example_project/
    .
    ├─ main.py
    ├─ config.yaml
    ├─ src/
    │   ├─ app.py
    │   └─ utils.py
    └─ empty_directory/
"""
from .core import creatree, tree_to_dict

__all__ = ["creatree", "tree_to_dict"]

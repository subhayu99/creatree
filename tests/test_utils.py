"""
Characterization tests for creatree.utils.

These document the *actual* current behavior of the small helper functions
used by creatree.core. No behavior is "fixed" here, only recorded.
"""
import re

from creatree.utils import (
    build_or_regex,
    is_root,
    remove_comments,
    replace_empty_dict_with_none,
)


class TestIsRoot:
    def test_dot_is_root(self):
        assert is_root(".") is True

    def test_single_char_line_is_not_root(self):
        # is_root() is `line == "." or len(line.strip()) > 1` -- a single
        # non-dot character has stripped length 1, which is not > 1.
        assert is_root("a") is False

    def test_multi_char_line_is_root(self):
        assert is_root("ab") is True

    def test_whitespace_only_line_is_not_root(self):
        # strips to "" (length 0), and it isn't the literal string "."
        assert is_root("   ") is False


class TestBuildOrRegex:
    def test_escapes_regex_metacharacters(self):
        pattern = build_or_regex(["a.b", "c*d", "|-"])
        assert pattern == "a\\.b|c\\*d|\\|\\-"

    def test_escaped_pattern_matches_literally_not_as_wildcard(self):
        pattern = build_or_regex(["a.b"])
        # A literal "." must not act as a regex "any character" wildcard.
        assert re.fullmatch(pattern, "a.b")
        assert re.fullmatch(pattern, "aXb") is None


class TestRemoveComments:
    def test_strips_comment_key_recursively(self):
        tree = {
            "a": {"___comment___": "x", "b": {"___comment___": "y"}},
            "c": {"___comment___": ""},
        }
        result = remove_comments(tree, "___comment___")
        assert result == {"a": {"b": {}}, "c": {}}

    def test_no_comment_key_left_at_any_depth(self):
        tree = {"a": {"___comment___": "x", "b": {"___comment___": "y"}}}
        result = remove_comments(tree, "___comment___")
        assert "___comment___" not in result["a"]
        assert "___comment___" not in result["a"]["b"]


class TestReplaceEmptyDictWithNone:
    def test_empty_dict_without_trailing_slash_becomes_none(self):
        tree = {"file.py": {}}
        result = replace_empty_dict_with_none(tree)
        assert result == {"file.py": None}

    def test_empty_dict_with_trailing_slash_stays_empty_dict(self):
        tree = {"dir/": {}}
        result = replace_empty_dict_with_none(tree)
        assert result == {"dir/": {}}

    def test_recurses_into_nonempty_values(self):
        tree = {"nested/": {"inner.py": {}}}
        result = replace_empty_dict_with_none(tree)
        assert result == {"nested/": {"inner.py": None}}

"""
Characterization tests for creatree.core.

These tests document the *actual* behavior of the tree-parsing and
tree-creation pipeline as implemented today, including a couple of
surprising edge cases (marked "QUIRK"). They intentionally assert the
observed behavior rather than a "corrected" one, so a future reimplementation
(e.g. a TS port) has a faithful behavioral spec to match.
"""
import pytest

from creatree.core import (
    _build_metadata_list,
    create_tree,
    creatree,
    tree_to_dict,
)


GLYPH_TREE = """
root/
├── a
│   ├── b.py
│   └── c.py
├── d/
└── e.py
"""


def test_tree_to_dict_glyph_nesting_include_comments_true():
    result = tree_to_dict(GLYPH_TREE, include_comments=True)
    assert result == {
        "root/": {
            "___comment___": "",
            "a": {
                "___comment___": "",
                "b.py": {"___comment___": ""},
                "c.py": {"___comment___": ""},
            },
            "d/": {"___comment___": ""},
            "e.py": {"___comment___": ""},
        }
    }


def test_tree_to_dict_glyph_nesting_include_comments_false():
    result = tree_to_dict(GLYPH_TREE, include_comments=False)
    assert result == {
        "root/": {
            "a": {"b.py": None, "c.py": None},
            "d/": {},
            "e.py": None,
        }
    }


def test_comment_captured_and_absent_comment_is_empty_string():
    tree = "root/\n├── a.py # first file\n└── b.py\n"
    result = tree_to_dict(tree, include_comments=True)
    assert result["root/"]["a.py"]["___comment___"] == "first file"
    assert result["root/"]["b.py"]["___comment___"] == ""


def test_multiple_roots_in_one_input():
    tree = "root1/\n├── a\nroot2/\n├── b\n"
    result = tree_to_dict(tree, include_comments=False)
    assert result == {"root1/": {"a": None}, "root2/": {"b": None}}


def test_deeper_nesting_three_plus_levels():
    tree = """
root/
├── a/
│   ├── b/
│   │   ├── c.py
│   │   └── d.py
│   └── e.py
└── f.py
"""
    result = tree_to_dict(tree, include_comments=False)
    assert result == {
        "root/": {
            "a/": {
                "b/": {"c.py": None, "d.py": None},
                "e.py": None,
            },
            "f.py": None,
        }
    }


@pytest.mark.parametrize("prefix", ["├──", "└──", "│──", "|-", "→ "])
def test_each_prefix_variant_is_recognized(prefix):
    tree = f"root/\n{prefix} a.py\n{prefix} b.py\n"
    result = tree_to_dict(tree, include_comments=False)
    assert result == {"root/": {"a.py": None, "b.py": None}}


def test_quirk_plain_indent_without_glyphs_produces_flat_roots():
    # QUIRK (known Python limitation): without one of the glyph prefixes
    # from config.PREFIXES, _build_metadata_list can't distinguish a
    # plain-indented child from a new root. is_root() only requires the
    # stripped line to be longer than one character, so EVERY line in a
    # glyph-less, plain-indented tree satisfies it and becomes its own
    # top-level entry. Because no prefix regex matched, the "name" is the
    # raw line, so leading whitespace also survives straight into the key.
    tree = "root/\n    child/\n"
    result = tree_to_dict(tree, include_comments=False)
    assert result == {"root/": {}, "    child/": {}}


def test_quirk_comment_stripping_can_corrupt_sibling_indentation():
    # QUIRK: when a line carries a "# comment", _build_metadata_list does
    # `line.split("#")[0].strip()` before locating the name -- and .strip()
    # discards leading whitespace only for that line. A sibling line without
    # a comment keeps its original leading whitespace. The two lines then
    # compute different `index` values even though they were written at the
    # same visual indentation, and since the tree builder nests purely by
    # comparing `index`, the sibling gets mis-nested as a child.
    tree = "root/\n  ├── a.py # comment here\n  ├── b.py\n"

    metadata = _build_metadata_list(tree)
    a_meta = next(m for m in metadata if m.name == "a.py")
    b_meta = next(m for m in metadata if m.name == "b.py")
    assert a_meta.index == 4  # leading 2 spaces stripped away by comment handling
    assert b_meta.index == 6  # leading 2 spaces preserved -- no comment on this line

    result = tree_to_dict(tree, include_comments=False)
    # b.py ends up nested *inside* a.py instead of being a's sibling.
    assert result == {"root/": {"a.py": {"b.py": None}}}


def test_create_tree_creates_dirs_and_files(tmp_path):
    tree_dict = {
        "root/": {
            "___comment___": "",
            "a.py": {"___comment___": "entry point"},
            "b.py": {"___comment___": ""},
            "sub/": {"___comment___": ""},
        }
    }
    create_tree(tree_dict, tmp_path)

    root = tmp_path / "root"
    assert root.is_dir()
    assert (root / "a.py").read_text() == "# entry point"
    assert (root / "b.py").read_text() == ""
    assert (root / "sub").is_dir()


def test_create_tree_skips_existing_file_and_preserves_content(tmp_path):
    (tmp_path / "root").mkdir()
    existing = tmp_path / "root" / "keep.txt"
    existing.write_text("ORIGINAL CONTENT")

    tree_dict = {"root/": {"keep.txt": {"___comment___": "new comment ignored"}}}
    create_tree(tree_dict, tmp_path)

    assert existing.read_text() == "ORIGINAL CONTENT"


def test_quirk_comment_written_into_any_file_type(tmp_path):
    # QUIRK: create_tree has no notion of file type or binary-ness. Any file
    # name -- including one that looks like a binary asset such as a .png --
    # gets the same "# <comment>" *text* written into it as file content.
    tree_dict = {"root/": {"img.png": {"___comment___": "not real image data"}}}
    create_tree(tree_dict, tmp_path)

    content = (tmp_path / "root" / "img.png").read_text()
    assert content == "# not real image data"


def test_creatree_end_to_end(tmp_path):
    tree = "proj/\n├── a.py # entry\n└── sub/\n    └── b.py\n"
    result = creatree(tree, where_to_create=str(tmp_path))

    proj_path = tmp_path / "proj"
    assert set(result.keys()) == {proj_path}
    assert proj_path.is_dir()
    assert (proj_path / "a.py").is_file()
    assert (proj_path / "sub" / "b.py").is_file()

    # QUIRK: create_tree() mutates the tree_dict it is given, in place -- it
    # pops "___comment___" out of every node's dict as it consumes the
    # comment to write file content. creatree() passes that same dict object
    # (by reference, inside the returned mapping) into create_tree(), so by
    # the time it comes back to the caller every comment has already been
    # stripped out, even though tree_to_dict() defaults to
    # include_comments=True.
    assert result[proj_path] == {"a.py": {}, "sub/": {"b.py": {}}}

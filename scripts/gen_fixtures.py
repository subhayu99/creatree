#!/usr/bin/env python3
"""
Generate parity fixtures for the TypeScript port of the creatree parser.

Each fixture is a JSON file capturing one glyph-tree input string and the
*exact* dictionary that `creatree.core.tree_to_dict(input, include_comments=True)`
produces for it. The TypeScript test suite deep-equals its own parse result
(converted to the same shape) against `expectedDict` to prove behavioral
parity with the Python reference implementation.

See: creatree-desktop/packages/parser/fixtures/README.md for the exact
fixture JSON shape and the rules for what may appear in `parity/` fixtures
(glyph-prefixed trees and root lines only -- no plain-indentation nesting,
no `$*N` repeaters, no bracketed copy paths; those are TS-only extensions
and belong in `extensions/`, authored by hand).

Usage:
    uv run python scripts/gen_fixtures.py [--out DIR]

`--out` defaults to `../creatree-desktop/packages/parser/fixtures/parity`
resolved relative to this repo's root (i.e. the directory containing this
script's parent, `scripts/..`).

This script only ever deletes/rewrites the `*.json` files it owns inside
the target directory -- rerunning it is idempotent and safe.
"""

import argparse
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from creatree.core import tree_to_dict

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = "../creatree-desktop/packages/parser/fixtures/parity"

MODE = "glyph-parity"


def _source_tag() -> str:
    """Build the `source` field, e.g. "python-creatree@0.1.4"."""
    try:
        v = version("creatree")
    except PackageNotFoundError:
        v = "0.0.0"
    return f"python-creatree@{v}"


# ---------------------------------------------------------------------------
# Fixture cases
#
# Each entry is (kebab-case name, input string). Only glyph-prefixed trees
# and root lines appear here -- see module docstring / fixtures README for
# why plain-indentation nesting and TS-only extensions are excluded.
#
# Across the whole suite every entry of `creatree.config.PREFIXES` appears
# at least once:
#   "├──" -> basic-glyph-tree, nested-three-levels, tree-command-output, ...
#   "└──" -> basic-glyph-tree, nested-three-levels, tree-command-output, ...
#   "├─", "└─", "│──", "│─", "|-", "|--", "+- ", "→ " -> prefix-variants
# ---------------------------------------------------------------------------

CASES: list[tuple[str, str]] = [
    (
        "basic-glyph-tree",
        # One root dir, a commented file, and an uncommented (empty) dir.
        # This is verbatim the worked example from the fixtures README.
        "root/\n├── a.py # entry\n└── docs/\n",
    ),
    (
        "nested-three-levels",
        # 4 levels deep in practice (project/ -> src/ -> utils/ -> helpers.py),
        # using ├──/└── branches and │   continuation-guide indentation.
        "project/\n"
        "├── src/\n"
        "│   ├── main.py\n"
        "│   └── utils/\n"
        "│       └── helpers.py\n"
        "└── README.md\n",
    ),
    (
        "empty-dir-trailing-slash",
        # "empty/" has no children of its own: with include_comments=True
        # its node is `{"___comment___": ""}` -- structurally empty aside
        # from the comment key (tree_to_dict never omits that key; a bare
        # `{}` only happens when include_comments=False, which parity
        # fixtures never use). "data/" is included as a non-empty sibling
        # for contrast.
        "project/\n├── data/\n│   └── file.txt\n└── empty/\n",
    ),
    (
        "comments-everywhere",
        # Root comment, directory comment, and file comment all in one tree.
        "root/ # root comment\n├── sub/ # dir comment\n│   └── file.txt # file comment\n",
    ),
    (
        "multiple-roots",
        # Two independent root trees back-to-back in one input string.
        "projectA/\n├── a.py\n└── b.py\nprojectB/\n├── c.py\n",
    ),
    (
        "prefix-variants",
        # Exercises 8 of the 10 config.PREFIXES entries in one tree
        # ("├──" and "└──" are covered by the other fixtures instead):
        #   ├─   │──   |-   |--   +-    →    └─   │─
        #
        # NOTE on "|--": PREFIXES lists "|-" *before* "|--", so the regex
        # alternation in _build_metadata_list always matches the shorter
        # "|-" first and the second "-" spills into the captured name. That
        # is genuine, documented behavior of the Python parser (not a typo
        # in this fixture) -- "|--delta.py" parses to the name "-delta.py".
        # A TS port must reproduce this quirk bug-for-bug to be at parity.
        #
        # Different prefixes consume different column widths before the
        # name starts (e.g. "├─ " puts the name at column 3, "│── " at
        # column 4), so mixing them at nominal "same level" indentation
        # naturally produces some incidental nesting below -- that is real,
        # verified parser behavior, not a mistake.
        "root/\n"
        "├─ alpha.py\n"
        "│── beta.py\n"
        "|- gamma.py\n"
        "|--delta.py\n"
        "+- epsilon.py\n"
        "→ zeta.py\n"
        "└─ eta.py\n"
        "│─ theta.py\n",
    ),
    (
        "tree-command-output",
        # Realistic output of the Unix `tree` command, including its
        # trailing blank line + "N directories, M files" summary line.
        # That summary line matches no prefix, is longer than one
        # character, and so is genuinely parsed as a second (bogus) root
        # entry by is_root()'s fallback -- verified real behavior, kept
        # here deliberately as a documented parser characteristic.
        ".\n"
        "├── LICENSE\n"
        "├── README.md\n"
        "├── src\n"
        "│   ├── index.js\n"
        "│   └── utils\n"
        "│       └── helpers.js\n"
        "└── package.json\n"
        "\n"
        "2 directories, 5 files\n",
    ),
    (
        "no-trailing-newline-blank-lines",
        # Leading blank lines (with stray indentation), trailing blank
        # lines, and no final newline. tree_to_dict() runs tree.strip()
        # over the whole input before splitting into lines, so all of
        # this is inert -- verified to parse identically to the clean case.
        "\n\n  root/\n├── a.py\n└── b.py",
    ),
    (
        "dot-root",
        # Root line is exactly ".", as produced by `tree` when run in the
        # current directory. is_root() special-cases line == "." so the
        # dict key is the literal string ".".
        ".\n├── a.py\n└── b.py\n",
    ),
    (
        "root-only",
        # A single root line with no children at all.
        "root/\n",
    ),
]


def wipe_owned_json(out_dir: Path) -> None:
    """Delete every *.json file this generator owns in `out_dir`."""
    if not out_dir.exists():
        return
    for f in out_dir.glob("*.json"):
        f.unlink()


def generate(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    wipe_owned_json(out_dir)

    source = _source_tag()
    written: list[Path] = []

    for name, input_str in CASES:
        expected_dict = tree_to_dict(input_str, include_comments=True)
        payload = {
            "name": name,
            "source": source,
            "mode": MODE,
            "input": input_str,
            "expectedDict": expected_dict,
        }

        out_path = out_dir / f"{name}.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        written.append(out_path)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"Output directory for fixtures (default: {DEFAULT_OUT}, "
        "resolved relative to this repo's root).",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (REPO_ROOT / out_dir).resolve()

    written = generate(out_dir)

    print(f"Wrote {len(written)} fixture(s) to {out_dir}")
    for path in written:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()

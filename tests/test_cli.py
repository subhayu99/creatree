"""
Characterization tests for the creatree console script (creatree.cli).

These drive the *installed* CLI entry point via `uv run creatree` in a
subprocess, exactly as an end user would invoke it, rather than calling
creatree.cli.main() in-process.
"""
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_cli(args, input_text=None):
    return subprocess.run(
        ["uv", "run", "creatree", *args],
        input=input_text,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_stdin_pipe_creates_tree(tmp_path):
    tree_str = "root/\n├── a.py # hi\n└── b.py\n"
    result = run_cli(["-w", str(tmp_path)], input_text=tree_str)

    assert result.returncode == 0
    assert "Created tree" in result.stdout
    assert (tmp_path / "root" / "a.py").is_file()
    assert (tmp_path / "root" / "b.py").is_file()


def test_tree_from_file_argument(tmp_path):
    tree_file = tmp_path / "tree.txt"
    tree_file.write_text("root2/\n├── c.py\n")

    result = run_cli([str(tree_file), "-w", str(tmp_path)])

    assert result.returncode == 0
    assert "Created tree" in result.stdout
    assert (tmp_path / "root2" / "c.py").is_file()


def test_missing_file_argument_raises_file_not_found(tmp_path):
    missing = tmp_path / "does_not_exist.txt"

    result = run_cli([str(missing), "-w", str(tmp_path)])

    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr
    assert "does not exist" in result.stderr

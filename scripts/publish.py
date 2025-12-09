#!/usr/bin/env python3
"""
Script to help publish creatree to PyPI.
"""

import re
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, check=True):
    """Run a command and print it."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def update_version_in_pyproject(new_version):
    """Update the version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    # Read the file
    content = pyproject_path.read_text()

    # Update version using regex
    version_pattern = r'^version = "[\d\.]+"'
    new_version_line = f'version = "{new_version}"'

    if not re.search(version_pattern, content, re.MULTILINE):
        print("Error: Could not find version line in pyproject.toml")
        sys.exit(1)

    updated_content = re.sub(version_pattern, new_version_line, content, flags=re.MULTILINE)

    # Write back to file
    pyproject_path.write_text(updated_content)
    print(f"✅ Updated version to {new_version} in pyproject.toml")


def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    version_match = re.search(r'^version = "([\d\.]+)"', content, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    return None


def main():
    # Check if version argument is provided
    if len(sys.argv) < 2:
        current_version = get_current_version()
        print("Usage: python scripts/publish.py <version>")
        if current_version:
            print(f"Current version: {current_version}")
        print("Example: python scripts/publish.py 0.1.4")
        sys.exit(1)

    new_version = sys.argv[1]

    # Validate version format (basic check)
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print(
            f"Error: Invalid version format '{new_version}'. Use semantic versioning (e.g., 0.1.4)"
        )
        sys.exit(1)

    # Ensure we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Run this from the project root.")
        sys.exit(1)

    print(f"🚀 Publishing creatree v{new_version} to PyPI")
    print("=" * 60)

    # Step 1: Update version in pyproject.toml
    print(f"\n1. Updating version to {new_version}...")
    current_version = get_current_version()
    if current_version:
        print(f"   Current version: {current_version}")
        print(f"   New version: {new_version}")
    update_version_in_pyproject(new_version)

    # Step 2: Run uv lock
    print("\n2. Updating dependency lock file...")
    run_cmd("uv lock")

    # Step 3: Git commit
    print("\n3. Committing version update...")
    run_cmd("git add pyproject.toml uv.lock")
    run_cmd(f'git commit -m "chore: upgrade to {new_version}"')

    # Step 4: Clean previous builds
    print("\n4. Cleaning previous builds...")
    run_cmd("rm -rf dist/ build/ *.egg-info/")

    # Step 5: Install build dependencies
    print("\n5. Installing build dependencies...")
    run_cmd("pip install --upgrade build twine")

    # Step 6: Build the package
    print("\n6. Building package...")
    run_cmd("python -m build")

    # Step 7: Check the package
    print("\n7. Checking package...")
    run_cmd("twine check dist/*")

    # Step 8: Show what will be uploaded
    print("\n8. Package contents:")
    run_cmd("ls -la dist/", check=False)

    # Step 9: Ask for confirmation
    response = input(f"\n9. Upload v{new_version} to PyPI? (y/N): ").strip().lower()
    if response != "y":
        print("Cancelled.")
        print("Note: Version has been updated and committed to git.")
        return

    # Step 10: Upload to PyPI
    print("\n10. Uploading to PyPI...")
    print("Note: You may need to enter your PyPI credentials or API token")
    run_cmd("twine upload dist/*")

    # Step 11: Create git tag (optional)
    tag_response = input(f"\n11. Create git tag v{new_version}? (y/N): ").strip().lower()
    if tag_response == "y":
        run_cmd(f"git tag v{new_version}")
        push_response = input("Push tag to remote? (y/N): ").strip().lower()
        if push_response == "y":
            run_cmd("git push origin --tags")

    print(f"\n✅ Successfully published v{new_version} to PyPI!")
    print("\nUsers can now install with:")
    print("  pip install creatree")
    print("  uv pip install creatree")
    print("  uv tool install creatree")


def test_upload():
    """Upload to TestPyPI first for testing."""
    if len(sys.argv) < 3:
        print("Usage: python scripts/publish.py test <version>")
        print("Example: python scripts/publish.py test 0.1.4")
        sys.exit(1)

    new_version = sys.argv[2]

    print(f"🧪 Testing upload of v{new_version} to TestPyPI")
    print("=" * 50)

    # Update version
    print(f"\n1. Updating version to {new_version}...")
    update_version_in_pyproject(new_version)

    # Update lock file
    print("\n2. Updating dependency lock file...")
    run_cmd("uv lock")

    # Clean and build
    print("\n3. Cleaning and building...")
    run_cmd("rm -rf dist/ build/ *.egg-info/")
    run_cmd("pip install --upgrade build twine")
    run_cmd("python -m build")
    run_cmd("twine check dist/*")

    # Upload to TestPyPI
    print("\n4. Uploading to TestPyPI...")
    run_cmd("twine upload --repository testpypi dist/*")

    print(f"\n✅ Test upload of v{new_version} complete!")
    print("\nTest installation with:")
    print(f"  pip install --index-url https://test.pypi.org/simple/ creatree=={new_version}")

    # Ask if they want to commit
    commit_response = input("\nCommit version update to git? (y/N): ").strip().lower()
    if commit_response == "y":
        run_cmd("git add pyproject.toml uv.lock")
        run_cmd(f'git commit -m "chore: upgrade to {new_version} (test)"')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_upload()
    else:
        main()

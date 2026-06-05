import os
from pathlib import Path
from typing import List

def scan_files(folder: Path) -> List[Path]:
    """Return a list of all file paths under *folder* (recursively) while excluding the .git directory.
    The returned paths are absolute ``Path`` objects.
    """
    files: List[Path] = []
    for root, dirs, filenames in os.walk(folder):
        # Skip .git directories
        if ".git" in dirs:
            dirs.remove('.git')
        for name in filenames:
            files.append(Path(root) / name)
    return files

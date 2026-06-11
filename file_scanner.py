import os
from pathlib import Path
from typing import List

# Optional third‑party library for .gitignore parsing
try:
    from pathspec import PathSpec
except ImportError:  # pragma: no cover
    PathSpec = None  # type: ignore[misc]


def _load_gitignore(folder: Path) -> PathSpec:
    """Load .gitignore patterns from *folder* using ``pathspec``.

    If a ``.gitignore`` file exists, its lines are read and combined with a set of
    default ignore patterns that cover common development artifacts. The resulting
    ``PathSpec`` object can be used to test whether a relative path should be
    ignored.
    """
    # Default patterns that are always ignored, even when no .gitignore exists.
    default_patterns = [
        "venv/",
        "__pycache__/",
        ".pytest_cache/",
        "node_modules/",
        ".idea/",
        ".vscode/",
    ]

    gitignore_path = folder / ".gitignore"
    if gitignore_path.is_file():
        with gitignore_path.open() as f:
            # Combine user‑defined patterns with defaults.
            lines = [line.rstrip() for line in f if line.strip() and not line.startswith("#")]
        patterns = default_patterns + lines
    else:
        # No .gitignore – use only the defaults.
        patterns = default_patterns

    # ``gitwildmatch`` provides the same rule set Git uses.
    return PathSpec.from_lines("gitwildmatch", patterns)


def scan_files(folder: Path) -> List[Path]:
    """Return a list of file paths that have changes (untracked or modified).
    
    If the directory is a git repository, it uses git to find changed files.
    Otherwise, it falls back to walking the directory and applying ignore rules.
    """
    try:
        from git import Repo, InvalidGitRepositoryError
        repo = Repo(folder)
        changed_files = set()
        
        # Untracked files
        for item in repo.untracked_files:
            changed_files.add(folder / item)
            
        # Modified or deleted files (not staged)
        for item in repo.index.diff(None):
            if item.a_path:
                changed_files.add(folder / item.a_path)
                
        # Staged files
        try:
            for item in repo.index.diff("HEAD"):
                if item.a_path:
                    changed_files.add(folder / item.a_path)
        except Exception:
            pass # HEAD might not exist yet in a fresh repo
            
        # Filter to ensure we only return existing files (ignoring deleted ones)
        files = [p for p in changed_files if p.is_file()]
        # Sort for deterministic output
        return sorted(files)
    except Exception:
        # Fallback if not a valid git repository or gitpython fails
        pass

    # Prepare the ignore matcher; fall back gracefully if ``pathspec`` is missing.
    spec = _load_gitignore(folder) if PathSpec is not None else None

    files: List[Path] = []
    for root, dirs, filenames in os.walk(folder):
        # Always skip the .git directory.
        if ".git" in dirs:
            dirs.remove('.git')
        # Compute relative root for pattern matching.
        rel_root = Path(root).relative_to(folder)
        for name in filenames:
            file_path = Path(root) / name
            # Build a path relative to the repository root for matching.
            rel_path = (rel_root / name).as_posix()
            # If we have a pathspec, use it to decide whether to ignore.
            if spec is not None and spec.match_file(rel_path):
                continue
            files.append(file_path)
    return files

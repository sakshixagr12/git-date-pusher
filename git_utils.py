import sys
from pathlib import Path
from git import Repo, GitCommandError

# Public wrapper functions expected by main.py

def ensure_git_repo(folder: Path) -> Repo:
    """Initialize or return existing Git repository in *folder*."""
    return initialize_git(folder)

def set_remote(folder: Path, remote_url: str) -> None:
    """Set or update the 'origin' remote for the repo in *folder*."""
    repo = ensure_git_repo(folder)
    setup_remote(repo, remote_url)

def commit_file(folder: Path, file_path: Path, commit_message: str, commit_date: str) -> None:
    """Commit *file_path* using the repo in *folder* with custom date."""
    repo = ensure_git_repo(folder)
    commit_file_internal(repo, file_path, commit_message, commit_date)

def push_branch(folder: Path, branch: str, force: bool = False) -> None:
    """Push *branch* from the repo in *folder* to its 'origin' remote."""
    repo = ensure_git_repo(folder)
    push_to_github(repo, branch, force)

# Internal helper implementations

def initialize_git(folder: Path) -> Repo:
    """Create a new git repo if missing, otherwise return existing repo."""
    if not folder.is_dir():
        raise NotADirectoryError(f"'{folder}' is not a valid directory")
    repo_path = folder / ".git"
    if repo_path.exists():
        print("✅ Git repository already initialized.")
        return Repo(folder)
    try:
        repo = Repo.init(folder)
        print("🔧 Initialized new Git repository.")
        return repo
    except GitCommandError as e:
        print(f"❌ Failed to initialise repository: {e}", file=sys.stderr)
        raise

def setup_remote(repo: Repo, remote_url: str) -> None:
    """Add or update the 'origin' remote for *repo*."""
    try:
        origin = repo.remote(name="origin")
        if origin.url != remote_url:
            resp = input(f"❓ Remote 'origin' points to {origin.url}. Override with {remote_url}? (y/N): ").strip().lower()
            if resp != "y":
                print("🛑 Keeping existing remote.")
                return
            origin.set_url(remote_url)
            print(f"✅ Remote 'origin' updated to {remote_url}")
    except ValueError:
        try:
            repo.create_remote('origin', remote_url)
            print(f"✅ Remote 'origin' set to {remote_url}")
        except GitCommandError as e:
            print(f"❌ Failed to create remote: {e}", file=sys.stderr)
            raise

def add_file(repo: Repo, file_path: Path) -> None:
    """Stage *file_path* for commit."""
    try:
        rel_path = file_path.relative_to(repo.working_tree_dir)
        repo.index.add([str(rel_path)])
        print(f"✅ Staged {rel_path}")
    except Exception as e:
        print(f"❌ Failed to stage {file_path}: {e}", file=sys.stderr)
        raise

def commit_file_internal(repo: Repo, file_path: Path, commit_message: str, commit_date: str) -> None:
    """Commit a file with a custom author/committer date (midday)."""
    try:
        add_file(repo, file_path)
        env = {
            "GIT_AUTHOR_DATE": f"{commit_date}T12:00:00",
            "GIT_COMMITTER_DATE": f"{commit_date}T12:00:00",
        }
        repo.git.commit('--allow-empty', '-m', commit_message, env=env)
        print(f"✅ Committed {file_path.name} with date {commit_date}")
    except GitCommandError as e:
        print(f"❌ Commit failed: {e}", file=sys.stderr)
        raise

def push_to_github(repo: Repo, branch: str, force: bool = False) -> None:
    """Push *branch* to the 'origin' remote on GitHub."""
    try:
        if force:
            repo.git.push('origin', branch, '--force')
        else:
            repo.git.push('origin', branch)
        print(f"🚀 Pushed branch '{branch}' to origin{' (force)' if force else ''}.")
    except GitCommandError as e:
        print(f"❌ Push failed: {e}", file=sys.stderr)
        raise

def get_current_branch(folder: Path) -> str:
    """Return the name of the currently checked‑out branch for *folder*.
    Raises a ValueError if the repository is in a detached HEAD state.
    """
    repo = ensure_git_repo(folder)
    try:
        return repo.active_branch.name
    except TypeError:
        # repo.active_branch is None when HEAD is detached
        raise ValueError("Repository is in a detached HEAD state; no active branch.")

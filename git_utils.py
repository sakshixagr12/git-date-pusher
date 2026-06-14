import sys
import time
from pathlib import Path
from git import Repo, GitCommandError

from typing import List

# Public wrapper functions expected by main.py

def ensure_git_repo(folder: Path) -> Repo:
    """Initialize or return existing Git repository in *folder*."""
    return initialize_git(folder)

def set_remote(folder: Path, remote_url: str) -> None:
    """Set or update the 'origin' remote for the repo in *folder*."""
    repo = ensure_git_repo(folder)
    setup_remote(repo, remote_url)

def commit_files(folder: Path, file_paths: List[Path], commit_message: str, commit_date: str) -> None:
    """Commit multiple *file_paths* using the repo in *folder* with custom date."""
    repo = ensure_git_repo(folder)
    commit_files_internal(repo, file_paths, commit_message, commit_date)

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

def add_files(repo: Repo, file_paths: List[Path]) -> None:
    """Stage a list of *file_paths* for commit."""
    try:
        rel_paths = [str(fp.relative_to(repo.working_tree_dir)) for fp in file_paths]
        repo.index.add(rel_paths)
        print(f"✅ Staged {len(rel_paths)} files")
    except Exception as e:
        print(f"❌ Failed to stage files: {e}", file=sys.stderr)
        raise

def commit_files_internal(repo: Repo, file_paths: List[Path], commit_message: str, commit_date: str) -> None:
    """Commit multiple files with a custom author/committer date (midday)."""
    try:
        add_files(repo, file_paths)
        env = {
            "GIT_AUTHOR_DATE": commit_date,
            "GIT_COMMITTER_DATE": commit_date,
        }
        repo.git.commit('--allow-empty', '-m', commit_message, env=env)
        print(f"✅ Committed {len(file_paths)} files with date {commit_date}")
    except GitCommandError as e:
        print(f"❌ Commit failed: {e}", file=sys.stderr)
        raise
def attempt_sync(repo: Repo, branch: str) -> bool:
    """Attempt to sync the local branch with origin/branch using rebase, fallback to merge."""
    print(f"🔄 Syncing local branch '{branch}' with remote...")
    try:
        # Try rebase first
        repo.git.pull('--rebase', 'origin', branch)
        print("✅ Sync successful (rebase).")
        return True
    except GitCommandError:
        print("⚠️ Rebase failed, attempting to abort and fallback to merge...")
        try:
            repo.git.rebase('--abort')
        except GitCommandError:
            pass # Ignore if not in rebase state
            
        try:
            # Fallback to merge safely
            repo.git.pull('--no-rebase', 'origin', branch)
            print("✅ Sync successful (merge).")
            return True
        except GitCommandError:
            print("❌ Merge fallback failed due to unresolvable conflicts.", file=sys.stderr)
            try:
                repo.git.merge('--abort')
            except GitCommandError:
                pass
            return False

def get_remote_state(folder: Path, branch: str) -> dict:
    """Fetch remote state and return a dict comparing local and upstream branch."""
    repo = ensure_git_repo(folder)
    state = {"status": "unknown", "ahead": 0, "behind": 0}
    try:
        # Read-only fetch to update remote tracking branch info
        repo.remotes.origin.fetch()
        
        # Check if the branch exists on remote
        if f"origin/{branch}" not in [r.name for r in repo.refs]:
            state["status"] = "no_upstream"
            return state
            
        ahead = sum(1 for _ in repo.iter_commits(f'origin/{branch}..{branch}'))
        behind = sum(1 for _ in repo.iter_commits(f'{branch}..origin/{branch}'))
        
        state["ahead"] = ahead
        state["behind"] = behind
        
        if ahead > 0 and behind > 0:
            state["status"] = "diverged"
        elif ahead > 0:
            state["status"] = "ahead"
        elif behind > 0:
            state["status"] = "behind"
        else:
            state["status"] = "clean"
            
    except Exception:
        # If fetch fails (e.g. no internet, wrong remote url), just ignore
        pass
    
    return state

def auto_recover(repo: Repo, branch: str, error_msg: str) -> bool:
    """Orchestrator for common git failures. Returns True if recovered."""
    error_msg = error_msg.lower()
    
    # 1. Non-fast-forward / Fetch First
    if "fetch first" in error_msg or "non-fast-forward" in error_msg or "updates were rejected" in error_msg:
        print("🔧 [RECOVERY] Detected remote changes ahead of local. Attempting auto-sync...")
        return attempt_sync(repo, branch)
        
    # 2. Missing branch / upstream not set
    if "has no upstream branch" in error_msg or "src refspec" in error_msg or "does not match any" in error_msg:
        print(f"🔧 [RECOVERY] Missing upstream branch '{branch}'. Setting upstream and pushing...")
        try:
            repo.git.push('--set-upstream', 'origin', branch)
            print("✅ [RECOVERY] Successfully pushed and set upstream.")
            return True
        except GitCommandError as e:
            print(f"❌ [RECOVERY] Failed to push upstream: {e}", file=sys.stderr)
            return False
            
    # 3. Remote connection errors
    if "could not read from remote" in error_msg or "repository not found" in error_msg:
        print("❌ [RECOVERY] Remote repository access failed. Check origin URL and permissions.", file=sys.stderr)
        return False
        
    return False

def sync_and_push(repo: Repo, branch: str) -> None:
    """Auto-sync engine: checks remote, syncs if behind, pushes with retries."""
    MAX_RETRIES = 3
    
    # Ensure remote tracking branch information is up to date
    try:
        repo.git.fetch('origin')
    except GitCommandError as e:
        print(f"⚠️ Could not fetch from origin: {e}")
        # Continue to attempt push anyway
        
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            repo.git.push('origin', branch)
            return # Push succeeded!
        except GitCommandError as e:
            error_msg = str(e)
            print(f"⚠️ Push rejected on attempt {attempt}/{MAX_RETRIES}.")
            if attempt >= MAX_RETRIES:
                print("❌ Max recovery retries exceeded. Manual intervention required.", file=sys.stderr)
                raise
                
            # Attempt auto-recovery
            if not auto_recover(repo, branch, error_msg):
                print("❌ Auto-recovery failed. Please resolve manually.", file=sys.stderr)
                raise

def push_to_github(repo: Repo, branch: str, force: bool = False) -> None:
    """Push *branch* to the 'origin' remote on GitHub using auto-sync unless forced."""
    try:
        if force:
            repo.git.push('origin', branch, '--force')
        else:
            sync_and_push(repo, branch)
        print(f"🚀 Pushed branch '{branch}' to origin{' (force)' if force else ''}.")
    except GitCommandError as e:
        print(f"❌ Push failed: {e}", file=sys.stderr)
        raise

def get_current_branch(folder: Path) -> str:
    """Return the name of the currently checked‑out branch for *folder*.
    Attempts auto-recovery if in detached HEAD.
    """
    repo = ensure_git_repo(folder)
    try:
        return repo.active_branch.name
    except TypeError:
        print("⚠️ [RECOVERY] Detected detached HEAD state.")
        # Try to find if any branch points to current commit
        current_commit = repo.head.commit
        for branch in repo.heads:
            if branch.commit == current_commit:
                print(f"🔧 [RECOVERY] Found branch '{branch.name}' at current commit. Checking out...")
                branch.checkout()
                return branch.name
        
        # Otherwise, create a recovery branch
        recovery_branch = f"recovery-{int(time.time())}"
        print(f"🔧 [RECOVERY] No existing branch found at HEAD. Creating branch '{recovery_branch}'...")
        new_branch = repo.create_head(recovery_branch)
        new_branch.checkout()
        return recovery_branch

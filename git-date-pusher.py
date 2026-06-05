#!/usr/bin/env python3
"""git-date-pusher.py

A tiny interactive helper that walks you through adding a date‑stamped commit for every file
in a folder and pushes the result to a GitHub repository.

Features
--------
1. Prompt for a folder that contains the files you want to version.
2. Initialise a git repository in that folder (or use the existing one).
3. Prompt for the remote GitHub URL and the target branch (default ``main``).
4. List all files (ignoring the ``.git`` directory).
5. Choose one of two modes:
   * **Mode 1** – ask for a date *per file*.
   * **Mode 2** – use a single date for *all* files.
6. For each file ask for a commit message (default ``Add <filename>``) and create a commit
   with the supplied date.
7. Push the commits to the remote.

The script is deliberately simple – it only relies on the standard library and the
``git`` executable being available in ``PATH``.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

def run_git(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run a ``git`` command in *cwd* and return the CompletedProcess.

    Errors are printed to ``stderr`` and the script exits with a non‑zero status.
    """
    result = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Git error: {' '.join(args)}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result


def prompt(message: str, default: str | None = None) -> str:
    """Display *message* and return the user's input.

    If the user just hits **Enter** and *default* is provided, the default value is returned.
    """
    if default is not None:
        prompt_msg = f"{message} [{default}]: "
    else:
        prompt_msg = f"{message}: "
    response = input(prompt_msg).strip()
    return response if response else (default if default is not None else "")


def ask_folder() -> Path:
    while True:
        folder = prompt("📁 Folder path (absolute)")
        p = Path(folder).expanduser().resolve()
        if p.is_dir():
            return p
        print(f"❌ '{folder}' is not a valid directory. Please try again.")


def ensure_git_repo(repo_path: Path) -> None:
    if (repo_path / ".git").exists():
        print("✅ Git repository already initialised.")
        return
    print("Initialising new git repository…")
    run_git(["init"], cwd=repo_path)
    print(" Repository initialised.")


def set_remote(repo_path: Path) -> None:
    # Check if a remote named 'origin' already exists
    existing = run_git(["remote"], cwd=repo_path).stdout.strip().splitlines()
    if "origin" in existing:
        # Ask whether to override
        answer = prompt(" Remote 'origin' already configured. Override? (y/N)", default="N")
        if answer.lower() != "y":
            print(" Keeping existing remote configuration.")
            return
        run_git(["remote", "remove", "origin"], cwd=repo_path)
    url = prompt(" GitHub repository URL (e.g. https://github.com/user/repo.git)")
    if not url:
        print(" No URL provided – aborting.")
        sys.exit(1)
    run_git(["remote", "add", "origin", url], cwd=repo_path)
    print("✅ Remote 'origin' set.")


def get_branch() -> str:
    branch = prompt("🌿 Branch name", default="main")
    return branch


def list_files(repo_path: Path) -> List[Path]:
    files = []
    for root, _, filenames in os.walk(repo_path):
        # Skip the .git directory entirely
        if ".git" in root.split(os.sep):
            continue
        for fn in filenames:
            file_path = Path(root) / fn
            # Store relative path for git commands
            files.append(file_path.relative_to(repo_path))
    return files


def select_mode() -> int:
    print("\n🛠️  Choose a commit date mode:")
    print("  1) Ask for a date **per file** (more granular)")
    print("  2) Use a **single date** for all files (quick)")
    while True:
        choice = prompt("Enter 1 or 2")
        if choice in {"1", "2"}:
            return int(choice)
        print("❌ Invalid choice – please type 1 or 2.")


def default_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def commit_file(repo_path: Path, rel_path: Path, commit_date: str, message: str) -> None:
    # Stage the file
    run_git(["add", str(rel_path)], cwd=repo_path)
    # Use the ISO 8601 format accepted by Git for --date
    iso_date = f"{commit_date}T12:00:00"
    run_git(["commit", "--date", iso_date, "-m", message], cwd=repo_path)
    print(f"✅ Committed {rel_path} with date {commit_date}")


def push_branch(repo_path: Path, branch: str) -> None:
    print(f"🚀 Pushing to origin/{branch} …")
    run_git(["push", "-u", "origin", branch], cwd=repo_path)
    print("✅ Push completed.")


def main() -> None:
    repo_path = ask_folder()
    ensure_git_repo(repo_path)
    set_remote(repo_path)
    branch = get_branch()
    # Ensure we are on the correct branch
    run_git(["checkout", "-B", branch], cwd=repo_path)

    all_files = list_files(repo_path)
    if not all_files:
        print("❌ No files found in the folder (excluding .git). Exiting.")
        sys.exit(0)
    print(f"\n📄 Found {len(all_files)} file(s):")
    for i, f in enumerate(all_files, 1):
        print(f"  {i}. {f}")

    mode = select_mode()
    if mode == 2:
        # One date for all files
        shared_date = prompt("📅 Date for all files (YYYY-MM-DD)", default=default_date())
    else:
        shared_date = None

    for idx, rel_path in enumerate(all_files, 1):
        print(f"\n--- File {idx}/{len(all_files)}: {rel_path} ---")
        if mode == 1:
            commit_date = prompt("📅 Commit date (YYYY-MM-DD)", default=default_date())
        else:
            commit_date = shared_date
        default_msg = f"Add {rel_path.name}"
        commit_msg = prompt("💬 Commit message", default=default_msg)
        commit_file(repo_path, rel_path, commit_date, commit_msg)

    push_branch(repo_path, branch)
    print("\n🎉 All done! Your changes have been pushed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✋ Interrupted by user. Exiting.")
        sys.exit(1)

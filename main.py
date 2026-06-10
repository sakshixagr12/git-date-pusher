# Git Date Pusher
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from git import GitCommandError

# Project utilities
from git_utils import ensure_git_repo, set_remote, commit_file, push_branch, get_current_branch
from file_scanner import scan_files
from date_handler import get_today_str

# Rich UI helpers
from rich_interface import (
    welcome,
    status,
    display_commit_mode_menu,
    choose_multiple_files,
    choose_single_file,
    console,
)
from rich.prompt import Prompt, Confirm


def get_valid_date(prompt: str) -> str:
    """Prompt for a date in YYYY‑MM‑DD format, default today."""
    while True:
        user_input = Prompt.ask(prompt, default="").strip()
        if not user_input:
            return get_today_str()
        try:
            datetime.strptime(user_input, "%Y-%m-%d")
            return user_input
        except ValueError:
            console.print("❌ Invalid date format. Please use YYYY‑MM‑DD.", style="red")


def generate_commit_message(file_path: os.PathLike) -> str:
    """Generate a human‑readable commit message based on filename/extension.

    Known mappings:
        *.html  -> "Create homepage structure" (for index.html)
        *.html  -> "Create <name> page" (for other html files)
        *.css   -> "Add application styling"
        *.js    -> "Implement application logic"
        *.py    -> "Add Python script"
        *.json  -> "Add JSON configuration"
        *.md    -> "Update project documentation"
        README.*-> "Update project documentation"
    Fallback: "Add <filename>"
    """
    filename = os.path.basename(str(file_path))
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext == ".html":
        if name.lower() == "index":
            return "Create homepage structure"
        return f"Create {name} page"
    if ext == ".css":
        return "Add application styling"
    if ext == ".js":
        return "Implement application logic"
    if ext == ".py":
        return "Add Python script"
    if ext == ".json":
        return "Add JSON configuration"
    if ext == ".md" or name.lower().startswith("readme"):
        return "Update project documentation"
    return f"Add {filename}"


def main():
    # Welcome banner
    welcome()

    parser = argparse.ArgumentParser(description="Git Date Pusher")
    parser.add_argument("-d", "--directory", type=Path, help="Folder containing files")
    parser.add_argument("-r", "--remote", help="GitHub repository URL")
    parser.add_argument("-b", "--branch", help="Target branch (defaults to current branch)")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without modifying the repository")
    parser.add_argument("--auto-message", action="store_true", help="Automatically accept generated commit messages without prompting")
    parser.add_argument("-m", "--mode", choices=["1", "2"], default="1", help="1: date per file, 2: one date for all")
    args = parser.parse_args()

    # Resolve directory
    folder = args.directory or Path(Prompt.ask("📁 Folder path (absolute)")).resolve()

    # Choose commit mode via Rich UI (1=all,2=multiple,3=single)
    commit_mode = str(display_commit_mode_menu())

    # Initialise repo (skip in dry‑run)
    if not args.dry_run:
        ensure_git_repo(folder)
        remote_url = args.remote or Prompt.ask("🔗 GitHub repo URL", default="")
        if remote_url:
            set_remote(folder, remote_url)

    # Determine branch
    branch = args.branch or get_current_branch(folder)

    all_files = scan_files(folder)
    if not all_files:
        console.print("No files found.", style="red")
        return

    # Determine files to process based on UI selection
    if commit_mode == "1":
        files_to_process = all_files
    elif commit_mode == "2":
        files_to_process = choose_multiple_files(all_files)
    elif commit_mode == "3":
        files_to_process = choose_single_file(all_files)
    else:
        console.print(f"Invalid commit mode selected: {commit_mode}", style="red")
        return

    # Shared date handling when CLI mode flag "-m 2" is used
    shared_date = None
    if args.mode == "2":
        shared_date = get_valid_date("📅 Date for all files")

    successes, failures = [], []

    for file_path in files_to_process:
        commit_date = shared_date if shared_date else get_valid_date(f"📅 Date for {file_path.name}")
        generated_msg = generate_commit_message(file_path)
        if args.auto_message or Confirm.ask(f"Use generated message: '{generated_msg}'?", default=True):
            msg = generated_msg
        else:
            msg = Prompt.ask(f"💬 Commit message for {file_path.name}", default=f"Add {file_path.name}")
        if args.dry_run:
            console.print(f"[DRY RUN] Would commit {file_path.name} on {commit_date}")
            successes.append(str(file_path))
        else:
            try:
                commit_file(folder, file_path, msg, commit_date)
                successes.append(str(file_path))
            except GitCommandError as e:
                failures.append((str(file_path), str(e)))

    # Summary output
    console.print("\n[bold]=== Commit Summary ===")
    for f in successes:
        console.print(f"✅ {f}")
    for f, err in failures:
        console.print(f"❌ {f}: {err}")

    if not args.dry_run:
        try:
            push_branch(folder, branch)
            console.print("🚀 Push completed successfully.", style="green")
        except GitCommandError as e:
            console.print(f"❌ Push failed: {e}", style="red")

if __name__ == "__main__":
    main()

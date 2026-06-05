# Git Date Pusher
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from git import GitCommandError

from git_utils import ensure_git_repo, set_remote, commit_file, push_branch, get_current_branch
from file_scanner import scan_files
from date_handler import get_today_str


def get_valid_date(prompt: str) -> str:
    """Prompt for a date in YYYY-MM-DD format, default today."""
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            return get_today_str()
        try:
            datetime.strptime(user_input, "%Y-%m-%d")
            return user_input
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")


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
    parser = argparse.ArgumentParser(description="Git Date Pusher")
    parser.add_argument("-d", "--directory", type=Path, help="Folder containing files")
    parser.add_argument("-r", "--remote", help="GitHub repository URL")
    parser.add_argument("-b", "--branch", help="Target branch (defaults to current branch)")
    parser.add_argument("-m", "--mode", choices=["1", "2"], default="1",
                        help="1: date per file, 2: one date for all")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show actions without modifying the repository")
    parser.add_argument("--auto-message", action="store_true",
                        help="Automatically accept generated commit messages without prompting")
    args = parser.parse_args()

    folder = args.directory or Path(input("📁 Folder path (absolute) ")).resolve()

    # Repository setup (skip in dry‑run)
    if not args.dry_run:
        ensure_git_repo(folder)
        remote_url = args.remote or input("🔗 GitHub repo URL: ").strip()
        if remote_url:
            set_remote(folder, remote_url)
    else:
        remote_url = args.remote or input(
            "🔗 GitHub repo URL (dry‑run, press Enter to skip): ").strip()
        if remote_url:
            print(f"[DRY RUN] Would set remote to {remote_url}")

    # Determine branch
    if args.branch:
        branch = args.branch
    else:
        try:
            branch = get_current_branch(folder)
            print(f"Detected current branch: '{branch}'")
        except Exception as e:
            print(f"Failed to detect current branch: {e}", file=sys.stderr)
            return

    files = scan_files(folder)
    if not files:
        print("No files found.")
        return

    shared_date = None
    if args.mode == "2":
        shared_date = get_valid_date("📅 Date for all files (YYYY-MM-DD, Enter=today) ")

    successes = []
    failures = []

    for file_path in files:
        commit_date = shared_date if args.mode == "2" else get_valid_date(
            f"📅 Date for {file_path.name} (YYYY-MM-DD, Enter=today) ")
        generated_msg = generate_commit_message(file_path)
        if args.auto_message:
            msg = generated_msg
        else:
            use_generated = input(
                f'Generated message: "{generated_msg}". Use this? (Y/n): '
            ).strip().lower()
            if use_generated in ("", "y", "yes"):
                msg = generated_msg
            else:
                msg = input(
                    f"💬 Commit message for {file_path.name} (Enter=Add {file_path.name}) "
                ).strip()
                if not msg:
                    msg = f"Add {file_path.name}"
        if args.dry_run:
            print(f"[DRY RUN] Would commit {file_path} with message '{msg}' on date {commit_date}")
            successes.append(str(file_path))
        else:
            try:
                commit_file(folder, file_path, msg, commit_date)
                successes.append(str(file_path))
            except GitCommandError as e:
                failures.append((str(file_path), str(e)))

    # Summary
    print("\n=== Commit Summary ===")
    if successes:
        print("✅ Successful commits:")
        for f in successes:
            print(f"  - {f}")
    if failures:
        print("❌ Failed commits:")
        for f, err in failures:
            print(f"  - {f}: {err}")

    if args.dry_run:
        print("[DRY RUN] Completed without making any changes.")
    else:
        try:
            push_branch(folder, branch)
            print("🚀 Push completed successfully.")
        except GitCommandError as e:
            print(f"❌ Push failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

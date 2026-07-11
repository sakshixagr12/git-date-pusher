# Git Date Pusher
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from git import GitCommandError

# Project utilities
from git_utils import ensure_git_repo, set_remote, commit_files, push_branch, get_current_branch
from file_scanner import scan_files
from date_handler import get_today_str, get_valid_datetime, get_timeline_input, generate_date_schedule

# Rich UI helpers
from rich_interface import (
    welcome,
    status,
    display_commit_mode_menu,
    choose_multiple_files,
    choose_single_file,
    commit_preview,
    run_dry_preview,
    display_date_mode_menu,
    timeline_preview,
    console,
)
from rich.prompt import Prompt, Confirm
from collections import defaultdict

def group_files(files: list[Path]) -> list[list[Path]]:
    """Group files by top-level directory and then by extension."""
    groups = defaultdict(list)
    for f in files:
        ext = f.suffix.lower()
        parent = f.parent.name
        groups[(parent, ext)].append(f)
    return list(groups.values())

def generate_commit_message(files: list[str]) -> str:
    """Generate a human‑readable commit message based on filenames/extensions."""
    if not files:
        return "Update project files"
        
    if len(files) == 1:
        f = files[0]
        name = Path(f).name
        name_lower = name.lower()
        
        if name_lower == "index.html": return "Create homepage"
        if name_lower == "dashboard.html": return "Create dashboard page"
        if name_lower == "login.html": return "Create login page"
        if name_lower in ["register.html", "signup.html"]: return "Create registration page"
        if name_lower == "style.css": return "Add application styling"
        if name_lower == "app.js": return "Implement application logic"
        if name_lower == "main.py": return "Implement main functionality"
        if name_lower == "readme.md": return "Update project documentation"
        if name_lower == "rest.html": return "Create restaurant page"
        
        stem = Path(f).stem
        clean_name = stem.replace("-", " ").replace("_", " ").lower()
        
        if clean_name.endswith("page") or clean_name.endswith("homepage"):
            return f"Create {clean_name}"
        else:
            return f"Create {clean_name} page"
            
    exts = set()
    for f in files:
        _, ext = os.path.splitext(f)
        exts.add(ext.lower())
        
    if len(exts) == 1:
        ext = exts.pop()
        if ext == ".html":
            return "Update web page"
        elif ext == ".css":
            return "Improve styling"
        elif ext == ".js":
            return "Enhance functionality"
        elif ext == ".pdf":
            return "Add document"
        elif ext == ".py":
            return "Add Python script"
        elif ext == ".json":
            return "Add JSON configuration"
        elif ext in {".md", ".txt"}:
            return "Update documentation"
            
    # If multiple types exist
    if {".html", ".css", ".js"}.intersection(exts):
        return "Update web project assets"
        
    return "Update project files"

def prompt_commit_message(batch_name: str, generated_msg: str) -> str:
    """Prompt the user for a commit message, allowing them to accept the generated one or enter a custom one."""
    if Confirm.ask(f"Use generated message: '{generated_msg}' for {batch_name}?", default=True):
        console.print(f"[green]✓ Using generated message[/green]\n  {generated_msg}\n")
        return generated_msg
    else:
        while True:
            msg = Prompt.ask("Enter custom commit message").strip()
            if msg:
                console.print(f"[cyan]✓ Using custom message[/cyan]\n  {msg}\n")
                return msg
            console.print("[red]Message cannot be empty. Please enter a valid message.[/red]")

def main():
    # Welcome banner
    welcome()

    parser = argparse.ArgumentParser(description="Git Date Pusher")
    parser.add_argument("-d", "--directory", type=Path, help="Folder containing files")
    parser.add_argument("-r", "--remote", help="GitHub repository URL")
    parser.add_argument("-b", "--branch", help="Target branch (defaults to current branch)")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without modifying the repository")
    parser.add_argument("--auto-message", action="store_true", help="Automatically accept generated commit messages without prompting")
    parser.add_argument("-f", "--force", action="store_true", help="Force push to the remote repository")
    parser.add_argument("-m", "--mode", choices=["1", "2", "3"], help="1: one date for all, 2: date per file, 3: timeline mode")
    # Smart default flags – mutually exclusive
    smart_group = parser.add_mutually_exclusive_group()
    smart_group.add_argument("--now", action="store_true", help="Use current date and time")
    smart_group.add_argument("--today", action="store_true", help="Use today at 12:00:00")
    smart_group.add_argument("--yesterday", action="store_true", help="Use yesterday at 12:00:00")
    smart_group.add_argument("--last-week", action="store_true", help="Use date 7 days ago at 12:00:00")
    
    # Batching flags
    parser.add_argument("--all", action="store_true", help="Group all modified files into intelligent batches")
    parser.add_argument("--folder", type=Path, help="Target a specific subdirectory to group its files into a single batch commit")
    
    args = parser.parse_args()

    # Determine which smart flag (if any) was provided
    smart_flag = None
    if getattr(args, "now", False):
        smart_flag = "--now"
    elif getattr(args, "today", False):
        smart_flag = "--today"
    elif getattr(args, "yesterday", False):
        smart_flag = "--yesterday"
    elif getattr(args, "last_week", False):
        smart_flag = "--last-week"

    # Resolve directory
    folder = args.directory or Path(Prompt.ask("📁 Folder path (absolute)")).resolve()

    # Choose commit mode via Rich UI (1=all,2=multiple,3=single) if not batched
    commit_mode = "batch" if args.all or args.folder else str(display_commit_mode_menu())

    # Initialise repo (skip in dry‑run)
    if not args.dry_run:
        ensure_git_repo(folder)
        remote_url = args.remote or Prompt.ask("🔗 GitHub repo URL", default="")
        if remote_url:
            set_remote(folder, remote_url)

    # Determine branch
    branch = args.branch or get_current_branch(folder)

    # Scan files respecting .gitignore etc.
    if args.folder:
        target_dir = (folder / args.folder).resolve()
        all_files = scan_files(target_dir)
    else:
        all_files = scan_files(folder)
        
    if not all_files:
        console.print("No files found.", style="red")
        return

    # Determine batches based on UI selection or flags
    grouped_batches = []
    if args.folder:
        grouped_batches = [all_files]
    elif args.all:
        grouped_batches = group_files(all_files)
    else:
        if commit_mode == "1":
            files_to_process = all_files
        elif commit_mode == "2":
            files_to_process = choose_multiple_files(all_files)
        elif commit_mode == "3":
            files_to_process = choose_single_file(all_files)
        else:
            console.print(f"Invalid commit mode selected: {commit_mode}", style="red")
            return
        grouped_batches = [[f] for f in files_to_process]

    # Determine Date Mode
    date_mode = args.mode if args.mode else display_date_mode_menu()

    # Shared date handling when date mode is "1" (Same Date For All Files)
    shared_date = None
    if date_mode == "1":
        shared_date = get_valid_datetime("📅 Date for all files", smart_flag=smart_flag)

    # Build commit plan
    commits = []
    if date_mode == "3":
        start_date_str, end_date_str, time_str = get_timeline_input()
        schedule = generate_date_schedule(start_date_str, end_date_str, len(grouped_batches), time_str)
        
        # Calculate average gap
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        gap_days = (end_dt - start_dt).days
        avg_gap = round(gap_days / max(1, len(grouped_batches) - 1), 2) if len(grouped_batches) > 1 else 0
        
        preview_items = []
        for i, batch in enumerate(grouped_batches):
            batch_name = batch[0].name if len(batch) == 1 else f"{len(batch)} files in {batch[0].parent.name}"
            generated_msg = generate_commit_message([str(f) for f in batch])
            preview_items.append((batch_name, schedule[i], generated_msg))
            
        summary_info = {
            "files": len(grouped_batches),
            "start": start_date_str,
            "end": end_date_str,
            "time": time_str,
            "gap": avg_gap
        }
            
        # Print timeline preview table
        timeline_preview(preview_items)
            
        # Bulk message confirmation
        if args.auto_message:
            accept_all = True
        else:
            accept_all = Confirm.ask("Accept all generated commit messages?", default=True)
            
        for i, batch in enumerate(grouped_batches):
            batch_name, commit_date, generated_msg = preview_items[i]
            if accept_all:
                msg = generated_msg
            else:
                msg = prompt_commit_message(batch_name, generated_msg)
            commits.append((batch, msg, commit_date))
    else:
        for batch in grouped_batches:
            batch_name = batch[0].name if len(batch) == 1 else f"{len(batch)} files in {batch[0].parent.name}"
            commit_date = shared_date if shared_date else get_valid_datetime(f"📅 Date for {batch_name}", smart_flag=smart_flag)
            generated_msg = generate_commit_message([str(f) for f in batch])
            if args.auto_message:
                msg = generated_msg
            else:
                msg = prompt_commit_message(batch_name, generated_msg)
            commits.append((batch, msg, commit_date))

    # Show preview and ask for confirmation
    summary_info = summary_info if date_mode == "3" else None
    if not commit_preview(repo_name=folder.name, branch=branch, commit_items=commits, summary_info=summary_info):
        console.print("Process cancelled by user.")
        return

    if args.dry_run:
        repo_state = {
            "repo_name": folder.name,
            "branch": branch,
            "remote": remote_url if "remote_url" in locals() and remote_url else "origin",
            "commits": commits
        }
        console.print(f"[bold yellow]{run_dry_preview(repo_state)}[/bold yellow]")
        return
        
    successes, failures = [], []
    from git_utils import commit_files
    total_commits = len(commits)
    for idx, (batch, msg, commit_date) in enumerate(commits, start=1):
        batch_name = batch[0].name if len(batch) == 1 else f"{len(batch)} files in {batch[0].parent.name}"
        try:
            commit_files(folder, batch, msg, commit_date)
            for f in batch:
                successes.append(str(f))
            console.print(f"[green]✓ [{idx}/{total_commits}] {batch_name}[/green]\n    Message: {msg}\n")
        except GitCommandError as e:
            for f in batch:
                failures.append((str(f), str(e)))
            console.print(f"[red]❌ [{idx}/{total_commits}] {batch_name}[/red]\n    Error: {e}\n")

    # Summary output
    from rich_interface import final_summary
    timeline_range = f"{start_date_str} to {end_date_str}" if date_mode == "3" else "N/A"
    final_summary(
        total_files=len(successes) + len(failures),
        total_commits=len(commits),
        branch=branch,
        timeline_range=timeline_range,
        successes=len(successes),
        failures=len(failures)
    )

    if failures:
        console.print("\n[bold red]Failed Files:[/bold red]")
        for f, err in failures:
            console.print(f"❌ {f}: {err}")

    if not args.dry_run:
        try:
            push_branch(folder, branch, force=args.force)
            console.print(f"🚀 Push completed successfully.{' (forced)' if args.force else ''}", style="green")
        except GitCommandError as e:
            console.print(f"❌ Push failed: {e}", style="red")

if __name__ == "__main__":
    main()

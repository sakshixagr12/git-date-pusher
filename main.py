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

from commit_generator import generate_commit_message

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
    push_enabled = not args.dry_run
    if not commit_preview(repo_name=folder.name, branch=branch, commit_items=commits, summary_info=summary_info, push_enabled=push_enabled):
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
            console.print(f"[bright_green]✓[/bright_green] [[cyan]{idx}/{total_commits}[/cyan]] [green]{batch_name}[/green]\n    Date: {commit_date}\n    Message: {msg}\n")
        except GitCommandError as e:
            for f in batch:
                failures.append((str(f), str(e)))
            console.print(f"[red]✗[/red] [[cyan]{idx}/{total_commits}[/cyan]] [green]{batch_name}[/green]\n\nReason:\n{e}\n")

    # Calculate stats for summary
    remote_str = remote_url if "remote_url" in locals() and remote_url else "origin"
    files_selected = sum(len(b) for b, _, _ in commits)
    
    date_mode_mapping = {"1": "Same Date", "2": "Different Dates", "3": "Timeline"}
    date_mode_str = date_mode_mapping.get(date_mode, "Unknown")
    
    commit_range = None
    timeline_span = None
    if commits:
        dates = []
        for _, _, d_str in commits:
            try:
                parts = d_str.split()
                if len(parts) == 2:
                    dt = datetime.strptime(d_str, "%Y-%m-%d %H:%M:%S")
                else:
                    dt = datetime.strptime(d_str, "%Y-%m-%d")
                dates.append(dt)
            except Exception:
                pass
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            commit_range = (min_date.strftime("%Y-%m-%d %H:%M:%S"), max_date.strftime("%Y-%m-%d %H:%M:%S"))
            span_days = (max_date - min_date).days
            if span_days > 0:
                timeline_span = f"{span_days} days"
            else:
                timeline_span = "0 days"

    # Push logic before summary
    push_success = True
    push_msg = "Push completed successfully."
    if not args.dry_run:
        try:
            push_branch(folder, branch, force=args.force)
            push_msg = f"Push completed successfully.{' (forced)' if args.force else ''}"
        except GitCommandError as e:
            push_success = False
            push_msg = str(e)
    else:
        push_msg = "Dry run: no push executed."

    # Final Summary output
    from rich_interface import final_summary
    final_summary(
        repo_name=folder.name,
        branch=branch,
        remote=remote_str,
        files_selected=files_selected,
        files_committed=len(successes),
        successes=len(successes),
        failed=len(failures),
        date_mode_str=date_mode_str,
        timeline_used=(date_mode == "3"),
        timeline_span=timeline_span,
        commit_range=commit_range,
        push_status=(push_success, push_msg),
        failures_list=failures
    )

if __name__ == "__main__":
    main()

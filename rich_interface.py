import sys
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.table import Table
from rich.align import Align
from rich.prompt import Prompt, Confirm

console = Console()


def welcome() -> None:
    """Display a colorful welcome banner."""
    banner = Text("Git Date Pusher", style="bold magenta on black", justify="center")
    console.print(Panel(banner, title="🚀", subtitle="Ready to push your commits", expand=False))


def display_commit_mode_menu() -> int:
    """Show the commit mode selection menu and return the chosen option (1, 2, or 3)."""
    menu_text = "Select Commit Mode"
    options = [
        "[1] Commit all files\n    Commit every discovered file",
        "[2] Commit selected files\n    Choose multiple files from a list",
        "[3] Commit a single file\n    Commit one specific file",
    ]
    panel = Panel.fit("\n".join(options), title=menu_text, border_style="bright_blue")
    console.print(panel)
    while True:
        choice = console.input("Choice: ")
        if choice in {"1", "2", "3"}:
            return int(choice)
        console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")


def display_date_mode_menu() -> str:
    """Show the date mode selection menu and return the chosen option (1, 2, or 3)."""
    menu_text = "Select Date Mode"
    options = [
        "[1] Same Date For All Files",
        "[2] Different Date Per File",
        "[3] Timeline Mode",
    ]
    panel = Panel.fit("\n".join(options), title=menu_text, border_style="bright_blue")
    console.print(panel)
    while True:
        choice = console.input("Choice: ")
        if choice in {"1", "2", "3"}:
            return choice
        console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")


def choose_multiple_files(files: List[Path]) -> List[Path]:
    """Display a numbered table of files and let the user select multiple via comma-separated numbers.

    Returns the list of selected Path objects.
    """
    table = Table(title="Files Found", show_header=False)
    table.add_column("No.")
    table.add_column("File")
    for i, f in enumerate(files, start=1):
        table.add_row(str(i), f.name)
    console.print(table)
    while True:
        raw = console.input("Enter file numbers (comma separated): ")
        try:
            indices = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if not indices:
                console.print("[red]No files selected. Please enter at least one number.[/red]")
                continue
            unique_indices = list(dict.fromkeys(indices))
            selected = [files[i - 1] for i in unique_indices]
            return selected
        except Exception:
            console.print("[red]Invalid input. Please enter valid numbers separated by commas.[/red]")


def choose_single_file(files: List[Path]) -> List[Path]:
    """Display a numbered table of files and let the user select a single file.

    Returns a list containing the selected Path.
    """
    table = Table(title="Files Found", show_header=False)
    table.add_column("No.")
    table.add_column("File")
    for i, f in enumerate(files, start=1):
        table.add_row(str(i), f.name)
    console.print(table)
    while True:
        raw = console.input("Enter file number: ")
        try:
            idx = int(raw.strip())
            if 1 <= idx <= len(files):
                return [files[idx - 1]]
            else:
                raise ValueError()
        except Exception:
            console.print("[red]Invalid input. Please enter a valid number.[/red]")



def status(msg: str, success: bool = True) -> None:
    """Print a colored status line.

    Args:
        msg: Message to display.
        success: If True, show a green check; otherwise red cross.
    """
    symbol = "✅" if success else "❌"
    style = "green" if success else "red"
    console.print(f"{symbol} [{style}]{msg}[/]")


def process_files(files: List[Path], folder: Path, mode: int, shared_date: str | None) -> None:
    """Iterate over files with a progress bar, committing each.

    This function expects the caller to have imported the commit function
    from ``git_utils``. It only handles the UI portion.
    """
    from git_utils import commit_files  # Imported locally to avoid circular imports

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as prog:
        task = prog.add_task("Committing files…", total=len(files))
        for file_path in files:
            # Determine commit date based on mode
            if mode == 1:
                # ask per file (reuse date_handler for prompting)
                from date_handler import get_valid_datetime
                commit_date = get_valid_datetime(
                    f"📅 Date for {file_path.name} (YYYY-MM-DD), Time (HH:MM:SS optional): "
                )
            else:
                commit_date = shared_date  # type: ignore

            # Prompt for commit message (reuse date_handler for convenience)
            msg = input(f"💬 Commit message for {file_path.name} (Enter='Add {file_path.name}'): ").strip()
            if not msg:
                msg = f"Add {file_path.name}"

            commit_files(folder, [file_path], msg, commit_date)
            prog.update(task, advance=1)


def truncate_string(s: str, max_length: int = 44) -> str:
    """Truncate a string to a max length, appending '...' if necessary."""
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."

def truncate_filename(f: str, max_length: int = 30) -> str:
    """Truncate filename preserving extension if possible."""
    if len(f) <= max_length:
        return f
    parts = f.rsplit('.', 1)
    if len(parts) == 2:
        ext = "." + parts[1]
        name = parts[0]
        if len(ext) > max_length - 3:
            return f[:max_length - 3] + "..."
        keep = max_length - len(ext) - 3
        if keep <= 0:
            return f[:max_length - 3] + "..."
        return name[:keep] + "..." + ext
    else:
        return f[:max_length - 3] + "..."

def commit_preview(repo_name: str, branch: str, commit_items: List[Tuple[List[Path], str, str]], summary_info: dict = None) -> bool:
    """Display a preview of the commits and ask for confirmation.

    Args:
        repo_name: Name of the repository (folder name).
        branch: Target branch name.
        commit_items: List of tuples (file_paths, commit_message, commit_date).
        summary_info: Optional dictionary containing summary statistics (for Timeline mode).

    Returns:
        True if the user chooses to proceed, False otherwise.
    """
    from rich.console import Group

    table = Table(header_style="cyan")
    table.add_column("#")
    table.add_column("File")
    table.add_column("Commit Date")
    table.add_column("Commit Message")
    
    serial_no = 1
    total_commits = len(commit_items)
    total_files = sum(len(paths) for paths, _, _ in commit_items)

    for paths, msg, date in commit_items:
        trunc_msg = truncate_string(msg, 44)
        for path in paths:
            trunc_file = truncate_filename(path.name, 30)
            table.add_row(
                f"[cyan]{serial_no}[/cyan]",
                f"[green]{trunc_file}[/green]",
                f"[bright_blue]{date}[/bright_blue]",
                f"[yellow]{trunc_msg}[/yellow]"
            )
            serial_no += 1

    group_items = [
        Text(f"Repository : {repo_name}"),
        Text(f"Branch     : {branch}"),
    ]
    
    if summary_info:
        gap = summary_info['gap']
        gap_str = f"{int(gap)} days" if gap == int(gap) else f"{gap} days"
        group_items.append(Text(f"Timeline Range: {summary_info['start']} to {summary_info['end']}"))
        group_items.append(Text(f"Average Gap: {gap_str}"))

    group_items.extend([
        Text(""),
        table,
        Text(""),
        Text(f"Total Files : {total_files}", style="bold green"),
        Text(f"Total Commits : {total_commits}", style="bold green"),
    ])

    panel = Panel(
        Group(*group_items),
        title="COMMIT PREVIEW",
        border_style="magenta",
        expand=False
    )
    console.print(panel)
    return Confirm.ask("Proceed?", default=True)


def timeline_preview(file_date_mapping: List[Tuple[str, str, str]]) -> None:
    """Display a rich table preview of the timeline mode commits.

    Args:
        file_date_mapping: List of tuples (batch_name, date_str, message).
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Date")
    table.add_column("Message")
    
    for name, date_str, msg in file_date_mapping:
        table.add_row(name, date_str, msg)

    console.print(table)


def run_dry_preview(repo_state: dict) -> str:
    """Format a step-by-step dry run execution preview without running commands.
    
    Expected repo_state keys:
        - repo_name: str
        - branch: str
        - remote: str
        - commits: List[Tuple[List[Path], str, str]] (file_paths, message, date)
    """
    lines = []
    lines.append("=" * 60)
    lines.append(" DRY RUN EXECUTION FLOW ".center(60, "="))
    lines.append("=" * 60)
    lines.append(f"Target Repository : {repo_state.get('repo_name')}")
    lines.append(f"Target Branch     : {repo_state.get('branch')}")
    lines.append(f"Target Remote     : {repo_state.get('remote')}")
    lines.append("-" * 60)
    
    for idx, (f_paths, msg, date) in enumerate(repo_state.get('commits', []), start=1):
        lines.append(f"Step {idx}: Commit Batch ({len(f_paths)} files)")
        for p in f_paths:
            lines.append(f"  [Staged] {p.name}")
        lines.append(f"  [Action] git commit -m \"{msg}\"")
        lines.append(f"  [Date]   {date}")
        lines.append("-" * 60)
        
    lines.append("Final Step: Push")
    lines.append(f"  [Action] git push {repo_state.get('remote')} {repo_state.get('branch')}")
    lines.append("=" * 60)
    lines.append(" END OF DRY RUN ".center(60, "="))
    lines.append("=" * 60)
    
    return "\n".join(lines)
def final_summary(total_files: int, total_commits: int, branch: str, timeline_range: str, successes: int, failures: int) -> None:
    """Print a rich final summary panel."""
    table = Table(show_header=False, box=None)
    table.add_row("✓ Total Files Processed", str(total_files))
    table.add_row("✓ Total Commits Created", str(total_commits))
    if timeline_range != "N/A":
        table.add_row("✓ Timeline range used", timeline_range)
    table.add_row("✓ Successful Commits", f"[bright_green]{successes}[/bright_green]")
    table.add_row("✓ Failed Commits", f"[red]{failures}[/red]" if failures > 0 else "0")

    panel = Panel(
        Align.center(table),
        title="[bold]=== Final Summary ===[/bold]",
        border_style="bright_green" if failures == 0 else "bright_yellow",
    )
    console.print(panel)

if __name__ == "__main__":
    # The rich_interface module is primarily for UI utilities.
    # Running this file directly demonstrates the welcome banner.
    welcome()
    status("Demo mode – no real Git actions performed.")
    sys.exit(0)

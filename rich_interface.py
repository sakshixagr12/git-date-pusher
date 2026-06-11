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
            selected = [files[i - 1] for i in indices]
            return selected
        except Exception:
            console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")


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
    from git_utils import commit_file  # Imported locally to avoid circular imports

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
                from date_handler import get_valid_date
                commit_date = get_valid_date(
                    f"📅 Date for {file_path.name} (YYYY-MM-DD, empty for today): "
                )
            else:
                commit_date = shared_date  # type: ignore

            # Prompt for commit message (reuse date_handler for convenience)
            msg = input(f"💬 Commit message for {file_path.name} (Enter='Add {file_path.name}'): ").strip()
            if not msg:
                msg = f"Add {file_path.name}"

            commit_file(folder, file_path, msg, commit_date)
            prog.update(task, advance=1)


def commit_preview(repo_name: str, branch: str, commit_items: List[Tuple[Path, str, str]]) -> bool:
    """Display a preview of the commits and ask for confirmation.

    Args:
        repo_name: Name of the repository (folder name).
        branch: Target branch name.
        commit_items: List of tuples (file_path, commit_message, commit_date).

    Returns:
        True if the user chooses to proceed, False otherwise.
    """
    # Prepare data strings
    files = ", ".join([p.name for p, _, _ in commit_items])
    messages = ", ".join([msg for _, msg, _ in commit_items])
    dates = ", ".join([date for _, _, date in commit_items])
    total = len(commit_items)

    # Build a table with the preview information
    table = Table(show_header=False, box=None)
    table.add_row("Repository:", repo_name)
    table.add_row("Branch:", branch)
    table.add_row("Files Selected:", files or "(none)")
    table.add_row("Commit Messages:", messages or "(none)")
    table.add_row("Commit Dates:", dates or "(none)")
    table.add_row("Total Commits:", str(total))

    panel = Panel(
        Align.center(table),
        title="COMMIT PREVIEW",
        border_style="bright_magenta",
    )
    console.print(panel)
    # Ask for confirmation
    return Confirm.ask("Proceed?", default=True)


def summary(total: int, successes: int) -> None:
    """Print a final summary table."""
    tbl = Table(title="Run Summary", show_header=False)
    tbl.add_row("Total files processed", str(total))
    tbl.add_row("Successful commits", str(successes))
    tbl.add_row("Failed commits", str(total - successes))
    console.print(tbl)

if __name__ == "__main__":
    # The rich_interface module is primarily for UI utilities.
    # Running this file directly demonstrates the welcome banner.
    welcome()
    status("Demo mode – no real Git actions performed.")
    sys.exit(0)

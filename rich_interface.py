import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.table import Table

console = Console()


def welcome() -> None:
    """Display a colorful welcome banner."""
    banner = Text("Git Date Pusher", style="bold magenta on black", justify="center")
    console.print(Panel(banner, title="🚀", subtitle="Ready to push your commits", expand=False))


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


def summary(total: int, successes: int) -> None:
    """Print a final summary table."""
    tbl = Table(title="Run Summary", show_header=False)
    tbl.add_row("Total files processed", str(total))
    tbl.add_row("Successful commits", str(successes))
    tbl.add_row("Failed commits", str(total - successes))
    console.print(tbl)

if __name__ == "__main__":
    # Simple demo when run directly
    welcome()
    status("Demo mode – no real Git actions performed.")
    sys.exit(0)

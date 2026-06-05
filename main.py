import argparse
from pathlib import Path
from git_utils import ensure_git_repo, set_remote, commit_file, push_branch
from file_scanner import scan_files
from date_handler import get_today_str

def main():
    parser = argparse.ArgumentParser(description="Git Date Pusher")
    parser.add_argument("-d", "--directory", type=Path, help="Folder containing files")
    parser.add_argument("-r", "--remote", help="GitHub repository URL")
    parser.add_argument("-b", "--branch", default="main", help="Target branch")
    parser.add_argument("-m", "--mode", choices=["1", "2"], default="1",
                        help="1: date per file, 2: one date for all")
    args = parser.parse_args()

    folder = args.directory or Path(input("📁 Folder path (absolute) ")).resolve()
    ensure_git_repo(folder)

    remote_url = args.remote or input("🔗 GitHub repo URL: ").strip()
    if remote_url:
        set_remote(folder, remote_url)

    branch = args.branch

    files = scan_files(folder)
    if not files:
        print("❌ No files found.")
        return

    shared_date = None
    if args.mode == "2":
        date_input = input("📅 Date for all files (YYYY-MM-DD, Enter=today) ").strip()
        shared_date = date_input or get_today_str()

    for file_path in files:
        if args.mode == "1":
            date_input = input(f"📅 Date for {file_path.name} (YYYY-MM-DD, Enter=today) ").strip()
            commit_date = date_input or get_today_str()
        else:
            commit_date = shared_date
        msg = input(f"💬 Commit message for {file_path.name} (Enter=Add {file_path.name}) ").strip()
        if not msg:
            msg = f"Add {file_path.name}"
        commit_file(folder, file_path, msg, commit_date)

    push_branch(folder, branch)

if __name__ == "__main__":
    main()

# Git Date Pusher

A lightweight command‑line tool that lets you create **date‑stamped commits** for every file in a folder and push them to a GitHub repository.  Perfect for back‑dating work, creating realistic project histories, or preparing demo repositories.

---

## ✨ Features

- ✅ **Automatic Git initialization** – works on any folder.
- 🌐 **Remote configuration** – add or overwrite the `origin` remote.
- 📂 **Recursive file scanning** – skips the `.git` directory automatically.
- 📅 **Flexible date handling** – choose a single date for all files or a different date per file.
- 🎯 **Evenly distributed date schedule** – generate a commit timeline across a date range.
- 🚀 **One‑click push** – all commits are pushed in a single operation.
- 🎨 **Rich terminal UI** – colorful banners, progress bars, and summaries.
- 🛠️ **Modular design** – cleanly separated modules (`file_scanner`, `date_handler`, `git_utils`).

---

## 🛠️ Installation

```bash
# Clone the repository (or copy the folder into your workspace)
git clone https://github.com/your‑username/git-date-pusher.git
cd git-date-pusher

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **Tip:** The `requirements.txt` contains `GitPython` and `rich` – the only external libraries required.

---

## ▶️ Usage

```bash
python main.py [options]
```

### Options
| Flag | Description |
|------|-------------|
| `-d`, `--directory` | Path to the project folder (if omitted you will be prompted). |
| `-r`, `--remote` | GitHub repo URL (e.g. `https://github.com/user/repo.git`). |
| `-b`, `--branch` | Target branch name – defaults to `main`. |
| `-m`, `--mode`   | `1` – date per file, `2` – one date for all files. |

### Interactive flow
1. **Folder** – you are asked for the absolute path to the folder containing the files.
2. **Git init** – a repository is created if `.git` does not exist.
3. **Remote** – you provide the GitHub URL; the script will ask before overwriting an existing remote.
4. **Branch** – choose the branch to push to.
5. **File list** – the script shows every file that will be committed.
6. **Date mode** – pick a single date for the whole project or a separate date per file.
7. **Commit** – for each file you can edit the commit message; the date is applied automatically.
8. **Push** – all commits are pushed in one go.
9. **Summary** – a colourful table summarises the operation.

---

## 📸 Screenshots

> *Replace the placeholders with actual screenshots from your terminal.*

| Step | Screenshot |
|------|------------|
| Welcome banner & file list | ![welcome](./assets/welcome.png) |
| Progress bar while committing | ![progress](./assets/progress.png) |
| Final summary table | ![summary](./assets/summary.png) |

---

## 📝 Example Workflow

```bash
# 1️⃣ Start the tool in the folder you want to back‑date
python main.py -d /path/to/my/project -r https://github.com/me/my‑project.git

# 2️⃣ Choose "2" for a single date for all files
#    → Enter the start date: 2024‑01‑01
#    → Enter the end date:   2024‑02‑01
#    → The tool will create an evenly‑spaced schedule for the 20 files.

# 3️⃣ Review each commit message (or press Enter to accept the default).

# 4️⃣ When the progress bar finishes, the tool pushes everything:
🚀 Pushed branch 'main' to origin.

# 5️⃣ A summary table is shown:
┌─────────────────────┬───────────────┐
│ Total files          │ 20            │
│ Successful commits   │ 20            │
│ Failed commits       │ 0             │
└─────────────────────┴───────────────┘
```

That’s it – you now have a repository whose history spans the chosen date range!

---

## 🙌 Contributing

Feel free to open issues or pull requests.  Suggestions for new UI features, additional date‑distribution strategies, or CI integration are welcome.

---

## 📄 License

MIT © 2026 Sakshi Agrahari

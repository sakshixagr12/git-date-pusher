# Git Date Pusher

A lightweight command‑line tool that lets you create **date‑stamped commits** for every file in a folder and push them to a GitHub repository.  Perfect for back‑dating work, creating realistic project histories, or preparing demo repositories.

---

## ✨ Features

- ✅ **Automatic Git initialization** – works on any folder.
- 🌐 **Remote configuration** – add or overwrite the `origin` remote.
- 📂 **Recursive file scanning** – skips the `.git` directory automatically.
- 📅 **Flexible date handling** – choose a single date for all files or a different date per file.
- 🚀 **One‑click push** – all commits are pushed in a single operation.
- 🎨 **Rich terminal output and summaries.**
- 🛠️ **Modular design** – cleanly separated modules (`file_scanner`, `date_handler`, `git_utils`).
- 🔀 **Automatic branch detection** – the tool uses the currently checked‑out Git branch (no automatic creation, renaming, or switching of branches).
- ✉️ **Automatic commit message generation** – messages are generated based on file type.
- ⚡ **Auto‑message mode** – `--auto-message` flag accepts generated messages without prompting.
- 🧪 **Dry‑run support** – preview actions without changing the repository.
- 📊 **Commit summary reporting** – clear tables of successes and failures.

---

## 📦 Installation

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
| `-b`, `--branch` | Target branch name – defaults to the **currently checked‑out branch**. |
| `-m`, `--mode`   | `1` – date per file, `2` – one date for all files. |
| `--auto-message` | Automatically accept generated commit messages without prompting. |

### Automatic Commit Messages
Commit messages are generated automatically based on the file type:

- **HTML pages** – `Create homepage structure` for `index.html` or `Create <name> page` for other HTML files.
- **CSS files** – `Add application styling`.
- **JavaScript files** – `Implement application logic`.
- **Python files** – `Add Python script`.
- **JSON files** – `Add JSON configuration`.
- **Markdown files** – `Update project documentation`.
- **README files** – `Update project documentation`.

**Fallback:** If a file type is not recognized, the tool uses `Add <filename>`.

#### Example Mappings
```
index.html   → Create homepage structure
about.html   → Add about page
style.css    → Add application styling
app.js       → Implement application logic
main.py      → Implement main functionality
config.json  → Configure application settings
README.md    → Update project documentation
```

### Interactive flow
1. **Folder** – you are asked for the absolute path to the folder containing the files.
2. **Git init** – a repository is created if `.git` does not exist.
3. **Remote** – you provide the GitHub URL; the script will ask before overwriting an existing remote.
4. **Branch** – the tool detects the current branch and uses it (you can override with `-b`).
5. **File list** – the script shows every file that will be committed.
6. **Date mode** – pick a single date for the whole project or a separate date per file.
7. **Commit** – for each file a generated commit message is shown; you can accept it, edit it, or (with `--auto-message`) skip the prompt.
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
# 1️⃣ Start the tool
python main.py -d /path/to/my/project -r https://github.com/me/my-project.git --auto-message

# 2️⃣ Choose mode "1" (date per file) or "2" (one date for all files)
#    → Enter date: 2024-01-15

# 3️⃣ With `--auto-message` the generated commit messages are accepted automatically.

# 4️⃣ The tool commits each file and pushes:
🚀 Push completed successfully.

# 5️⃣ A summary is shown:
=== Commit Summary ===
✅ Successful commits:
  - index.html
  - style.css
  - app.js
```

That's it – you now have a repository with back‑dated commits!

---

## 🙌 Contributing

Feel free to open issues or pull requests.  Suggestions for new UI features, additional date‑distribution strategies, or CI integration are welcome.

---

## Safety Notice

⚠️ This tool modifies commit timestamps and Git history structure. Use only on repositories you own or have explicit permission to modify.

---

## Permissions & Access

This tool does not bypass GitHub permissions. All push and merge rights depend on repository settings and collaborator access. Users must have write access to the target repository.



## 📄 License

MIT © 2026 Sakshi Agrahari

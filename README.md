# Git Date Pusher

A lightweight command-line tool that helps developers create realistic Git commit histories by assigning custom dates and times to commits and pushing them directly to GitHub.

Perfect for:

* Learning Git workflows
* Demonstration repositories
* Portfolio projects
* Reconstructing project timelines
* Educational purposes

---

# ✨ Features

<<<<<<< HEAD
- ✅ **Automatic Git initialization** – works on any folder.
- 🌐 **Remote configuration** – add or overwrite the `origin` remote.
- 📂 **Recursive file scanning** – skips the `.git` directory automatically.
- 📅 **Flexible date handling** – choose a single date for all files, a different date per file, or use Timeline Mode to distribute dates evenly.
- 🚀 **One‑click push** – all commits are pushed in a single operation.
- 🎨 **Rich terminal output and summaries.**
- 🛠️ **Modular design** – cleanly separated modules (`file_scanner`, `date_handler`, `git_utils`).
- 🔀 **Automatic branch detection** – the tool uses the currently checked‑out Git branch (no automatic creation, renaming, or switching of branches).
- ✉️ **Automatic commit message generation** – messages are generated based on file type.
- ⚡ **Auto‑message mode** – `--auto-message` flag accepts generated messages without prompting.
- 🧪 **Dry‑run support** – preview actions without changing the repository.
- 📊 **Commit summary reporting** – clear tables of successes and failures.
=======
## Core Git Features

* ✅ Automatic Git repository initialization
* 🌐 Remote repository configuration
* 🔀 Automatic branch detection
* 🚀 One-click push to GitHub
* 🧪 Dry-run mode for safe testing
>>>>>>> 315ec34af4de5604d5cc7f3aa43b3eb90168c796

---

## File Management

### 📂 Smart File Scanning

* Recursively scans project files
* Automatically skips `.git`
* Respects `.gitignore`
* Ignores common development artifacts:

  * `venv`
  * `__pycache__`
  * `node_modules`
  * `.idea`
  * `.vscode`

---

## Commit Modes

Choose how files should be committed:

### 1️⃣ Commit All Files

Commit every tracked file discovered in the project.

### 2️⃣ Commit Multiple Files

Interactively select multiple files.

### 3️⃣ Commit Single File

Choose exactly one file to commit.

---

## Flexible Date Handling

You can provide:

### Natural Keywords

```text
today
yesterday
day-before
```

### Custom Dates

```text
2026-06-10
2026-01-15
2025-12-25
```

### Modes

* Same date for all commits
* Different date for every file

---

## Flexible Time Handling

### Default Time

```text
12:00:00
```

### Custom Time

```text
09:15:00
14:30:00
18:45:00
```

Users may provide a custom time or simply press Enter to use the default.

---

## Intelligent Commit Messages

The tool automatically generates commit messages based on file type.

| File Type  | Generated Message                       |
| ---------- | --------------------------------------- |
| HTML       | Create homepage structure / Create page |
| CSS        | Add application styling                 |
| JavaScript | Implement application logic             |
| Python     | Add Python script                       |
| JSON       | Add JSON configuration                  |
| Markdown   | Update project documentation            |
| README     | Update project documentation            |

### Fallback

```text
Add <filename>
```

Example:

```text
Add app.py
Add dashboard.jsx
Add config.yaml
```

---

## Custom Commit Messages

Users may:

* Accept generated messages
* Edit generated messages
* Write completely custom messages

---

## Commit Preview Screen

Before creating commits, Git Date Pusher displays a preview containing:

* Repository name
* Branch name
* Selected files
* Commit messages
* Commit dates
* Total commits

Example:

```text
Repository: git-date-pusher
Branch: main

Selected Files:
✓ main.py
✓ README.md
✓ git_utils.py

Commit Dates:
✓ 2026-06-10 14:00:00
✓ 2026-06-11 10:30:00
✓ 2026-06-12 09:15:00

Total Commits: 3

Proceed? [Y/N]
```

---

## Rich Terminal Interface

Powered by Rich:

* Beautiful banners
* Interactive menus
* Colored status messages
* Progress indicators
* Commit summaries

---

## Commit Summary Reporting

After execution:

```text
=== Commit Summary ===

✅ main.py
✅ README.md
✅ git_utils.py

🚀 Push completed successfully.
```

Failed commits are displayed separately.

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/sakshixagr12/git-date-pusher.git

cd git-date-pusher
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Usage

```bash
python main.py
```

or

```bash
python main.py [options]
```

<<<<<<< HEAD
### Options
| Flag | Description |
|------|-------------|
| `-d`, `--directory` | Path to the project folder (if omitted you will be prompted). |
| `-r`, `--remote` | GitHub repo URL (e.g. `https://github.com/user/repo.git`). |
| `-b`, `--branch` | Target branch name – defaults to the **currently checked‑out branch**. |
| `-m`, `--mode`   | `1` – one date for all, `2` – date per file, `3` – timeline mode. |
| `--time` | Enables optional time entry for commits (default 12:00:00). |
=======
---
>>>>>>> 315ec34af4de5604d5cc7f3aa43b3eb90168c796

## Available Options

<<<<<<< HEAD
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
blog.html                → Create blog page
E-Commerce Homepage.html → Create e commerce homepage
fruits.html              → Create fruits page
Hospital dashboard.html  → Create hospital dashboard page
index.html               → Create homepage structure
dashboard.html           → Create dashboard page
login.html               → Add login page
signup.html              → Add registration page
style.css                → Add application styling
app.js                   → Implement application logic
main.py                  → Add Python script
README.md                → Update project documentation
```

### Interactive flow
1. **Folder** – you are asked for the absolute path to the folder containing the files.
2. **Git init** – a repository is created if `.git` does not exist.
3. **Remote** – you provide the GitHub URL; the script will ask before overwriting an existing remote.
4. **Branch** – the tool detects the current branch and uses it (you can override with `-b`).
5. **File list** – the script shows every file that will be committed.
6. **Date mode** – pick `Same Date For All Files`, `Different Date Per File`, or `Timeline Mode`.
7. **Commit** – for each file a generated commit message is shown; you can accept it, edit it, or (with `--auto-message`) skip the prompt.
8. **Push** – all commits are pushed in one go.
9. **Summary** – a colourful table summarises the operation.
=======
| Flag                | Description                    |
| ------------------- | ------------------------------ |
| `-d`, `--directory` | Target project directory       |
| `-r`, `--remote`    | GitHub repository URL          |
| `-b`, `--branch`    | Target branch                  |
| `-m`, `--mode`      | Date mode                      |
| `--auto-message`    | Auto accept generated messages |
| `--dry-run`         | Preview actions only           |
>>>>>>> 315ec34af4de5604d5cc7f3aa43b3eb90168c796

---

## Example

```bash
<<<<<<< HEAD
# 1️⃣ Start the tool
python main.py -d /path/to/my/project -r https://github.com/me/my-project.git --auto-message

# 2️⃣ Choose Date Mode: 1 (Same Date), 2 (Different Date), or 3 (Timeline Mode)
#    → For Timeline Mode, enter Start Date: 2026-06-01, End Date: 2026-06-10
#    → Review the Timeline Preview showing files, dates, and generated messages.

# 3️⃣ With `--auto-message` the generated commit messages are accepted automatically.

# 4️⃣ The tool commits each file and pushes:
🚀 Push completed successfully.

# 5️⃣ A rich Final Summary is shown:
=== Final Summary ===
✓ Total files processed     3
✓ Total commits created     3
✓ Branch pushed             main
✓ Timeline range used       2026-06-01 to 2026-06-10
✓ Success count             3
✓ Failure count             0
=======
python main.py \
-d ./my-project \
-r https://github.com/user/my-project.git \
--auto-message
>>>>>>> 315ec34af4de5604d5cc7f3aa43b3eb90168c796
```

---

# 🔄 Workflow

### Step 1

Select project folder.

### Step 2

Repository setup:

* Git initialization
* Remote configuration
* Branch detection

### Step 3

Choose commit mode:

```text
1. All Files
2. Multiple Files
3. Single File
```

### Step 4

Choose dates.

Examples:

```text
today
yesterday
2026-06-10
```

### Step 5

Choose times.

Examples:

```text
09:00:00
14:15:00
18:30:00
```

Or press Enter to use:

```text
12:00:00
```

### Step 6

Review generated commit messages.

### Step 7

View commit preview screen.

### Step 8

Confirm:

```text
Proceed? [Y/N]
```

### Step 9

Commits are created and pushed automatically.

---

# 📋 Version History

## v1.2.0

### Added

* `.gitignore` support
* Commit preview confirmation screen
* Custom commit time support
* Natural date keywords
* Improved file selection workflow

### Improved

* User experience
* Validation
* Error handling
* Commit creation workflow

---

## v1.1.0

### Added

* Rich terminal UI
* Automatic commit messages
* Multiple commit modes
* Dry-run support
* Branch auto-detection
* Commit summaries
* One-click push

---

# 🛡️ Safety Notice

This tool modifies Git commit timestamps and repository history.

Use it only on repositories that:

* You own
* You have permission to modify
* Are intended for educational, testing, or demonstration purposes

---

# 🔐 Permissions

Git Date Pusher does not bypass GitHub permissions.

Users must have:

* Valid Git credentials
* Write access to the repository
* Permission to push to the target branch

---

# 🤝 Contributing

Contributions are welcome.

Ideas for future releases:

* Commit scheduling
* AI-powered commit messages
* GUI version
* GitHub Actions integration
* Interactive timeline visualization

Feel free to open issues and pull requests.

---

# 📄 License

MIT License

Copyright (c) 2026 Sakshi Agrahari

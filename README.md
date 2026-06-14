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

## Core Git Features

* ✅ Automatic Git repository initialization
* 🌐 Remote repository configuration
* 🔀 Automatic branch detection
* 🚀 One-click push to GitHub
* 🧪 Dry-run mode for safe testing

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

---

## Available Options

| Flag                | Description                    |
| ------------------- | ------------------------------ |
| `-d`, `--directory` | Target project directory       |
| `-r`, `--remote`    | GitHub repository URL          |
| `-b`, `--branch`    | Target branch                  |
| `-m`, `--mode`      | Date mode                      |
| `--auto-message`    | Auto accept generated messages |
| `--dry-run`         | Preview actions only           |

---

## Example

```bash
python main.py \
-d ./my-project \
-r https://github.com/user/my-project.git \
--auto-message
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

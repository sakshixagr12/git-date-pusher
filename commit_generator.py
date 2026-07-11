import os
from pathlib import Path

KEYWORD_MAP = {
    "login": "login",
    "signup": "signup",
    "register": "registration",
    "auth": "authentication",
    "profile": "profile",
    "dashboard": "dashboard",
    "home": "homepage",
    "index": "homepage",
    "about": "about",
    "contact": "contact",
    "navbar": "navigation bar",
    "nav": "navigation",
    "footer": "footer",
    "search": "search",
    "payment": "payment",
    "checkout": "checkout",
    "cart": "shopping cart",
    "admin": "admin panel",
    "user": "user management",
    "weather": "weather",
    "hospital": "hospital",
    "student": "Student class",
    "library": "Library class",
    "graph": "graph algorithms",
    "tree": "tree data structure",
    "linked_list": "linked list",
    "queue": "queue",
    "stack": "stack",
    "binary_search": "binary search",
    "lca": "lowest common ancestor",
    "bst": "binary search tree",
    "responsive": "responsive layout",
    "validation": "form validation"
}

def generate_commit_message(files: list[str]) -> str:
    """Generate a human-readable, conventional commit message based on filenames/extensions."""
    if not files:
        return "chore: update project files"
        
    if len(files) == 1:
        f = files[0]
        name = Path(f).name
        name_lower = name.lower()
        stem = Path(f).stem.lower()
        _, ext = os.path.splitext(name_lower)
        
        # Exact filename matches
        if name_lower == "readme.md": return "docs: update project documentation"
        if name_lower == "changelog.md": return "docs: update changelog"
        if name_lower == "config.json": return "chore: configure application settings"
        if name_lower == "package.json": return "build: update project dependencies"
        if name_lower == "main.py": return "feat: implement main functionality"
        if name_lower == "app.js": return "feat: implement application logic"
        if name_lower == "style.css": return "style: add application styling"
        if name_lower == "scanner.py": return "feat: implement file scanner"
        if name_lower == "git_utils.py": return "feat: add Git utility functions"

        # Determine type prefix based on extension
        prefix = "feat"
        if ext == ".css":
            prefix = "style"
        elif ext in [".md", ".txt"]:
            prefix = "docs"
        elif ext in [".json", ".yaml", ".yml", ".ini"]:
            prefix = "chore"
            
        # Check keywords
        concept = None
        for key, val in KEYWORD_MAP.items():
            if key in stem:
                concept = val
                break
                
        if concept:
            if ext == ".css":
                if concept in ["navigation bar", "footer"]:
                    return f"{prefix}: design {concept}"
                elif concept == "responsive layout":
                    return f"{prefix}: improve {concept}"
                else:
                    return f"{prefix}: style {concept} page" if "page" not in concept else f"{prefix}: style {concept}"
            elif ext == ".html":
                if concept == "homepage":
                    return f"{prefix}: create homepage"
                elif concept in ["login", "about", "contact"]:
                    return f"{prefix}: add {concept} page"
                return f"{prefix}: create {concept} page" if "page" not in concept else f"{prefix}: create {concept}"
            elif ext == ".js":
                if concept == "authentication":
                    return f"{prefix}: add authentication logic"
                if concept == "login":
                    return f"{prefix}: implement login functionality"
                if concept == "form validation":
                    return f"{prefix}: implement form validation"
                return f"{prefix}: implement {concept} logic"
            elif ext in [".py", ".cpp", ".java"]:
                return f"{prefix}: implement {concept}"
            else:
                return f"{prefix}: add {concept}"

        # Fallback if no keyword found
        clean_name = stem.replace("-", " ").replace("_", " ")
        if ext == ".html":
            if clean_name.endswith("page") or clean_name.endswith("homepage"):
                return f"{prefix}: create {clean_name}"
            return f"{prefix}: add {clean_name}"
        elif ext == ".css":
            return f"{prefix}: add {clean_name} styling"
        elif ext in [".js", ".py", ".cpp", ".java"]:
            return f"{prefix}: implement {clean_name}"
        else:
            return f"{prefix}: add {clean_name} implementation" if ext in [".cpp", ".java", ".py", ".go", ".rs"] else f"{prefix}: add {clean_name}"

    # Multiple files logic
    exts = set()
    for f in files:
        _, ext = os.path.splitext(f)
        exts.add(ext.lower())
        
    if len(exts) == 1:
        ext = exts.pop()
        if ext == ".html":
            return "feat: update web pages"
        elif ext == ".css":
            return "style: improve styling"
        elif ext == ".js":
            return "feat: enhance functionality"
        elif ext == ".pdf":
            return "docs: add documents"
        elif ext in [".py", ".cpp", ".java"]:
            return "feat: add implementation files"
        elif ext == ".json":
            return "chore: update configuration"
        elif ext in {".md", ".txt"}:
            return "docs: update documentation"
            
    # If multiple types exist
    if {".html", ".css", ".js"}.intersection(exts):
        return "feat: update web project assets"
        
    return "chore: update project files"

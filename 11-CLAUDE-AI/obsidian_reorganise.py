"""
obsidian_reorganise.py — Generic Obsidian vault folder reorganiser.

Moves loose files from a target folder into subfolders using keyword-based rules.
Uses the Obsidian CLI so WikiLinks are automatically updated.

Usage:
    python obsidian_reorganise.py --config path/to/config.yaml          # dry-run (default)
    python obsidian_reorganise.py --config path/to/config.yaml --execute

Config file format: see reorganise-config-OBS-MU-ResearchLab.yaml for a full example.

Requirements:
    pip install pyyaml
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")


DEFAULT_CLI = r"D:\ObsidianProgram\Obsidian.com"
DEFAULT_EXTENSIONS = [".md", ".canvas", ".r", ".py"]


def is_wsl() -> bool:
    try:
        return "microsoft" in open("/proc/version").read().lower()
    except FileNotFoundError:
        return False


def obsidian_move(filename: str, vault_dest: str, cli: str) -> bool:
    """Move a file via Obsidian CLI so WikiLinks are auto-updated.

    Automatically selects the correct invocation method:
      - WSL:            routes through cmd.exe (Linux can't reach Windows named pipe)
      - Windows native: calls the exe directly
    """
    if is_wsl():
        cmd_str = f'{cli} move file="{filename}" to="{vault_dest}"'
        run_args = ["/mnt/c/Windows/System32/cmd.exe", "/c", cmd_str]
    else:
        run_args = [cli, "move", f"file={filename}", f"to={vault_dest}"]

    result = subprocess.run(run_args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR moving {filename}: {result.stderr.strip() or result.stdout.strip()}")
        return False
    return True


def get_destination(filename: str, rules: list) -> str | None:
    """Return the first matching destination folder for a filename, or None."""
    for folder, keywords in rules:
        for kw in keywords:
            if kw.lower() in filename.lower():
                return folder
    return None


def is_scratch(filename: str, patterns: list, exact: set) -> bool:
    if filename in exact:
        return True
    return any(p.lower() in filename.lower() for p in patterns)


def load_config(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Reorganise an Obsidian vault folder using keyword-based rules."
    )
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument(
        "--execute", action="store_true",
        help="Actually move files (default is dry-run preview)"
    )
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    dry_run = not args.execute

    vault_root = Path(cfg["vault_path"])
    target_folder = cfg["target_folder"].strip("/")
    root = vault_root / target_folder
    cli = cfg.get("obsidian_cli", DEFAULT_CLI)
    extensions = tuple(cfg.get("extensions", DEFAULT_EXTENSIONS))

    # Build rules as list of (folder_name, [keywords]) — order matters, first match wins
    rules = [(r["folder"], r["keywords"]) for r in cfg.get("rules", [])]
    scratch_patterns = cfg.get("scratch_patterns", [])
    scratch_exact = set(cfg.get("scratch_exact", []))

    if not root.exists():
        sys.exit(f"Target folder not found: {root}")

    loose_files = [
        f for f in root.iterdir()
        if f.is_file() and f.suffix in extensions
    ]

    moves = {}
    deletes = []
    unmatched = []

    for f in sorted(loose_files):
        if is_scratch(f.name, scratch_patterns, scratch_exact):
            deletes.append(f)
            continue
        dest = get_destination(f.name, rules)
        if dest:
            moves[f] = root / dest / f.name
        else:
            unmatched.append(f.name)

    print(f"=== MATCHED: {len(moves)} files ===")
    for src, dst in sorted(moves.items(), key=lambda x: str(x[1])):
        print(f"  {src.name}  →  {dst.parent.name}/")

    print(f"\n=== TO DELETE: {len(deletes)} scratch files ===")
    for f in sorted(deletes):
        print(f"  {f.name}")

    print(f"\n=== UNMATCHED: {len(unmatched)} files ===")
    for name in sorted(unmatched):
        print(f"  {name}")

    if not dry_run:
        # Ensure destination folders exist on disk (CLI needs them)
        for folder, _ in rules:
            (root / folder).mkdir(exist_ok=True)

        moved = 0
        failed = 0
        for src, dst in moves.items():
            vault_dest = f"{target_folder}/{dst.parent.name}"
            if obsidian_move(src.stem, vault_dest, cli):
                moved += 1
            else:
                failed += 1

        for f in deletes:
            f.unlink()

        print(f"\nDone. Moved {moved}, failed {failed}, deleted {len(deletes)} scratch files.")
    else:
        print("\n*** DRY RUN — pass --execute to apply changes ***")


if __name__ == "__main__":
    main()

from pathlib import Path
import shutil
import sys
import click

STRATA_TEMPLATES = Path.home() / ".strata" / "scaffolds"


def prompt_overwrite(path: Path, overwrite_all: bool) -> tuple[bool, bool]:
    """
    Ask the user what to do if a file already exists.

    Returns:
        (should_write, overwrite_all)
    """
    if overwrite_all:
        return True, overwrite_all

    click.echo(f"File exists: {path}")
    choice = click.prompt(
        "[o]verwrite / [s]kip / overwrite [a]ll / [q]uit",
        default="s",
        show_default=True,
    ).lower()

    if choice == "o":
        return True, overwrite_all
    if choice == "a":
        return True, True
    if choice == "s":
        return False, overwrite_all
    if choice == "q":
        click.echo("Aborted.")
        sys.exit(1)

    click.echo("Invalid choice, skipping.")
    return False, overwrite_all


def copy_scaffold(src: Path, dest: Path, inline: bool):
    overwrite_all = False

    for item in src.rglob("*"):
        relative = item.relative_to(src)
        target = dest / relative

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        if target.exists() and inline:
            should_write, overwrite_all = prompt_overwrite(target, overwrite_all)
            if not should_write:
                continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def init_scaffold(
    scaffold_name: str,
    app_name: str | None = None,
    *,
    templates_dir: Path = STRATA_TEMPLATES,
):
    """
    Core scaffold initializer.

    CLI owns argument parsing.
    This function owns filesystem behavior.
    """
    scaffold_path = templates_dir / scaffold_name

    if not scaffold_path.exists():
        raise FileNotFoundError(f"Scaffold not found: {scaffold_path}")

    if app_name:
        # Project mode
        dest = Path.cwd() / app_name
        if dest.exists():
            raise FileExistsError(f"Directory already exists: {dest}")

        dest.mkdir()
        copy_scaffold(scaffold_path, dest, inline=False)
        return dest

    # Inline / integration mode
    dest = Path.cwd()
    copy_scaffold(scaffold_path, dest, inline=True)
    return dest

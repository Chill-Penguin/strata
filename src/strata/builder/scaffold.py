"""
scaffold.py

This module implements Strata's "scaffold" feature.

Scaffolding is responsible for generating a new project or module
from a predefined folder and file structure, similar to:
- django-admin startproject
- cookiecutter
- rails new

A scaffold:
- Lives in ~/.strata/scaffolds/<scaffold-name>/
- Contains a template directory
- Optionally contains a scaffold.yml metadata file

This module does NOT:
- Build docker-compose files
- Resolve environment variables
- Expand infrastructure blocks

It only creates files and folders.
"""

from pathlib import Path
import shutil
import yaml
from jinja2 import Environment, FileSystemLoader

# Import STRATA_DIR so we know where user-level scaffolds live
from strata.config import STRATA_DIR


def scaffold_root() -> Path:
    """
    Return the base directory where all user-defined scaffolds live.

    Example:
        ~/.strata/scaffolds/
    """
    return STRATA_DIR / "scaffolds"


def load_scaffold(name: str) -> Path:
    """
    Locate a scaffold by name and return its path.

    If the scaffold does not exist, raise an error so the CLI
    can fail fast and inform the user.
    """
    root = scaffold_root() / name

    if not root.exists():
        raise FileNotFoundError(
            f"Scaffold '{name}' not found in {scaffold_root()}"
        )

    return root


def render_template(src: Path, dest: Path, context: dict):
    """
    Render a single Jinja template file.

    - src:  path to the .tpl file
    - dest: destination path without the .tpl extension
    - context: dictionary of variables (e.g. {"name": "myapp"})

    This function:
    1. Creates a Jinja environment rooted at the template's directory
    2. Loads the template file
    3. Renders it using the provided context
    4. Writes the result to disk
    """

    # Create a Jinja environment that loads templates
    # from the directory containing the source file
    env = Environment(
        loader=FileSystemLoader(src.parent),
        keep_trailing_newline=True,  # Important for text files
    )

    # Load the template file by name
    template = env.get_template(src.name)

    # Render the template and write the result to disk
    dest.write_text(template.render(context))


def copy_tree(template_root: Path, target_root: Path, context: dict):
    """
    Copy an entire scaffold template tree to a new target directory.

    This function:
    - Recursively walks the scaffold's template directory
    - Replaces {{ name }} in folder and file names
    - Renders .tpl files using Jinja
    - Copies non-template files as-is

    Example:
        template/{{ name }}/main.py.tpl
        ->
        myapp/myapp/main.py
    """

    # Walk every file and directory in the template tree
    for path in template_root.rglob("*"):

        # Determine this path relative to the template root
        relative = path.relative_to(template_root)

        # Replace {{ name }} in path components
        # (directories and filenames)
        rendered_parts = [
            part.replace("{{ name }}", context["name"])
            for part in relative.parts
        ]

        # Build the final destination path
        dest_path = target_root.joinpath(*rendered_parts)

        # If this is a directory, just create it
        if path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        # Ensure the destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # If the file is a Jinja template, render it
        if path.suffix == ".tpl":
            render_template(
                src=path,
                dest=dest_path.with_suffix(""),
                context=context,
            )
        else:
            # Otherwise, copy the file exactly as-is
            shutil.copy2(path, dest_path)


def run_scaffold(scaffold_name: str, target_name: str):
    """
    Execute a scaffold.

    Parameters:
    - scaffold_name: name of the scaffold (e.g. "python-cli")
    - target_name:   name of the new project/module (e.g. "myapp")
    - cwd:           current working directory (where output goes)

    This is the main entry point used by the CLI.
    """

    # Locate the scaffold on disk
    scaffold = load_scaffold(scaffold_name)
    cwd = Path.cwd()

    # Load scaffold metadata if present
    # (Currently optional, but future-proofed)
    meta_file = scaffold / "scaffold.yml"
    meta = {}

    if meta_file.exists():
        meta = yaml.safe_load(meta_file.read_text())

    # The directory containing the files to copy
    template_root = scaffold / "template"

    if not template_root.exists():
        raise RuntimeError(
            f"Scaffold '{scaffold_name}' is missing a template/ directory"
        )

    # The directory that will be created
    target_root = cwd / target_name

    # Prevent accidental overwrites
    if target_root.exists():
        raise FileExistsError(
            f"Target '{target_name}' already exists"
        )

    # Variables available to Jinja templates
    context = {
        "name": target_name,
    }

    # Copy and render the scaffold
    copy_tree(template_root, target_root, context)

    # Success message for the user
    print(
        f"✔ Created '{target_name}' using scaffold '{scaffold_name}'"
    )

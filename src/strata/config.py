from pathlib import Path
import yaml

STRATA_DIR = Path.home() / ".strata"
CONFIG_FILE = STRATA_DIR / "config.yml"

def ensure_setup():
    if not STRATA_DIR.exists():
        raise RuntimeError("Run `strata setup` first")

def load_config():
    ensure_setup()
    return yaml.safe_load(CONFIG_FILE.read_text())

def template_roots(project_root: Path):
    """
    Resolution order:
    1. project
    2. user
    3. built-in
    """
    from importlib.resources import files
    return [
        project_root,
        STRATA_DIR,
        files("strata")
    ]

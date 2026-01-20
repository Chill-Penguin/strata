# src/strata/setup.py
import shutil
from pathlib import Path
from importlib.resources import files
from strata.config import STRATA_DIR

def run_setup():
    source = files("strata").joinpath("templates")
    STRATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, STRATA_DIR, dirs_exist_ok=True)
    shutil.copyfile(
        files("strata").joinpath("config.yml"),
        STRATA_DIR.joinpath("config.yml")
    )
    print(f"Strata setup complete. Templates copied to {STRATA_DIR}")

def run_uninstall():
    """
    Remove everything created by run_setup().
    WARNING: This will delete the entire STRATA_DIR directory!
    """
    if not STRATA_DIR.exists():
        print(f"No Strata setup found at {STRATA_DIR}. Nothing to uninstall.")
        return

    # Safety check: confirm STRATA_DIR is not root or home
    if STRATA_DIR.resolve() in [Path("/"), Path.home().resolve()]:
        raise RuntimeError(f"Refusing to delete critical directory: {STRATA_DIR}")

    # Delete the whole directory
    shutil.rmtree(STRATA_DIR)
    print(f"Strata uninstall complete. Removed {STRATA_DIR}")
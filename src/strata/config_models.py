from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml


@dataclass(frozen=True)
class UserConfig:
    user_root: Path

    block_dir: Path
    vars_dir: Path
    entries_dir: Path

    default_env_files: List[Path]

    overwrite: bool

    @classmethod
    def from_yaml(cls, raw: dict) -> "UserConfig":
        """
        Convert raw YAML dict into a validated, normalized config object.
        """
        try:
            user_root = Path(raw["paths"]["user_root"]).expanduser()
            vars_dir = user_root / raw["paths"]["templates"]["vars"]
            default_env_files = []
            for env_file in raw["paths"]["env"]["defaults"]:
                default_env_files.append(vars_dir / Path(env_file))

            print(f"default_env_files: {default_env_files}")

            return cls(
                user_root=user_root,

                block_dir=user_root / raw["paths"]["templates"]["blocks"],
                vars_dir=user_root / raw["paths"]["templates"]["vars"],
                entries_dir=user_root / raw["paths"]["templates"]["entries"],
                default_env_files=default_env_files,
                overwrite=bool(raw["behavior"].get("overwrite", False)),
            )

        except KeyError as e:
            raise RuntimeError(f"Invalid config.yml structure, missing key: {e}")


def discover_project_root(start: Path) -> Path:
    """
    Walk upward from `start` until a `strata/` directory is found.
    """
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / "strata").is_dir():
            return p
    raise RuntimeError("Could not discover project root (missing strata/ directory)")


@dataclass(frozen=True)
class ProjectConfig:
    """Typed representation of a project-level .strata.yml configuration."""

    version: int = 1

    # Env layering (fully resolved paths)
    default_env_files: List[Path] = field(default_factory=lambda: [Path("base.env"), Path("docker.env")])
    profiles: Dict[str, List[Path]] = field(default_factory=lambda: {
        "dev": [Path("dev.env")],
        "qa": [Path("qa.env")],
        "prod": [Path("prod.env")],
    })
    project_root: Optional[Path] = None

    # Template locations (single directories)
    blocks_dir: Path = Path("blocks")
    vars_dir: Path = Path("vars")

    # Output settings
    output_dir: Path = Path(".")
    overwrite: bool = False

    # Defaults
    default_profile: str = "dev"

    @classmethod
    def from_file(
        cls,
        start_dir: Optional[Path] = None,
        file_path: Optional[Path] = None,
    ) -> "ProjectConfig":
        """
        Load .strata.yml if it exists, otherwise return defaults.

        - start_dir: directory to begin project root discovery (defaults to CWD)
        - file_path: optional override path to .strata.yml
        """
        start_dir = start_dir or Path.cwd()
        project_root = discover_project_root(start_dir)

        # Define fixed structure
        strata_dir = project_root / "strata"
        vars_dir = strata_dir / "vars"
        blocks_dir = strata_dir / "blocks"

        # Load config file if it exists
        cfg_path = file_path or project_root / ".strata.yml"
        if not cfg_path.exists():
            # Defaults: fully resolve env paths under vars_dir
            return cls(
                default_env_files=[(vars_dir / p).resolve() for p in cls().default_env_files],
                profiles={
                    k: [(vars_dir / p).resolve() for p in v]
                    for k, v in cls().profiles.items()
                },
                blocks_dir=blocks_dir.resolve(),
                vars_dir=vars_dir.resolve(),
                output_dir=project_root.resolve(),
            )

        raw = yaml.safe_load(cfg_path.read_text()) or {}

        # --- Helper to resolve env files under vars_dir ---
        def _env_paths(lst: List[str]) -> List[Path]:
            return [(vars_dir / Path(p)).resolve() for p in lst]

        env_cfg = raw.get("env", {})
        env_defaults = _env_paths(env_cfg.get("defaults", []))
        env_profiles = {
            name: _env_paths(files)
            for name, files in env_cfg.get("profiles", {}).items()
        }

        # --- Output configuration ---
        output_cfg = raw.get("output", {})
        output_dir = project_root / Path(output_cfg.get("directory", "."))
        overwrite = bool(output_cfg.get("overwrite", False))

        # --- Defaults ---
        default_profile = raw.get("defaults", {}).get("profile", "dev")

        return cls(
            version=raw.get("version", 1),
            default_env_files=env_defaults or [(vars_dir / p).resolve() for p in cls().default_env_files],
            profiles=env_profiles or {
                k: [(vars_dir / p).resolve() for p in v]
                for k, v in cls().profiles.items()
            },
            blocks_dir=blocks_dir.resolve(),
            vars_dir=vars_dir.resolve(),
            output_dir=output_dir.resolve(),
            overwrite=overwrite,
            default_profile=default_profile,
            project_root=project_root.resolve(),
        )
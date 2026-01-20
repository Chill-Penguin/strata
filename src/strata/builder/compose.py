from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from strata.builder.env import resolve_env_order
from strata.config import load_config, template_roots
from strata.config_models import UserConfig, ProjectConfig
from strata.builder.preprocess import preprocess_to_jinja
from strata.builder.render import render_jinja_template


# -----------------------------
# Helpers
# -----------------------------

def strip_tpl_suffix(path: Path) -> Path:
    if path.suffix != ".tpl":
        raise ValueError(f"Expected .tpl file, got {path}")
    return path.with_suffix("")



# -----------------------------
# Main build function
# -----------------------------

def build_stack(stack_name: str, profile=None):
    """
    Build a docker-compose file from a stack template.

    Steps:
    1. Resolve stack template
    2. Load variables (env layering)
    3. Recursively expand blocks
    4. Fill variables
    5. Repeat until stable
    6. Write output to disk
    """

    stack_path = Path(stack_name)
    if not stack_path.exists():
        raise FileNotFoundError(f"Stack file not found: {stack_name}")
    stack_file = stack_path.resolve()

    project_root = stack_file.parent
    raw_config = load_config()
    base_config = UserConfig.from_yaml(raw_config)

    project_config = ProjectConfig.from_file()
    project_env_files = project_config.default_env_files.copy()

    selected_profile = profile or project_config.default_profile
    profile_env_files = project_config.profiles.get(selected_profile, [])

    env_vars = resolve_env_order(base_config.default_env_files, project_env_files=project_env_files, profile_env_files=profile_env_files)
    #for k, v in env_vars.items():
    #    print(f"ENV: {k}={v}")

    template_dirs = template_roots(project_root)

    strata_dir = project_root / "strata"
    build_dir = strata_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)


   # -----------------------------
    # Preprocess stack file → Jinja template
    # -----------------------------
     # 1. Preprocess (include crawling + Jinja conversion)
    processed_file = preprocess_to_jinja(
        entry_template=stack_file,
        project_root=project_root,
        template_dirs=template_dirs,
        build_dir=build_dir,
    )

    # 2. Render with Jinja
    rendered_text = render_jinja_template(
        source_file=processed_file,
        template_dirs=[build_dir],
        env_vars=env_vars,
    )


    # -----------------------------
    # Write output
    # -----------------------------
    output_path = strip_tpl_suffix(stack_path)
    output_path.write_text(rendered_text)

    print(f"Stack rendered to {output_path}")
    return output_path

from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def create_jinja_env(template_dirs: List[Path]) -> Environment:
    return Environment(
        loader=FileSystemLoader([str(p) for p in template_dirs]),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_jinja_template(
    source_file: Path,
    template_dirs: List[Path],
    env_vars: Dict[str, str],
) -> str:
    env = create_jinja_env(template_dirs)
    template = env.get_template(source_file.name)
    return template.render(**env_vars)

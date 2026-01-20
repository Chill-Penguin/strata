# src/strata/builder/env.py
from pathlib import Path

def parse_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        env[key] = value
    return env

def load_env(files):
    merged = {}
    for file in files:
        merged.update(parse_env(file))
    return merged

def resolve_env_order( default_env_files, project_env_files, profile_env_files=None):
    env= {}
    for path in default_env_files:
        env.update(parse_env(path))
    for path in project_env_files:
        env.update(parse_env(path))
    if profile_env_files:
        for path in profile_env_files:
            env.update(parse_env(path))
    return env
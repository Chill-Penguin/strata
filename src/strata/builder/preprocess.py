import re
from pathlib import Path
from typing import Dict, List, Set
import shutil

# -----------------------------
# Regex Patterns
# -----------------------------

INCLUDE_RE = re.compile(r"^(?P<indent>\s*)#\s*@include\s+(?P<name>[\w\-./]+)\s*$")
VARS_START_RE = re.compile(r"^\s*#\s*@vars\s*$")
VAR_LINE_RE = re.compile(r"^\s*#\s*(\w+)\s*:\s*(.+)$")
LIST_KEY_RE = re.compile(r"^\s*#\s*(\w+)\s*:\s*$")
LIST_ITEM_RE = re.compile(r"^\s*#\s*-\s*(.+)$")



# -----------------------------
# Helpers
# -----------------------------

def parse_inline_vars(lines: List[str], start: int) -> tuple[Dict[str, object], int]:
    vars_dict: Dict[str, object] = {}
    i = start + 1

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()

        if not stripped.startswith("#"):
            break

        # key: value
        match = VAR_LINE_RE.match(stripped)
        if match:
            vars_dict[match.group(1)] = match.group(2)
            i += 1
            continue

        # key:  (start of list)
        match = LIST_KEY_RE.match(stripped)
        if match:
            key = match.group(1)
            items = []
            i += 1

            while i < len(lines):
                item_line = lines[i].lstrip()
                item_match = LIST_ITEM_RE.match(item_line)
                if not item_match:
                    break
                items.append(item_match.group(1))
                i += 1

            vars_dict[key] = items
            continue

        i += 1

    return vars_dict, i



def find_template(template_name: str, template_dirs: List[Path]) -> Path:
    for root in template_dirs:
        print(f"Searching for template '{template_name}' in '{root}'")
        candidate = root / f"{template_name}.yml.tpl"
        candidate_blocks = root / "blocks" / f"{template_name}.yml.tpl"
        if candidate_blocks.exists():
            return candidate_blocks
        if candidate.exists():
            return candidate
        
    raise FileNotFoundError(f"Template not found: {template_name}")


def convert_file_to_jinja(
    source_path: Path,
    build_path: Path,
    template_dirs: List[Path],
    discovered: Set[str],
    queue: List[str],
):
    """
    Convert a single Strata template into a Jinja template.
    """

    lines = source_path.read_text().splitlines(keepends=True)
    output: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = INCLUDE_RE.match(line)

        if not match:
            output.append(line)
            i += 1
            continue

        indent = match.group("indent")
        indent_width = len(indent)
        name = match.group("name")

        # Track include for later crawling
        if name not in discovered:
            discovered.add(name)
            queue.append(name)

        i += 1
        vars_block = {}

        if i < len(lines) and VARS_START_RE.match(lines[i]):
            vars_block, i = parse_inline_vars(lines, i)

        # Scoped vars
        if vars_block:
            output.append(f"{indent}{{% with %}}\n")
            for k, v in vars_block.items():
                if isinstance(v, list):
                    output.append(f"{indent}{{% set {k} = {v} %}}\n")
                else:
                    output.append(f"{indent}{{% set {k} = {v!r} %}}\n")


        # ✅ Filter block include (correct Jinja)
        output.append(f"{{% filter indent({indent_width}, true) %}}\n")
        output.append(f"{{% include \"{name}.yml.tpl\" %}}\n")
        output.append(f"{{% endfilter %}}\n")

        if vars_block:
            output.append(f"{{% endwith %}}\n")

    build_path.write_text("".join(output))



# -----------------------------
# Main Preprocessor (QUEUE)
# -----------------------------

def preprocess_to_jinja(
    entry_template: Path,
    template_dirs: List[Path],
    project_root: Path,
    build_dir: Path
) -> Path:
    """
    Crawl all Strata templates starting from entry_template,
    convert them to pure Jinja, and write them to strata/build/.

    Returns the path to the converted entry template.
    """

    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    queue: List[str] = []
    discovered: Set[str] = set()

    entry_name = entry_template.stem.replace(".yml", "")
    discovered.add(entry_name)
    queue.append(entry_name)

    while queue:
        current = queue.pop(0)

        source = find_template(current, template_dirs)
        target = build_dir / f"{current}.yml.tpl"

        convert_file_to_jinja(
            source_path=source,
            build_path=target,
            template_dirs=template_dirs,
            discovered=discovered,
            queue=queue,
        )

    return build_dir / f"{entry_name}.yml.tpl"

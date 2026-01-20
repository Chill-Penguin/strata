# Strata

## Purpose

Strata is a CLI tool for defining, composing, and scaffolding project structures using reusable templates.
It has two core responsibilities:

1. **Build stacks** – Render infrastructure or configuration files from composable templates (via Jinja).
2. **Scaffold projects** – Generate new project folder structures (similar to `django-admin startapp`) from predefined blueprints.

This README focuses on *using* Strata, not its internal architecture.

---

## Installation & Setup

### Requirements
- Python 3.11+
- `pip` or `pipx`

### Install (development)
```bash
git clone <your-repo-url>
cd strata
pip install -e .
```

### Verify installation
```bash
strata --help
```

You should see available commands such as `build`, `init`, and `debug`.

---

## First-Time Run Test

Run the debug preprocessor against an example stack file:

```bash
strata debug preprocess stacks/example.yml
```

This will:
- Expand `@include` directives
- Convert inline `@vars` blocks into valid Jinja
- Output the rendered Jinja template for inspection

If this works without errors, your environment is set up correctly.

---

## Using Strata to Build Stacks

### Stack Files

Stack files live under:

```
stacks/
  my-stack.yml
```

A stack file may include reusable blocks:

```yaml
# @include docker/service
# @vars
#   service_name: api
#   port: 8000
```

### Blocks

Reusable blocks live under:

```
blocks/
  docker/
    service.yml.tpl
```

Blocks are standard Jinja templates and receive variables from:
- Inline `@vars`
- Global variables loaded at runtime

---

## Environment Files

Environment variables are stored as YAML:

```
env/
  dev.yml
  prod.yml
```

Example:
```yaml
project_name: myapp
domain: example.com
```

These variables are:
- Loaded at script startup
- Available globally to all templates
- Overridable by inline `@vars`

---

## Scaffolding New Projects

### Purpose of Scaffold

Scaffolding is the *inverse* of stack building.
Instead of rendering config from templates, it creates new project structures from predefined blueprints.

Think:
```bash
django-admin startapp blog
```

But configurable and language-agnostic.

---

### Blueprint Layout

Blueprints live under:

```
scaffolds/
  python-cli/
    __name__/
      __init__.py
      main.py
    pyproject.toml
```

Notes:
- `__name__` is replaced with the project name
- Files may be plain text or Jinja templates

---

### Creating a New Project

```bash
strata init python-cli myapp
```

This will:
1. Locate `scaffolds/python-cli`
2. Copy its structure
3. Replace `__name__` with `myapp`
4. Render any Jinja templates
5. Output a ready-to-use project folder

Result:
```
myapp/
  myapp/
    __init__.py
    main.py
  pyproject.toml
```

---

## Adding New Stacks

1. Create a new stack file:
   ```
   stacks/my-stack.yml
   ```

2. Reference reusable blocks:
   ```yaml
   # @include docker/service
   ```

3. Add or reuse block templates under:
   ```
   blocks/<category>/<name>.yml.tpl
   ```

---

## Adding New Scaffolds

1. Create a new scaffold directory:
   ```
   scaffolds/node-api/
   ```

2. Define the desired folder structure
3. Use `__name__` where the project name should appear
4. Optionally use Jinja for dynamic files

Test with:
```bash
strata init node-api test-project
```

---

## Philosophy

- **Composable over monolithic**
- **Explicit over magic**
- **Readable templates over DSLs**
- **Scaffolding and building are separate concerns**

Strata is meant to be predictable, inspectable, and boring—in the best way.

---

## License

MIT

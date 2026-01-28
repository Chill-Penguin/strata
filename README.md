# Strata

## Purpose

Strata is a CLI tool for defining, composing, and scaffolding project structures using reusable templates.
It has two core responsibilities:

1. **Build stacks** – Render infrastructure, configuration, or any other text file from composable templates (via Jinja).
2. **Scaffold projects** – Generate new project folder structures (similar to `django-admin startapp`) from predefined blueprints.

---

## Installation & Setup

### Requirements
- Python 3.11+
- `pip` or `pipx`

### Install (development)
```bash
git clone https://github.com/Chill-Penguin/strata.git
cd strata
pip install -e .
```

### Verify installation
```bash
strata --help
```

You should see available commands such as `build`, `init`, and `setup`.


### Create home directory
This will create the .strata folder in your home directory which will be covered in more detail later.
```
strata setup
```

---


## Building Stacks

### Stack Files

Stack files are the starting template for any file that needs to be built. Stacks could be docker-compose files, HTML files, or any text file where it makes sense to divide and conquer. Example stack files can be found in:

```
~/.strata/
    stacks/
```

Stack file exist in your project directory and support standard text, Jinja template code, and custom Strata directives.

### Strata directives
Strata currently supports a comment style directive system meant to be human readable while remaining valid syntax. These directives are then pre-compiled into jinja syntax before building the file. All directives must have a hash style comment followed by a space before.

#### @include
The include directive is used to insert reusable blocks into the file. It supports inline variabled which will be used for that specific block. This allows multiple of the same block in a file with different variables.

```
  # @include base_service_template
  # @vars
  #   service_name: homepage
  #   image: ghcr.io/gethomepage/homepage
  #   traefik_port: 3000
  #   volumes:
  #     - ./config:/app/config
  #     - /var/run/docker.sock:/var/run/docker.sock

  # @include base_service_template
  # @vars
  #   service_name: adminer
  #   image: adminer
  #   traefik_port: 8080
  #   homepage_group: Admin
  #   homepage_name: Adminer
  #   homepage_icon: adminer.png
  #   homepage_description: Database client
  #   timezone: America/Chicago

  # @include base_traefik_network_template
```


### Blocks

Blocks are reusable components which can be included in stacks. Blocks may include other blocks as needed through the @include directive.
Examples of blocks live under:

```
~/.strata/
    blocks/
```

Blocks function as standard Jinja templates and receive variables from:
- Inline `@vars`
- Global variables loaded at runtime


### Building a stack
Stacks can be built (rendered) with the command
```
strata build <filename>
```

---

## Environment Files

Strata supports a layered environment file structure. Environment files can live:
- under the ~/.strata/vars directory
- in the project strata/vars directory
- as inline variables defined in the @include directive

On script startup, environment files are prioritized according to their distance from the target file. Meaning the resolution order top to bottom is:
1. Inline vars
2. Project vars
3. Global vars

This allows the user to define variables that apply to multiple projects and can change those values in one location to apply to all projects as needed.

---

## Scaffolding New Projects

### Purpose of Scaffold

Scaffolding is an additional layer on top of stacks. Scaffolds allow you to define template directories and files in order to bootstrap project folders.

Think:
```bash
django-admin startapp blog
```

But configurable and language-agnostic.

---

### Scaffold Layout
Scaffolds are defined inside of the .strata home directory.

```
~/.strata/
    scaffolds/
```

Each scaffold should be placed inside of its own subdirectory with a descriptive name. For instance

```
~/.strata/
    scaffolds/
        python-cli/
            main.py
            commands/
            etc/
```

---

### Creating a New Project
Scaffolds are created using the init command. The init command takes the name of the scaffold to be created and an optional project folder name. If specified, the project folder will be created first and then the scaffold will be copied over. If no project name is specified, the scaffold will be copied to the current working directory.

```bash
strata init python-cli myapp
```

This will:
1. Locate `scaffolds/python-cli`
2. Copy its structure
3. Replace `__name__` with `myapp`
4. Render any Jinja templates (soon!)
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


# src/strata/cli.py
import click
from pathlib import Path

@click.group()
def cli():
    """Strata CLI"""
    pass

@cli.command()
def setup():
    from strata.setup import run_setup
    run_setup()

@cli.command()
def uninstall():
    from strata.setup import run_uninstall

    click.echo("WARNING: This will delete your entire Strata setup directory!")
    confirm = click.confirm("Are you sure you want to continue?", default=False)
    if not confirm:
        click.echo("Uninstall canceled.")
        return
    
    run_uninstall()

@cli.command()
@click.argument("template_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--profile", default="dev", help="Environment profile to use (dev, qa, prod)")
def build(template_path, profile):
    from strata.config import ensure_setup
    from strata.builder.compose import build_stack

    ensure_setup()
    build_stack(template_path, profile=profile)

@cli.command()
@click.argument("template_name")
@click.argument("module_name")
def init(template_name, module_name):
    from strata.builder.scaffold import init_project
    init_project(template_name, module_name)

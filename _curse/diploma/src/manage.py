import click

from src.commands.create_admin import create_admin


@click.group()
def cli():
    pass


cli.add_command(create_admin)

if __name__ == '__main__':
    cli()

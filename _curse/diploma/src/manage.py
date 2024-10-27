import click

from src.commands.create_admin import create_admin
from src.commands.insert_languages import insert_languages
from src.commands.insert_report_reasons import insert_report_reasons
from src.commands.start_translator_consumer import start_translator_consumer
from src.commands.start_mail_consumer import start_mail_consumer


@click.group()
def cli():
    pass


cli.add_command(create_admin)
cli.add_command(insert_languages)
cli.add_command(insert_report_reasons)
cli.add_command(start_translator_consumer)
cli.add_command(start_mail_consumer)

if __name__ == '__main__':
    cli()

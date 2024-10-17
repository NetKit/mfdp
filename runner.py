import click
import asyncio

from app.telegram import run_bot


@click.group()
def cli():
    pass


@click.command()
def bot():
    """Command to start the Telegram bot."""
    asyncio.run(run_bot())


cli.add_command(bot)

if __name__ == "__main__":
    cli()

from pathlib import Path

import click

from feedcraft.rss import parse_rss


@click.group()
def main():
    pass


def _is_feed_any_rss(feed: str) -> bool:
    return "<rss" in feed


@main.command()
# Add a feed_path argument to the command
@click.argument("feed_path", type=click.Path(exists=True))
def parse(feed_path: Path):
    """Parse the RSS feed at the given FEED_PATH and print the titles of the items."""

    with open(feed_path, "r", encoding="utf-8") as f:
        feed_content = f.read()

    if not _is_feed_any_rss(feed_content):
        click.echo(
            "The provided file does not appear to be a valid RSS feed.", err=True
        )
        return

    feed = parse_rss(feed_content)

    click.echo(f"Feed Title: {feed.channel.title}")
    click.echo("Items:")
    for item in feed.channel.items:
        click.echo(f"- {item.pub_date}: {item.title}")


@main.command()
@click.argument("feed_dir_path", type=click.Path(exists=True, dir_okay=True))
def parse_dir(feed_dir_path: Path):
    """Parse all RSS feeds in the given FEED_DIR_PATH and print the titles of the items."""

    feed_dir = Path(feed_dir_path)

    for i, feed_file in enumerate(feed_dir.iterdir()):
        if feed_file.is_file():
            with open(feed_file, "r", encoding="utf-8") as f:
                feed_content = f.read()

            if not _is_feed_any_rss(feed_content):
                click.echo(
                    f"[{i + 1}] {feed_file.name}: not a valid RSS feed",
                    err=True,
                )
                continue

            try:
                feed = parse_rss(feed_content)
            except Exception as e:
                click.echo(f"[{i + 1}] Error parsing {feed_file}: {str(e)}", err=True)
                continue

            click.echo(
                f"\n\n-------\n\n[{i + 1}]\nFeed Title: {feed.channel.title} (from {feed_file.name})"
            )
            click.echo("Items:")
            for item in feed.channel.items:
                click.echo(f"- {item.pub_date}: {item.title}")


if __name__ == "__main__":
    main()

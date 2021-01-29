"""Console script for gnome_next_meeting_applet."""
import sys
import click

import gnome_next_meeting_applet.applet as gnma


@click.command()
def main(args=None):
    """Console script for gnome_next_meeting_applet."""
    gnma.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

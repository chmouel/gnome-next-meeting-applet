"""Console script for gnome_next_meeting_applet."""
import argparse
import sys

from gnma import applet, dbusclient


def parse_args():
    parser = argparse.ArgumentParser(description="Gnome next meeting applet")
    parser.add_argument(
        "--verbose", "-v", dest="verbose", action="store_true", help="verbose"
    )

    client_parser = parser.add_subparsers(help="Dbus Client")
    dbus_parser = client_parser.add_parser("dbus")
    dbus_parser.add_argument(
        "dbus_command",
        choices=[
            "get_event",
            "get_event_url",
            "get_event_json",
            "open_event_url",
            "get_event_document",
        ],
    )
    return parser.parse_args()


def cli():
    """Console script for gnome_next_meeting_applet."""
    args = parse_args()
    if "dbus_command" in args:
        db_client = dbusclient.DBUSClient()
        db_client.commands(args)
        return 0
    applet.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover

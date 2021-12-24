"""Console script for gnome_next_meeting_applet."""
import argparse
import sys

import dbus

from gnma import applet, dbusservice


def parse_args():
    parser = argparse.ArgumentParser(description="Gnome next meeting applet")
    parser.add_argument("--get-last-status",
                        choices=["plain"],
                        help="Get last status directly from command line")
    parser.add_argument("--verbose",
                        "-v",
                        dest="verbose",
                        action="store_true",
                        help="verbose")
    return parser.parse_args()


def get_via_dbus():
    notfy_intf = dbus.Interface(
        dbus.SessionBus().get_object(
            dbusservice.DBUS_BUS_NAME,
            "/" + dbusservice.DBUS_BUS_NAME.replace(".", "/")),
        dbusservice.DBUS_BUS_NAME)
    return notfy_intf.GetNextMeeting()


def get_last_status(mode):
    try:
        nextone = get_via_dbus()
    except dbus.exceptions.DBusException:
        return ""
    if not nextone:
        return ""
    if mode == "plain":
        return f"{nextone[0]} - {nextone[1]}"
    return ""


def cli():
    """Console script for gnome_next_meeting_applet."""
    args = parse_args()
    if args.get_last_status:
        status = get_last_status(args.get_last_status)
        if status:
            print(status)
        return 0

    applet.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover

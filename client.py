import argparse
import json

import dbus

DBUS_SERVICE = "gnma.GnmaService"


def getnext():
    notfy_intf = dbus.Interface(
        dbus.SessionBus().get_object(DBUS_SERVICE,
                                     "/" + DBUS_SERVICE.replace(".", "/")),
        DBUS_SERVICE)
    return notfy_intf.GetNextMeeting()


def main():
    parser = argparse.ArgumentParser("gnome-next-meeting-applet client")
    parser.add_argument('mode', choices=["plain"])
    args = parser.parse_args()
    if args.mode == "plain":
        nextone = getnext()
        if not nextone:
            return ""
        print(f"{nextone[0]} - {nextone[1]}")

    # TODO: in waybar json we can output percentage so if we are in a meeting
    # we can output how long we have until it finishes 🥵


if __name__ == '__main__':
    main()

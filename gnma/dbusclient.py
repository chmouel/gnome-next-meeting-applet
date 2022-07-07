import argparse
import json

import dbus
import gi  # type:ignore

gi.require_version("Gtk", "3.0")
# pylint: disable=E0611
from gi.repository import Gtk as gtk

from gnma import dbusservice


class DBUSClient:
    verbose: bool
    dbus_intf: dbus.Interface

    def start_dbus_interface(self) -> bool:
        try:
            self.dbus_intf = dbus.Interface(
                dbus.SessionBus().get_object(
                    dbusservice.DBUS_BUS_NAME,
                    "/" + dbusservice.DBUS_BUS_NAME.replace(".", "/"),
                ),
                dbusservice.DBUS_BUS_NAME,
            )
        except dbus.exceptions.DBusException as excp:
            if self.verbose:
                raise excp
            return False
        return True

    def commands(self, args: argparse.Namespace):
        self.verbose = args.verbose
        if not self.start_dbus_interface():
            return

        if args.dbus_command == "get_event":
            ret = self.get_event_plain()
            if ret:
                print(ret)
        elif args.dbus_command == "get_event_json":
            ret = self.get_event_json()
            if ret:
                print(ret)
        elif args.dbus_command == "get_event_url":
            ret = self.get_event_url()
            if ret:
                print(ret)
        elif args.dbus_command == "get_event_document":
            ret = self.get_event_document()
            if ret:
                print(ret)
        elif args.dbus_command == "open_event_url":
            ret = self.get_event_url()
            if ret:
                print(ret)
                gtk.show_uri(None, ret, gtk.get_current_event_time())

    def get_event_url(self) -> str:
        try:
            eventurl = self.dbus_intf.GetNextEventURL()
        except dbus.exceptions.DBusException as excp:
            if self.verbose:
                raise excp
            return ""
        if not eventurl:
            return ""
        return eventurl

    def get_event_json(self) -> str:
        try:
            nextone = self.dbus_intf.GetNextEvent()
        except dbus.exceptions.DBusException as excp:
            if self.verbose:
                raise excp
            return ""

        ret = {
            "tooltip": f"{nextone[0]} - {nextone[1]}",
            "percentage": 1,
            "timeto": nextone[0],
            "title": nextone[1],
            "text": nextone[0],
        }
        return json.dumps(ret)

    def get_event_plain(self) -> str:
        try:
            nextone = self.dbus_intf.GetNextEvent()
        except dbus.exceptions.DBusException as excp:
            if self.verbose:
                raise excp
            return ""
        if not nextone:
            return ""
        return f"{nextone[0]} - {nextone[1]}"

    def get_event_document(self) -> str:
        try:
            doc = self.dbus_intf.GetEventDocument()
        except dbus.exceptions.DBusException as excp:
            if self.verbose:
                raise excp
            return ""
        return doc

# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# pylint: disable=no-self-use
"""Gnome next meeting calendar applet via Google Calendar"""
import datetime
import os.path
import pathlib
import re
import typing

import dateutil.relativedelta as dtrelative
import dateutil.tz as dttz
import pytz
import yaml

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gdk as gdk
from gi.repository import GLib as glib
from gi.repository import Gtk as gtk

import gnome_next_meeting_applet.evolution_calendars as evocal

APP_INDICTOR_ID = "gnome-next-meeting-applet"

DEFAULT_CONFIG = {
    # TODO(chmouel): should be plural
    "restrict_to_calendar": [],
    "skip_non_accepted": True,
    "my_emails": [],
    "max_results": 10,
    "title_max_char": 20,
    "refresh_interval": 300,
    "event_organizers_icon": {},
    "change_icon_minutes": 2,
    "default_icon": "‣",
}

VIDEOCALL_DESC_REGEXP = [
    r"Join Zoom Meeting\n(https://zoom.us/j/[^\n]*)"
    r"This event has a video call.\nJoin: (https://meet.google.com/[^\n]*)"
]


class Applet:
    """Applet: class"""

    events: typing.List = []
    indicator = None

    def __init__(self):
        self.config = DEFAULT_CONFIG
        self.config_dir = os.path.expanduser(
            f"{glib.get_user_config_dir()}/{APP_INDICTOR_ID}"
        )

        configfile = pathlib.Path(self.config_dir) / "config.yaml"
        if configfile.exists():
            self.config = {**DEFAULT_CONFIG, **yaml.safe_load(configfile.open())}
        else:
            configfile.parent.mkdir(parents=True)
            configfile.write_text(yaml.safe_dump(DEFAULT_CONFIG))
            self.config = DEFAULT_CONFIG
            
        self.autostart_file = pathlib.Path(
            f"{glib.get_user_config_dir()}/autostart/gnome-next-meeting-applet.desktop"
        ).expanduser()

    def htmlspecialchars(self, text):
        """Replace html chars"""
        return (
            text.replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def first_event(self, event):
        """Show first event in menubar"""
        # not sure why but on my gnome version (arch 40.4.0) we don't need to do
        # htmlspecialchars in bar, but i am sure on ubuntu i needed that, YMMV :-d !
        summary = event.get_summary().get_value().strip()[: self.config["title_max_char"]]
        now = datetime.datetime.now().astimezone(pytz.timezone("UTC"))

        start_time = evocal.get_ecal_as_utc(event.get_dtstart())
        end_time = evocal.get_ecal_as_utc(event.get_dtend())

        if start_time < now < end_time:
            _rd = dtrelative.relativedelta(end_time, now)
        else:
            _rd = dtrelative.relativedelta(start_time, now)

        humzrd = ""
        for dttype in (("day", _rd.days), ("hour", _rd.hours), ("minute", _rd.minutes)):
            if dttype[1] == 0:
                continue
            humzrd += f"{dttype[1]} {dttype[0]}"
            if dttype[1] > 1:
                humzrd += "s"
            humzrd += " "
        if start_time < now < end_time:
            humzrd = humzrd.strip() + " left"
        return f"{humzrd.strip()} - {summary}"

    def get_all_events(self):
        """Get all events from Google Calendar API"""
        # event_list = json.load(open("/tmp/allevents.json"))

        evolutionCalendar = evocal.EvolutionCalendarWrapper()
        # TODO: add filtering user option GUI instead of just yaml
        event_list = evolutionCalendar.get_all_events(
            restrict_to_calendar=self.config["restrict_to_calendar"]
        )
        ret = []

        events_sorted = sorted(
            event_list, key=lambda x: evocal.get_ecal_as_utc(x.get_dtstart())
        )
        for event in events_sorted:
            if event.get_status().value_name != "I_CAL_STATUS_CONFIRMED":
                print("SKipping not confirmed")
                continue

            skipit = False
            if self.config["skip_non_accepted"]:
                skipit = True
                for attendee in event.get_attendees():
                    for myemail in self.config["my_emails"]:
                        if (
                            attendee.get_value().replace("mailto:", "") == myemail
                            and attendee.get_partstat().value_name
                            == "I_CAL_PARTSTAT_ACCEPTED"
                        ):
                            skipit = False
            if skipit:
                continue

            ret.append(event)

        return ret

    # pylint: disable=unused-argument
    def set_indicator_icon_label(self, source):
        now = datetime.datetime.now().astimezone(pytz.timezone("UTC"))
        first_start_time = evocal.get_ecal_as_utc(self.events[0].get_dtstart())
        first_end_time = evocal.get_ecal_as_utc(self.events[0].get_dtend())

        if (
            now
            > (
                first_start_time
                - datetime.timedelta(minutes=self.config["change_icon_minutes"])
            )
            and not now > first_start_time
        ):
            source.set_icon(self.get_icon_path("notification"))
        elif now >= first_end_time:  # need a refresh
            self.make_menu_items()
            return self.set_indicator_icon_label(source)
        else:
            source.set_icon(self.get_icon_path("calendar"))

        source.set_label(f"{self.first_event(self.events[0])}", APP_INDICTOR_ID)
        return True

    def get_icon_path(self, icon):
        devpath = pathlib.Path(__file__).parent.parent / "images"
        if not devpath.exists():
            devpath = pathlib.Path("/usr/share/gnome-next-meeting/images")

        for ext in ["svg", "png"]:
            if (devpath / f"{icon}.{ext}").exists():
                return str(devpath / f"{icon}.{ext}")
        return "x-office-calendar-symbolic"

    # pylint: disable=unused-argument
    def applet_quit(self, source):
        gtk.main_quit()

    def applet_click(self, source):
        gtk.show_uri(None, source.location, gdk.CURRENT_TIME)

    def make_menu_items(self):
        self.events = self.get_all_events()

        menu = gtk.Menu()
        now = datetime.datetime.now().astimezone(pytz.timezone("UTC"))
        currentday = ""

        event_first = self.events[0]
        event_first_start_time = evocal.get_ecal_as_utc(event_first.get_dtstart())
        event_first_end_time = evocal.get_ecal_as_utc(event_first.get_dtend())

        if (
            event_first_start_time < now
            and now < event_first_end_time
            and event_first.get_attachments()
        ):
            menuitem = gtk.MenuItem(label="📑 Open current meeting document")
            menuitem.location = event_first.get_attachments()[0].get_url()
            menuitem.connect("activate", self.applet_click)
            menu.add(menuitem)
            menu.append(gtk.SeparatorMenuItem())
            menu.append(gtk.MenuItem(" "))

        for event in self.events[0 : int(self.config["max_results"])]:
            # TODO print the day
            start_time = evocal.get_ecal_as_utc(event.get_dtstart())
            start_time = start_time.astimezone(dttz.gettz())

            _cday = start_time.strftime("%A %d %B %Y")

            if _cday != currentday:
                if currentday != "":
                    menu.append(gtk.MenuItem(label=""))
                todayitem = gtk.MenuItem(
                    label=f'<span size="large" font="FreeSerif:18">{_cday}</span>'
                )
                todayitem.get_child().set_use_markup(True)
                todayitem.location = f"https://calendar.google.com/calendar/r/day/{start_time.strftime('%Y/%m/%d')}"
                todayitem.connect("activate", self.applet_click)
                menu.append(todayitem)
                menu.append(gtk.SeparatorMenuItem())
                currentday = _cday

            summary = self.htmlspecialchars(event.get_summary().get_value().strip())
            organizer = event.get_organizer().get_value().replace("mailto:", "")

            icon = self.config["default_icon"]
            for regexp in self.config["event_organizers_icon"]:
                if re.match(regexp, organizer):
                    icon = self.config["event_organizers_icon"][regexp]
                    break

            start_time_str = start_time.strftime("%H:%M")
            if now >= start_time:
                summary = f"<i>{summary}</i>"
            menuitem = gtk.MenuItem(label=f"{icon} {summary} - {start_time_str}")
            menuitem.get_child().set_use_markup(True)

            match_videocall_summary = self._match_videocall_url_from_summary(event)

            if event.get_location() and event.get_location().startswith("https://"):
                menuitem.location = event.get_location()
            elif match_videocall_summary:
                menuitem.location = match_videocall_summary
            else:
                menuitem.location = ""

            menuitem.connect("activate", self.applet_click)
            menu.append(menuitem)

        menu.append(gtk.SeparatorMenuItem())

        settingMenu = gtk.Menu()
        label = (
            "Remove autostart" if self.autostart_file.exists() else "Auto start at boot"
        )
        item_autostart = gtk.MenuItem(label=label)
        item_autostart.connect("activate", self.install_uninstall_autostart)
        settingMenu.add(item_autostart)
        settingItem = gtk.MenuItem("Setting")
        settingItem.set_submenu(settingMenu)
        menu.add(settingItem)

        item_quit = gtk.MenuItem(label="Quit")
        item_quit.connect("activate", self.applet_quit)
        menu.add(item_quit)

        menu.show_all()

        self.indicator.set_menu(menu)

    def _match_videocall_url_from_summary(self, event) -> str:
        # can you have multiple descriptions???
        text = event.get_descriptions()[0].get_value()
        for reg in VIDEOCALL_DESC_REGEXP:
            match = re.search(reg, text)
            if match:
                url = match.groups()[0]
                return url
        return ""

    def install_uninstall_autostart(self, source):

        if self.autostart_file.exists():
            self.autostart_file.unlink()
            source.set_label("Auto start at boot")
            return

        self.autostart_file.write_text(
            """#!/usr/bin/env xdg-open
[Desktop Entry]
Categories=Productivity;
Comment=Google calendar applet to show next meetings
Exec=gnome-next-meeting-applet
Icon=calendar
Name=Google Calendar next meeting
StartupNotify=false
Type=Application
Version=1.0
"""
        )
        source.set_label("Remove autostart")

    def build_indicator(self):
        self.indicator = appindicator.Indicator.new(
            APP_INDICTOR_ID,
            self.get_icon_path("calendar"),
            appindicator.IndicatorCategory.SYSTEM_SERVICES,
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.make_menu_items()
        self.set_indicator_icon_label(self.indicator)
        glib.timeout_add_seconds(30, self.set_indicator_icon_label, self.indicator)
        glib.timeout_add_seconds(self.config["refresh_interval"], self.make_menu_items)
        gtk.main()

    def main(self):
        self.build_indicator()


def run():
    c = Applet()
    c.main()


if __name__ == "__main__":
    run()

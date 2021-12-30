# -*- coding: utf-8 -*-
import datetime
import logging
import pathlib
import re
import dbus.exceptions

import gi  # type:ignore
import yaml

gi.require_version("AppIndicator3", "0.1")
gi.require_version("EDataServer", "1.2")
gi.require_version("Gtk", "3.0")
# pylint: disable=E0611 disable=C0411
from gi.repository import AppIndicator3 as appindicator  # type:ignore
from gi.repository import EDataServer
from gi.repository import Gtk as gtk
from gi.repository import GLib as glib

from gnma import config
from gnma import gnome_online_account_cal as goacal
from gnma import strings
from gnma import dbusservice

APP_INDICTOR_ID = "gnome-next-meeting-applet"


class Applet(goacal.GnomeOnlineAccountCal):

    def __init__(self, args):
        self.args = args
        super().__init__()
        self.config = config.DEFAULT_CONFIG
        self.last_sorted = None
        self.indicator = appindicator.Indicator.new(
            APP_INDICTOR_ID,
            "calendar",
            appindicator.IndicatorCategory.SYSTEM_SERVICES,
        )
        try:
            self.dbus_server = dbusservice.DBusService(self)
        except dbus.exceptions.DBusException:
            logging.debug("cannot start dbus service")
        self.autostart_file = pathlib.Path(
            f"{glib.get_user_config_dir()}/autostart/gnome-next-meeting-applet.desktop"
        )

    def set_logging(self):
        if self.args.verbose:
            logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

    def get_or_init_config(self) -> None:
        configfile = pathlib.Path(config.CONFIG_FILE).expanduser()
        if configfile.exists():
            logging.debug("loading configfile: %s", configfile)
            self.config = {
                **config.DEFAULT_CONFIG,
                **yaml.safe_load(configfile.open())
            }
            if self.config["verbose"]:
                self.args.verbose = True
                self.set_logging()
            return
        logging.debug("creating configfile %s", str(configfile))
        configfile.parent.mkdir(parents=True)
        configfile.write_text(yaml.safe_dump(config.DEFAULT_CONFIG))
        self.config = config.DEFAULT_CONFIG

    def sort_and_filter_event(self):
        ret = []
        events = sorted(self.all_events.values(), key=lambda x: x.start_dttime)
        if events is None:
            return []
        for event in events:
            if datetime.datetime.now() > event.end_dttime:
                del self.all_events[event.uid]
                logging.debug("[skipping] elapsed: %s", event.summary)
                continue
            if (self.config["skip_non_confirmed"]
                    and event.comp.get_status().value_name !=
                    "I_CAL_STATUS_CONFIRMED"):
                logging.debug("[SKIP] non confirmed event")
                continue

            skipit = False
            if self.config["skip_non_accepted"] and self.config["my_emails"]:
                skipit = True
                for attendee in event.comp.get_attendees():
                    for myemail in self.config["my_emails"]:
                        if (attendee.get_value().replace("mailto:",
                                                         "") == myemail
                                and attendee.get_partstat().value_name
                                == "I_CAL_PARTSTAT_ACCEPTED"):
                            skipit = False
            if skipit:
                logging.debug("[SKIP] not accepted: %s",
                              event.comp.get_summary().get_value())
                del self.all_events[event.uid]
                continue

            ret.append(event)

        lastids = [x.uid for x in ret[:self.config["max_results"]]]
        if self.last_sorted and self.last_sorted == lastids:
            return []

        self.last_sorted = lastids
        return ret[:self.config["max_results"]]

    def first_event_label(self, event):
        """Show first event in menubar"""
        comp = event.comp

        # not sure why but on my gnome version (arch 40.4.0) we don't need to do
        # htmlspecialchars in bar, but i am sure on ubuntu i needed that, YMMV :-d !
        summary = comp.get_summary().get_value().strip()
        if self.config["strip_title_emojis"]:
            summary = strings.remove_emojis(summary)

        now = datetime.datetime.now()
        if event.end_dttime == now:
            return ["Meeting over 😲", summary]
        humanized_str = strings.humanize_time(event.start_dttime,
                                              event.end_dttime)
        return [humanized_str, summary]

    def get_icon_path(self, icon):
        if (f"icon_{icon}_path" in self.config
                and pathlib.Path(self.config[f"icon_{icon}_path"]).exists()):
            return self.config[f"icon_{icon}_path"]

        devpath = pathlib.Path(__file__).parent.parent / "data" / "images"
        if not devpath.exists():
            devpath = pathlib.Path(
                "/usr/share/gnome-next-meeting-applet/images")
        if not devpath.exists():
            devpath = pathlib.Path(
                "/app/share/icons/gnome-next-meeting-applet")

        for ext in ["svg", "png"]:
            if (devpath / f"{icon}.{ext}").exists():
                return str(devpath / f"{icon}.{ext}")
        return "x-office-calendar-symbolic"

    def open_source_location(self, source):
        if source.location == "":
            return
        logging.debug("Opening Location: %s", source.location)
        gtk.show_uri(None, source.location, gtk.get_current_event_time())

    def _get_icon(self, event):
        now = datetime.datetime.now()
        # pylint: disable=C0113,R1705
        if (now >
            (event.start_dttime -
             datetime.timedelta(minutes=self.config["change_icon_minutes"]))
                and not now > event.start_dttime):
            return [self.get_icon_path("before_event"), "Meeting start soon!"]
        elif now >= event.start_dttime and event.end_dttime > now:
            return [self.get_icon_path("in_event"), "In meeting! Focus"]
        return [self.get_icon_path("default"), "Next meeting"]

    def get_icon_label(self, event=None):
        if event is None:
            if len(self.all_events) > 0:
                self.make_menu_items()
                event = self.all_events[self.last_sorted[0]]
            else:
                return []
        icon, tooltip = self._get_icon(event)
        humanized_str, title = self.first_event_label(event)
        return [icon, tooltip, humanized_str, title]

    def set_indicator_icon_label(self, event=None):
        geticon = self.get_icon_label(event)
        if not geticon:
            return True
        # pylint: disable=W0632
        (icon, tooltip, humanized_str, title) = geticon
        self.indicator.set_icon_full(icon, tooltip)

        title = title[:self.config["title_max_char"]]
        self.indicator.set_label(f"{humanized_str} - {title}", APP_INDICTOR_ID)
        return True

    def add_last_item(self, menu):
        setting_menu = gtk.Menu()
        label = ("Remove autostart"
                 if self.autostart_file.exists() else "Auto start at boot")
        item_autostart = gtk.MenuItem(label=label)
        item_autostart.connect("activate", self.install_uninstall_autostart)
        setting_menu.add(item_autostart)

        setting_item = gtk.MenuItem()
        setting_item.set_label("Setting")
        setting_item.set_submenu(setting_menu)
        menu.add(setting_item)

        item_quit = gtk.MenuItem(label="Quit")
        item_quit.connect("activate", gtk.main_quit)
        menu.add(item_quit)
        menu.show_all()
        self.indicator.set_menu(menu)

    def make_attacchment_item(self, menu, event):
        now = datetime.datetime.now()
        if not (event.start_dttime < now and now < event.end_dttime
                and event.comp.get_attachments()):
            return menu
        menuitem = gtk.MenuItem(label="📑 Open current meeting document")
        menuitem.location = event.comp.get_attachments()[0].get_url()
        menuitem.connect("activate", self.open_source_location)
        menu.add(menuitem)
        menu.append(gtk.SeparatorMenuItem())
        return menu

    def get_meeting_url(self, event=None) -> str:
        if event is None:
            if len(self.all_events) > 0:
                self.make_menu_items()
                event = self.all_events[self.last_sorted[0]]
            else:
                return ""

        if event.comp.get_location() and event.comp.get_location().startswith(
                "https://"):
            return event.comp.get_location()

        match_videocall_summary = self.match_videocall_url_from_summary(event)
        if match_videocall_summary:
            return match_videocall_summary

        return ""

    def make_menu_items(self):
        menu = gtk.Menu()

        events = self.sort_and_filter_event()
        if not events:
            return
        first_event = events[0]
        self.set_indicator_icon_label(first_event)
        menu = self.make_attacchment_item(menu, first_event)

        currentday = ""
        for event in events:
            event_day = event.start_dttime.strftime("%A %d %B %Y")
            if event_day != currentday:
                menu = self.add_current_day(menu, event, currentday)
                currentday = event_day

            summary = strings.htmlspecialchars(
                event.comp.get_summary().get_value().strip())
            if datetime.datetime.now() >= event.start_dttime:
                summary = f"<i>{summary}</i>"
            icon = self.make_icon(event)
            start_time_str = event.start_dttime.strftime("%H:%M")
            menuitem = gtk.MenuItem(
                label=f"{icon} {summary} - {start_time_str}")
            menuitem.get_child().set_use_markup(True)

            menuitem.location = self.get_meeting_url(event)
            menuitem.connect("activate", self.open_source_location)
            menu.append(menuitem)

        self.add_last_item(menu)

    def make_icon(self, event):
        icon = self.config["default_icon"]
        _organizer = event.comp.get_organizer()
        if _organizer:
            organizer = _organizer.get_value().replace("mailto:", "")
            for regexp in self.config["event_organizers_icon"]:
                if re.match(regexp, organizer):
                    icon = self.config["event_organizers_icon"][regexp]
                    break

        if icon == self.config["default_icon"]:
            title = event.comp.get_summary().get_value()
            for regexp in self.config["title_match_icon"]:
                if re.match(regexp, title):
                    icon = self.config["title_match_icon"][regexp]
        return icon

    def add_current_day(self, menu, event, currentday):
        event_day = event.start_dttime.strftime("%A %d %B %Y")
        if currentday != "":
            menu.append(gtk.MenuItem(label=""))
        todayitem = gtk.MenuItem(
            label=f'<span size="large">{event_day}</span>')
        todayitem.get_child().set_use_markup(True)
        prefix_url = self.config["calendar_day_prefix_url"]
        # this only works with google calendar i think
        todayitem.location = f"{prefix_url}/{event.start_dttime.strftime('%Y/%m/%d')}"
        todayitem.connect("activate", self.open_source_location)
        menu.append(todayitem)
        menu.append(gtk.SeparatorMenuItem())
        return menu

    def match_videocall_url_from_summary(self, event) -> str:
        descriptions = event.comp.get_descriptions()
        if not descriptions:
            return ""
        # can you have multiple descriptions???
        text = descriptions[0].get_value()
        for reg in config.VIDEOCALL_DESC_REGEXP:
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
        self.autostart_file.write_text(config.AUTOSTART_DESKTOP_FILE)
        source.set_label("Remove autostart")

    def run(self):
        self.set_logging()
        self.get_or_init_config()
        EDataServer.SourceRegistry.new(None, self.goa_registry_callback)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        glib.timeout_add_seconds(2, self.set_indicator_icon_label)
        gtk.main()


def run(args):
    Applet(args).run()

# -*- coding: utf-8 -*-
import datetime
import logging
import pathlib
import re
import dbus.exceptions

import gi  # type:ignore
import yaml

gi.require_version("EDataServer", "1.2")
gi.require_version("Gtk", "3.0")

try:
    gi.require_version("AppIndicator3", "0.1")
except ValueError:
    gi.require_version("AyatanaAppIndicator3", "0.1")

try:
    from gi.repository import AppIndicator3 as appindicator
except ImportError:
    try:
        from gi.repository import AyatanaAppIndicator3 as appindicator  # type:ignore
    except ImportError as e:
        raise Exception("Cannot find ayatana or appindicator3 library") from e

# pylint: disable=E0611 disable=C0411
from gi.repository import EDataServer
from gi.repository import Gtk as gtk
from gi.repository import GLib as glib

from gnma import config
from gnma import gnome_online_account_cal as goacal
from gnma import strings
from gnma import dbusservice
from gnma import icons

APP_INDICTOR_ID = "gnome-next-meeting-applet"


class Applet(goacal.GnomeOnlineAccountCal):
    def __init__(self, args):
        self.args = args
        super().__init__()
        self.config = config.DEFAULT_CONFIG
        self.last_sorted = []
        self.last_label = ""
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
            self.config = {**config.DEFAULT_CONFIG, **yaml.safe_load(configfile.open())}
            if self.config["verbose"]:
                self.args.verbose = True
                self.set_logging()
            return
        logging.debug("creating configfile %s", str(configfile))
        if not configfile.parent.exists():
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
                logging.debug("[SKIP] elapsed: %s", event.summary)
                continue
            if (
                    self.config["starts_today_only"]
                    and datetime.datetime.now().date() < event.end_dttime.date()
            ):
                del self.all_events[event.uid]
                logging.debug("[SKIP] non today event: %s", event.summary)
                continue
            if (
                    self.config["skip_non_confirmed"]
                    and event.comp.get_status().value_name != "I_CAL_STATUS_CONFIRMED"
            ):
                logging.debug("[SKIP] non confirmed event")
                continue
            if self.config["skip_all_day"] and event.all_day:
                logging.debug("[SKIP] all day event")
                continue

            skipit = False
            if self.config["skip_non_accepted"] and self.config["my_emails"]:
                skipit = True
                for attendee in event.comp.get_attendees():
                    for myemail in self.config["my_emails"]:
                        if (
                                attendee.get_value().replace("mailto:", "") == myemail
                                and attendee.get_partstat().value_name
                                == "I_CAL_PARTSTAT_ACCEPTED"
                        ):
                            skipit = False
            if skipit:
                logging.debug(
                    "[SKIP] not accepted: %s", event.comp.get_summary().get_value()
                )
                del self.all_events[event.uid]
                continue

            ret.append(event)

        lastids = [x.uid for x in ret[: self.config["max_results"]]]
        if self.last_sorted and self.last_sorted == lastids:
            return []

        self.last_sorted = lastids
        return ret[: self.config["max_results"]]

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
        humanized_str = strings.humanize_time(event.start_dttime, event.end_dttime)
        return [humanized_str, summary]

    def open_description_window(self, source):

        def parse_description_to_markdown(description_string):
            """
            Parses the event descriptions into Pango markup with clickable links.
            E-Mail descriptions are very unsafe, so it's trivial to break the markup conversion.
            This is why we escape the descriptions and explicitly convert escaped URLs in
            angle-bracket format back to a clickable markup URL. Regular URLs are not
            escaped, hence we use a normal regex.
            """
            # Matches normal inline links with white-space in front.
            normal_url_regex = r"(\s)(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}" \
                               r"\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:$§%_\+.~#?&\/=]*))"
            # Matches links in the escaped angle-bracket format (e.g. Link<URL>)
            # See https://www.rfc-editor.org/rfc/rfc2822#section-3.4
            escaped_angle_bracket_url_regex = r"(\S*)&lt;(.+?(?=&gt;))&gt;"

            description_markup = glib.markup_escape_text(description_string)
            description_markup = re.sub(
                escaped_angle_bracket_url_regex,
                r'<a href="\2" title="\2">\1</a>',
                description_markup
            )
            description_markup = re.sub(
                normal_url_regex,
                r'\1<a href="\2" title="\2">\2</a>',
                description_markup)

            return description_markup

        class EventDescriptionWindow(gtk.Window):
            def __init__(self):
                super().__init__(title="Please manually select meeting link")
                self.set_default_size(600, 400)

                self.grid = gtk.Grid()
                self.add(self.grid)

                scrolled_window = gtk.ScrolledWindow()
                scrolled_window.set_hexpand(True)
                scrolled_window.set_vexpand(True)
                self.grid.attach(scrolled_window, 0, 1, 3, 1)

                self.label = gtk.Label()
                self.label.set_selectable(True)
                scrolled_window.add(self.label)

                # Set all event descriptions in label
                summary_string = source.event.comp.get_summary().get_value()
                description_string = "\n".join(
                    map(lambda desc: desc.get_value(), source.event.comp.get_descriptions()))

                label_string = (summary_string + "\n" + description_string) \
                               or "Event description is empty."
                parsed_label_string = parse_description_to_markdown(label_string)
                self.label.set_markup(parsed_label_string)

        win = EventDescriptionWindow()
        win.show_all()

    def open_source_location(self, source):
        if source.location == "":
            return
        logging.debug("Opening Location: %s", source.location)
        gtk.show_uri(None, source.location, gtk.get_current_event_time())

    def get_event(self):
        if len(self.all_events) > 0:
            self.make_menu_items()
            return self.all_events[self.last_sorted[0]]
        return None

    def set_indicator_icon_label(self, event=None):
        if event is None:
            event = self.get_event()
            if not event:
                return True
        getlabel = self.first_event_label(event)
        if not getlabel:
            return True
        # pylint: disable=W0632
        humanized_str, title = getlabel
        title = title[: self.config["title_max_char"]]

        new_label = f"{humanized_str} - {title}"
        if self.last_label == new_label:
            return True

        icon, tooltip = icons.by_event_time(self.config, event)
        self.indicator.set_icon_full(icon, tooltip)

        self.last_label = new_label
        self.indicator.set_label(new_label, APP_INDICTOR_ID)
        return True

    def add_last_item(self, menu):
        menu.append(gtk.SeparatorMenuItem())

        setting_menu = gtk.Menu()
        label = (
            "Remove autostart" if self.autostart_file.exists() else "Auto start at boot"
        )
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

    def make_attachment_item(self, menu, event):
        now = datetime.datetime.now()
        if not (
                event.start_dttime < now
                and now < event.end_dttime
                and event.comp.get_attachments()
        ):
            return menu
        menuitem = gtk.MenuItem(label="📑 Open current meeting document")
        menuitem.location = event.comp.get_attachments()[0].get_url()
        menuitem.connect("activate", self.open_source_location)
        menu.add(menuitem)
        menu.append(gtk.SeparatorMenuItem())
        return menu

    def get_meeting_url(self, event=None) -> str:
        if event is None:
            event = self.get_event()
            if not event:
                return ""

        if event.comp.get_location() and event.comp.get_location().startswith(
                "https://"
        ):
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
        menu = self.make_attachment_item(menu, first_event)

        currentday = ""
        for event in events:
            event_day = event.start_dttime.strftime("%A %d %B %Y")
            if event_day != currentday:
                menu = self.add_current_day(menu, event, currentday)
                currentday = event_day

            summary = strings.htmlspecialchars(
                event.comp.get_summary().get_value().strip()
            )
            if datetime.datetime.now() >= event.start_dttime:
                summary = f"<i>{summary}</i>"
            icon = self.make_icon(event)
            start_time_str = event.start_dttime.strftime("%H:%M")
            menuitem = gtk.MenuItem(label=f"{icon} {summary} - {start_time_str}")
            menuitem.get_child().set_use_markup(True)
            location = self.get_meeting_url(event)
            if not location:
                menuitem.event = event
                menuitem.connect("activate", self.open_description_window)
            else:
                menuitem.location = location
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
        todayitem = gtk.MenuItem(label=f'<span size="large">{event_day}</span>')
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
        glib.timeout_add_seconds(30, self.set_indicator_icon_label)
        gtk.main()


def run(args):
    Applet(args).run()

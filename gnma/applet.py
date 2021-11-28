# -*- coding: utf-8 -*-
import datetime
import logging
import pathlib

import dateutil.relativedelta as dtrelative
import gi  # type:ignore
import yaml

gi.require_version('AppIndicator3', '0.1')
gi.require_version('EDataServer', '1.2')
gi.require_version('Gtk', '3.0')
# pylint: disable=E0611 disable=C0411
from gi.repository import AppIndicator3 as appindicator  # type:ignore
from gi.repository import EDataServer
from gi.repository import Gtk as gtk

from gnma import config
from gnma import gnome_online_account_cal as goacal
from gnma import strings

APP_INDICTOR_ID = "gnome-next-meeting-applet"


class Applet(goacal.GnomeOnlineAccountCal):
    def __init__(self, args):
        self.args = args
        super().__init__()
        self.config = config.DEFAULT_CONFIG
        self.last_sorted = None
        self.indicator = None

    def set_logging(self):
        if self.args.verbose:
            logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

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
            if self.config["skip_non_confirmed"] and event.comp.get_status(
            ).value_name != "I_CAL_STATUS_CONFIRMED":
                logging.debug("[SKIP] non confirmed event")
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
        summary = (comp.get_summary().get_value().strip()
                   [:self.config["title_max_char"]])
        if self.config["strip_title_emojis"]:
            summary = strings.remove_emojis(summary)

        now = datetime.datetime.now()
        logging.debug("First event in UTC start_time: %s send_time: %s",
                      event.start_dttime, event.end_dttime)

        if event.end_dttime == now:
            return f" Meeting over 😲 - {summary}"
        if event.start_dttime < now < event.end_dttime:
            _rd = dtrelative.relativedelta(event.end_dttime, now)
        else:
            _rd = dtrelative.relativedelta(event.start_dttime, now)

        humanized_str = strings.humanize_rd(_rd, event.start_dttime,
                                            event.end_dttime)
        return f"{humanized_str} - {summary}"

    def get_icon_path(self, icon):
        if f"icon_{icon}_path" in self.config and pathlib.Path(
                self.config[f"icon_{icon}_path"]).exists():
            return self.config[f"icon_{icon}_path"]

        devpath = pathlib.Path(__file__).parent.parent / "images"
        if not devpath.exists():
            devpath = pathlib.Path(
                "/usr/share/gnome-next-meeting-applet/images")

        for ext in ["svg", "png"]:
            if (devpath / f"{icon}.{ext}").exists():
                return str(devpath / f"{icon}.{ext}")
        return "x-office-calendar-symbolic"

    def set_indicator_icon_label(self, event):
        now = datetime.datetime.now()
        # pylint: disable=C0113
        if (now >
            (event.start_dttime -
             datetime.timedelta(minutes=self.config["change_icon_minutes"]))
                and not now > event.start_dttime):
            self.indicator.set_icon_full(self.get_icon_path("before_event"),
                                         "Meeting start soon!")
        elif now >= event.start_dttime and event.end_dttime > now:
            logging.debug(
                "current in meeting, now: %s, first_start_time: %s, first_end_time: %s",
                now, event.start_dttime, event.end_dttime)
            self.indicator.set_icon_full(self.get_icon_path("in_event"),
                                         "In meeting! Focus")
        elif now >= event.end_dttime:  # need a refresh
            self.make_menu_items()
            self.set_indicator_icon_label(event)
        else:
            self.indicator.set_icon_full(self.get_icon_path("default"),
                                         "Next meeting")

        self.indicator.set_label(f"{self.first_event_label(event)}",
                                 APP_INDICTOR_ID)
        return True

    def add_last_item(self, menu):
        item_quit = gtk.MenuItem(label="Quit")
        item_quit.connect("activate", gtk.main_quit)
        menu.add(item_quit)
        menu.show_all()
        self.indicator.set_menu(menu)

    def make_menu_items(self):
        menu = gtk.Menu()

        events = self.sort_and_filter_event()
        if not events:
            self.add_last_item(menu)
            return

        self.set_indicator_icon_label(events[0])
        self.add_last_item(menu)

    def run(self):
        self.set_logging()
        self.get_or_init_config()
        self.indicator = appindicator.Indicator.new(
            APP_INDICTOR_ID,
            "calendar",
            appindicator.IndicatorCategory.SYSTEM_SERVICES,
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        EDataServer.SourceRegistry.new(None, self.goa_registry_callback)
        gtk.main()


def run(args):
    Applet(args).run()

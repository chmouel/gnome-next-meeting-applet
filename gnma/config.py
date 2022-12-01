import gi  # type: ignore

# pylint: disable=C0413, W1202
gi.require_version("GLib", "2.0")

from gi.repository import GLib as glib  # type: ignore

DEFAULT_CONFIG = {
    # TODO(chmouel): should be plural
    "restrict_to_calendar": [],
    "skip_non_confirmed": True,
    "skip_non_accepted": False,
    "skip_all_day": False,
    "starts_today_only": False,
    "my_emails": [],
    "max_results": 10,
    "title_max_char": 20,
    "event_organizers_icon": {},
    "title_match_icon": {},
    "change_icon_minutes": 5,
    "default_icon": "‣",
    "calendar_day_prefix_url": "https://calendar.google.com/calendar/r/day/",
    "verbose": False,
    # wether removing the emojis from title when showing in the menubar, so to
    # keep the menubar clean
    "strip_title_emojis": False,
}

CONFIG_FILE = f"{glib.get_user_config_dir()}/gnome-next-meeting-applet/config.yaml"

VIDEOCALL_DESC_REGEXP = [
    r"href=\"(https:..primetime.bluejeans.com.a2m.live-event.([^\/\"])*\")",
    r"(https://(\w+\.)?zoom.\w{,2}(/j)?/\d+\??[^\"\n\s]*)",
    r"(https://meet.google.com/[^\n]*)",
    r"(https://meet.lync.com/[^\n]*)",
    r"(https://meet.office.com/[^\n]*)",
    r"(https://meet.microsoft.com/[^\n]*)",
    r"(https://teams.microsoft.com/[^>\n]*)",
    r"(https://(\w+\.)?webex.*MTID=[^\s]+)",
]

AUTOSTART_DESKTOP_FILE = """#!/usr/bin/env xdg-open
[Desktop Entry]
Keywords=Event;Calendar
Categories=GNOME;Office;Calendar;GTK
Exec=gnome-next-meeting-applet
Icon=gnome-next-meeting-applet
Name=Google Calendar next meeting applet
Type=Application
X-GNOME-Autostart-enabled=true
Terminal=false
"""

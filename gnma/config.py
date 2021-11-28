DEFAULT_CONFIG = {
    # TODO(chmouel): should be plural
    "restrict_to_calendar": [],
    "skip_non_confirmed": True,
    "skip_non_accepted": False,
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

CONFIG_FILE = "~/.config/gnome-next-meeting-applet/config.yaml"

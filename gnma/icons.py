import datetime
import pathlib


def get_path(config, icon: str) -> str:
    if (
        f"icon_{icon}_path" in config
        and pathlib.Path(config[f"icon_{icon}_path"]).exists()
    ):
        return config[f"icon_{icon}_path"]

    devpath = pathlib.Path(__file__).parent.parent / "data" / "images"
    if not devpath.exists():
        for path in [
            "/usr/share/gnome-next-meeting-applet/images",
            "/app/share/icons/gnome-next-meeting-applet",
        ]:
            _dv = pathlib.Path(path)
            if _dv.exists():
                devpath = _dv
                break
    if devpath.exists():
        for ext in ["svg", "png"]:
            if (devpath / f"{icon}.{ext}").exists():
                return str(devpath / f"{icon}.{ext}")
    return "x-office-calendar-symbolic"


def by_event_time(config, event) -> list:
    now = datetime.datetime.now()
    # pylint: disable=C0113,R1705
    if (
        now
        > (
            event.start_dttime
            - datetime.timedelta(minutes=config["change_icon_minutes"])
        )
        and not now > event.start_dttime
    ):
        return [get_path(config, "before_event"), "Meeting start soon!"]
    elif now >= event.start_dttime and event.end_dttime > now:
        return [get_path(config, "in_event"), "In meeting! Focus"]
    return [get_path(config, "default"), "Next meeting"]

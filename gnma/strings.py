import datetime
import re

import humanize
import dateutil.relativedelta as dtr


def realhumanize(now: datetime.datetime, end_time: datetime.datetime) -> str:
    attrs = ["years", "months", "days", "hours", "minutes"]

    def make_human_readable(delta):
        # pylint: disable=consider-using-f-string
        return [
            "%d %s"
            % (getattr(delta, attr), attr if getattr(delta, attr) > 1 else attr[:-1])
            for attr in attrs
            if getattr(delta, attr)
        ]

    dtrelative = dtr.relativedelta(end_time, now)
    delta = " ".join(make_human_readable(dtrelative))
    return delta


# Replace html chars
def htmlspecialchars(text):
    return (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def humanize_time(start_time: datetime.datetime, end_time: datetime.datetime) -> str:
    now = datetime.datetime.now()

    if end_time == now:
        return "meeting is over"

    # if event already started
    if start_time <= now <= end_time:
        return realhumanize(now - datetime.timedelta(minutes=1), end_time) + " left"
    try:
        minimum_unit = "minutes"
        inoneday = now + datetime.timedelta(days=1)
        if start_time > inoneday:
            minimum_unit = "days"

        natural = humanize.precisedelta(
            start_time + datetime.timedelta(minutes=1),
            minimum_unit=minimum_unit,
            format="%d",
        )
    except AttributeError:
        natural = humanize.naturaldelta(start_time)

    days = False

    # if we are over a day then show date
    reldt = dtr.relativedelta(start_time, now)
    relhour = now.hour + reldt.hours
    # if we are over for tomorrow then show the time
    if relhour >= 24 or reldt.days > 0:
        days = True
        # if we are after midninght but less than a dayshow tomorrow
        if reldt.days == 0:
            natural = "Tomorrow"
        else:
            natural = start_time.strftime("%a %d %b")

    # remove plural
    if len(natural.split(" ")) == 2 and natural[0] == "1" and natural[-1] == "s":
        natural = natural[0:-1]

    if days:
        start_time_h_m = start_time.strftime("%H:%M")
        natural += f" at {start_time_h_m}"

    # strip minutes, seconds and all if we have multiple days left to the next
    # minute to short things up
    return natural


# remove_emojis from https://stackoverflow.com/a/58356570
def remove_emojis(data):
    emoj = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        re.UNICODE,
    )
    return re.sub(emoj, "", data)

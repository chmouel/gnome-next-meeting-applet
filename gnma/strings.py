import datetime
import re

import dateutil.relativedelta as dtrelative


# Replace html chars
def htmlspecialchars(text):
    return (text.replace("&", "&amp;").replace('"', "&quot;").replace(
        "<", "&lt;").replace(">", "&gt;"))


# remove_emojis from https://stackoverflow.com/a/58356570
def remove_emojis(data):
    emoj = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+",
        re.UNICODE)
    return re.sub(emoj, '', data)


def humanize_rd(
    relative: dtrelative.relativedelta,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
) -> str:
    humzrd = ""
    for dttype in (("day", relative.days), ("hour", relative.hours),
                   ("minute", relative.minutes)):
        if dttype[1] == 0:
            continue
        humzrd += f"{dttype[1]} {dttype[0]}"
        if dttype[1] > 1:
            humzrd += "s"
        humzrd += " "

    if start_time < datetime.datetime.now() < end_time:
        humzrd = humzrd.strip() + " left"
    return humzrd.strip()

import datetime
import re

import humanize


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


def humanize_time(start_time: datetime.datetime,
                  end_time: datetime.datetime) -> str:
    now = datetime.datetime.now()

    if end_time == now:
        return "meeting is over"

    # if event already started
    if start_time <= now <= end_time:
        try:
            natural = humanize.naturaldelta(
                end_time, when=(now - datetime.timedelta(minutes=1)))
        except TypeError:
            natural = humanize.naturaldelta(end_time)
        return natural + " left"
    try:
        natural = humanize.precisedelta(start_time +
                                        datetime.timedelta(minutes=1),
                                        minimum_unit="minutes",
                                        format="%d")
    except AttributeError:
        natural = humanize.naturaldelta(start_time)
    return natural

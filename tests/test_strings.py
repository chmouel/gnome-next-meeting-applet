import datetime

from gnma import strings


# test strings.humanize_time output with pytest
def test_under_a_minutes():
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(minutes=1)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == '1 minute left'


def test_humanize_an_hour_left():
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=1)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == '1 hour left'


def test_humanize_until_to_minute():
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=1)
    end_time = start_time + datetime.timedelta(minutes=1)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == '1 minute'


def test_humanize_until_to_hours_minutes():
    now = datetime.datetime.now()
    start_time = now + (datetime.timedelta(hours=1) +
                        datetime.timedelta(minutes=11))
    end_time = start_time + datetime.timedelta(minutes=5)

    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == '1 hour and 11 minutes'


def test_humanize_until_to_more_than_a_day():
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=1) + datetime.timedelta(
        minutes=2)
    end_time = start_time + datetime.timedelta(minutes=2)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == 'tomorrow at ' + start_time.strftime("%H:%M")


def test_humanize_until_to_more_than_a_day_plural():
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=2) + datetime.timedelta(
        minutes=2)
    end_time = start_time + datetime.timedelta(minutes=2)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == '2 days at ' + start_time.strftime("%H:%M")


def test_humanize_until_to_more_than_a_day_and_hours():
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=1) + datetime.timedelta(
        hours=20) + datetime.timedelta(minutes=33)
    end_time = start_time + datetime.timedelta(minutes=2)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == 'tomorrow at ' + start_time.strftime("%H:%M")


def test_humanize_until_to_more_than_two_days():
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(days=2)
    end_time = start_time + datetime.timedelta(minutes=2)
    humanized_time = strings.humanize_time(start_time, end_time)
    assert humanized_time == '2 days at ' + start_time.strftime("%H:%M")

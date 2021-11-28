import datetime

import gi  # type:ignore

gi.require_version('EDataServer', '1.2')
# pylint: disable=E0611
from gi.repository import EDataServer  # type:ignore


class Event():
    # pylint: disable=W0613
    def __init__(self, uid: str, color: str, summary: str, all_day: bool,
                 start_dttime: datetime.datetime,
                 end_dttime: datetime.datetime, mod_dttime: datetime.datetime,
                 comp: str):
        self.__dict__.update(locals())


class CalendarInfo():
    def __init__(self, source, client):
        self.source = source
        self.client = client

        self.color = source.get_extension(
            EDataServer.SOURCE_EXTENSION_CALENDAR).get_color()

        self.start = None
        self.end = None

        self.view = None
        self.view_cancellable = None

    def destroy(self):
        if self.view_cancellable is not None:
            self.view_cancellable.cancel()

            if self.view is not None:
                self.view.stop()
        self.view = None

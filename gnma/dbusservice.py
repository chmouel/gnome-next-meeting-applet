import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

PACKAGE_NAME = "gnma"
DBUS_BUS_NAME = "com.chmouel.gnomeNextMeetingApplet"
DBUS_OBJ_PATH = f'/{DBUS_BUS_NAME.replace(".", "/")}'

DBusGMainLoop(set_as_default=True)


class DBusService(dbus.service.Object):
    """DBUS server with signals and methods"""

    # pylint: disable=C0103, W0212
    def __init__(self, service):
        self.service = service
        bus_name = dbus.service.BusName(DBUS_BUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_OBJ_PATH)

    @dbus.service.method(dbus_interface=DBUS_BUS_NAME, out_signature="as")
    def GetNextEvent(self):
        event = self.service.get_event()
        if not event:
            return []
        return self.service.first_event_label(event)

    @dbus.service.method(dbus_interface=DBUS_BUS_NAME, out_signature="s")
    def GetNextEventURL(self):
        eventurl = self.service.get_meeting_url()
        if not eventurl:
            return ""
        return eventurl

    @dbus.service.method(dbus_interface=DBUS_BUS_NAME, out_signature="s")
    def GetEventDocument(self) -> str:
        self.service.sort_and_filter_event()
        if not self.service.all_events or not self.service.last_sorted:
            return ""
        event = self.service.all_events[self.service.last_sorted[0]]
        if not event.comp.get_attachments():
            return ""

        return event.comp.get_attachments()[0].get_url()

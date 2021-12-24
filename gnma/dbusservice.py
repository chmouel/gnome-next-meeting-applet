import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

PACKAGE_NAME = "gnma"
DBUS_BUS_NAME = f'{PACKAGE_NAME}.{PACKAGE_NAME.capitalize()}Service'
DBUS_OBJ_PATH = f'/{DBUS_BUS_NAME.replace(".", "/")}'

DBusGMainLoop(set_as_default=True)


class DBusService(dbus.service.Object):
    """  DBUS server with signals and methods """

    # pylint: disable=C0103, W0212, R0201
    def __init__(self, service):
        self.service = service
        bus_name = dbus.service.BusName(DBUS_BUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_OBJ_PATH)

    @dbus.service.method(dbus_interface=DBUS_BUS_NAME, out_signature='as')
    def GetNextMeeting(self):
        geticon = self.service.get_icon_label(None)
        if not geticon:
            return []
        # Todo: is icon useful? 🤔
        _, _, humanized_str, title = geticon
        return [humanized_str, title]

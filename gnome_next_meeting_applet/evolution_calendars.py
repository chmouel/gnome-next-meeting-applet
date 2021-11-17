# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
#
# from Gabriel Le Breton (@GabLeRoux) https://askubuntu.com/a/1371087
import pytz
import datetime

import gi

import dateutil.parser as dtparse

gi.require_version("EDataServer", "1.2")
from gi.repository import EDataServer

gi.require_version("ECal", "2.0")
from gi.repository import ECal

from gi.repository import Gio

# https://lazka.github.io/pgi-docs/Gio-2.0/classes/Cancellable.html#Gio.Cancellable
GIO_CANCELLABLE = Gio.Cancellable.new()


def get_ecal_as_utc(ecalcomp) -> datetime.datetime:
    if not ecalcomp:
        return datetime.datetime.now().astimezone(pytz.timezone("UTC"))
    tz = pytz.timezone(ecalcomp.get_tzid() or "UTC")
    ts = ecalcomp.get_value().as_timet()
    dt = tz.normalize(tz.localize(datetime.datetime.utcfromtimestamp(ts)))
    return dt.astimezone(pytz.timezone("UTC"))


class EvolutionCalendarWrapper:
    @staticmethod
    def _get_gnome_calendars():
        # https://lazka.github.io/pgi-docs/EDataServer-1.2/classes/SourceRegistry.html#EDataServer.SourceRegistry.new_sync
        registry = EDataServer.SourceRegistry.new_sync(GIO_CANCELLABLE)
        return EDataServer.SourceRegistry.list_sources(
            registry, EDataServer.SOURCE_EXTENSION_CALENDAR
        )

    def _get_gnome_events_from_calendar_source(self, source: EDataServer.Source):
        # https://lazka.github.io/pgi-docs/ECal-2.0/classes/Client.html#ECal.Client
        client = ECal.Client()

        # https://lazka.github.io/pgi-docs/ECal-2.0/classes/Client.html#ECal.Client.connect_sync
        new_client = client.connect_sync(
            source=source,
            source_type=ECal.ClientSourceType.EVENTS,
            wait_for_connected_seconds=1,  # this should probably be configured
            cancellable=GIO_CANCELLABLE,
        )
        events = []
        seen = []
        if not new_client:
            return events
        # https://lazka.github.io/pgi-docs/ECal-2.0/classes/Client.html#ECal.Client.get_object_list_as_comps_sync
        ret, values = new_client.get_object_list_as_comps_sync(
            sexp="#t", cancellable=GIO_CANCELLABLE
        )
        if not ret:
            return events

        for value in values:
            if not value:
                continue
            start_time = get_ecal_as_utc(value.get_dtstart())
            end_time = get_ecal_as_utc(value.get_dtend())
            now = datetime.datetime.now().astimezone(pytz.timezone("UTC"))

            if now >= end_time:
                continue

            ## save memory for stuff we won't care
            if start_time > (now + datetime.timedelta(weeks=4)):
                continue

            uuid = value.get_id().get_uid()
            # sometime we get doublons whatever the reasons is
            if uuid in seen:
                continue
            seen.append(uuid)
            events.append(value)
        return events

    # TODO: calendar filtering
    def get_all_events(self, restrict_to_calendar=[]):
        calendars = self._get_gnome_calendars()
        events = []
        for source in calendars:
            if restrict_to_calendar and source.get_display_name() not in restrict_to_calendar:
                continue
            events += self._get_gnome_events_from_calendar_source(source)
        return events

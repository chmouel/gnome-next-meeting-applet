import datetime
import logging

import gi  # type:ignore

from gnma import types

gi.require_version("ECal", "2.0")
gi.require_version("EDataServer", "1.2")
gi.require_version("Gio", "2.0")
gi.require_version("ICal", "3.0")
gi.require_version('GLib', '2.0')
# pylint: disable=C0411,E0611
from gi.repository import (
    ECal,
    EDataServer,
    Gio,
    GLib,
    ICal,  # type:ignore
    ICalGLib)


class GnomeOnlineAccountError(Exception):
    pass


class GnomeOnlineAccountCal:
    def __init__(self):
        self.registry = []
        self.client_appeared_id = 0
        self.client_disappeared_id = 0
        self.registry_watcher = None
        self.calendars = {}
        self.interface = None
        self.update_timezone()
        self.indicator = None
        self.all_events = {}

    def update_timezone(self):
        location = ECal.system_timezone_get_location()

        if location is None:
            self.zone = ICalGLib.Timezone.get_utc_timezone().copy()
        else:
            self.zone = ICalGLib.Timezone.get_builtin_timezone(location).copy()

    # pylint: disable=unused-argument
    def goa_registry_callback(self, source, res):
        try:
            self.registry = EDataServer.SourceRegistry.new_finish(res)
        except GLib.Error as gliberror:
            raise GnomeOnlineAccountError from gliberror

        self.registry_watcher = EDataServer.SourceRegistryWatcher.new(
            self.registry, None)

        self.client_appeared_id = self.registry_watcher.connect(
            "appeared", self.source_appeared)
        self.client_disappeared_id = self.registry_watcher.connect(
            "disappeared", self.source_disappeared)
        self.registry_watcher.connect("filter", self.is_relevant_source)

        # This forces the watcher to notify about all pre-existing sources (so
        # the callbacks can process them)
        self.registry_watcher.reclaim()

    # pylint: disable=no-self-use
    def is_relevant_source(self, watcher, source):
        relevant = (source.has_extension(EDataServer.SOURCE_EXTENSION_CALENDAR)
                    and source.get_extension(
                        EDataServer.SOURCE_EXTENSION_CALENDAR).get_selected())
        return relevant

    def ecal_client_connected(self, _, res, source):
        try:
            client = ECal.Client.connect_finish(res)
            client.set_default_timezone(self.zone)

            calendar = types.CalendarInfo(source, client)
            self.calendars[source.get_uid()] = calendar

            # self.interface.set_property("has-calendars", True)

            self.create_view_for_calendar(calendar)
        except GLib.Error as gliberror:
            # what to do
            raise GnomeOnlineAccountError from gliberror

    def create_view_for_calendar(self, calendar):
        if calendar.view_cancellable is not None:
            calendar.view_cancellable.cancel()
        calendar.view_cancellable = Gio.Cancellable()

        if calendar.view is not None:
            calendar.view.stop()
        calendar.view = None

        current_month_start = datetime.datetime.now()
        current_month_end = datetime.datetime.now() + datetime.timedelta(
            weeks=4)
        calendar.start = datetime.datetime.timestamp(current_month_start)
        calendar.end = datetime.datetime.timestamp(current_month_end)
        from_iso = ECal.isodate_from_time_t(calendar.start)
        to_iso = ECal.isodate_from_time_t(calendar.end)
        location = self.zone.get_location()
        # pylint: disable=line-too-long
        query = f'occur-in-time-range? (make-time "{from_iso}") (make-time "{to_iso}") "{location}"'
        calendar.client.get_view(query, calendar.view_cancellable,
                                 self.got_calendar_view, calendar)

    def got_calendar_view(self, client, res, calendar):
        if calendar.view_cancellable.is_cancelled():
            return

        try:
            _, view = client.get_view_finish(res)
            calendar.view = view
        except GLib.Error as gliberror:
            print("get view failed: ", gliberror)
            raise GnomeOnlineAccountError from gliberror

        view.set_flags(ECal.ClientViewFlags.NOTIFY_INITIAL)
        view.connect("objects-added", self.view_objects_added, calendar)
        view.connect("objects-modified", self.view_objects_modified, calendar)
        view.connect("objects-removed", self.view_objects_removed, calendar)
        view.start()

    def view_objects_added(self, view, objects, calendar):
        self.handle_new_or_modified_objects(view,
                                            objects,
                                            calendar,
                                            mod="added")

    def view_objects_modified(self, view, objects, calendar):
        self.handle_new_or_modified_objects(view,
                                            objects,
                                            calendar,
                                            mod="modified")

    def view_objects_removed(self, view, component_ids, calendar):
        self.handle_removed_objects(view, component_ids, calendar)

    def get_id_from_comp_id(self, comp_id, source_id):
        if comp_id.get_rid() is not None:
            return f"{source_id}:{comp_id.get_uid()}:{comp_id.get_rid()}"
        return f"{source_id}:{comp_id.get_uid()}"

    def handle_removed_objects(self, view, component_ids, calendar):
        source_id = calendar.source.get_uid()

        for comp_id in component_ids:
            uid = self.get_id_from_comp_id(comp_id, source_id)
            del self.all_events[uid]
            # pylint: disable=no-member
            self.make_menu_items()

    def recurrence_generated(self, ical_comp, instance_start, instance_end,
                             calendar, cancellable):
        if calendar.view_cancellable.is_cancelled():
            return False

        comp = ECal.Component.new_from_icalcomponent(ical_comp)
        comptext = comp.get_summary()
        if comptext is not None:
            summary = comptext.get_value()
        else:
            summary = ""

        default_zone = calendar.client.get_default_timezone()

        dts_timezone = instance_start.get_timezone()
        if dts_timezone is None:
            dts_timezone = default_zone

        dte_timezone = instance_end.get_timezone()
        if dte_timezone is None:
            dte_timezone = default_zone

        all_day = instance_start.is_date()
        start_timet = instance_start.as_timet_with_zone(dts_timezone)
        start_dttime = datetime.datetime.fromtimestamp(start_timet)
        end_timet = instance_end.as_timet_with_zone(dte_timezone)
        end_dttime = datetime.datetime.fromtimestamp(end_timet)
        mod_prop = ical_comp.get_first_property(
            ICalGLib.PropertyKind.LASTMODIFIED_PROPERTY)
        ical_time_modified = mod_prop.get_lastmodified()
        # Modified time "last-modified" is utc
        mod_timet = ical_time_modified.as_timet()
        mod_dttime = datetime.datetime.fromtimestamp(mod_timet)

        uid = self.create_uid(calendar, comp)
        if not uid in self.all_events:
            self.all_events[uid] = types.Event(
                uid,
                calendar.color,
                summary,
                all_day,
                start_dttime,
                end_dttime,
                mod_dttime,
                comp,
            )
        # pylint: disable=no-member
        self.make_menu_items()
        return True

    def handle_new_or_modified_objects(self, view, objects, calendar, mod):
        if calendar.view_cancellable.is_cancelled():
            return

        for ical_comp in objects:
            if ical_comp.get_uid() is None:
                continue

            if (not ECal.util_component_is_instance(ical_comp)
                ) and ECal.util_component_has_recurrences(ical_comp):
                calendar.client.generate_instances_for_object(
                    ical_comp,
                    calendar.start,
                    calendar.end,
                    calendar.view_cancellable,
                    self.recurrence_generated,
                    calendar,
                )
            else:
                comp = ECal.Component.new_from_icalcomponent(ical_comp)
                comptext = comp.get_summary()
                uid = self.create_uid(calendar, comp)

                if mod == "added" and uid in self.all_events:
                    continue

                if comptext is not None:
                    summary = comptext.get_value()
                else:
                    summary = ""

                dts_prop = ical_comp.get_first_property(
                    ICalGLib.PropertyKind.DTSTART_PROPERTY)
                ical_time_start = dts_prop.get_dtstart()
                start_timet = self.ical_time_get_timet(calendar.client,
                                                       ical_time_start,
                                                       dts_prop)
                all_day = ical_time_start.is_date()

                dte_prop = ical_comp.get_first_property(
                    ICalGLib.PropertyKind.DTEND_PROPERTY)

                if dte_prop is not None:
                    ical_time_end = dte_prop.get_dtend()
                    end_timet = self.ical_time_get_timet(
                        calendar.client, ical_time_end, dte_prop)
                else:
                    end_timet = start_timet + (
                        60 * 30)  # Default to 30m if the end time is bad.

                mod_prop = ical_comp.get_first_property(
                    ICalGLib.PropertyKind.LASTMODIFIED_PROPERTY)
                ical_time_modified = mod_prop.get_lastmodified()
                # Modified time "last-modified" is utc
                mod_timet = ical_time_modified.as_timet()

                start_dttime = datetime.datetime.fromtimestamp(start_timet)
                end_dttime = datetime.datetime.fromtimestamp(end_timet)
                mod_dttime = datetime.datetime.fromtimestamp(mod_timet)

                self.all_events[uid] = types.Event(
                    uid,
                    calendar.color,
                    summary,
                    all_day,
                    start_dttime,
                    end_dttime,
                    mod_dttime,
                    comp,
                )
                # pylint: disable=no-member
                self.make_menu_items()

    def create_uid(self, calendar, ecal_comp):
        source_id = calendar.source.get_uid()
        comp_id = ecal_comp.get_id()
        return self.get_id_from_comp_id(comp_id, source_id)

    def source_appeared(self, watcher, source):
        ECal.Client.connect(
            source,
            ECal.ClientSourceType.EVENTS,
            10,
            None,
            self.ecal_client_connected,
            source,
        )

    def source_disappeared(self, watcher, source):
        try:
            calendar = self.calendars[source.get_uid()]
        except KeyError:
            # We had a source but it wasn't for a calendar.
            return

        self.interface.emit_client_disappeared(source.get_uid())
        calendar.destroy()

        if source.get_uid() in self.calendars:
            logging.debug("deleting event: %s", source.get_uid())
            del self.calendars[source.get_uid()]
        if len(self.calendars) > 0:
            return

        # self.interface.set_property("has-calendars", False)

    def ical_time_get_timet(self, client, ical_time, prop):
        tzid = prop.get_first_parameter(ICalGLib.ParameterKind.TZID_PARAMETER)
        if tzid:
            timezone = ECal.TimezoneCache.get_timezone(client, tzid.get_tzid())
        elif ical_time.is_utc():
            timezone = ICal.Timezone.get_utc_timezone()
        else:
            timezone = client.get_default_timezone()

        ical_time.set_timezone(timezone)
        return ical_time.as_timet_with_zone(timezone)

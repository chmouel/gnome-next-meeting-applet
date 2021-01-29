# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# pylint: disable=no-self-use
"""Gnome next meeting calendar applet via Google Calendar"""
import datetime
import json
import os.path
import pathlib
import re
import sys

import apiclient
import dateutil.parser as dtparse
import dateutil.relativedelta as dtrelative
import dateutil.tz as dttz
import httplib2
import oauth2client.file
import tzlocal
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gdk as gdk
from gi.repository import GLib as glib
from gi.repository import Gtk as gtk

APP_INDICTOR_ID = "gnome-next-meeting-applet"
RESTRICT_TO_CALENDAR = ["Work"]
PASS_CREDENTIALS_ID = "google-calendar-api-token"
SKIP_NON_ACCEEPTED = True
MY_EMAIL = "cboudjna@redhat.com"
MAX_RESULTS = 10
TITLE_MAX_CHAR = 20
EVENT_ORGANIZERS_ICON = {
    "^Tekton$":
    "🐱",
    r"(pbhattac|nkakkar|rbehera|vdemeest|kbaig|pchandra|ssadeghi|hshinde|nikthoma|pthangad|yhontyk|varadhya|pgarg|pradkuma|sashture|sthaha|gmontero|ppitonak)@redhat.com":
    "👷"
}
REFRESH_INTERVAL = 300  # seconds
CREDENTIALS_PATH = os.path.expanduser(
    f"~/.config/{APP_INDICTOR_ID}/calendar-python-quickstart.json")


class Applet:
    """Applet: class"""
    events = []
    indicator = None
    api_service = None

    def htmlspecialchars(self, text):
        """Replace html chars"""
        return (text.replace("&", "&amp;").replace('"', "&quot;").replace(
            "<", "&lt;").replace(">", "&gt;"))

    def first_event(self, event):
        """Show first even in toolbar"""
        summary = self.htmlspecialchars(
            event['summary'].strip()[:TITLE_MAX_CHAR])
        now = datetime.datetime.now(dttz.tzlocal()).astimezone(
            tzlocal.get_localzone())
        end_time = dtparse.parse(event['end']['dateTime']).astimezone(
            tzlocal.get_localzone())
        start_time = dtparse.parse(event['start']['dateTime']).astimezone(
            tzlocal.get_localzone())

        if now > start_time:
            _rd = dtrelative.relativedelta(end_time, now)
        else:
            _rd = dtrelative.relativedelta(start_time, now)
        humzrd = ""
        for dttype in (("day", _rd.days), ("hour", _rd.hours), ("minute",
                                                                _rd.minutes)):
            if dttype[1] == 0:
                continue
            humzrd += f"{dttype[1]} {dttype[0]}"
            if dttype[1] > 1:
                humzrd += "s"
            humzrd += " "
        if now > start_time:
            humzrd = humzrd.strip() + " left"
        return f"{humzrd.strip()} - {summary}"

    def _get_credentials(self):
        """Gets valid user credentials from storage.
        """
        credential_path = pathlib.Path(CREDENTIALS_PATH)
        if not credential_path.exists():
            # TODO: Graphical
            print("Credential has not been configured you need to launch "
                  " gnome-next-meeting-applet-auth")
            sys.exit(1)

        store = oauth2client.file.Storage(CREDENTIALS_PATH)
        return store.get()

    def get_from_gcal_calendar_entries(self):
        page_token = None
        calendar_ids = []
        event_list = []
        while True:
            # pylint: disable=no-member
            calendar_list = self.api_service.calendarList().list(
                pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if RESTRICT_TO_CALENDAR and calendar_list_entry[
                        'summary'] not in RESTRICT_TO_CALENDAR:
                    continue
                calendar_ids.append(calendar_list_entry['id'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        # pylint: disable=no-member
        for calendar_id in calendar_ids:
            uhy = self.api_service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=MAX_RESULTS,
                singleEvents=True,
                orderBy='startTime').execute()
            uhx = uhy.get('items', [])
            event_list = event_list + uhx
        return event_list

    def get_all_events(self):
        """Get all events from Google Calendar API"""
        event_list = json.load(open("/tmp/allevents.json"))
        # event_list = self.get_from_gcal_calendar_entries()

        ret = []
        for event in sorted(event_list,
                            key=lambda x: x['start'].get(
                                'dateTime', x['start'].get('date'))):
            if 'date' in event['start']:
                continue
            end_time = dtparse.parse(event['end']['dateTime']).astimezone(
                tzlocal.get_localzone())
            now = datetime.datetime.now(dttz.tzlocal()).astimezone(
                tzlocal.get_localzone())

            if now >= end_time:
                continue

            if 'attendees' not in event:
                continue

            # Get only accepted events
            skip_event = False
            if SKIP_NON_ACCEEPTED:
                skip_event = True
            for attendee in event['attendees']:
                if attendee['email'] == MY_EMAIL and attendee[
                        'responseStatus'] == "accepted":
                    skip_event = False
            if skip_event:
                continue
            ret.append(event)
        return ret

    # pylint: disable=unused-argument
    def set_indicator_icon_label(self, source):
        source.set_label(f"{self.first_event(self.events[0])}",
                         APP_INDICTOR_ID)
        return True

    # pylint: disable=unused-argument
    def applet_quit(self, source):
        gtk.main_quit()

    def applet_click(self, source):
        gtk.show_uri(None, source.location, gdk.CURRENT_TIME)

    def make_menu_items(self, source=None):
        self.events = self.get_all_events()

        menu = gtk.Menu()
        now = datetime.datetime.now(dttz.tzlocal()).astimezone(
            tzlocal.get_localzone())

        currentday = ""

        event_first = self.events[0]
        if now >= dtparse.parse(event_first['start']['dateTime']).astimezone(
                tzlocal.get_localzone()) and 'attachments' in event_first:
            menuitem = gtk.MenuItem(label="📑 Open current meeting document")
            menuitem.location = event_first['attachments'][0]['fileUrl']
            menuitem.connect('activate', self.applet_click)
            menu.add(menuitem)
            menu.append(gtk.SeparatorMenuItem())
            menu.append(gtk.MenuItem(" "))

        for event in self.events:
            # TODO print the day
            start_time = dtparse.parse(event['start']['dateTime']).astimezone(
                tzlocal.get_localzone())
            _cday = start_time.strftime('%A %d %B %Y')
            if _cday != currentday:
                if currentday != "":
                    menu.append(gtk.MenuItem(label=""))
                menu.append(gtk.MenuItem(label=_cday))
                menu.append(gtk.SeparatorMenuItem())
                currentday = _cday

            summary = self.htmlspecialchars(event['summary'].strip())

            organizer = event['organizer'].get('displayName',
                                               event['organizer'].get('email'))

            icon = "💆"
            for regexp in EVENT_ORGANIZERS_ICON:
                if re.match(regexp, organizer):
                    icon = EVENT_ORGANIZERS_ICON[regexp]
                    break

            start_time_str = start_time.strftime("%H:%M")
            if True or now >= start_time:
                summary = f"<span color='blue'>{summary}</span>"

            menuitem = gtk.MenuItem(
                label=f"{icon} {summary} - {start_time_str}")
            menuitem.get_child().set_use_markup(True)

            if 'location' in event and event['location'].startswith(
                    "https://"):
                menuitem.location = event['location']
            elif 'hangoutLink' in event:
                menuitem.location = event['hangoutLink']
            else:
                menuitem.location = ""

            menuitem.connect('activate', self.applet_click)
            menu.append(menuitem)

        menu.append(gtk.SeparatorMenuItem())

        item_refreh = gtk.MenuItem(label="Refresh")
        item_refreh.connect('activate', self.make_menu_items)
        menu.add(item_refreh)
        item_quit = gtk.MenuItem(label="Quit")
        item_quit.connect('activate', self.applet_quit)
        menu.add(item_quit)

        menu.show_all()

        self.indicator.set_menu(menu)

    def build_indicator(self):
        self.indicator = appindicator.Indicator.new(
            APP_INDICTOR_ID, "calendar",
            appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.make_menu_items()
        self.set_indicator_icon_label(self.indicator)
        glib.timeout_add_seconds(1, self.set_indicator_icon_label,
                                 self.indicator)
        glib.timeout_add_seconds(REFRESH_INTERVAL, self.make_menu_items)
        gtk.main()

    def main(self):
        credentials = self._get_credentials()
        http_authorization = credentials.authorize(httplib2.Http())
        self.api_service = apiclient.discovery.build('calendar',
                                                     'v3',
                                                     http=http_authorization)

        self.build_indicator()


def run():
    c = Applet()
    c.main()


if __name__ == '__main__':
    run()

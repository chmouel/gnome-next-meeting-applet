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
import argparse
import pathlib
import sys

import oauth2client.client
import oauth2client.file
import oauth2client.tools
import yaml

import gnome_next_meeting_applet.applet as gnma

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


def main():
    description = """This helper tool will authorize gnome-next-meeting-applet to use your
        calendar, you will need first generate a client secret from your Google API
        console, see README on GitHub
        https://git.io/Jt8qq for more details."""
    parser = argparse.ArgumentParser(description=description,
                                     parents=[oauth2client.tools.argparser])
    parser.add_argument(
        "client_secret_file",
        help="Client secret file as downloaded from Google API console.")
    args = parser.parse_args()

    fpath = pathlib.Path(args.client_secret_file)
    if not fpath.exists():
        print(f"I could not find the file: {fpath}")
        return 1

    dpath = pathlib.Path(gnma.CREDENTIALS_PATH)
    if not dpath.parent.exists():
        dpath.parent.mkdir(parents=True)

    store = oauth2client.file.Storage(gnma.CREDENTIALS_PATH)
    flow = oauth2client.client.flow_from_clientsecrets(args.client_secret_file,
                                                       SCOPES)
    flow.user_agent = "Gnome Next Meeting applet"
    # oauth2client.tools.run_flow(flow, store, args)

    configfile = pathlib.Path(gnma.CONFIG_DIR) / "config.yaml"
    if not configfile.exists():
        configfile.write_text(yaml.safe_dump(gnma.DEFAULT_CONFIG))

    print(f'Credentials has been stored in {dpath}')
    print('You can now launch gnome-next-meeting-applet')


if __name__ == '__main__':
    sys.exit(main())

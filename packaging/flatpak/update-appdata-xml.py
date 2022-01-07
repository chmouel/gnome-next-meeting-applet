#!/usr/bin/env python
import json
import shutil
import subprocess
import tempfile

import dateutil.parser as dtparse

xmlfile = "data/desktop/com.chmouel.gnomeNextMeetingApplet.appdata.xml"


def run(cmd):
    r = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return r.communicate()[0].decode().strip()


version = run(["poetry", "version"]).split(" ")[1]
_ghrelease = run([
    "gh", "release", "view", version, "--json", "body", "--json", "createdAt"
])
ghrelease = json.loads(_ghrelease)

date = dtparse.parse(ghrelease['createdAt']).strftime("%Y-%m-%d")

_appdata = run(["xq", ".", xmlfile])
appdata = json.loads(_appdata)

appdata['component']['releases']['release'].insert(0, {
    "@version": version,
    "@date": date,
    "#text": ghrelease['body'],
})
r = subprocess.Popen(
    ["yq", "-x"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)

print(r.communicate(input=json.dumps(appdata).encode())[0].decode().strip())

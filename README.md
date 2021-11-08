***This is currently beta software, would be great if you can help test this.***

# Gnome Next Meeting applet

An applet to show your next meetings in Gnome

* Free software: GNU General Public License v3

## Screenshot

![Screenshot](./.github/screenshot/screenshot.png)

## Installation

### Ubuntu
```
sudo add-apt-repository ppa:chmouel/gnome-next-meeting-applet
sudo apt-get -y install gnome-next-meeting-applet
```

### Fedora
You would need to install [`Top Indicator App`](https://extensions.gnome.org/extension/3681/top-indicator-app/) extension to be able to show it.

```

sudo dnf install python3-tzlocal python3-dateutil python3-google-auth python3-google-api-client python3-google-auth-httplib2 python3-httplib2 python3-oauth2client libappindicator-gtk3 python3-gobject python3-yaml
pip3 install --user git+https://github.com/chmouel/gnome-next-meeting-applet
gnome-next-meeting-applet-auth
```


## Features

* Make it easy to know how long you have until your next meeting.
* Detect video conference URL in location or google meet.
* Shows the documents link to the current meeting.
* Fully configurable.

## Configuration

### Applet configuration

The applet can be configured with a config.yaml yaml located in your
`$HOME/.config/gnome-next-meeting-applet/config.yaml`. This gets generated
automatically when launching `gnome-next-meeting-applet-auth`.

A configured example is located in the [config.sample.yaml](./config.samples.yaml).

* **default_icon**: The default icon when showing each meeting.
* **event_organizers_icon**: A map between a regexp matching the organizer to an
  icon. This allows you to easily differentiate certain type of meetings like
  the one from your team or colleagues.
* **max_results**: Max results to ask to google calendar api.
* **skip_non_accepted**: Skip the calendar events that you didn't accept, you
  need to configure `my_email` setting for that.
* **my_email**: Your email address
* **restrict_to_calendar**: Restrict to some calendar, by default it shows event from all calendars.
* **title_max_char**: The maximum length of the title
* **change_icon_minutes**: Before the meeting x minutes before the event we will
  change the icon to gently remind you to connect.


### Calendars

All calendars are configured directly in Gnome Online Account setting, it will grab it from there.

### Starting

You can just do :

Alt+F2 and start `gnome-next-meeting-applet` make sure you have done the oauth
dance previously.

There is a setting menu to add an autostart file to autostart it when gnome
launch.

### Credits

* This package was created with [`Cookiecutter`](https://github.com/audreyr/cookiecutter-pypackage) and the
[`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage) project template.
* Originally inspired from the [gnome next
  meeting](https://github.com/tjwells47/gnome-next-meeting) argos based
  extension.
* Used for a while the OSX application gnome-next-meeting
  https://apps.apple.com/us/app/next-meeting/id1017470484?mt=12 and missed it on
  Linux.
* Used code from from @GabLeRoux for evolution calendar integration - https://askubuntu.com/a/1371087

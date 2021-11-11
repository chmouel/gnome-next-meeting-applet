# Gnome Next Meeting applet

An applet to show your next meetings in Gnome

* Free software: GNU General Public License v3

### Features 

* Make it easy to know how long you have until your next meeting.
* Detect video conference URLs allow to quickly click on it to join (Google Meet, Zoom, Bluejeans, supported).
* Shows the documents link attached to the current meeting.
* Fully configurable.

### Screenshot

![Screenshot](./.github/screenshot/screenshot.png)

## Installation

### Ubuntu

```bash
sudo add-apt-repository ppa:chmouel/gnome-next-meeting-applet
sudo apt-get -y install gnome-next-meeting-applet
```

### Fedora

You first need to install this gnome extension to get [appindicator-support](https://extensions.gnome.org/extension/615/appindicator-support/), when this is installed you can simply do :

```bash
dnf copr enable chmouel/gnome-next-meeting-applet
dnf install gnome-next-meeting-applet
```

### Arch

Just install the package from AUR with your favourite aur installer (ie:
[yay](https://github.com/Jguer/yay))

https://aur.archlinux.org/packages/gnome-next-meeting-applet/

It depends on the
[`gnome-shell-extension-appindicator`](https://archlinux.org/packages/community/any/gnome-shell-extension-appindicator/)
extension package so you won't have to do manual instal there.

## Configuration

### Applet configuration

The applet can be configured with a config.yaml yaml located in your
`$XDG_CONFIG_HOME/gnome-next-meeting-applet/config.yaml`. It gets created
automatically with default value at startup if you don't have one already.

A configured example is located in the [config.sample.yaml](./config.samples.yaml).

* **default_icon**: The default icon when showing each meeting.
* **event_organizers_icon**: A map between a regexp matching the organizer to an
  icon. This allows you to easily differentiate certain type of meetings like
  the one from your team or colleagues.
* **max_results**: Max results to ask to google calendar api.
* **skip_non_accepted**: Skip the calendar events that you didn't accept, you
  need to configure `my_emails` setting for that.
* **my_emails**: A list of email addresses.
* **restrict_to_calendar**: Restrict to some calendar, by default it shows event from all calendars.
* **title_max_char**: The maximum length of the title
* **change_icon_minutes**: Before the meeting x minutes before the event we will
  change the icon to gently remind you to connect.
* **calendar_day_prefix_url**: The prefix URL for the day in the web calendar when clicking, by default this goes to google calendar URL.

### Calendars

All calendars are configured directly in Gnome Online Account setting, it will
grab the events from there. Here is some instructions on how to setup your
online calendars in Gnome :

<https://help.gnome.org/users/gnome-help/stable/accounts.html.en>

By default it will get all events from all calendars you are subscribed to, unless you are configuring 
the restrict_to_calendar variable.

### Starting it

There is a setting menu in the applet to add an autostart file to autostart it
when gnome launch or you can launch it manually from the Gnome overview
application launcher thingy.

### Credits

* This package was created with [`Cookiecutter`](https://github.com/audreyr/cookiecutter-pypackage) and the
[`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage) project template.
* Originally inspired from the [gnome next
  meeting](https://github.com/tjwells47/gnome-next-meeting) argos based
  extension.
* Used for a while the OSX application gnome-next-meeting
  <https://apps.apple.com/us/app/next-meeting/id1017470484?mt=12> and missed it on
  Linux.
* Used code from from @GabLeRoux for evolution calendar integration - <https://askubuntu.com/a/1371087>

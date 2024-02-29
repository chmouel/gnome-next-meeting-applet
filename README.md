
> [!CAUTION]
> Due of a lack of time and not using gnome any more, i am not able to support this project anymore.>
> Feel free to contact me on [Fosstodon](https://fosstodon.org/@chmouel) if you would like to take over this project

# Gnome Next Meeting applet

<img src="./data/desktop/icon.svg" width=64 height=64 align=center> An applet to show your next meetings with Gnome Online Accounts

<br>

### Features

* Use [Gnome Online Account](https://linuxkamarada.com/en/2019/04/10/get-the-most-out-of-gnome-syncing-your-google-account/) for calendar sources.
* Make it easy to know how long you have until your next meeting.
* Detect video conference URLs allow to quickly click on it to join (Google Meet, Zoom, Bluejeans, supported).
* Shows the documents link attached to the current meeting.
* Change icons 5mn before and after meeting.
* Fully configurable.

### Screenshot

![Screenshot](./.github/screenshot/screenshot.png)

## Installation

## Flatpak (preferred method)

<a href='https://flathub.org/apps/details/com.chmouel.gnomeNextMeetingApplet'><img height='40' alt='Download on Flathub' src='https://flathub.org/assets/badges/flathub-badge-en.png'/></a>

### [Ubuntu](https://launchpad.net/~chmouel/+archive/ubuntu/gnome-next-meeting-applet)
**DEPRECATED: Use the flatpak instead**

```bash
sudo add-apt-repository ppa:chmouel/gnome-next-meeting-applet
sudo apt-get -y install gnome-next-meeting-applet
```

### [Fedora](https://copr.fedorainfracloud.org/coprs/chmouel/gnome-next-meeting-applet)

You first need to install the appindicator-support with dnf:

```shell
dnf install gnome-shell-extension-appindicator
```

or from [extensions.gnome.org](https://extensions.gnome.org/extension/615/appindicator-support/).

when this is installed you can simply add the copr repository :

```bash
dnf copr enable chmouel/gnome-next-meeting-applet
dnf install gnome-next-meeting-applet
```

### [Arch](https://aur.archlinux.org/packages/gnome-next-meeting-applet/)

Just install the package [gnome-next-meeting-applet](https://aur.archlinux.org/packages/gnome-next-meeting-applet/) from AUR with your favourite aur installer (ie:
[yay](https://github.com/Jguer/yay))

It depends on the
[`gnome-shell-extension-appindicator`](https://archlinux.org/packages/community/any/gnome-shell-extension-appindicator/)
extension package so you won't have to do a manual instal here. Just make sure to logout/relogin to your gnome desktop and enable the appindicator gnome-extension via the ["gnome-extensions-app"](https://ubuntuhandbook.org/index.php/2021/05/gnome-tweaks-40-no-longer-manage-extensions/)

## Configuration

### Calendar sources

All calendars are configured directly in Gnome Online Account setting, it will
grab the events from there. Here is some instructions on how to setup your
online calendars in Gnome :

<https://help.gnome.org/users/gnome-help/stable/accounts.html.en>

By default it will get all events from all calendars you are subscribed to, unless you are configuring
the `restrict_to_calendar` variable in the `config.yaml` file. (see below).

### Applet configuration

The applet can be configured with a config.yaml yaml located in your
`$XDG_CONFIG_HOME/gnome-next-meeting-applet/config.yaml`. It gets created
automatically with default value at startup if you don't have one already.

A sample file is located here: [config.sample.yaml](./config.sample.yaml).

If using flatpak, you can do this to determine where your `$XDG_CONFIG_HOME`:

```bash
$ flatpak run --command=bash com.chmouel.gnomeNextMeetingApplet
[📦 com.chmouel.gnomeNextMeetingApplet ~]$ echo $XDG_CONFIG_HOME
/home/myuser/.var/app/com.chmouel.gnomeNextMeetingApplet/config
```

Settings:

* **default_icon**: The default icon when showing each meeting (default: ‣)
* **event_organizers_icon**: A map between a regexp matching the organizer to an
  icon. This allows you to easily differentiate certain type of meetings like
  the one from your team or colleagues.
* **title_match_icon**: A map between a regexp matching a tytle to an icon. This
  allows you to easily differentiate certain type of meetings by titles, like
  the recurring videogame break you are ought to deserve for your hard work.
* **max_results**: Max results to ask to google calendar api.
* **skip_non_accepted**: Skip the calendar events that you didn't accept, you
  need to configure `my_emails` setting for that.
* **skip_non_confirmed**: Skip calendar events that are not confirmed.
* **skip_all_day**: Skip all day events (default: `true`)
* **starts_today_only**: Skip all but today events.
* **my_emails**: A list of email addresses.
* **restrict_to_calendar**: Restrict to some calendar, by default it shows event from all calendars.
* **title_max_char**: The maximum length of the title
* **change_icon_minutes**: Before the meeting x minutes before the event we will
  change the icon to gently remind you to connect.
* **calendar_day_prefix_url**: The prefix URL for the day in the web calendar when clicking, by default this goes to google calendar URL.
* **strip_title_emojis**: wether removing the emojis from title when showing in
  the menubar, so to keep the panel clean


Default icons are customizatble too:

* **icon_default_path**: the default icon, it will use the icon
                   "x-office-calendar-symbolic" from gnome theme by default.
* **icon_in_event_path**: the icon when in event, it will show a colored calendar
                    icon by default.
* **icon_before_event_path**: an icon just before an event to show something is
coming up.

### Starting it

If you install your application via Flatpak, you will need to create autostart entry manually. The easiest way to do this is to use [gnome-tweaks](https://gitlab.gnome.org/GNOME/gnome-tweaks) and add the Next meeting applet in the "Startup Applications" tab.

If you have access to it, there is a setting menu in the applet to add an autostart file to autostart it when gnome launch or you can launch it manually from the Gnome overview application launcher thingy.

## Compatibility

Works with Gnome as long you have this appindicator applet (which is by default on Ubuntu*)

If you don't run on Gnome you need to make sure to first run the goa-daemon, for example on my arch system :

```shell
/usr/lib/goa-daemon --replace &
```

(binary path may vary by distros, see this bugzilla bug as well [#1340203](https://bugzilla.redhat.com/show_bug.cgi?id=1340203))

If your "launcher/panel/bar" (like xfce, kde, polybar, waybar, i3bar etc..) supports trays icons then
it would show the icon which you can click on it to see the full list of meetings. Usually you would not
be able to see the text directly on the panel/bar, to do this you can use the dbus interface.

## Dbus Interface and CLI

You have a dbus interface to integrate with a so called "panel" or bars that doesn't support the full appindicator specification like the gnome extensions does. Using the cli you can access that dbus interface to get to show your next meeting :

```shell
$ gnome-next-meeting-applet dbus get_event
1 hour, 5 minutes -- New Meeting
```

You can as well have it to open the next/current event url :

```shell
gnome-next-meeting-applet dbus open_event_url
```

which you can bind to a key in your Windows Manager or Gnome/KDE to quickly go to your meeting Video Conference URL.

### Sway/Waybar

An example of a custom module for [Waybar](https://github.com/Alexays/Waybar) :

```json
    "custom/gnma": {
        "format": " {} ",
        "interval": 5,
        "exec": "gnome-next-meeting-applet dbus get_event",
        "exec-if": "pgrep -f gnome-next-meeting-applet",
        "max-length": 50,
        "min-length": 1,
        "on-click": "gnome-next-meeting-applet dbus open_event_url",
    },
```

my sway/waybar config looks like this screenshot below and is [located here](https://github.com/chmouel/rc-config/blob/main/waybar/config) :

<meta http-equiv="content-type" content="text/html; charset=utf-8"><img src="https://i.imgur.com/wwXY2C8.png" style="max-height: 216.365px; min-height: 216.365px; max-width: 1874.8px;">

there is more room to improvements here to integrate with other "bars".

### Credits

* This package was created with [`Cookiecutter`](https://github.com/audreyr/cookiecutter-pypackage) and the
[`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage) project template.
* Originally inspired from the [gnome next
  meeting](https://github.com/tjwells47/gnome-next-meeting) argos based
  extension.
* Used for a while the OSX application gnome-next-meeting
  <https://apps.apple.com/us/app/next-meeting/id1017470484?mt=12> and missed it on
  Linux.
* Originally used code from [@GabLeRoux](https://github.com/gableroux) for evolution calendar integration - <https://askubuntu.com/a/1371087>
* Used code from cinnamon calendar server code <https://github.com/linuxmint/cinnamon/blob/fc57426d44c0f5a31fe29f268a15e9928e8b6a14/calendar-server/cinnamon-calendar-server.py> and adapted from gnome-shell calendar-server <https://gitlab.gnome.org/GNOME/gnome-shell/-/tree/main/src/calendar-server>

## License

[MIT](LICENSE.md) © [Chmouel Boudjnah](https://github.com/chmouel)

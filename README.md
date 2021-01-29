# Gnome Next Meeting applet

An applet to show your next meetings in Gnome


* Free software: GNU General Public License v3
* Documentation: https://gnome-next-meeting-applet.readthedocs.io.

## Screenshot

![Screenshot](./.github/screenshot/screenshot.png)

## Features

* Make it easy to know how long you have until your next meeting.
* Detect video conference URL in location or google meet.
* Shows the documents link to the current meeting.
* Fully configurable.

## Configuration

Before launching the applet you need to first generate a Google OAuth 2.0 Client
Credentials and authorize it.

* Go to the Google Cloud Console: https://console.developers.google.com/apis/credentials

* Select Create credentials and Oauth Client ID

![Create Credentials image](./.github/screenshot/create-oauth-1.png)

* Select "Desktop app" for the Application Type and give it a name.

![Create Desktop app](./.github/screenshot/create-oauth-2.png)

* On the next screen you can just click OK, since we will look over the auth json file.

* Now next to your created application you will see an icon to download the auth
  json file, click on it and store it somewhere in a name you can rememeber (ie: `client_secret.json`)

![Click on download file](./.github/screenshot/create-oauth-2.png)

* In the terminal launch `gnome-next-meeting-applet-auth` with the path to the auth json file : 

    `gnome-next-meeting-applet-auth ~/Downloads/client_secret.json`

* This will launch your webbrowser to do the oauth dance

* If your browser tells you the apps is unverified you can say it's okay (it's
  should be the one that you have created yourself).
  
* After the last click of authorizations the credentials has been created.

![Created](./.github/screenshot/create-oauth-5.png)

* You can now launch the gnome-next-meeting applet.

### Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter-pypackage) and the
`[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)`
project template.

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

Name:           gnome-next-meeting-applet
Version:        _VERSION_
Release:        1%{?dist}
Summary:        Gnome Next Meeting Applet

License:        GPLv3
URL:            http://github.com/chmouel/gnome-next-meeting-applet
Source0:        https://github.com/chmouel/%{name}/archive/%{name}-%{version}.tar.gz
   
BuildArch:      noarch
BuildRequires:  python3-devel

# gnome-settings-daemon
Requires:       python3-gobject
Requires:       python3-tzlocal
Requires:       python3-dateutil
Requires:       python3-oauth2client
Requires:       libappindicator-gtk3
Requires:       python3-gobject
Requires:       python3-yaml
Requires:       gnome-icon-theme

%description
Gnome next meeting applet will show your next appointment coming from Google
 Calendar.

%prep
%setup -q -n %{name}-%{version}

%build
%py3_build

%install
%py3_install
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/%{name}
mv $RPM_BUILD_ROOT/usr/images $RPM_BUILD_ROOT/%{_datadir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications/
cat <<EOF> $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop
[Desktop Entry]
Name=Gnome Calendar Next meeting
Comment=An applet for your calendar
Exec=sketch
Icon=calendar
Categories=Application;Productivity;
Type=Application
Terminal=0
EOF

# Register as an application to be visible in the software center
mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata

%files
%doc README.md AUTHORS.rst CONTRIBUTING.rst config.sample.yaml
%license LICENSE
%{python3_sitelib}/gnome_next_meeting_applet
%{python3_sitelib}/gnome_next_meeting_applet-%{version}-py%{python3_version}.egg-info
%{_bindir}/%{name}
%{_bindir}/%{name}-auth
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop

%changelog
* Fri Feb  5 2021 Chmouel Boudjnah <chmouel@chmouel.com> - 0.1.0-1
- first packaging version

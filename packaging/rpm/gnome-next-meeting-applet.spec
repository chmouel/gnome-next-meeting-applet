%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

Name:           gnome-next-meeting-applet
Version:        _VERSION_
Release:        1%{?dist}
Summary:        Gnome Next Meeting Applet

License:        MIT
URL:            http://github.com/chmouel/gnome-next-meeting-applet
Source0:        https://github.com/chmouel/%{name}/archive/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-toml
BuildRequires:  python3-poetry-core

# gnome-settings-daemon
Requires:       libappindicator-gtk3
Requires:       python3-gobject
Requires:       python3-dateutil
Requires:       python3-yaml
Requires:       python3-humanize
Requires:       evolution-data-server
Requires:       gnome-icon-theme

%description
Gnome next meeting applet will show your next appointments coming from your
calendar configured in Gnome Online Accounts or Evolution data server.

%generate_buildrequires
%pyproject_buildrequires
 
%prep
%setup -q -n %{name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/%{name}
cp -a data/images $RPM_BUILD_ROOT/%{_datadir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications/
install -m0644 data/desktop/%{name}.desktop $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop

mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons
install -m 0644 data/desktop/icon.svg $RPM_BUILD_ROOT%{_datadir}/icons/%{name}.svg

%files
%doc README.md config.sample.yaml
%license LICENSE
%{python3_sitelib}/gnma
%{python3_sitelib}/gnome_next_meeting_applet-%{version}.dist-info
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/%{name}.svg

%changelog
* Fri Nov 30 2021 Chmouel Boudjnah <chmouel@chmouel.com> - 2.0.0-1
- Use poetry pypackages

* Fri Feb  5 2021 Chmouel Boudjnah <chmouel@chmouel.com> - 0.1.0-1
- first packaging version

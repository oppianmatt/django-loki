%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           loki
Version:        0.6.0
Release:        2%{?dist}
Summary:        Buildbot manager application with buildbot func modules

Group:          Development/Tools
License:        GPLv3+
URL:            https://fedorahosted.com/loki/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       python >= 2.4, func >= 0.21, python-sqlalchemy > 0.4, python-director
BuildRequires:  python-devel, python-setuptools


%description
Loki is a manager application for buildbot
source building system.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/loki/
mkdir -p $RPM_BUILD_ROOT/usr/share/loki/users/
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT/
cp etc/* $RPM_BUILD_ROOT/%{_sysconfdir}/loki/


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc INSTALL LICENSE AUTHORS COPYING
# For noarch packages: sitelib
%config(noreplace) %{_sysconfdir}/loki/loki.conf
%{_sysconfdir}/loki/*.tpl
%{python_sitelib}/*
%attr (0755,root,root) %{_bindir}/*


%changelog
* Wed Nov 12 2008 Dan Radez <dradez@redhat.com> - 0.6.0-1
- massive changes to file structure. support to managme vm servers.

* Tue Sep 30 2008 Dan Radez <dradez@redhat.com> - 0.5.0-1
- updated version push to fedorahosted

* Mon Sep 22 2008 Dan Radez <dradez@redhat.com> - 0.4.0-1
- cleaned up spec for move into fedorahosted

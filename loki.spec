# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
# Use the info in setup.py
%{!?app_name: %define app_name %(%{__python} setup.py --name)}
%{!?app_version: %define app_version %(%{__python} setup.py --version)}
%{!?app_summary: %define app_summary %(%{__python} setup.py --description)}
%{!?app_description: %define app_description %(%{__python} setup.py --long-description)}
%{!?app_license: %define app_license %(%{__python} setup.py --license)}
%{!?app_url: %define app_url %(%{__python} setup.py --url)}


Name:           Django-app-loki
Version:        %{app_version}
Release:        1%{?dist}
Summary:        %{app_summary}

Group:          Applications/Internet
License:        %{app_license}
URL:            %{app_url}
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       Django-reusable-base, PyYAML, python-docutils, buildbot


%description
%{app_description}


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_usr}/share/django/apps/loki

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING LICENSE
# For noarch packages: sitelib
%{python_sitelib}/*
%dir %{_datadir}/django/apps/loki/
%{_datadir}/django/apps/loki/*
#%ghost %{python_sitelib}/*egg-info


%changelog
* Tue Nov 24 2009 Dan Radez <dradez@redhat.com> - 0.6.0-1
- Initial spec for loki rewrite

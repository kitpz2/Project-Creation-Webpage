Name:           project.creation.portal
Summary:        Web pages for Project Creation
Version:        1.0.0
Release:        1
License:    .   GPL
Group:          System Environment/Base
Source:         %{name}-%{version}.src.tar.gz
BuildRoot:      %{_tmppath}/%{name}-root
BuildArch:      noarch

%description
This package contains web pages for Project Creation service in CERN

%prep

%setup -n %{name}-%{version}

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install prefix=$RPM_BUILD_ROOT libInsdir=%{libInsdir} tabledir=%{tabledir} licdir=%{licdir}

%clean
rm -rf $RPM_BUILD_DIR/%{name}-%{version}
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/var/django/*

#%doc /usr/share/doc/%{name}/*

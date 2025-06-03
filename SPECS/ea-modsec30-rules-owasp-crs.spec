Name: ea-modsec30-rules-owasp-crs
Summary: OWASP ModSecurity Core Rule Set (CRS) for Mod Sec 3.0
Version: 3.3.7
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 2
Release: %{release_prefix}%{?dist}.cpanel
Vendor: cPanel, Inc.
Group: System Environment/Libraries
License: Apache v2
URL: https://github.com/coreruleset/coreruleset

# This provides the source we want. See markdown fiel in SOURCES/ for details
BuildRequires: ea-modsec2-rules-owasp-crs
Requires: ea-modsec30

Provides: ea-modsec-rules-owasp-crs
Conflicts: ea-modsec-rules-owasp-crs

Source3: pkg.prerm
Source4: pkg.postinst
Source5: pkg.preinst

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
AutoReq:   no

%description
The OWASP ModSecurity Core Rule Set (CRS) is a set of generic attack detection
 rules for use with ModSecurity or compatible web application firewalls.
 The CRS aims to protect web applications from a wide range of attacks,
 including the OWASP Top Ten, with a minimum of false alerts.

%install
rm -rf $RPM_BUILD_ROOT

# Sources for reuse by various webservers that do mod sec 3.0
mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3
/bin/cp -f /opt/cpanel/ea-modsec2-rules-owasp-crs/* $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/
/bin/cp -rf /etc/apache2/conf.d/modsec_vendor_configs/OWASP3/* $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3
mkdir -p $RPM_BUILD_ROOT/var/cpanel/modsec_vendors
perl -pi -e 's/ea-modsec2-rules-owasp-crs/ea-modsec30-rules-owasp-crs/' $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml
perl -pi -e 's/2\.9/3.0/g' $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml
/bin/cp -f $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml $RPM_BUILD_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml

# NGINX
mkdir -p $RPM_BUILD_ROOT/etc/nginx/conf.d/modsec_vendor_configs
ln -s  /opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3 $RPM_BUILD_ROOT/etc/nginx/conf.d/modsec_vendor_configs/OWASP3

# Apache
# The WHM system will not follow a symlink and you cannot hardlink directories so we keep a duplicate copy :(
mkdir -p $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/bin/cp -rf $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3/* $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%include %{SOURCE5}

%post
%include %{SOURCE4}

%preun
%include %{SOURCE3}

%posttrans

# RPM needs this (see ZC-7633 for details), already happening for deb via %{SOURCE4}
PERL=/usr/local/cpanel/3rdparty/bin/perl
$PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'

%files
%defattr(-, root, root, -)
/opt/cpanel/ea-modsec30-rules-owasp-crs
/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/etc/nginx/conf.d/modsec_vendor_configs/OWASP3
/var/cpanel/modsec_vendors/meta_OWASP3.yaml

%changelog
* Tue May 27 2025 Julian Brown <julian.brown@webpros.com> - 3.3.7-2
- ZC-12871: Correct the meta data

* Mon May 19 2025 Dan Muey <daniel.muey@webpros.com> - 3.3.7-1
- ZC-12842: Bump version to match upstream

* Tue Nov 29 2022 Travis Holloway <t.holloway@cpanel.net> - 3.3.4-1
- EA-10944: Bump version to match upstream

* Wed Mar 16 2022 Travis Holloway <t.holloway@cpanel.net> - 3.3.2-1
- EA-10394: Bump version to match upstream

* Wed Dec 29 2021 Dan Muey <dan@cpanel.net> - 3.3.0-9
- ZC-9573: Correct an order of operations installation issue on CentOS

* Thu Dec 16 2021 Dan Muey <dan@cpanel.net> - 3.3.0-8
- ZC-9203: Update DISABLE_BUILD to match OBS

* Wed Nov 03 2021 Travis Holloway <t.holloway@cpanel.net> - 3.3.0-7
- EA-10240: Update verbiage to be OS neutral

* Wed Nov 03 2021 Daniel Muey <dan@cpanel.net> - 3.3.0-6
- ZC-9450: correct version in YAML file

* Tue Apr 13 2021 Daniel Muey <dan@cpanel.net> - 3.3.0-5
- ZC-8756: Update for upstream ULC changes

* Tue Oct 06 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-4
- ZC-7710: If already disabled, re-disable to get the yum.conf to match reality

* Tue Sep 29 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-3
- ZC-7337: Changes to support ULC enabling/disabling updates for an RPM based vendor

* Thu Sep 10 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-2
- ZC-7524: update UI name and description to be 3.0

* Wed Aug 26 2020 Dan Muey <dan@cpanel.net> - 3.0.2-1
- ZC-5715: initial release

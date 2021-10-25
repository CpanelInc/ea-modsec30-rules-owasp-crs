Name: ea-modsec30-rules-owasp-crs
Summary: OWASP ModSecurity Core Rule Set (CRS) for Mod Sec 3.0
Version: 3.3.0
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 5
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
/bin/cp -f $RPM_BUILD_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml $RPM_BUILD_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml
perl -pi -e 's/ea-modsec2-rules-owasp-crs/ea-modsec30-rules-owasp-crs/' $RPM_BUILD_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml
perl -pi -e 's/2\.9/3.0/g' $RPM_BUILD_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml

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

if [ $1 -eq 0 ] ; then
    echo "Removing OWASP3 config"
    PERL=/usr/local/cpanel/3rdparty/bin/perl

    # We can't `/usr/local/cpanel/scripts/modsec_vendor remove OWASP3`
    #   because it also removes the RPM owned files creating many warnings later
    #   so we emulate the bits we need

    # 1. update installed_from.yaml
    $PERL -MCpanel::CachedDataStore -e \
      'my $hr=Cpanel::CachedDataStore::loaddatastore($ARGV[0]);delete $hr->{data}{OWASP3};Cpanel::CachedDataStore::savedatastore($ARGV[0], { data => $hr->{data} })' \
      /var/cpanel/modsec_vendors/installed_from.yaml

    # 2. update modsec_cpanel_conf_datastore
    $PERL -MYAML::Syck -e 'my $h=YAML::Syck::LoadFile($ARGV[0]);delete $h->{active_vendors}{OWASP3};delete $h->{vendor_updates}{OWASP3};for my $rid (keys %{$h->{disabled_rules}}) { delete $h->{disabled_rules}{$rid} if $h->{disabled_rules}{$rid} eq "OWASP3" } for my $pth (keys %{$h->{active_configs}}) { delete $h->{active_configs}{$pth} if $pth =~ m{^modsec_vendor_configs/OWASP3/} } YAML::Syck::DumpFile($ARGV[0], $h)' /var/cpanel/modsec_cpanel_conf_datastore

    #. 3 kill caches
    rm -rf /var/cpanel/modsec_vendors/meta_OWASP3.cache /var/cpanel/modsec_vendors/installed_from.cache /var/cpanel/modsec_cpanel_conf_datastore.cache

    # 4. rebuild modsec30.cpanel.conf based on new modsec_cpanel_conf_datastore
    $PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'

    # 5. remove updates-disabled from conf
    $PERL -MCpanel::SysPkgs -e 'my $pkg = "ea-modsec30-rules-owasp-crs";my $sp = Cpanel::SysPkgs->new;my ($parse, $write) = $sp->can("write_conf") ? qw(parse_conf write_conf) : qw(parse_yum_conf write_yum_conf);$parse="parse_pkgmgr_conf" if $sp->can("parse_pkgmgr_conf");$write = "write_pkgmgr_conf" if $sp->can("write_pkgmgr_conf");$sp->$parse;if ( grep { $_ eq $pkg } split /\s+/, $sp->{original_exclude_string} ) {$sp->{exclude_string} =~ s/(?:^$pkg$|^$pkg\s+|\s+$pkg\s+|\s+$pkg$)//g; $sp->$write;}'
fi

%posttrans

PERL=/usr/local/cpanel/3rdparty/bin/perl
$PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'

%files
%defattr(-, root, root, -)
/opt/cpanel/ea-modsec30-rules-owasp-crs
/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/etc/nginx/conf.d/modsec_vendor_configs/OWASP3
/var/cpanel/modsec_vendors/meta_OWASP3.yaml

%changelog
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

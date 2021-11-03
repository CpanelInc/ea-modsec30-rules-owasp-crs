#!/bin/bash

source debian/vars.sh

set -x

# Sources for reuse by various webservers that do mod sec 3.0
mkdir -p $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3
/bin/cp -f /opt/cpanel/ea-modsec2-rules-owasp-crs/* $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/
/bin/cp -rf /etc/apache2/conf.d/modsec_vendor_configs/OWASP3/* $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3
mkdir -p $DEB_INSTALL_ROOT/var/cpanel/modsec_vendors
perl -pi -e 's/ea-modsec2-rules-owasp-crs/ea-modsec30-rules-owasp-crs/' $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml
perl -pi -e 's/2\.9/3.0/g' $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml
/bin/cp -f $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/meta_OWASP3.yaml $DEB_INSTALL_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml

# NGINX
mkdir -p $DEB_INSTALL_ROOT/etc/nginx/conf.d/modsec_vendor_configs
ln -s /opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3 $DEB_INSTALL_ROOT/etc/nginx/conf.d/modsec_vendor_configs/OWASP3

# Apache
# The WHM system will not follow a symlink and you cannot hardlink directories so we keep a duplicate copy :(
mkdir -p $DEB_INSTALL_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/bin/cp -rf $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec30-rules-owasp-crs/OWASP3/* $DEB_INSTALL_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

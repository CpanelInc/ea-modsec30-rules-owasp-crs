#!/usr/bin/perl

# EA-13496: rule 901181 (new in upstream CRS v3.3.10) uses
# `ctl:ruleRemoveTargetByTag=<tag>;XML://@*`, which fails to parse on this
# package's exact combination - libmodsecurity 3.0.15 + ModSecurity-apache
# v0.1.1-beta (ea-modsec30-connector-apache24). cPanel's vendor-activation
# path (Whostmgr::ModSecurity::ModsecCpanelConf::manipulate ->
# validate_httpd_config) rebuilds and validates the full generated httpd
# config on every rule-file activation, and silently rolls back any file
# that fails - which meant the ENTIRE REQUEST-901-INITIALIZATION.conf file
# (including rule 901200, which zeroes the anomaly-score accumulator TX
# vars) never activated, and CRS's anomaly-score-based blocking never fired
# for any attack signature. See work/handoffs/EA-13492-modsec-rules-
# investigation.md for the full trace and live proof.
#
# CONFIRMED SCOPED TO THIS (experimental modsec30) PACKAGE ONLY: the same
# construct, live-tested against the CORE ea-apache24-mod_security2 +
# ea-modsec2-rules-owasp-crs stack (a materially different, older SecLang
# parser), parses and blocks correctly - "Access denied ... Operator GE
# matched 5 at TX:anomaly_score" with the anomaly score genuinely
# accumulating. This transform therefore runs ONLY on this package's own
# %install copy of the ruleset (after it's copied from whatever
# ea-modsec2-rules-owasp-crs produced), never touching the shared core
# package's content - ea-modsec2-rules-owasp-crs ships this rule unmodified.
#
# This is a functional no-op on our default deployment either way: XML
# attribute inspection is opt-in (id:900510 stays commented in our shipped
# crs-setup.conf), so disabling the rule that opts OUT of an already-off
# feature has zero behavioral effect beyond restoring the rest of the file.

use strict;
use warnings;

my $file = shift or die "usage: $0 <path-to-REQUEST-901-INITIALIZATION.conf>\n";

open( my $in, '<', $file ) or die "EA-13496: cannot read $file: $!\n";
my @lines = <$in>;
close($in);

my $in_rule = 0;
my $found   = 0;

for my $line (@lines) {
    if ( $line =~ /^SecRule TX:crs_xml_attr_inspect "\@eq 0" \\\s*$/ ) {
        $in_rule = 1;
        $found   = 1;
    }

    $line = "#$line" if $in_rule && $line !~ /^#/;

    if ( $in_rule && $line =~ /ver:'OWASP_CRS\/[\d.]+'"\s*$/ ) {
        $in_rule = 0;
    }
}

die "EA-13496: rule 901181 marker not found in $file - upstream content may "
  . "have changed shape; refusing to silently no-op. Re-check this transform "
  . "against the new content before re-running.\n"
  unless $found;

open( my $out, '>', $file ) or die "EA-13496: cannot write $file: $!\n";
print $out @lines;
close($out);

print "EA-13496: disabled rule 901181 in $file\n";

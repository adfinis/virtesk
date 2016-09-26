#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

# Copyright (c) 2013-2016, Adfinis SyGroup AG
#
# This file is part of Virtesk VDI.
#
# Virtesk VDI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Virtesk VDI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Virtesk VDI.  If not, see <http://www.gnu.org/licenses/>.

# System Imports
import os
import re
import logging
import subprocess


def get_dmidecode_sysuuid():
    result = []

    dmi = subprocess.check_output("sudo dmidecode -t1", shell=True)
    for line in dmi.splitlines():
        match_uuid = re.search('UUID:\s+([0-9A-Za-z_-]+)', line)
        if match_uuid:
            result.append(match_uuid.group(1).upper())
    return result


def find_dhclient_leasefiles():
    # Finds dhclient lease files.
    # More or less the same as:
    #  ps ax | grep dhclient
    #  and then looking at the -lf parameter.

    procdir = os.listdir('/proc')

    leasefiles = []
    for procfile in procdir:
        try:
            if procfile.isdigit():
                cmdfile_path = '/proc/%s/cmdline' % procfile
                with open(cmdfile_path, 'r') as cmdline_file:
                    cmdline_nullseperated = cmdline_file.read()
                cmdline = cmdline_nullseperated.split('\0')[0:-1]
                if len(cmdline) is 0:
                    continue
                if re.search('dhclient', cmdline[0]) is None:
                    continue

                i = cmdline.index('-lf')
                if i < len(cmdline):
                    leasefiles.append(cmdline[i + 1])
        except:
            continue

    return leasefiles


def extract_identifiers_from_leasefiles(leasefilepaths):
    hostnames = []
    fixedips = []
    for leasefilepath in leasefilepaths:
        if leasefilepath is None:
            return None
        logging.debug("reading dhclient-leasefile %s", leasefilepath)
        with open(leasefilepath, 'r') as leasefile:
            leasefilecontent = leasefile.read()

        leases = re.split("lease\s*\{([^\}]*)\}", leasefilecontent)

        for lease in leases:
            if lease is None:
                continue
            if re.match("\s*\Z", lease):
                continue

            match_fixedip = re.search(
                'fixed-address\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', lease)
            if match_fixedip:
                fixedip = match_fixedip.group(1)
                logging.debug("found fixed ip address in dhclient lease " +
                              "file: %s", fixedip)
                if fixedip not in fixedips:
                    fixedips.append(fixedip)

            match_hostname = re.search(
                'option\s*host-name\s*"([\w\-.]+)"', lease)
            if match_hostname:
                hostname = match_hostname.group(1)
                logging.debug("found hostname in dhclient lease file: %s",
                              hostname)

                # some dhcp servers serve FQDNs, some only short hostnames.
                # here, we do want short hostnames.
                match_fqdn = re.search('([\w\-]+)\..*', hostname)
                if match_fqdn:
                    hostname_fqdn = hostname
                    hostname = match_fqdn.group(1)
                    logging.debug(
                        "hostname: %s fqdn: %s" % (hostname_fqdn, hostname))

                if hostname not in hostnames:
                    hostnames.append(hostname)

    return (hostnames, fixedips)


def process_ip(ip):
    # RHEV-tags cannot contain dots in their names.
    # so we replace dots by hyphens.
    return ip.replace('.', '-')


def get_thinclient_identifiers():
    leasefilepaths = find_dhclient_leasefiles()
    (hostnames, fixedips) = extract_identifiers_from_leasefiles(leasefilepaths)
    identifiers = (["thinclient-hostname-%s" % x for x in hostnames] +
                   ["thinc*ient-hostname-%s" % x for x in hostnames] +
                   ["thinclient-ip-%s" % process_ip(x) for x in fixedips] +
                   ["thinc*ient-ip-%s" % process_ip(x) for x in fixedips])
    logging.debug("Found the following thinclient identifiers: %s",
                  ", ".join(identifiers))
    return identifiers


def get_dhcp_hostnames():
    leasefilepaths = find_dhclient_leasefiles()
    (hostnames, fixedips) = extract_identifiers_from_leasefiles(leasefilepaths)
    return hostnames


def main():
    print get_thinclient_identifiers()

if __name__ == "__main__":
    main()

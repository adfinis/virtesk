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
import subprocess
import re


def extract_identifiers_from_nmcli():
    fixedips = []
    hostnames = []
    nmcli_output = subprocess.check_output(['nmcli', 'device', 'show'], env={'LC_ALL': 'C'})
    for line in nmcli_output.splitlines():
        if re.match('^IP4\.ADDRESS.', line):
            key, value = get_line_key_value(line)
            value = value[:value.index("/")].strip()
            fixedips.append(value)
        elif re.match('^GENERAL\.CONNECTION.', line):
            key, value = get_line_key_value(line)
            dhcp_hostname = get_dhcp_hostname_from_connection(value)
            if dhcp_hostname:
                hostnames.append(dhcp_hostname)
    hostnamectl_output = subprocess.check_output('hostnamectl', env={'LC_ALL': 'C'})
    for line in hostnamectl_output.splitlines():
        if re.match('^Transient', line):
            key, value = get_line_key_value( line )
            hostnames.append(value)
    return (hostnames, fixedips)


def get_dhcp_hostname_from_connection(name):
    if name and name != '--':
        nmcli_output = subprocess.check_output(['nmcli', 'con', 'show', name], env={'LC_ALL': 'C'})
        for line in nmcli_output.splitlines():
            if re.match('^ipv4\.dhcp-hostname.', line):
                key, value = get_line_key_value(line)
                if value != '--':
                    return value


def get_line_key_value(line):
    if line:
        values = str(line).split(':')
        if len(values) == 2:
            key, value = values
            value = value.strip()
            return (key, value)


def get_active_connections():
    nmcli_output = subprocess.check_output(['nmcli', '-t', '-f', 'state', 'con', 'show', '--active'], env={'LC_ALL': 'C'})
    return len(nmcli_output.splitlines())

def main():
    print(extract_identifiers_from_nmcli())


if __name__ == "__main__":
    main()

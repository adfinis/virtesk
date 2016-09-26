#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

"""Defines constants for Ad-Sy RHEV tools"""

# Copyright (c) 2013-2016, Adfinis SyGroup AG
#
# This file is part of Amoothei-VDI.
#
# Amoothei-VDI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Amoothei-VDI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Amoothei-VDI.  If not, see <http://www.gnu.org/licenses/>.

import os

DEFAULT_CONFIGURATION_FILE_NAME = 'adsy-rhev-tools.config'

CONFIG_FILE_SEARCH_PATH = [
    os.path.expanduser('~/.config/virtesk-vdi/virtesk-vm-rollout.conf'),
    '/etc/virtesk-vdi/virtesk-vm-rollout.conf'
]

# Wait time in seconds after creating a new VM.
VM_CREATION_SLEEP_TIME = 15

# Wait time in seconds after various tasks concerning VMs
VM_SLEEP_TIME = 10

# Wait time in seconds after creating a new VM snapshot
CREATE_VM_SNAPSHOT_SLEEP_TIME = 8

# Wait time in seconds between attempts to check the state of freshly
# created VM snapshots
WAIT_FOR_SNAPSHOTS_READY_SLEEP_TIME = 4

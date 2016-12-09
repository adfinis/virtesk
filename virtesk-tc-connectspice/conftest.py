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
import pytest
import os.path


MOCK_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_mock_data/")


@pytest.yield_fixture(scope='module')
def active_connection():
    yield readfile('active_connection')


@pytest.yield_fixture(scope='module')
def nmcli_con_show_empty():
    yield readfile('nmcli_con_show_adsy_eap_empty')


@pytest.yield_fixture(scope='module')
def nmcli_con_show():
    yield readfile('nmcli_con_show_adsy_eap')


@pytest.yield_fixture(scope='module')
def nmcli_device_show_single_line():
    yield readfile('nmcli_device_show_single_line')


@pytest.yield_fixture(scope='module')
def nmcli_device_show():
    yield readfile('nmcli_device_show')


def readfile(filename):
    print(MOCK_DATA_PATH)
    with open(MOCK_DATA_PATH + filename, 'r') as f:
        return f.read()

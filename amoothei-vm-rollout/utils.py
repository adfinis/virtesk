#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

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


# System imports
import contextlib
import errno
import os
import shutil
import tempfile

# Project imports
import constants


class Failure:

    def __init__(self, msg):
        self.msg = msg


def get_valid_config_file(config_file):
    """
    Checks if the given parameter 'config_file'
    exists as file and is readable. If not, tries
    to get one possible configuration file within
    the path under CONFIG_FILE_SEARCH_PATH.
    """

    if config_file is not None:
        if os.path.exists(config_file):
            return config_file
        else:
            config_file = os.path.expanduser(config_file)
            if os.path.exists(config_file):
                return config_file
            else:
                raise Failure(
                    "Config file `{0}' does not exist.".format(config_file)
                )

    for config_file in constants.CONFIG_FILE_SEARCH_PATH:
        if os.path.exists(config_file):
            os.stat(config_file)
            return config_file

    raise Failure(
        "No config file specified on command line and no "
        "config file available at default locations."
    )


@contextlib.contextmanager
def tempdir(prefix):
    try:
        tempdir = tempfile.mkdtemp(prefix=prefix)
        yield tempdir
    finally:
        try:
            shutil.rmtree(tempdir)
        except OSError as e:
            # Reraise unless ENOENT: No such file or directory
            # (ok if directory has already been deleted)
            if e.errno != errno.ENOENT:
                raise

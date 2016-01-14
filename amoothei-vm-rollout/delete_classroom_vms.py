#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python
"""Documentation about the module... may be multi-line"""

# Copyright (c) 2013, Adfinis SyGroup AG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Adfinis SyGroup AG nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS";
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Adfinis SyGroup AG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# System Imports
import traceback
import argparse
import logging
import sys

# Project imports
import rhev_manager as adsy_rhev_manager
import utils as rhev_utils

try:
    # Commandline argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configfile',
        help="Absolute or relative path to configuration file,\
                e.g. '~/.config/adsy-rhev-tools.conf'.\
                If not given the application tries to determine the path\
                automatically."
    )

    parser.add_argument(
        'classroom', help="classroom to roll out"
    )

    args = parser.parse_args()

    config_file = rhev_utils.get_valid_config_file(
        args.configfile
    )
    classroom = args.classroom

    # Initialize RHEV manager
    rhev_manager = adsy_rhev_manager.RhevManager(
        config_file
    )

    rhev_manager.cleanup_classroom(classroom)

    # Cleanup
    rhev_manager.cleanup()

except Exception as ex:
    logging.exception("Unexpected error: {0}".format(ex))
    logging.exception(traceback.format_exc())
    sys.exit(-1) 


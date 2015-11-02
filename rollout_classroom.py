#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python
"""Invokes ADSY RHEV tools for rolling out the given class room."""

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
import logging
import os
import sys
import argparse
import subprocess
import string

# Project imports
import constants as constants

try:
    # Set python path
    sys.path.append(os.path.expanduser(os.getcwd()))

    # Set program
    program_name = 'python'

    # Get arguments
    arguments = ['manage_rhev.py']
    config_file = ['--configfile=']
    config_file.append(
        os.path.join(
            os.getcwd(),
            'config',
            'adsy-rhev-tools.conf'
        )
    )
    arguments.append(
        string.join(config_file, '')
    )
    arguments.append(constants.COMMANDS['rollout']['command'])
    system_arguments = sys.argv
    system_arguments.remove(sys.argv[0])
    arguments = arguments + system_arguments

    # Set command
    command = [program_name]
    command.extend(arguments)

    # Run RHEV tools
    output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
    print output

except Exception as ex:
    logging.exception("Unexpected error: {0}".format(ex))
    logging.exception(traceback.format_exc())

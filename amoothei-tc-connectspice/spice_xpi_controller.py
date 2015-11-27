#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

"""
Implements the binary protocol [0] over a unix domain socket necessary for
parameter passing, configuration and controlling a spice client.

Tested with remote-viewer.

Only the sending side is implemented.
The receiving side has been omitted, because it wasn't necessary.

Please be aware that the specification [0] contains many errors, so for real
hacking, you might want to consult the source code of spice-xpi:
 git clone git://anongit.freedesktop.org/spice/spice-xpi

[0]: http://spice-space.org/page/Whiteboard/ControllerProtocol
"""

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


import socket
import struct
import logging


CONTROLLER_HOST = 1
CONTROLLER_PORT = 2
CONTROLLER_SPORT = 3
CONTROLLER_PASSWORD = 4

CONTROLLER_SECURE_CHANNELS = 5
CONTROLLER_DISABLE_CHANNELS = 6

CONTROLLER_TLS_CIPHERS = 7
CONTROLLER_CA_FILE = 8
CONTROLLER_HOST_SUBJECT = 9

CONTROLLER_FULL_SCREEN = 10
CONTROLLER_SET_TITLE = 11

CONTROLLER_CREATE_MENU = 12
CONTROLLER_DELETE_MENU = 13

CONTROLLER_HOTKEYS = 14
CONTROLLER_SEND_CAD = 15

CONTROLLER_CONNECT = 16
CONTROLLER_SHOW = 17
CONTROLLER_HIDE = 18

CONTROLLER_ENABLE_SMARTCARD = 19

CONTROLLER_COLOR_DEPTH = 20
CONTROLLER_DISABLE_EFFECTS = 21

CONTROLLER_ENABLE_USB = 22
CONTROLLER_ENABLE_USB_AUTOSHARE = 23
CONTROLLER_USB_FILTER = 24

CONTROLLER_MENU_ITEM_CLICK = 1001,


def ControllerValue(message_id, arg):
    result = struct.pack("=III", message_id, 12, arg)
    logging.debug("INT: message_id: %s, ARG: %s, STRUCT: %s" %
                  (message_id, arg, result))
    return result


def ControllerValueBoolean(message_id, arg):
    arg_boolean = 1 if arg else 0
    result = struct.pack("=III", message_id, 12, arg_boolean)
    logging.debug("Bool: message_id: %s, ARG: %s, STRUCT: %s" %
                  (message_id, arg, result))
    return result


def ControllerDataString(message_id, arg):
    argplusnull = arg + '\0'
    b = argplusnull.encode('ascii')
    fmt = "=II%ds" % len(b)
    size = len(b) + 8

    result = struct.pack(fmt, message_id, size, argplusnull)
    logging.debug("STRING: message_id: %s, ARG: %s, LEN: %d/%d, STRUCT: %s" %
                  (message_id, arg, size, len(result), result))
    return result


def ControllerMsg(message_id):
    result = struct.pack("=II", message_id, 8)
    return result


def connect(
    socket_filename, host, port, secport, ticket, spice_ca_file, secure_channels=None, disable_channels=None,
            tls_ciphers=None, host_subject=None, window_title=None, hotkeys=None, disable_effects=None,
            ctrl_alt_delete=None, enable_usb=None, enable_usb_autoshare=None, usb_filter=None, **rest):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_filename)

    # send CONTROLLER_INIT

    magic = 0x4C525443
    version = 1
    size = 24

    credentials = 0
    flags = 1

    s.send(struct.pack("=IIIQI", magic, version, size, credentials, flags))

    # send CONTROLLER_HOST
    s.send(ControllerDataString(CONTROLLER_HOST, host))

    # send CONTROLLER_PORT
    if not port is None:
        s.send(ControllerValue(CONTROLLER_PORT, port))

    # send CONTROLLER_SPORT
    if not secport is None:
        s.send(ControllerValue(CONTROLLER_SPORT, secport))

    # send CONTROLLER_PASSWORD
    s.send(ControllerDataString(CONTROLLER_PASSWORD, ticket))

    # send CONTROLLER_FULL_SCREEN
    s.send(ControllerValue(CONTROLLER_FULL_SCREEN, 1))

    # CA_FILE
    s.send(ControllerDataString(CONTROLLER_CA_FILE, spice_ca_file))

    # CONTROLLER_HOST_SUBJECT
    if not host_subject is None:
        s.send(ControllerDataString(CONTROLLER_HOST_SUBJECT, host_subject))

    # TLS_CIPHERS
    if not tls_ciphers is None:
        s.send(ControllerDataString(CONTROLLER_TLS_CIPHERS, tls_ciphers))

    # SECURE_CHANNELS
    if not secure_channels is None:
        s.send(ControllerDataString(
            CONTROLLER_SECURE_CHANNELS, secure_channels))

    if not disable_channels is None:
        s.send(ControllerDataString(
            CONTROLLER_DISABLE_CHANNELS, disable_channels))

    # CONTROLLER_SET_TITLE
    if not window_title is None:
        s.send(ControllerDataString(CONTROLLER_SET_TITLE, window_title))

    if not hotkeys is None:
        s.send(ControllerDataString(CONTROLLER_HOTKEYS, hotkeys))

    if not ctrl_alt_delete is None:
        s.send(ControllerValueBoolean(CONTROLLER_SEND_CAD, ctrl_alt_delete))

    if not disable_effects is None:
        s.send(ControllerDataString(
            CONTROLLER_DISABLE_EFFECTS, disable_effects))

    if not enable_usb is None:
        s.send(ControllerValueBoolean(CONTROLLER_ENABLE_USB, enable_usb))

    if not enable_usb_autoshare is None:
        s.send(ControllerValueBoolean(
            CONTROLLER_ENABLE_USB_AUTOSHARE, enable_usb_autoshare))

    if not usb_filter is None:
        s.send(ControllerDataString(CONTROLLER_USB_FILTER, usb_filter))

    # CONNECT
    s.send(ControllerMsg(CONTROLLER_CONNECT))

    s.send(ControllerMsg(CONTROLLER_SHOW))

    s.close()

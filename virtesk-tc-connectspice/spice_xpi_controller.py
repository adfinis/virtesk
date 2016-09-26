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

# Copyright (c) 2013-2016, Adfinis SyGroup AG
#
# This file is part of Virtesk VDI
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
        socket_filename, host, port, secport, ticket, spice_ca_file,
        secure_channels=None, disable_channels=None, tls_ciphers=None,
        host_subject=None, window_title=None, hotkeys=None,
        disable_effects=None, ctrl_alt_delete=None, enable_usb=None,
        enable_usb_autoshare=None, usb_filter=None, **rest
):
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
    if port is not None:
        s.send(ControllerValue(CONTROLLER_PORT, port))

    # send CONTROLLER_SPORT
    if secport is not None:
        s.send(ControllerValue(CONTROLLER_SPORT, secport))

    # send CONTROLLER_PASSWORD
    s.send(ControllerDataString(CONTROLLER_PASSWORD, ticket))

    # send CONTROLLER_FULL_SCREEN
    s.send(ControllerValue(CONTROLLER_FULL_SCREEN, 1))

    # CA_FILE
    s.send(ControllerDataString(CONTROLLER_CA_FILE, spice_ca_file))

    # CONTROLLER_HOST_SUBJECT
    if host_subject is not None:
        s.send(ControllerDataString(CONTROLLER_HOST_SUBJECT, host_subject))

    # TLS_CIPHERS
    if tls_ciphers is not None:
        s.send(ControllerDataString(CONTROLLER_TLS_CIPHERS, tls_ciphers))

    # SECURE_CHANNELS
    if secure_channels is not None:
        s.send(ControllerDataString(
            CONTROLLER_SECURE_CHANNELS, secure_channels))

    if disable_channels is not None:
        s.send(ControllerDataString(
            CONTROLLER_DISABLE_CHANNELS, disable_channels))

    # CONTROLLER_SET_TITLE
    if window_title is not None:
        s.send(ControllerDataString(CONTROLLER_SET_TITLE, window_title))

    if hotkeys is not None:
        s.send(ControllerDataString(CONTROLLER_HOTKEYS, hotkeys))

    if ctrl_alt_delete is not None:
        s.send(ControllerValueBoolean(CONTROLLER_SEND_CAD, ctrl_alt_delete))

    if disable_effects is not None:
        s.send(ControllerDataString(
            CONTROLLER_DISABLE_EFFECTS, disable_effects))

    if enable_usb is not None:
        s.send(ControllerValueBoolean(CONTROLLER_ENABLE_USB, enable_usb))

    if enable_usb_autoshare is not None:
        s.send(ControllerValueBoolean(
            CONTROLLER_ENABLE_USB_AUTOSHARE, enable_usb_autoshare))

    if usb_filter is not None:
        s.send(ControllerDataString(CONTROLLER_USB_FILTER, usb_filter))

    # CONNECT
    s.send(ControllerMsg(CONTROLLER_CONNECT))

    s.send(ControllerMsg(CONTROLLER_SHOW))

    s.close()

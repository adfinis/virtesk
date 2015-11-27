#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

"""Diverse Hilfsfunktionen"""

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

# System imports
import sys
import copy
import os

# Project imports
# import constants


# def commonstringprefix(first, second):
#     """
#     Berechnet das gemeinsame Prefix von zwei Strings.
#
#     type first: str
#     type second: str
#     rtype: str
#
#     """
#
#     l = min(len(first), len(second))
#     i = 0
#     while i < l:
#         if (first[i] != second[i]):
#             break
#         i = i + 1
#     result = first[0:i]
#     return result
#
#
# def commonstringsuffix(first, second):
#     """
#     Berechnet das gemeinsame Suffix von zwei Strings.
#
#     type first: str
#     type second: str
#     rtype: str
#
#     """
#     flen = len(first)
#     slen = len(second)
#     l = min(flen, slen)
#     i = 1
#     while i <= l:
#         if(first[flen - i] != second[slen - i]):
#             break
#         i = i + 1
#     return first[flen - i + 1:]
#
#
# def findmiddle(first, second, count=None):
#     """
#     Macht aus zwei Strings, die einen Range der Grösse count
#     repräsentieren, eine Liste, die diesen Range explizit ausdrückt.
#     """
#
#     if len(first) != len(second):
#         raise Exception(
#             "strings passed to findmiddle() have to be of equal length."
#         )
#
#     length = len(first)
#     prefix = commonstringprefix(first, second)
#     suffix = commonstringsuffix(first, second)
#
#     plen = len(prefix)
#     slen = len(suffix)
#
#     firstmiddle = first[plen: length - slen]
#     secondmiddle = second[plen:length - slen]
#
#     print firstmiddle + "|" + secondmiddle
#
#     firstint = int(firstmiddle)
#     secondint = int(secondmiddle)
#
#     assert firstint <= secondint
#
#     if not count is None:
#         if secondint - firstint != count:
#             raise Exception(
#                 "findmiddle: {0} + {1} == %i violated".format(
#                     firstint, count, secondint
#                 )
#             )
#
#     digits = len(str(secondint))
#     formatstring = "%s%0" + str(digits) + "i%s"
#
#     values = range(firstint, secondint + 1)
#     result = [formatstring % (prefix, val, suffix) for val in values]
#     return result
#
#
# def processrangestring(arg, count=None):
#     strings = arg.split("...")
#     assert len(strings) == 2
#
#     return findmiddle(strings[0], strings[1], count)
#

def applyconfigdefaults(config, defaults):
    """
    Konvertiert eine Liste von pairs zu einem Dictionary
    Das erste Element im Pair wird jeweils als key
    genommen, das zweite als value.

    param config: [('url', '[url]'), ('username', '[username]')]
    type config: list
    param defaults: default-werte
    type defaults: dict
    rtype: dict
    """
    result = copy.copy(defaults)
    for pair in config:
        result[pair[0]] = pair[1]

    return result


def escape_for_ovirt_query(query):
    return query.replace('_', '*')

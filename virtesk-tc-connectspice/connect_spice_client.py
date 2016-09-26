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
import argparse
import ConfigParser
import os
import re
import shlex
import subprocess
import copy
import time
import logging.config
# import logging.handlers
import sys
import traceback
import textwrap
import psycopg2

# Project Imports
import spice_xpi_controller
import find_thinclient_identifier
import ovirtsdk.api


class connect_spice_client:

    def get_vm_from_db(self):
        logging.info("Running setup code for db connection...")
        postgres_db_connect = self.config_general['postgres_db_connect']
        sys_uuids = find_thinclient_identifier.get_dmidecode_sysuuid()
        dhcp_hostnames = find_thinclient_identifier.get_dhcp_hostnames()
        logging.info("Running setup code for db connection... done")

        for i in range(1, 5 + 1):
            try:
                logging.info(
                    "connecting to database... (iteration {})".format(i)
                )

                # Connect to an existing database
                conn = psycopg2.connect(postgres_db_connect)

                # Open a cursor to perform database operations
                cur = conn.cursor()

                # Query the database and obtain data as Python objects
                cur.execute(
                    "SELECT vm, thinclient, prio, id, shutdown_vm "
                    "FROM thinclient_everything_view WHERE "
                    "dhcp_hostname = ANY (%s) OR systemuuid = ANY (%s);",
                    (dhcp_hostnames, sys_uuids)
                )

                results = cur.fetchall()

                cur.close()
                conn.close()

                logging.info(
                    "connecting to database... done (iteration {})".format(i)
                )

                if results is None or len(results) == 0:
                    # TRANSLATE:
                    # "No VM is assigned to this thinclient."
                    raise AssertionFailedException(
                        "Es konnte keine passende VM "
                        "für diesen Thinclient gefunden werden."
                    )

                self.vm_name = results[0][0]
                self.shutdown_vm = results[0][4]

                self.vm = self.api.vms.get(self.vm_name)

                if self.vm is None:
                    # TRANSLATE:
                    # "The virtual machine assigned to this
                    #  thinclient does not exist."
                    raise AssertionFailedException(
                        "Die diesem Thinclient zugewiesene "
                        "virtuelle Maschine existiert nicht."
                    )
                return self.vm

            except Exception as ex:
                if (
                    ex.message is not None
                    and ex.message.startswith("timeout expired")
                ):
                    logging.info(
                        "connecting to database... failed. (iteration {})"
                        .format(i)
                    )
                    self.notify_waiting_for_db_connection()
                    time.sleep(2)
                    continue
                else:
                    logging.exception(ex)
                    raise ex

            logging.error("Connecting to database: giving up.")

            # TRANSLATE:
            # "Couldn't connect to database. Please check your network
            #  connection and try again."
            raise FailedToConnectToDatabaseException(
                "Es konnte keine Datenbank-Verbindung hergestellt werden.\n"
                "Bitte Netzwerk überprüfen und evt. erneut probieren."
            )

    def prepare_vm(self):
        # A spice-connection can only be established when the VM is running
        # (see CONSOLE_STATES below).
        # This function ensures that the VM is ready to establish a
        # a spice-connection.
        # The VM is started if necessary.

        CONSOLE_STATES = ['powering_up', 'up', 'reboot_in_progress']

        logging.info('Status of VM %s: %s', self.vm.name, self.vm.status.state)
        if self.vm.status.state == 'down':
            logging.debug('starting VM: %s', self.vm.name)
            self.vm.start()
            time.sleep(4)
            vm_id = self.vm.id
            while self.vm.status.state not in CONSOLE_STATES:
                self.notify_waiting_for_vm_launch()
                time.sleep(2)
                self.vm = self.api.vms.get(id=vm_id)
                logging.info('Status of VM %s: %s', self.vm.name,
                             self.vm.status.state)

            while self.vm.display.address is None:
                logging.debug('Display address of VM %s is not ready.',
                              self.vm.name)
                time.sleep(2)
                self.vm = self.api.vms.get(id=vm_id)

    def get_vm_ticket(self):
        # Get the connection parameters necessary to establish a spice
        # connection, notably the spice ticket.

        self.config_spice['host'] = self.vm.display.address
        proto = self.vm.display.type_

        if proto != 'spice':
            # TRANSLATE:
            # "The virtual machine assigned to this thinclient uses
            #  a display protocol that is not supported by this VDI solution."
            raise NotSpiceConsoleException(
                "Die diesem Thinclient " +
                "zugeordnete VM benützt ein nicht unterstütztes " +
                "Display-Protokoll.\n\n" +
                "Bitte verständigen Sie den System Administrator."
            )

        self.config_spice['port'] = self.vm.display.port
        self.config_spice['secport'] = self.vm.display.secure_port
        action = self.vm.ticket()

        if action.status.state != 'complete':
            # TRANSLATE:
            # "Couldn't get a spice ticket for the virtual machine assigned
            #  to this thinclient. Please try again. If the issue persists,
            #  then please contact the system administrator."
            raise GetSpiceTicketFailedException(
                "Es konnte kein Spice-Ticket für die diesem Thinclient " +
                "zugeordnete VM erstellt werden.\n\n" +
                "Bitte probieren Sie den Vorgang erneut.\n\n" +
                "Falls der Fehler mehrmals besteht, verständigen Sie bitte " +
                "den System Administrator.")
        self.config_spice['ticket'] = action.ticket.value

        logging.debug("Spice connection parameters: Host: %s, Port: %s, " +
                      "SecPort: %s, Ticket: %s", self.config_spice['host'],
                      self.config_spice['port'], self.config_spice['secport'],
                      self.config_spice['ticket'])

        self.last_spice_server = (
            "%s:(%s,%s)" % (
                self.config_spice['host'],
                self.config_spice['port'],
                self.config_spice['secport']
            )
        )

        # host_subject:
        # We need to get the host_subject, a value corresponding to the
        # common name in the ssl certificate of the spice server.
        # If we wouldn't do it, things work as long as the IP we connect to
        # matches the common name. However, if we use a dedicated spice
        # display network, then the IP we connect to and the common name don't
        # match. Therefore, we have to send the the correct host_subject value
        # to the spice-client to avoid SSL errors.

        host_subject = None
        if self.vm.host and self.vm.host.id:
            logging.debug("try to get the host_subject value...")
            host = self.api.hosts.get(id=self.vm.host.id)
            if hasattr(host, 'certificate') and host.certificate:
                if host.certificate.subject:
                    host_subject = host.certificate.subject
                    logging.info("host_subject: '%s'" % host_subject)
                else:
                    logging.info("host_subject not present")
            else:
                logging.info("host_subject not present")
        else:
            logging.info("can't get host_subject, because the host of the " +
                         "virtual machine is not defined.")

        if host_subject is '':
            logging.info("Got a empty host_subject. The hosts identity" +
                         " will not be validated.")
            host_subject = None

        self.config_spice['host_subject'] = host_subject

    def wait_until_unixdomainsocket_ready(self, socket, interval):
        # Wait until the socket file exists and is connected on the other side.
        # When this function returns, the socket is ready to be connected by a
        # client.
        while True:
            time.sleep(interval)
            if self.unix_socket_is_ready(socket):
                logging.debug("socket is ready.")
                break
            logging.debug("socket not ready, trying again...")

    def unix_socket_is_ready(self, socket):
        # Returns True iff a server process is bound to the
        # unix domain socket.
        #
        # Unfortunately, there is no efficient way to tell
        # if a process is bound to a socket, so we simply ask the
        # proc filesystem for it.
        #
        # Bash example with grep:
        #
        # $ grep /tmp/adsy-rhev-tools-spice-control-socket /proc/net/unix
        # f4f5e800: 00000002 [...] /tmp/adsy-rhev-tools-spice-control-socket
        #
        # Empty output        ===> remote-viewer is not ready
        # At least one line   ===> remote-viewer is ready

        with open('/proc/net/unix', 'r') as f:
            for line in f:
                if re.search(socket, line):
                    return True
        return False

    def execute_spice_client_program(self):
        # Starts the spice-client program in a subprocess.
        # Talks to the client though a unix-dommain-socket.
        # waits for the termination of the spice client.
        self.last_exception_info = None

        spice_command = shlex.split(self.config_spice['spice_client_command'])
        socket = self.config_spice['socket']
        logging.debug("using spice socket: %s", socket)
        os.environ['SPICE_XPI_SOCKET'] = socket
        process = subprocess.Popen(spice_command)

        # After starting the spice-client program, we have to give it
        # some time to create and bind to the unix domain socket.
        # Previously, time.sleep(1), was used to accomplish this.
        # This works fine on fast hardware, however, it is racy
        # when combining slow hardware combined with a slow startup of the
        # spice-client program.

        # Wait until the unix domain socket is ready...
        self.wait_until_unixdomainsocket_ready(socket, 0.5)

        spice_xpi_controller.connect(socket_filename=socket,
                                     **self.config_spice)

        returncode = process.wait()

        if returncode is 0:
            # TRANSLATE:
            # "Disconnected successfully."
            raise RetryException("Die Spice-Verbindung wurde ordnungsgemäss " +
                                 "beendet.")

        # TRANSLATE:
        # "The spice connection terminated abnormally."
        raise SpiceClientExitedAbnormallyException(
            "Die Spice-Verbindung wurde unsachgemäss beendet"
        )

    def parse_arguments(self):
        # Commandline argument parsing
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', dest='configfile', required=True,
                            type=file, help='Path to config file')
        self.args = parser.parse_args()

    def read_config_file(self):
        # reads the configuration file and applies default values.
        self.config_parser = ConfigParser.SafeConfigParser(allow_no_value=True)
        self.config_parser.readfp(self.args.configfile)
        self.config_file_location = self.args.configfile.name

        defaults_general = dict(
            shutdown_command=None, reboot_command=None,
        )

        self.config_general = self.applyconfigdefaults(
            self.config_parser.items('general', raw=True), defaults_general)
        defaults_connect = dict(ca_file=None, insecure=False, filter=False)

        self.config_connect = self.applyconfigdefaults(
            self.config_parser.items('connect', raw=True), defaults_connect)

        ca_file = os.path.expanduser(self.config_connect['ca_file'])

        if not os.path.isabs(ca_file):
            config_file_dir = os.path.dirname(self.config_file_location)
            ca_file = os.path.join(config_file_dir, ca_file)

        os.stat(ca_file)
        self.config_connect['ca_file'] = ca_file

    # Called while program waits for a dhcp lease
    # Shall display a message to user, like "waiting for network..."
    def notify_waiting_for_dhcplease(self):
        logging.info("notify_waiting_for_dhcplease")
        cmd = self.config_general['notify_cmd_waiting_for_dhcplease']
        subprocess.call(cmd, shell=True)

    # Called while program waits for DB connection
    # Shall display a message to user, like "connecting to database..."
    def notify_waiting_for_db_connection(self):
        logging.info("notify_waiting_for_db_connection")
        cmd = self.config_general['notify_cmd_waiting_for_db_connection']
        subprocess.call(cmd, shell=True)

    # Called while a vm is launching...
    # Shall display a message to user, like "launching vm <vm>..."
    def notify_waiting_for_vm_launch(self):
        logging.info("notify_waiting_for_vmlaunch")
        cmd = self.config_general['notify_cmd_waiting_for_vm_launch']
        subprocess.call(cmd, shell=True)

    def adjust_logging(self):
        # reads the logging configuration file and passes it
        # to the logging library

        # first, tilde expand the path.
        # then, if the path is relative, interpret it as a
        # relative to the main configuration file.
        logging_config_file = os.path.expanduser(
            self.config_general['log_config_file'])

        if not os.path.isabs(logging_config_file):
            config_file_dir = os.path.dirname(self.config_file_location)
            logging_config_file = os.path.join(config_file_dir,
                                               logging_config_file)

        logging.debug("loading the logging config file located at %s...",
                      logging_config_file)
        os.stat(logging_config_file)
        logging.config.fileConfig(logging_config_file,
                                  disable_existing_loggers=False)

        # Now we are able to log the configuration information...
        logging.debug("config_general = %s", self.config_general)
        logging.debug("config_connect = %s", self.config_connect)

    def read_spice_config(self):
        # reads the spice configuration.
        # First, the local configuration is read and defauls are applied.
        # Then, query RHEV for configuration tags.
        # Those tags are always overriding local configuration.
        # Only tags that are assigned to the REST-user (configured in section
        # [connect] in the configuration file) are considered (for
        # efficeny reasons)

        defaults_spice = dict(
            socket='/tmp/spice_controll_socket',
            spice_client_command='/usr/bin/remote-viewer --spice-controller',
            secure_channels=None,
            disable_channels=None,
            tls_ciphers=None,
            window_title='Adfinis SyGroup AG VDI Solution',
            hotkeys='toggle-fullscreen=shift+f11,release-cursor=shift+f12',
            disable_effects=None,
            ctrl_alt_delete=True,
            enable_usb=True,
            usb_autoshare=True,
            usb_filter=None,
        )

        self.config_spice_local = self.applyconfigdefaults(
            self.config_parser.items('spice', raw=True), defaults_spice)
        logging.debug("Spice configuration (local): %s",
                      self.config_spice_local)

        logging.debug("getting configuration from RHEV-Tags...")

        config_tags_user_query = self.config_general['config_tags_user_query']
        query = "usrname=%s" % config_tags_user_query
        users = self.api.users.list(query=query)
        user = users[0]
        tags = user.tags.list()

        self.config_spice_tags = {}
        for tag in tags:
            match = re.match("config_thinclient_spice_(.+)", tag.name)
            if match:
                key = match.group(1)
                rest_id = tag.id
                tag = self.api.tags.get(id=rest_id)
                value = tag.description

                if value is not None and not re.match("\s*\Z", value):
                    logging.debug("Config via rhev-tag: %s = %s", key, value)
                    self.config_spice_tags[key] = value

        # RHEV-Tags (if present) are always overriding the local configuration
        self.config_spice = copy.copy(self.config_spice_local)
        for key in self.config_spice_tags.keys():
            self.config_spice[key] = self.config_spice_tags[key]

        # spice_ca_file is tilde expanded and, if it is a relative path,
        # interpreted as a path relative to the main configuration file.
        spice_ca_file = os.path.expanduser(self.config_spice['spice_ca_file'])

        if not os.path.isabs(spice_ca_file):
            config_file_dir = os.path.dirname(self.config_file_location)
            spice_ca_file = os.path.join(config_file_dir, spice_ca_file)

        os.stat(spice_ca_file)
        self.config_spice['spice_ca_file'] = spice_ca_file

    def connect_to_rest_api(self):
        # Connect to to the REST-API of RHEV.
        # Connection information (url, username/password, ...) is taken from
        # the section [connect] in the configuration file

        if self.api is not None:
            try:
                self.api.disconnect()
            except Exception as ex:
                logging.debug("Disconnecting from RHEV-REST-API: " +
                              "Silently dropped Exception: " + str(ex))

        for i in range(1, 5 + 1):
            try:
                logging.info(
                    "connecting to REST-API... (iteration {})".format(i)
                )
                self.api = ovirtsdk.api.API(**self.config_connect)
                logging.info("connecting to REST-API: successfull")
                return
            except Exception as ex:
                logging.info(
                    "connecting to REST-API... failed. "
                    "Error: `{}', iteration: {}".format(ex, i)
                )

                # No notifications on first try..
                if i > 1:
                    self.notify_waiting_for_dhcplease()

                time.sleep(2)
                continue

            logging.exception(ex)
            logging.error("Connecting to REST-API: giving up.")

            # TRANSLATE:
            # "Failed to connect to API.\n"
            # "Please check the network connection and try again."
            raise FailedToConnectToRestAPIException(
                "Es konnte keine API-Verbindung hergestellt werden.\n"
                "Bitte Netzwerk überprüfen und evt. erneut probieren."
            )

    def collect_debug_information(self):
        # collects debug information to be shown in the support window.
        result = ""

        envvariables = filter(
            lambda x: re.match('^CONNECT_SPICE_CLIENT_.*', x),
            os.environ.keys()
        )

        if len(envvariables) > 0:
            result += (
                "===========================================================\n"
                "    Version\n"
                "===========================================================\n"
            )
            for envvariable in envvariables:
                if envvariable in os.environ:
                    value = os.environ[envvariable]
                else:
                    value = "(undef)"
                result += "%s=%s\n" % (envvariable, value)

            result += "\n\n"

        with open("/proc/self/cmdline", 'r') as f:
            self_process_cmdline = f.read()

        self_process_cmdline = "\n".join(
            textwrap.wrap(self_process_cmdline.replace('\0', ' '), 60))

        # TRANSLATE:
        # "Last connection"
        result += (
            "===========================================================\n"
            "    letzte Verbindung\n"
            "===========================================================\n"
        )

        # TRANSLATE:
        # "Assigned VM(s): "
        # "Spice server: "
        # "Tags: "
        # "Program command line: "
        result += "Zugewiesene VM(s): " + str(self.last_vm_names) + "\n"
        result += "Spice-Server: " + self.last_spice_server + "\n"
        result += "Tags: " + str(self.last_vm_tags) + "\n"
        result += "Programmaufruf: " + self_process_cmdline + "\n"
        result += (
            "SysUUIDs: " +
            str(find_thinclient_identifier.get_dmidecode_sysuuid()) +
            "\n"
        )

        result += "\n\n"

        if self.last_exception_info is not None:
            # TRANSLATE:
            # "Last Exception"
            result += (
                "===========================================================\n"
                "    letzte Exception\n"
                "===========================================================\n"
            )
            result += "ERROR: " + str(self.last_exception_info[1]) + "\n"
            result += "".join(
                traceback.format_exception(*self.last_exception_info))
            result += "\n\n"

        cmds = ["date", "uname -a", "/sbin/ifconfig -a",
                "/sbin/ip route list", "/usr/bin/xrandr"]

        for cmd in cmds:
            result += (
                "===========================================================\n"
                "    " + cmd + "\n"
                "===========================================================\n"
            )
            try:
                cmdlist = shlex.split(cmd)
                output = subprocess.check_output(cmdlist, shell=False)
                result += output + "\n"
            except Exception as ex:
                logging.exception(ex)
                result += ("(Failed to execute this command, see logfile " +
                           "for details.)\n\n")

        # result = "\n".join(textwrap.wrap(result,60))
        return result

    def show_support_gui(self, oldexception):
        # Shows a support message from config: "support_message_file"
        # Also shows alot of debug information.

        support_message_file = os.path.expanduser(
            self.config_general['support_message_file'])

        if not os.path.isabs(support_message_file):
            config_file_dir = os.path.dirname(self.config_file_location)
            support_message_file = os.path.join(config_file_dir,
                                                support_message_file)

        logging.debug("loading the support message file located at %s...",
                      support_message_file)
        os.stat(support_message_file)
        with open(support_message_file, 'r') as f:
            support_message = f.read()

        cmd = self.config_general['dialog_command_support']
        cmdlist = shlex.split(cmd)
        message = self.collect_debug_information()

        message = support_message + message
        logging.debug("support_command: %s", cmdlist + [message])
        subprocess.call(cmdlist + [message], shell=False)
        self.raise_again = oldexception

    def raise_exception_again_in_main_action_sequence(self):
        # Raise the exception 'raise_again'.
        # This is needed, so that after displaying the support gui,
        # the same error message as before is shown again.
        if self.raise_again is not None:
            ex = self.raise_again
            self.raise_again = None
            raise ex

    def wait_for_dhcp_lease(self):
        logging.info("waiting for dhcp lease file...")
        for iteration in range(1, 5 + 1):
            leasefiles = find_thinclient_identifier.find_dhclient_leasefiles()
            if len(leasefiles) > 0:
                logging.info("waiting for dhcp lease file... done")
                return
            self.notify_waiting_for_dhcplease()
            time.sleep(4)

        # TRANSLATE:
        # "Network error. Please contact the system administrator."
        raise NetworkError(
            "Netzwerk Fehler: Bitte kontaktieren Sie den System Administrator"
        )

    def main_action_sequence(self):
        self.raise_exception_again_in_main_action_sequence()

        self.parse_arguments()

        self.read_config_file()

        self.adjust_logging()

        self.wait_for_dhcp_lease()

        self.connect_to_rest_api()

        self.read_spice_config()

        self.get_vm_from_db()

        self.prepare_vm()

        self.get_vm_ticket()

        self.execute_spice_client_program()

    def shutdown_vm_action_sequence(self):
        try:
            self.parse_arguments()

            self.read_config_file()

            self.adjust_logging()

            logging.info("Auto-Shutdown program started...")

            self.wait_for_dhcp_lease()

            self.connect_to_rest_api()

            self.get_vm_from_db()

            if self.vm is not None and self.shutdown_vm:
                logging.info("Auto-Shutdown VM `{0}'".format(self.vm_name))
                self.vm.shutdown()
            else:
                logging.info("No Auto-Shutdown.")
        except Exception as ex:
            logging.info("Auto-Shutdown failed: `{0}'".format(ex))

    def __init__(self):
        self.api = None
        self.vm = None
        self.last_vm_names = []
        self.last_spice_server = "-"
        self.last_vm_tags = []
        self.last_exception_info = None
        self.raise_again = None

    def main(self):
        self.error_handling_loop()

    def error_handling_loop(self):
        # Main loop:
        # * runs the main action sequence
        # * dispatches to the appropriate error handler if necessary.

        while True:
            try:
                self.main_action_sequence()
            except RetryException as ex:
                self.handleRetryException(ex)
            except NoRetryException as ex:
                self.handleNoRetryException(ex)
            except Exception as ex:
                self.last_exception_info = sys.exc_info()
                self.handleUnknownException(ex)
            finally:
                logging.info("Restarting main-loop....")

    def handleRetryException(self, ex):
        # Shows a small graphical userinterface with the error message
        # The user can choose between
        # * retry
        # * shutdown thinclient
        # * reboot thinclient
        try:
            cmd = self.config_general['dialog_command_with_retry']
            cmdlist = shlex.split(cmd)
            message = ex.message
            returncode = subprocess.call(cmdlist + [message])
            if returncode == 0:
                return
            if returncode == 1:
                return
            if returncode == 101:
                return
            if returncode == 102:
                self.shutdown()
            if returncode == 103:
                self.reboot()
            if returncode == 104:
                self.show_support_gui(ex)
            else:
                logging.error("unhandled returncode of " +
                              "dialog_command_with_retry: %i." % returncode)
        except Exception as ex:
            self.handleExceptionHandlingError(ex)

    def handleNoRetryException(self, ex):
        # Shows a small graphical userinterface with the error message
        # The user can choose between
        # * shutdown thinclient
        # * reboot thinclient
        try:
            cmd = self.config_general['dialog_command_without_retry']
            cmdlist = shlex.split(cmd)
            returncode = subprocess.call(cmdlist + [ex.message])
            if returncode == 102:
                self.shutdown()
            if returncode == 103:
                self.reboot()

            else:
                logging.error("unhandled returncode of " +
                              "dialog_command_without_retry: %i. Exiting " +
                              "ungracefully with exit code -1." % returncode)
            sys.exit(-1)
        except Exception as ex:
            self.handleExceptionHandlingError(ex)

    def handleUnknownException(self, ex):
        # handles Exceptions that don't have a special error handling designed.
        # The end-user can't see the exception message.
        # The exception message is logged.
        logging.exception(ex)

        # TRANSLATE:
        # "A general error occured."
        # "Please contact the system administrator."
        masking_exception = MaskingException(
            "Ein allgemeiner Fehler ist " +
            "aufgetreten.\n\n" +
            "Bitte kontaktieren sie den System Administrator."
        )
        self.handleRetryException(masking_exception)

    def handleExceptionHandlingError(self, ex):
        # If an error occours during exception handling, we terminate
        # the whole program.

        logging.exception(ex)
        logging.error("Serious error in error handling code: " + str(ex))
        sys.exit(-1)

    def shutdown(self):
        # shuts the thinclient down, e.g. issues
        # sudo shutdown -h now (or something similar)
        try:
            cmd = self.config_general['shutdown_command']
            cmdlist = shlex.split(cmd)
            logging.debug("shutdown-command: %s", cmdlist)
            subprocess.call(cmdlist, shell=False)
            # TRANSLATE:
            # "Shutting down system..."
            raise ShutdownInProgress("Das System wird heruntergefahren...")
        except Exception as ex:
            self.handleExceptionHandlingError(ex)

    def reboot(self):
        # reboots the thinclient, e.g. issues
        # sudo shutdown -r now (or somethin similar)
        try:
            cmd = self.config_general['reboot_command']
            cmdlist = shlex.split(cmd)
            logging.debug("reboot-command: %s", cmdlist)
            subprocess.call(cmdlist, shell=False)
            # TRANSLATE:
            # "Restarting system..."
            raise RebootInProgress("Das System wird neu gestartet...")
        except Exception as ex:
            self.handleExceptionHandlingError(ex)

    def applyconfigdefaults(self, config, defaults):
        result = copy.copy(defaults)
        for pair in config:
            result[pair[0]] = pair[1]

        return result


# Exception class hierarchies. Used to classify and categorize exceptions.
class RetryException(Exception):
    pass


class NoRetryException(Exception):
    pass


class MaskingException(RetryException):
    pass


class GetSpiceTicketFailedException(RetryException):
    pass


class SpiceClientExitedAbnormallyException(RetryException):
    pass


class ToManyVMsAssignedToThisThinclientException(RetryException):
    pass


class NotSpiceConsoleException(RetryException):
    pass


class FailedToConnectToDatabaseException(RetryException):
    pass


class FailedToConnectToRestAPIException(RetryException):
    pass


class AssertionFailedException(RetryException):
    pass


class ShutdownInProgress(RetryException):
    pass


class RebootInProgress(RetryException):
    pass


class NetworkError(RetryException):
    pass

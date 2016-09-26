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
import os
import time
import logging
import logging.config
import configobj
import sys
import argparse
import textwrap

# Project imports
import rhev
import utils
import constants


class RhevManager():

    def __init__(self, configuration_file):
        assert(configuration_file)

        self.config_file = configuration_file
        self.logger = None
        self.rhev_lib = None
        self.base_configuration = None

        self.read_base_configuration()
        self.initialize_logging()

        self.rhev_lib = rhev.rhev(self.base_configuration)

    @staticmethod
    def construct_from_cmdargs(description):
        epilog = textwrap.dedent('''
        The following config file locations are used, first match wins:
            * Command line argument
            * ~/.config/virtesk-vdi/virtesk-vm-rollout.conf
            * /etc/virtesk-vdi/virtesk-vm-rollout.conf
        ''')

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog, description=description)

        parser.add_argument(
            '--config',
            help="Absolute or relative path to configuration file."
        )

        parser.add_argument(
            'virtroom', help="virtual room to act on"
        )

        args = parser.parse_args()

        config_file = utils.get_valid_config_file(
            args.config
        )

        room = args.virtroom

        # Initialize RHEV manager
        rhev_manager = RhevManager(
            config_file
        )

        return rhev_manager, room

    def cleanup(self):
        self.rhev_lib.cleanup()

    def read_base_configuration(self):
        try:
            self.base_configuration = configobj.ConfigObj(
                self.config_file,
                file_error=True
            )
            self.base_configuration['general']['config_file'] = (
                self.config_file
            )
            logging.info('Successfully read base configuration')

        except (configobj.ConfigObjError, IOError), e:
            raise Exception(
                "Could not read '{0}': {1}".format(
                    os.path.abspath(self.config_file), e
                )
            )

    def initialize_logging(self):
        assert(self.config_file)

        try:
            config_file_path, config_file_name = os.path.split(
                self.config_file
            )

            log_config_file = os.path.join(
                config_file_path,
                self.base_configuration['logging']['config_file']
            )

            log_file = self.base_configuration['logging']['log_file']

            logging.config.fileConfig(log_config_file, defaults={
                'log_file':     log_file,
                'file_mode':    'a'
            })

            self.logger = logging.getLogger(__name__)
            self.base_configuration['logging']['config_file'] = log_config_file

            self.logger.debug('Successfully initialized logger')
            self.logger.debug(
                "Using configuration file '{0}'".format(log_config_file)
            )

        except Exception as ex:
            logging.error(
                "Failed to initialize logging. "
                "Logfile: `{0}'. Error details: `{1}'".format(log_file, ex)
            )
            sys.exit(-1)

    def cleanup_classroom(self, classroom):
        if not classroom:
            raise Exception('No classrom given')

        self.logger.info("cleaning up classroom '{0}'".format(classroom))

        try:
            # Get VMs for given classroom
            self.logger.debug(
                "Getting VMs for classroom '{0}'".format(classroom)
            )
            vms_for_classroom = self.rhev_lib.get_vms_for_classroom(classroom)

            if vms_for_classroom:
                # Teardown of VMs
                for vm in vms_for_classroom:
                    self.rhev_lib.delete_vm(vm)

            self.logger.info(
                "Successfully cleaned up classroom '{0}'".format(classroom)
            )

        except Exception, e:
            raise Exception(
                "Cleaning up classroom '{0}' failed: {1}".format(classroom, e)
            )

    # reset vms to snapshot
    def reset_classroom(self, classroom):
        if not classroom:
            raise Exception('No classroom given')

        self.logger.info(
            "Starting to reset classroom '{0}'".format(classroom)
        )

        # Get VMs for given classroom
        vms_for_classroom = self.rhev_lib.get_vms_for_classroom(
            classroom)

        for vm in vms_for_classroom:
            self.rhev_lib.reset_vm_to_snapshot(vm)

    def analyze_config_of_classroom(self, classroom):
        self.logger.info(
            "Analyzing configuration of classroom {0}".format(classroom)
        )

        # Get VMs for given classroom
        vms_for_classroom = self.rhev_lib.get_vms_for_classroom(
            classroom)

        for vmconfig in vms_for_classroom:
            self.logger.debug(str(vmconfig))

        if self.rhev_lib.check_if_vms_exist(vms_for_classroom):
            self.logger.info(
                "Some VMs already exist. Please delete them before rollout"
            )
            self.rhev_lib.analyze_snapshots(vms_for_classroom)

    def start_all_vms_in_room(self, classroom):
        self.logger.info("Starting VMs in Room... {0}".format(classroom))

        # Get VMs for given classroom
        vms_for_classroom = self.rhev_lib.get_vms_for_classroom(
            classroom
        )

        for vmconfig in vms_for_classroom:
            self.logger.debug(str(vmconfig))

        for vmconfig in vms_for_classroom:
            self.rhev_lib.start_vm_if_possible(vmconfig)

    def shutdown_all_vms_in_room(self, classroom):
        self.logger.info("Shutting down VMs in Room... {0}".format(classroom))

        # Get VMs for given classroom
        vms_for_classroom = self.rhev_lib.get_vms_for_classroom(
            classroom)

        for vmconfig in vms_for_classroom:
            self.logger.debug(str(vmconfig))

        for vmconfig in vms_for_classroom:
            self.rhev_lib.shutdown_vm_if_possible(vmconfig)

    def rollout_classroom(self, classroom):
        if not classroom:
            raise Exception('No classroom given')

        try:
            with utils.tempdir("virtesk-virtroom-rollout-") as temp_dir:
                self.logger.info(
                    "Starting to roll out classroom '{0}'".format(classroom)
                )

                # Get VMs for given classroom
                vms_for_classroom = self.rhev_lib.get_vms_for_classroom(
                    classroom)

                for vmconfig in vms_for_classroom:
                    self.logger.debug(str(vmconfig))

                # Make sure the VMs don't exist (avoiding conflicts)
                if self.rhev_lib.check_if_vms_exist(vms_for_classroom):
                    self.logger.error(
                        "Some VMs already exist. Please delete them first"
                    )
                    sys.exit(-1)

                # Create (template) VMs
                for vm in vms_for_classroom:
                    self.rhev_lib.create_standalone_vm(vm)
                    # sys.exit(0)
                    time.sleep(constants.VM_CREATION_SLEEP_TIME)

                # Wait for VMs to shut donw
                self.rhev_lib.wait_for_vms_down(
                    vmconfigs=vms_for_classroom,
                    formatstring="VM {0} successfully created"
                )

                # Add NIC and initiate sysprep
                for vm in vms_for_classroom:
                    self.rhev_lib.add_vm_nic(vm)
                    self.rhev_lib.sysprep_vm(vm, temp_dir)
                    self.logger.info('Waiting for sysprep to finish')
                    time.sleep(constants.VM_SLEEP_TIME)

                # Wait for VMs to shut down
                msg_formatstring = \
                    "VM {0} has been stopped after running Autounattend.xml."

                self.rhev_lib.wait_for_vms_down(
                    vmconfigs=vms_for_classroom,
                    formatstring=msg_formatstring
                )

                # Postprocess VMs:
                # Eject ISOs, set statless and add (user-) group.
                # Create a snapshot of every VM.
                for vm in vms_for_classroom:
                    self.rhev_lib.postprocess_vm(vm)

                # Wait for all VM snapshots to become ready.
                self.rhev_lib.wait_for_vm_snapshots_ready(vms_for_classroom)

                # Start VMs
                for vm in vms_for_classroom:
                    self.rhev_lib.start_vm_after_rollout(vm)

                self.logger.info(
                    "Finished rolling out classroom '{0}' successfully".format(
                        classroom
                    )
                )

        except Exception, e:
            logging.exception(e)
            raise Exception(
                "Rolling out classroom '{0}' failed: {1}".format(classroom, e)
            )

        return True

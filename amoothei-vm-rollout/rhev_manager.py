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
import os
import time
import logging
import logging.config
import configobj
import sys

# Project imports
# import singletonmixin
import rhev
import constants
import mytemporary_directory as tmpdir


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

            log_file = os.path.join(
                os.getcwd(),
                self.base_configuration['logging']['log_file']
            )

            logging.config.fileConfig(log_config_file, defaults={
                'log_file':     log_file,
                'file_mode':    'w'
            })

            self.logger = logging.getLogger(__name__)
            self.base_configuration['logging']['config_file'] = log_config_file

            self.logger.debug('Successfully initialized logger')
            self.logger.debug(
                "Using configuration file '{0}'".format(log_config_file)
            )

        except Exception as ex:
            raise Exception(
                'Unexpected error while initialize logging: {0}'.format(ex)
            )

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
    def reset_classroom(self,classroom):
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

    def analyze_config_of_classroom(self,classroom):
        self.logger.info("Analyzing configuration of classroom {0}".format(classroom))

        # Get VMs for given classroom
        vms_for_classroom = self.rhev_lib.get_vms_for_classroom(
                    classroom)

        for vmconfig in vms_for_classroom:
            self.logger.debug(str(vmconfig))

        if self.rhev_lib.check_if_vms_exist(vms_for_classroom):
            self.logger.info("Some VMs already exist. Please delete them before rollout")
            self.rhev_lib.analyze_snapshots(vms_for_classroom)



    def rollout_classroom(self, classroom):
        if not classroom:
            raise Exception('No classroom given')

        try:
            with tmpdir.TemporaryDirectory("vdi_vm_rollout-") as temp_dir:
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
                    self.logger.error("Some VMs already exist. Please delete them first")
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

                # Eject ISOs, set statless and add (user-) group.
                # Create a snapshot of every VM.
                # vm_snapshots = []
                for vm in vms_for_classroom:
                    self.rhev_lib.postprocess_vm(vm)

                    # creating the snapshot must be the final task in this
                    # loop.
                    # description = ("ADSY_RHEV_TOOLS, STOPPED, FIXIP={0}/{1}, " +
                    #               "initial snapshot after vm creation using " +
                    #               "adsy_rhev_tools succeded.").format(
                    # vm['ip'], vm['netmask_as_suffix'])

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

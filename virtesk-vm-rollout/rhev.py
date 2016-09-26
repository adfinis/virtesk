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

# System Imports
import os
import pprint
import time
import copy
import subprocess
import re
import string
import logging
import logging.config
import sys

# Project imports
import constants
import ovirtsdk.api
import ovirtsdk.xml
import mako             # http://www.makotemplates.org/
import mako.exceptions
import mako.template


class rhev:

    def __init__(self, base_configuration):
        assert(base_configuration)

        self.api = None
        self.connect_configuration = {}
        self.ISO_DOMAIN = None
        self.VDI_CLUSTER = None
        self.scripttime = time.localtime()
        self.scripttime_string = "%i-%02i-%02i-%02i%02i" % (
            self.scripttime.tm_year,
            self.scripttime.tm_mon,
            self.scripttime.tm_mday,
            self.scripttime.tm_hour,
            self.scripttime.tm_min
        )
        self.base_configuration = base_configuration
        self.logger = None

        try:
            self.initialize_logging()
            self.read_connect_configuration()
            self.connect(self.connect_configuration)

            self.logger.info(
                "Connected to '{0}' successfully!".format(
                    self.api.get_product_info().name
                )
            )
        except Exception as ex:
            logging.error(
                "An unknown error occoured while setting things up. "
                "This shouldn't happen. Traceback will follow."
            )
            logging.exception(ex)

            sys.exit(-1)

    def initialize_logging(self):
        try:
            self.logger = logging.getLogger(__name__)

        except Exception as ex:
            logging.error(
                "Failed to initialize logging. "
                "Error details: `{}'".format(str(ex))
            )
            sys.exit(-1)

    def get_configfile_absolutepath(self, filename):
        path = os.path.expanduser(filename)

        if not os.path.isabs(path):
            path = os.path.join(self.config_file_dir, path)

        # Fail early:
        # Check if path exists? raise an exception otherwise.
        os.stat(path)

        return path

    def read_connect_configuration(self, section=None):
        config = self.connect_configuration

        self.config_file_dir = os.path.dirname(
            self.base_configuration['general']['config_file']
        )

        if section is None:
            section = self.base_configuration['general']['connect']

        config['url'] = section['url']

        # Get CA file path
        config['ca_file'] = self.get_configfile_absolutepath(
            section['ca_file']
        )

        config['username'] = section['username']
        config['password'] = section['password']

        optional_string_params = ['key_file', 'cert_file']
        optional_int_params = ['timeout', 'session_timeout']
        optional_boolean_params = [
            'persistent_auth', 'renew_session', 'insecure',
            'validate_cert_chain', 'filter', 'debug'
        ]

        for key in optional_string_params:
            if key in section:
                config[key] = section[key]

        for key in optional_int_params:
            if key in section:
                try:
                    config[key] = section.as_int(key)
                except Exception:
                    logging.error(
                        "Config error: {0}={1}: cannot convert {1} to int!"
                        .format(key, section[key])
                    )
                    sys.exit(-1)

        for key in optional_boolean_params:
            if key in section:
                try:
                    config[key] = section.as_bool(key)
                except Exception:
                    logging.error(
                        "Config error: {0}={1}: cannot convert {1} to boolean!"
                        .format(key, section[key])
                    )
                    sys.exit(-1)

    def dumpconnectinfo(self, section=None):
        self.read_connect_configuration(section=section)

        self.logger.info("Connect configuration settings:")
        self.logger.info(pprint.pformat(self.connect_configuration))

    def get_vms_for_classroom(self, classroom):
        result = []

        self.logger.debug(
            "Getting VMs for classroom '{0}'".format(classroom)
        )

        if not classroom:
            raise Exception('No classroom given')

        section_name = 'room ' + classroom
        if section_name in self.base_configuration.keys():
            # Get current class room
            section = self.base_configuration[section_name]

            subsections = section.keys()

            # Build list with VMs
            for subsection in subsections:
                if isinstance(section[subsection], dict):
                    result += self.build_vm_list_for_key(
                        classroom,
                        subsection,
                        section
                    )
                else:
                    self.logger.warn(
                        "Config section `{0}': skipping "
                        "unparseable config item: '{1}={2}'.".format(
                            section_name,
                            subsection,
                            section[subsection]
                        )
                    )

        else:
            raise Exception("Classroom '%s' was not found" % classroom)

        if len(result) <= 0:
            raise Exception("Classroom '%s' has no VMs" % classroom)

        self.logger.debug(
            "Got {0} VMs for classroom '{1}'".format(len(result), classroom)
        )

        return result

    def build_vm_list_for_key(self, roomname, key, configuration_array):
        try:
            vm_list = []

            vm_ids = eval(configuration_array[key]['ids'])

            # To how many digits shall we pad the vm_id?
            # answer: vm_id_digits.
            if len(vm_ids) > 0:
                max_vm_id = max([int(x) for x in vm_ids])
                vm_id_digits = len("%i" % max_vm_id)

                # we pad always to at least 2 digits.
                if vm_id_digits < 2:
                    vm_id_digits = 2

            for vm_id in vm_ids:
                current_id = int(vm_id)

                current_id_padded = (
                    "%0" + str(vm_id_digits) + "i"
                ) % current_id

                current_vm = configuration_array[key]

                ip_address_suffix = int(
                    current_vm['ip_addresses_suffix']
                ) + current_id - 1

                rhev_vm_name = string.Template(
                    current_vm['names']
                )

                rhev_vm_name = rhev_vm_name.safe_substitute(
                    roomname=roomname,
                    id=current_id_padded
                )

                computerName = rhev_vm_name

                if len(rhev_vm_name) > 15:
                    msg = "Name of VM {} greater than 15 characters long. "
                    "This isn't supported by RHEV and Windows.".format(
                        rhev_vm_name
                    )
                    raise Exception(msg)

                # validate and compile regex
                reset_to_snapshot_regex_string = current_vm[
                    'reset_to_snapshot_regex'
                ]
                try:
                    reset_to_snapshot_regex = re.compile(
                        reset_to_snapshot_regex_string
                    )
                except re.error:
                    logging.error(
                        "Invalid regex `{0}={1}' configured in section `{2}'. "
                        "Exiting...".format(
                            'reset_to_snapshot_regex',
                            reset_to_snapshot_regex_string,
                            key
                        )
                    )
                    sys.exit(-1)

                vm_config = dict(
                    rhev_vm_name=rhev_vm_name,
                    memory=eval(current_vm['memory']),
                    ip=string.Template(
                        current_vm['ip_addresses']
                    ).safe_substitute(
                        suffix=ip_address_suffix
                    ),
                    netmask_as_suffix=current_vm['netmask_suffix'],
                    ComputerName=computerName,
                    network_name=current_vm['network_name'],
                    template=current_vm['template_name'],
                    description=current_vm['description'],
                    cluster=current_vm['cluster'],
                    default_gw=current_vm['default_gateway'],
                    autounattend_templatefile=self.get_configfile_absolutepath(
                        current_vm['autounattend_templatefile']),
                    scripttime=self.scripttime_string,
                    tc_user=current_vm['tc_user'],
                    workaround_os=current_vm['workaround_os'],
                    workaround_timezone=current_vm['workaround_timezone'],
                    os=current_vm['os'],
                    timezone=current_vm['timezone'],
                    usb_enabled=current_vm['usb'].strip() == 'enabled',
                    snapshot_description=current_vm['snapshot_description'],
                    reset_to_snapshot_regex=reset_to_snapshot_regex,
                    rollout_startvm=(
                        current_vm['rollout_startvm'].strip() == 'True'
                    ),
                    reset_startvm = current_vm['reset_startvm'].strip(),
                    stateless = current_vm['stateless'].strip() == 'True'
                )

                vm_list.append(vm_config)
        except KeyError as ex:
            logging.error(
                "Configuration error, room `{0}', subsection `{1}': "
                "Key `{2}' is mandatory.".format(roomname, key, str(ex))
            )
            sys.exit(-1)
        return vm_list

    def connect(self, config):
        config_copy = copy.copy(config)
        config_copy['password'] = "XXXXXXXXXXXXXXX"

        logging.debug(
            "Trying to connect to REST API using the "
            "following configuration: {0}..."
            .format(str(config_copy))
        )

        try:
            self.api = ovirtsdk.api.API(**config)

            logging.info(
                "Connected to REST-API successfully."
            )
        except Exception as ex:
            logging.error(
                "Failed to connect to REST-API. "
                "Error message: `{0}'. Configuration: {1}. "
                "Will print a Traceback now."
                .format(str(ex), str(config))
            )
            logging.exception(ex)
            sys.exit(-1)

    def create_standalone_vm(self, vmconfig):
        vm_name = vmconfig['rhev_vm_name']
        vm_cluster = self.api.clusters.get(name=vmconfig['cluster'])
        vm_template = self.api.templates.get(name=vmconfig['template'])
        assert vm_template is not None, "assert not vm_template is None"
        vm_os = ovirtsdk.xml.params.OperatingSystem(
            boot=[ovirtsdk.xml.params.Boot(dev="hd")],
            type_=vmconfig['workaround_os']
        )
        vm_params = ovirtsdk.xml.params.VM(
            name=vm_name,
            memory=vmconfig['memory'],
            cluster=vm_cluster,
            template=vm_template,
            os=vm_os,
            timezone=vmconfig['workaround_timezone'],
            description=vmconfig['description']
        )
        vm = None

        try:
            self.logger.debug(
                "Creating standalone VM '{0}'".format(
                    vm_name
                )
            )
            vm = self.api.vms.add(vm=vm_params, expect="201-created")
            vmconfig['vm'] = vm
            self.logger.debug(
                "Status of vm '{0}': {1}".format(
                    vm_name, vm.status.state
                )
            )

            return vm

        except Exception as ex:
            raise Exception("Adding virtual machine '{0}' failed: {1}".format(
                vm_name, ex
            ))

    def enable_usb(self, vmconfig):
        # enables usb for an existing VM.

        # enabling usb cannot be done while creating the VM, because that
        # might trigger a RHEV-bug [0].
        # [0] https://project.adfinis-sygroup.ch/issues/6764
        if vmconfig['usb_enabled']:
            vm_usb = ovirtsdk.xml.params.Usb(enabled=True, type_='native')
            vmconfig['vm'].set_usb(vm_usb)

    def wait_for_vms_down(
            self,
            vmconfigs=None,
            vm_names=None,
            formatstring=None
    ):
        if vm_names is None:
            pending_vms = [vmconfig['rhev_vm_name'] for vmconfig in vmconfigs]
        else:
            pending_vms = copy.copy(vm_names)
        while len(pending_vms) > 0:
            for vm_name in pending_vms:
                if self.api.vms.get(vm_name).status.state == 'down':
                    pending_vms.remove(vm_name)
                    if formatstring is not None:
                        self.logger.debug(formatstring.format(vm_name))
            time.sleep(5)

    def add_vm_nic(self, vmconfig):
        vm = vmconfig['vm']
        vm_name = vmconfig['rhev_vm_name']
        nic_name = "nic0"
        nic_interface = "virtio"
        nic_network_name = vmconfig['network_name']

        existing_nics = vm.nics.list()
        if len(existing_nics) > 0:
            self.logger.info(
                "Remove existing networks from VM {} ...".format(vm_name))
            for existing_nic in existing_nics:
                existing_nic.delete()
            vm.update()
            self.logger.info(
                "Remove existing networks from VM {} ... done".format(vm_name))

        self.logger.info("Adding network '%s' to VM '%s'" %
                         (nic_network_name, vm_name))

        try:
            nic_network = self.api.networks.get(name=nic_network_name)

            nic_params = ovirtsdk.xml.params.NIC(
                name=nic_name,
                interface=nic_interface,
                network=nic_network
            )

            nic = vm.nics.add(nic_params, expect="201-created")
            mac = nic.get_mac().get_address()
            vmconfig['mac'] = mac
            mac_win = (re.sub(":", "-", mac)).upper()
            vmconfig['MACwin'] = mac_win

            self.logger.info(
                "Network interface '{0}' ({1}) added to '{2}'".format(
                    nic.get_name(), mac, vm.get_name()
                ))

            self.logger.info(
                "Status: '{0}'".format(
                    self.api.vms.get(vm.get_name()).status.state
                ))

        except Exception as ex:
            raise Exception(
                "Adding network interface to '{0}' failed: {1}".format(
                    vm.get_name(), ex
                ))

    def attach_floppy(self, vmconfig):
        floppyname = vmconfig['floppyname']
        ovirt_worker_floppy_prefix = self.base_configuration[
            'general']['ovirt_worker_floppy_prefix']
        ovirt_worker_floppy_path = "{}/{}".format(
            ovirt_worker_floppy_prefix, floppyname)

        vm = vmconfig['vm']

        # save existing custom properties for restoring them later
        saved_cust_props = vm.get_custom_properties()
        vmconfig['saved_cust_props'] = saved_cust_props

        cust_prop = ovirtsdk.xml.params.CustomProperty(
            name="floppy", value=ovirt_worker_floppy_path)

        vm.set_custom_properties(
            ovirtsdk.xml.params.CustomProperties(custom_property=[cust_prop]))
        vm.update()

    def detach_and_cleanup_floppy(self, vmconfig):
        # Detaching floppy from VM Configuration
        vm = vmconfig['vm']

        # Restoring custom properties:
        # First, we set empty properties - this is necessary for the
        # corner case where the saved properties are empty.
        # Then we restore the saved properties.
        vm.set_custom_properties(ovirtsdk.xml.params.CustomProperties())
        vm.update()
        vm.set_custom_properties(vmconfig['saved_cust_props'])

        # Remove floppy image from SFTP server
        sftp_floppy_cleanup_cmd = self.base_configuration[
            'general']['sftp_floppy_cleanup_cmd']
        sftp_cmd = sftp_floppy_cleanup_cmd.format(vmconfig['floppyname'])
        logging.debug("executing sftp cleanup cmd: {}".format(sftp_cmd))
        subprocess.check_output(sftp_cmd, shell=True)

    def sysprep_vm(self, vmconfig, temp_dir):
        self.logger.info("Running sysprep for VM '%s'" %
                         vmconfig['rhev_vm_name'])
        self.create_floppy(vmconfig, temp_dir)
        self.upload_floppy(vmconfig)
        self.attach_floppy(vmconfig)

        self.start_vm(vmconfig)

    def start_vm(self, vmconfig):
        vm = vmconfig['vm']
        vm.start()

    def start_vm_if_possible(self, vmconfig):
        vmname = vmconfig['rhev_vm_name']

        vm = self.api.vms.get(vmname)
        if vm is None:
            logging.info(
                "Not starting VM {0}. "
                "Reason: VM not found.".format(vmname)
            )
        elif vm.status.state == 'up':
            logging.info(
                "Not starting VM {0}. "
                "Reason: VM is already running".format(vmname)
            )
        else:
            logging.info(
                "Starting VM {0}. "
                "Current VM state: `{1}'".format(vmname, vm.status.state)
            )
            try:
                vm.start()
            except Exception as ex:
                logging.error(
                    "Starting VM {0} failed. Reason: `{1}'.".format(vmname, ex)
                )

    def shutdown_vm_if_possible(self, vmconfig):
        vmname = vmconfig['rhev_vm_name']

        vm = self.api.vms.get(vmname)
        if vm is None:
            logging.info(
                "Not shutting down VM {0}. "
                "Reason: VM not found.".format(vmname)
            )
        elif vm.status.state == 'down':
            logging.info(
                "Not shutting down VM {0}. "
                "Reason: VM isn't running.".format(vmname)
            )
        else:
            logging.info(
                "Shutting down VM {0}. "
                "Current VM state: `{1}'".format(vmname, vm.status.state)
            )
            try:
                vm.shutdown()
            except Exception as ex:
                logging.error(
                    "Shutting down VM {0} failed. "
                    "Reason: `{1}'.".format(vmname, ex)
                )

    def postprocess_vm(self, vmconfig):
        # sync state from ovirt
        vmconfig['vm'] = self.api.vms.get(vmconfig['rhev_vm_name'])

        self.enable_usb(vmconfig)
        self.adjust_os_and_timezone(vmconfig)
        self.detach_and_cleanup_floppy(vmconfig)
        self.set_stateless(vmconfig)
        self.vm_adduser(vmconfig)

        # sync changes back to ovirt
        vmconfig['vm'].update()

        self.create_vm_snapshot(vmconfig)

    def start_vm_after_rollout(self, vmconfig):
        if vmconfig['rollout_startvm']:
            self.logger.debug(
                "starting VM {0} ...".format(vmconfig['rhev_vm_name'])
            )
            vmconfig['vm'].start()
            time.sleep(1)

    def adjust_os_and_timezone(self, vmconfig):
        vmconfig['vm'].set_timezone(vmconfig['timezone'])
        vmconfig['vm'].get_os().set_type(vmconfig['os'])

    def set_stateless(self, vmconfig):
        stateless = vmconfig['stateless']
        vmconfig['vm'].set_stateless(stateless)

    def upload_floppy(self, vmconfig):
        sftp_floppy_upload_cmd = self.base_configuration[
            'general']['sftp_floppy_upload_cmd']
        sftp_cmd = sftp_floppy_upload_cmd.format(
            vmconfig['floppypath'], vmconfig['floppyname'])
        logging.debug("executing cmd: {}".format(sftp_cmd))
        subprocess.check_output(sftp_cmd, shell=True)
        os.remove(vmconfig['floppypath'])

    def create_floppy(self, vmconfig, temp_dir):
        content = self.apply_unattend_xml_template(vmconfig)
        floppyname = "floppy-{}-{}.img".format(
            self.scripttime_string, vmconfig['rhev_vm_name'])
        floppypath = "{}/{}".format(temp_dir, floppyname)
        logging.debug("Zeroing floppy image file {}".format(floppypath))

        dd_cmd = "dd if=/dev/zero of={} bs=1440K count=1".format(floppypath)
        subprocess.check_call(dd_cmd, shell=True)
        logging.debug(
            "Creating msdos filesystem on floppy image {}".format(floppypath))
        subprocess.check_call("mkfs.msdos {}".format(floppypath), shell=True)
        sysprep_path = "{}/sysprep.inf".format(temp_dir)
        with open(sysprep_path, "w") as text_file:
            text_file.write(content)
        logging.debug(
            "Copy file into floppy image {} using mtools".format(floppypath))
        subprocess.check_call(
            "mcopy -i {} {} ::/".format(floppypath, sysprep_path), shell=True)
        logging.debug("Listing floppy image content of {}".format(floppypath))
        subprocess.check_call("mdir -i {} ::/".format(floppypath), shell=True)
        vmconfig['floppyname'] = floppyname
        vmconfig['floppypath'] = floppypath

    def apply_unattend_xml_template(self, vmconfig):
        try:
            t = mako.template.Template(
                filename=vmconfig['autounattend_templatefile']
            )
            result = t.render(**vmconfig)

            return result

        except:
            raise Exception(mako.exceptions.text_error_template().render())

    def delete_vm(self, vmconfig):
        if 'vm' in vmconfig:
            vm = vmconfig['vm']
        else:
            vm = self.api.vms.get(vmconfig['rhev_vm_name'])

        if vm is not None:
            vm_name = vm.get_name()
            self.force_stop_vm(vm_name)
            if not (vm.get_vmpool() is None):
                self.logger.info("Detaching VM '%s'" % vm_name)
                vm.detach()
            self.logger.info("Deleting VM '%s'" % vm_name)

            deletion_successfull = False
            for iteration in range(1, 5 + 1):
                try:
                    vm.delete()
                    deletion_successfull = True
                    break
                except:
                    self.logger.warn(
                        "Deleting VM {0} failed in iteration {1}... "
                        "trying again...".format(vm_name, iteration)
                    )
                    time.sleep(2)

            if not deletion_successfull:
                self.logger.warn("Deleting VM {0}: *last try*".format(vm_name))
                vm.delete()

            while not self.api.vms.get(vm_name) is None:
                time.sleep(1)

            self.logger.info("Successfully deleted VM {0}.".format(vm_name))

        else:
            self.logger.warn(
                "Tried to delete VM '{}' but it seems not to be on "
                "RHEV server".format(vmconfig['rhev_vm_name'])
            )

    def force_stop_vm(self, vm_name):
        # try 4 times to stop the VM
        for attempt in range(1, 5):
            vm = self.api.vms.get(vm_name)
            if vm.status.state == 'down':
                break

            try:
                vm.stop()
            except Exception as ex:
                logging.debug(
                    "Stopping VM {} failed. Hiding exception {}."
                    .format(vm_name, str(ex))
                )

        # last attempt, not hiding exceptions...
        vm = self.api.vms.get(vm_name)
        if vm.status.state == 'down':
            logging.debug("VM {} ist down.".format(vm_name))
        else:
            # On grave RHEV problems, this will throw
            # an exception and stop the program.
            vm.stop()

    def get_all_rhev_vms(self):
        vm_list = []
        vm_page_index = 1
        vm_page_current = self.api.vms.list(query="page %s" % vm_page_index)

        while(len(vm_page_current) != 0):
            vm_list = vm_list + vm_page_current
            vm_page_index = vm_page_index + 1
            try:
                vm_page_current = self.api.vms.list(
                    query="page %s" % vm_page_index
                )
            except Exception as ex:
                raise Exception(
                    "Error retrieving page '{0}' of list: '{1}'".format(
                        vm_page_index, ex
                    )
                )

        vm_list.reverse()
        return vm_list

    def eject(self, vmconfig):
        try:
            vm = vmconfig['vm']
            vm.cdroms.get(id="00000000-0000-0000-0000-000000000000").delete()
        except Exception as ex:
            self.logger.fatal("Ejecting cd-rom failed: %s" % ex)

    def adjust_ostype(self, reference_vmconfig, target_vmconfig):
        reference_vm = reference_vmconfig['vm']
        os = reference_vm.get_os()

        target_vm = target_vmconfig['vm']
        target_vm.set_os(os)
        target_vm.update()

    def vm_adduser(self, vmconfig):
        # Gives the role "UserRoleWithReconnect" to the user <user> on <vm>.
        # The role UserRoleWithReconnect must exist on your RHEV system.
        # See doc/virtesk-tc-connectspice.rst for details.

        vm = vmconfig['vm']
        user_name = vmconfig['tc_user']

        if user_name == 'None':
            return
        role = self.api.roles.get("UserRoleWithReconnect")

        # The following query doesn't work:
        # user = self.api.users.get(user_name)
        # Reason: api.users.get searches for the firstname of the
        # user instead of searching for usrname.
        # To circumvent this, we use the RHEV-query-language to search
        # for usrname.

        users = self.api.users.list(query="usrname=%s" % user_name)
        logging.debug("Number of users found for usrname %s: %s", user_name,
                      len(users))
        assert len(users) == 1
        user = users[0]

        vm.permissions.add(
            ovirtsdk.xml.params.Permission(
                user=user, role=role
            )
        )

    def create_vm_snapshot(self, vmconfig):
        # Creates a snapshot of a VM with a given description.
        #
        # Doesn't wait for the snapshot creation process to finish.
        # The VM should not be used until the snapshot is ready.
        # Please use wait_for_vm_snapshots_ready(...) after calling this
        # function.

        vmconfig['snapshot_description'] = (
            string.Template(vmconfig['snapshot_description'])
            .safe_substitute(vmconfig)
        )
        description = vmconfig['snapshot_description']

        if description == "":
            logging.info(
                "Not creating a snaphost for vm {0}."
                .format(vmconfig['rhev_vm_name'])
            )
            return

        try:
            vm = vmconfig['vm']
            if vm.get_stateless():
                logging.info(
                    "Not creating a snaphost for VM {0}. "
                    "Reason: VM is stateless."
                    .format(vmconfig['rhev_vm_name'])
                )
                return
            logging.debug("Creating a snapshot(description: %s) of vm %s... ",
                          description, vm.name)
            snapshot = vm.snapshots.add(ovirtsdk.xml.params.Snapshot(
                description=description))

            # save this object, so we can ask for status later.
            vmconfig['pending_snapshot'] = snapshot

        except Exception as ex:
            logging.error("Creating a snapshot(description: %s) " +
                          "of vm %s... FAILED", description, vm.name)
            raise(ex)

    def wait_for_vm_snapshots_ready(self, vmconfigs):
        snapshots = []
        for vmconfig in vmconfigs:
            if 'pending_snapshot' in vmconfig:
                snapshots.append(vmconfig['pending_snapshot'])

        # Given a list of snapshots, this function waits until all of them
        # are in state 'ok'.
        # Please use this function together with create_vm_snapshot(...).

        number_of_snapshots = len(snapshots)
        logging.debug("Waiting for %d snapshots to become ready...",
                      number_of_snapshots)
        while len(snapshots) > 0:
            for snapshot in snapshots:
                # REST-API call to get an updated snapshot object.
                # "snapshot.vm.snapshots" is an attribute from the
                # parentclass ( the VM itself). The id of a VM snapshot
                # is only valid within the context of
                # a VM (snapshot ids are not global).
                vm = self.api.vms.get(id=snapshot.vm.id)
                snapshot_updated = vm.snapshots.get(id=snapshot.id)
                status = snapshot_updated.get_snapshot_status()
                if status == 'ok':
                    logging.debug("Creating a snapshot(description: %s) " +
                                  " of vm %s... done",
                                  snapshot.description, vm.name)
                    snapshots.remove(snapshot)
            time.sleep(constants.WAIT_FOR_SNAPSHOTS_READY_SLEEP_TIME)

        logging.debug("All %d snapshots became ready.", number_of_snapshots)

    def get_hosts(self):
        hosts_list = self.api.hosts.list()

        for host in hosts_list:
            self.logger.info("%s (%s)" % (host.get_name(), host.get_id()))

    def get_logger(self):
        return self.logger

    def cleanup(self):
        product_name = self.api.get_product_info().name
        self.api.disconnect()
        self.logger.info("Disconnected from '%s' successfully!" % product_name)

    def reset_vm_to_snapshot(self, vmconfig):
        autoreset_snapshot_regex = vmconfig['reset_to_snapshot_regex']
        vm_was_running_before_reset = False

        vm_name = vmconfig["rhev_vm_name"]

        vm = self.api.vms.get(vm_name)
        if vm is None:
            logging.error(
                "could not reset VM {}, VM does not exist".format(vm_name)
            )
            return

        if vm.get_stateless():
            logging.info(
                "VM {0} is stateless, reset is not supported. "
                "Skipping.".format(vm_name)
            )
            return
        snapshots = vm.snapshots.list()
        candidate_snapshots = [
            s for s in snapshots if re.search(
                autoreset_snapshot_regex,
                s.description
            )
        ]
        if len(candidate_snapshots) > 1:
            logging.error(
                "could not reset VM {}, to many snaphosts are matching "
                "the regex `{}'.".format(vm_name, autoreset_snapshot_regex)
            )
            return

        if len(candidate_snapshots) == 0:
            logging.error(
                "could not reset VM {}, no snaphosts are matching the "
                "regex `{}'.".format(vm_name, autoreset_snapshot_regex)
            )
            return
        snapshot = candidate_snapshots[0]

        vm_ready = False
        for iteration in range(1, 5 + 1):
            vm = self.api.vms.get(vm.name)
            if vm.status.state == 'down':
                vm_ready = True
                break
            if vm.status.state == 'up':
                vm_was_running_before_reset = True
                logging.info(
                    "VM {} is running, forcefully stop VM...".format(vm_name)
                )
                vm.stop()
                time.sleep(4)
                continue
            else:
                logging.error(
                    "VM {0} in unknown state '{1}', trying to stop it..."
                    .format(vm_name, vm.status.state)
                )
                vm.stop()
                time.sleep(4)
                continue

        if not vm_ready:
            logging.error(
                "VM {0} in unknown state '{1}', "
                "reset for this vm will be skipped..."
                .format(vm_name, vm.status.state)
            )
            return

        logging.info(
            "Trying to reset VM {} to snapshot {} ..."
            .format(vm_name, snapshot.description)
        )

        snapshot.restore()
        self.wait_for_vms_down([vmconfig])

        logging.info(
            "Trying to reset VM {} to snapshot {} ... done"
            .format(vm_name, snapshot.description)
        )

        if vmconfig['reset_startvm'].lower() == 'always':
            logging.info("Starting VM {0}.".format(vm_name))
            vm.start()
        elif (
            vmconfig['reset_startvm'].lower() == 'auto'
            and vm_was_running_before_reset
        ):
            logging.info(
                "VM {0} was running before reset, lets start it again..."
                .format(vm_name)
            )
            vm.start()
        else:
            logging.info(
                "Not starting VM {0} after reset (disabled by configuration)."
                .format(vm_name)
            )

    def check_if_vms_exist(self, vms):
        some_vm_exist = False

        for vmconfig in vms:
            vm_name = vmconfig['rhev_vm_name']
            exists = self.api.vms.get(vm_name) is not None

            if exists:
                self.logger.info("VM {0} exists.".format(vm_name))
                some_vm_exist = True
            else:
                self.logger.info("VM {0} doesnt exist.".format(vm_name))

        return some_vm_exist

    def analyze_snapshots(self, vms_for_classroom):
        for vmconfig in vms_for_classroom:
            autoreset_snapshot_regex = vmconfig['reset_to_snapshot_regex']
            vm_name = vmconfig["rhev_vm_name"]

            vm = self.api.vms.get(vm_name)
            if vm is None:
                logging.info("VM {0} does not exist".format(vm_name))
                continue

            if vm.get_stateless():
                logging.info("VM {0} is stateless.".format(vm_name))
            else:
                logging.info("VM {0} is not stateless.".format(vm_name))

            snapshots = vm.snapshots.list()

            logging.info("Snapshots of VM {0}: {1}.".format(
                vm_name,
                [s.description for s in snapshots]
            ))

            snapshots_matching_pattern = [
                s.description for s in snapshots
                if re.search(autoreset_snapshot_regex, s.description)
            ]

            logging.info(
                "Snapshots of VM `{0}' that match pattern `{1}': `{2}'."
                .format(
                    vm_name,
                    autoreset_snapshot_regex.pattern,
                    snapshots_matching_pattern
                )
            )

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
import argparse
import sys
import os
import pprint
import time
import copy
import subprocess
import re
import string
import configobj
import logging
import logging.config

# Project imports
import constants
import ovirtsdk.api
import ovirtsdk.xml
import mako				# http://www.makotemplates.org/
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
            raise Exception("Unexpected error: {0}".format(ex))

    def initialize_logging(self):
        try:
            self.logger = logging.getLogger(__name__)

        except Exception, ex:
            raise Exception(
                'Unexpected error while initialize logging: {0}'.format(
                    ex
                )
            )

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
            section['ca_file'])

        config['username'] = section['username']
        # password_key = section['password_key']
        # config['password'] =
        # self.base_configuration['general']['connect']['password']
        config['password'] = section['password']
        # config['isofolder'] = section['isofolder']
        # config['remoteshell'] = section['remoteshell'].split()

    def dumpconnectinfo(self, section=None):
        self.read_connect_configuration(section=section)

        self.logger.info("Connect configuration settings:")
        self.logger.info(pprint.pformat(self.connect_configuration))

    def get_vms_for_classroom(self, classroom):
        result = []
        classroom_was_found = False

        self.logger.debug(
            "Getting VMs for classroom '{0}'".format(classroom)
        )

        if not classroom:
            raise Exception('No classroom given')

        for class_room in self.base_configuration.keys():
            if 'classroom' in class_room and classroom in class_room:
                classroom_was_found = True

                # Get current class room
                class_room = self.base_configuration[class_room]

                # Build list with VMs

                # Teacher VMs
                result += self.build_vm_list_for_key('teacher_vms', class_room)

                # Student VMs
                result += self.build_vm_list_for_key('student_vms', class_room)

        if not classroom_was_found:
            raise Exception("Classroom '%s' was not found" % classroom)

        if len(result) <= 0:
            raise Exception("Classroom '%s' has no VMs" % classroom)

        self.logger.debug(
            "Got {0} VMs for classroom '{1}'".format(len(result), classroom)
        )

        return result

    def build_vm_list_for_key(self, key, configuration_array):
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
            current_id_padded = ("%0" + str(vm_id_digits) + "i") % current_id
            current_vm = configuration_array[key]
            current_vdi = configuration_array['vdi']

            ip_address_suffix = int(
                current_vm['ip_addresses_suffix']
            ) + current_id - 1

            rhev_vm_name = string.Template(
                current_vm['names']
            )

            rhev_vm_name = rhev_vm_name.safe_substitute(
                roomname=configuration_array['name'],
                id=current_id_padded
            )

            computerName = rhev_vm_name

            if len(rhev_vm_name) > 15:
                msg = ("Name of VM %s greater than 15 characters long. " +
                       "This isn't supported by RHEV and Windows.") % rhev_vm_name
                raise Exception(msg)

            vm_config = dict(
                rhev_vm_name=rhev_vm_name,
                memory=eval(current_vm['memory']),
                ip=string.Template(
                    current_vm['ip_addresses']
                ).safe_substitute(
                    suffix=ip_address_suffix
                ),
                netmask_as_suffix=current_vdi['netmask_suffix'],
                ComputerName=computerName,
                # vlan=current_vdi['vlan'],
                network_name=current_vdi['network_name'],
                template=current_vm['template_name'],
                description=current_vm['description'],
                cluster=current_vm['cluster'],
                default_gw=current_vdi['default_gateway'],
                autounattend_templatefile=self.get_configfile_absolutepath(
                    configuration_array['autounattend_templatefile']),
                scripttime=self.scripttime_string,
                tc_user=current_vm['tc_user'],
                workaround_os=current_vm['workaround_os'],
                workaround_timezone=current_vm['workaround_timezone'],
                os=current_vm['os'],
                timezone=current_vm['timezone'],
                usb=dict(
                    enabled=current_vdi['usb']['enabled']
                )
            )

            vm_list.append(vm_config)

        return vm_list

    def connect(self, config):
        self.api = ovirtsdk.api.API(
            url=config['url'],
            username=config['username'],
            password=config['password'],
            ca_file=config['ca_file'],
            persistent_auth=False
        )

    def create_standalone_vm(self, vmconfig):
        vm_name = vmconfig['rhev_vm_name']
        vm_cluster = self.api.clusters.get(name=vmconfig['cluster'])
        vm_template = self.api.templates.get(name=vmconfig['template'])
        assert not vm_template is None, "assert not vm_template is None"
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
            # timezone="Europe/Berlin",
            # timezone="W. Europe Standard Time",
            # timezone="Europe/London",
            timezone=vmconfig['workaround_timezone'],
            description=vmconfig['description'])
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
        vm = vmconfig['vm']
        vm_usb = ovirtsdk.xml.params.Usb(enabled=True, type_='native')
        vm.set_usb(vm_usb)
        vm.update()

    def wait_for_vms_down(self, vmconfigs=None, vm_names=None, formatstring=None):
        if vm_names is None:
            pending_vms = [vmconfig['rhev_vm_name'] for vmconfig in vmconfigs]
        else:
            pending_vms = copy.copy(vm_names)
        while len(pending_vms) > 0:
            for vm_name in pending_vms:
                if self.api.vms.get(vm_name).status.state == 'down':
                    pending_vms.remove(vm_name)
                    if not formatstring is None:
                        self.logger.debug(formatstring.format(vm_name))
            time.sleep(5)

    def add_vm_nic(self, vmconfig):
        vm = vmconfig['vm']
        vm_name = vmconfig['rhev_vm_name']
        nic_name = "nic0"
        nic_interface = "virtio"
        # nic_network_name = "br_v" + str(vmconfig['vlan'])
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

        cust_prop = ovirtsdk.xml.params.CustomProperty(
            name="floppy", value=ovirt_worker_floppy_path)

        vm.set_custom_properties(
            ovirtsdk.xml.params.CustomProperties(custom_property=[cust_prop]))
        vm.update()

    def detach_and_cleanup_floppy(self, vmconfig):
        # Detaching floppy from VM Configuration
        vm = vmconfig['vm']
        vm.set_custom_properties(ovirtsdk.xml.params.CustomProperties())

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

        # self.create_iso(vmconfig)
        # self.attach_iso(vmconfig)
        self.start_vm(vmconfig)

#     def attach_iso(self, vmconfig):
#         iso = self.ISO_DOMAIN.files.get(vmconfig['autounattend_filename'])
#         self.logger.info("Attaching ISO image '%s' for VM '%s'" % (
#             vmconfig['autounattend_filename'],
#             vmconfig['rhev_vm_name']
#         ))
#         vm = vmconfig['vm']
#         cdrom = ovirtsdk.xml.params.CdRom(vm=vm, file=iso)
#         vm.cdroms.add(cdrom)
#         vm.update()
#

#     def adjust_vm(self, vmconfig):
# 	vm = vmconfig['vm']
# 	initialization = ovirtsdk.xml.params.Initialization()
# 	vm.set_initialization(initialization)
# 	vm.update()

    def start_vm(self, vmconfig):
        vm = vmconfig['vm']
        # initialization = ovirtsdk.xml.params.Initialization()

        # vm.set_initialization(initialization)
        # vm.update()

        # action = ovirtsdk.xml.params.Action()
        # logging.debug("Sleeping 10 seconds....")
        # time.sleep(10)

        # vm.start(action)

        # vm.get_os().set_type('rhel_7x64')
        # vm.set_next_run_configuration_exists(False)
        # vm.set_payloads(ovirtsdk.xml.params.Payloads())
        # vm.set_floppies(ovirtsdk.xml.params.Floppies())
        # vm.update()
        vm.start()
        # sys.exit(0)
        # vm.start(ovirtsdk.xml.params.Action(host=self.api.hosts.get("eponine")))

    def postprocess_vm(self, vmconfig):
        # sync state from ovirt
        vmconfig['vm'] = self.api.vms.get(vmconfig['rhev_vm_name'])

        self.adjust_os_and_timezone(vmconfig)
        self.detach_and_cleanup_floppy(vmconfig)
        self.set_stateless(vmconfig, False)  # FIXME
        self.vm_adduser(vmconfig)

        # sync changes back to ovirt
        vmconfig['vm'].update()

    def adjust_os_and_timezone(self, vmconfig):
        vmconfig['vm'].set_timezone(vmconfig['timezone'])
        vmconfig['vm'].get_os().set_type(vmconfig['os'])

    def set_stateless(self, vmconfig, stateless=True):
        vm = vmconfig['vm']
        vm.set_stateless(stateless)
        vm.update()

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
        subprocess.check_call(
            "dd if=/dev/zero of={} bs=1440K count=1".format(floppypath), shell=True)
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

#     def create_iso(self, vmconfig):
#         unattendxml = self.apply_unattend_xml_template(vmconfig)
#         isofilename = "autounattend-vm-%s.iso" % vmconfig['rhev_vm_name']
#         isopath = self.connect_configuration['isofolder'] + isofilename
#
#         script = '''DIR=`mktemp -d /tmp/ADSY-VDI-POOL-MANAGE.XXXXXXXXXXXXXXXXXX`
# echo $DIR;
#         mkdir $DIR/cdrom
#         cat > $DIR/cdrom/Autounattend.xml << "EOFEOFEOF"
#         %s
#
# EOFEOFEOF
# echo ==== Start autounattend.xml ====
# cat $DIR/cdrom/Autounattend.xml
# echo ==== end autounattend.xml ====
#         genisoimage -quiet -J -input-charset iso8859-1 -o %s $DIR/cdrom/
#
#         ''' % (unattendxml, isopath)
#
#         call_args = self.connect_configuration['remoteshell'] + [script]
#         subprocess.check_call(call_args)
#
#         vmconfig['autounattend_filename'] = isofilename
#
    def apply_unattend_xml_template(self, vmconfig):
        try:
            t = mako.template.Template(
                filename=vmconfig['autounattend_templatefile']
            )
            result = t.render(**vmconfig)

            # with open("Autounattend.xml", "w") as text_file:
            #    text_file.write(result)

            return result

        except:
            raise Exception(mako.exceptions.text_error_template().render())

    def delete_vm(self, vmconfig):
        if 'vm' in vmconfig:
            vm = vmconfig['vm']
        else:
            vm = self.api.vms.get(vmconfig['rhev_vm_name'])

        if not vm is None:
            vm_name = vm.get_name()
            self.force_stop_vm(vm_name)
            if not (vm.get_vmpool() is None):
                self.logger.info("Detaching VM '%s'" % vm_name)
                vm.detach()
            self.logger.info("Deleting VM '%s'" % vm_name)
            vm.delete()
            while not self.api.vms.get(vm_name) is None:
                time.sleep(1)
        else:
            self.logger.warn("Tried to delete VM '%s' but it seems not to be on RHEV server" %
                             vmconfig['rhev_vm_name'])

    def force_stop_vm(self, vm_name):
        vm = self.api.vms.get(vm_name)
        try:
            vm.stop()
        except Exception as ex:
            pass
        self.wait_for_vms_down(vm_names=[vm_name])

    def create_rhev_pool(self, poolconfig):
        name = poolconfig['name']

        template = self.api.templates.get(poolconfig['template_name'])
        poolconfig['template'] = template

        # FIXME: OS = win7x64 setzen
        vmpool_param = ovirtsdk.xml.params.VmPool()
        vmpool_param.set_name(name)
        vmpool_param.set_template(template)
        vmpool_param.set_cluster(self.VDI_CLUSTER)
        vmpool_param.set_size(poolconfig['initial_size'])
        self.logger.info("Creating pool '%s'" % name)
        self.api.vmpools.add(
            vmpool_param,
            expect="Expect: 201-created"
        )
        pool = self.api.vmpools.get(name)
        assert not (pool is None), "not (pool is None)"
        self.logger.info("Pool '%s' created." % name)

        poolconfig['pool'] = pool
        self.logger.info("Collecting a list of VMs in pool '%s'" % name)
        self.get_rhev_pool_vms(poolconfig)
        return pool

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

    def get_rhev_pool_vms(self, poolconfig):
        # FIXME: dies ist ineffizient, denn hier
        # werden von allen VMs im RHEV alle Infos geholt,
        # aber eigentlich werden nur die Infos von ca. 22 VMs gebraucht.
        result = []
        pool = poolconfig['pool']
        vm_list = self.get_all_rhev_vms()
        for vm in vm_list:
            vm_name = vm.get_name()
            vm_pool = vm.get_vmpool()
            if vm_pool is None:
                continue
            if vm_pool.get_id() == pool.get_id():
                result.append(vm)
        poolconfig['list_of_precreated_pool_vms'] = result
        return result

    def create_rhev_pool_vm(self, vmconfig):
        vm_name = vmconfig['rhev_vm_name']
        poolconfig = vmconfig['poolconfig']
        precreated_pool_vms = poolconfig['list_of_precreated_pool_vms']
        self.logger.info("Creating pool VM '%s'" % vm_name)

        try:
            pool_name = poolconfig['name']
            pool = poolconfig['pool']
            assert len(
                precreated_pool_vms) > 0, "precreated_pool_vms(list) > 0"
            vm = precreated_pool_vms.pop()

            assert not (vm is None), "assert not (vm is None)"

            vm_pool = vm.get_vmpool()
            assert not (vm_pool is None), "assert not (vm_pool is None)"
            assert vm_pool.get_id() == pool.get_id(
            ), "assert vm_pool.get_id() == pool.get_id()"
            self.logger.info(
                "Renaming VM '{0}' to '{1}'".format(
                    vm.get_name(), vm_name
                )
            )
            vm.set_name(vm_name)
            vm.update()
            vmconfig['vm'] = vm
            self.logger.info("Finished creation of pool VM '%s'" % vm_name)
        except Exception as ex:
            raise Exception(
                "Creating pool VM '{0}' FAILED: {1}".format(
                    vm_name, ex
                ))

    def eject(self, vmconfig):
        try:
            vm = vmconfig['vm']
            vm.cdroms.get(id="00000000-0000-0000-0000-000000000000").delete()
        except Exception as ex:
            self.logger.fatal("Ejecting cd-rom failed: %s" % ex)

    def delete_pool(self, pool_name):
        pool = self.api.vmpools.get(pool_name)
        if pool is None:
            self.logger.error("Pool '%s' not found" % pool_name)
        else:
            self.logger.info("Found pool: '%s'" % pool_name)

            vm_list = self.get_all_rhev_vms()
            waitfor_list = []

            for vm in vm_list:
                vm_name = vm.get_name()
                vm_pool = vm.get_vmpool()
                if vm_pool is None:
                    continue
                if vm_pool.get_id() == pool.get_id():
                    if self.api.vms.get(vm_name).status.state != 'down':
                        vm.stop()
                        down = False
                        while not down:
                            time.sleep(1)
                            down = self.api.vms.get(
                                vm_name).status.state == 'down'
                    self.logger.info("Detaching VM '%s'" % vm.name)
                    vm.detach()
                    self.logger.info("Deleting VM '%s'" % vm.name)
                    vm.delete()
                    waitfor_list += vm_name

            while len(waitfor_list) > 0:
                for vm_name in waitfor_list:
                    if self.api.vms.get(vm_name) is None:
                        waitfor_list.remove(vm_name)
                time.sleep(1)

            self.logger.info("Deleting pool '%s'" % pool_name)
            pool.delete()

            while not (self.api.vmpools.get(pool_name) is None):
                time.sleep(1)

    def prestartAll(self, poolconfig):
        pool = poolconfig['pool']
        size = pool.get_size()
        pool.set_prestarted_vms(size)
        pool.update()

    def adjust_ostype(self, reference_vmconfig, target_vmconfig):
        reference_vm = reference_vmconfig['vm']
        os = reference_vm.get_os()

        target_vm = target_vmconfig['vm']
        target_vm.set_os(os)
        target_vm.update()

    def pool_addgroup(self, poolconfig):
        pool = poolconfig['pool']
        group_name = poolconfig['univention_group']
        if group_name == 'None':
            return
        role = self.api.roles.get("UserRole")
        group = self.api.groups.get(group_name)
        pool.permissions.add(
            ovirtsdk.xml.params.Permission(
                group=group,
                role=role
            )
        )

#     def vm_addgroup(self, vmconfig):
#         vm = vmconfig['vm']
#         group_name = vmconfig['univention_group']
#
#         if group_name == 'None':
#             return
#         role = self.api.roles.get("UserRole")
#         group = self.api.groups.get(group_name)
#         vm.permissions.add(
#             ovirtsdk.xml.params.Permission(
#                 group=group, role=role
#             )
#         )
#
    def vm_adduser(self, vmconfig):
        # Gives the Role <role> to the User <user> on <vm>.
        # FIXME: user/role should be configurable.

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

    def create_vm_snapshot(self, vmconfig, description):
        # creates a snapshot of a VM with a given description.
        # returns a ovirtsdk.infrastructure.brokers.VMSnapshot object.
        #
        # Doesn't wait for the snapshot creation process to finish.
        # The VM should not be used until the snapshot is ready.
        # Please use wait_for_vm_snapshots_ready(...) after calling this
        # function.
        try:
            vm = vmconfig['vm']
            logging.debug("Creating a snapshot(description: %s) of vm %s... ",
                          description, vm.name)
            snapshot = vm.snapshots.add(ovirtsdk.xml.params.Snapshot(
                description=description))
            return snapshot
        except Exception as ex:
            logging.error("Creating a snapshot(description: %s) " +
                          "of vm %s... FAILED", description, vm.name)
            raise(ex)

    def wait_for_vm_snapshots_ready(self, snapshots):
        # Given a list of snapshots, this function waits until all of them
        # are in state 'ok'.
        # Please use this function together with create_vm_snapshot(...).

        number_of_snapshots = len(snapshots)
        logging.debug("Waiting for %d snapshots to become ready...",
                      number_of_snapshots)
        while len(snapshots) > 0:
            for snapshot in snapshots:
                # REST-API call to get an updated snapshot object.
                # "snapshot.vm.snapshots" is an attribute from the parentclass (
                # the VM itself). The id of a VM snapshot is only valid within
                # the context of a VM (snapshot ids are not global).
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

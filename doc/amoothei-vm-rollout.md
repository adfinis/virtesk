Introduction
==============
amoothei-vm-rollout is a script for creating/cloneing a lot of windows 7 virtual machines.
Those win7 VMs can then be assigned to and displayed on thinclients.

The script creates new VMs based on an existing Ovirt VM Template, and assings hostname, static IP address, ... to it and makes sure the new VM is joined into an Active Directory (or Samba4) domain.

The process is based on Windows Sysprep / Unattended.xml technologies.

See also: [Compatibility](Compatibility.md)


System preparation
==================
To run amoothei-vm-rollout, the system must be prepared first:

1. Setting up [floppy payload mechanism](sftp-floppy-upload.md)


Goldimage preparation
======================
The Goldimage is the Win7 VM "archetype" that will be cloned later.

Details are described [here](Goldimage.md)


Installing amoothei-vm-rollout
=================================


Configuring amoothei-vm-rollout
===================================





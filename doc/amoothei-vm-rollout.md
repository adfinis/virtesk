## Introduction
amoothei-vm-rollout is a script for creating/cloneing a lot of windows 7 virtual machines.
Those win7 VMs can then be assigned to and displayed on thinclients.

The script creates new VMs based on an existing Ovirt VM Template, and assings hostname, static IP address, ... to it and makes sure the new VM is joined into an Active Directory (or Samba4) domain.

The process is based on Windows Sysprep / Unattended.xml technologies.

See also: [Compatibility](Compatibility.md)

## Tools
### amoothei-virtroom-show
Parses and validates the room configuration, checks if the VMs exists, and lists their snapshosts.

Prerequisites:
* valid room configuration

### amoothei-virtroom-rollout
Roll out a virtual room.

Prerequisites:
* VMs of the virtual room shall not exist

How it works:
1. Configuration parsing and validation
2. Create VMs from Ovirt Template
3. Attach Network to VM
4. Create individual Autounattend.xml using a template mechanism
5. Generate payload floppy, containing individual Autounattend.xml (filename: A:\sysprep.inf)
6. Run VM with payload attached. This configures Windows according to the settings in Autounattend.xml 
7. Wait until all VMs of a virtual room are shut down
8. Postprocess VMs (USB settings, stateless feature, add permissions for technical vdi accounts, create snapshots, ...)
9. Start VMs

### amoothei-virtroom-delete
Deletes all VMs of a virtual room. 

### amoothei-virtroom-reset
Reset VMs of a virtual room to a snapshot state.

How it works:
1. Configuration parsing and validation
2. Stop VMs if they are running
3. Restore state to snapshot
4. Optional: Start VMs again

Reset to snapshot state is not supported for stateless VMs

### Usage
```
amoothei-virtroom-show [--config CONFIG] myroom
amoothei-virtroom-rollout [--config CONFIG] myroom
amoothei-virtroom-delete [--config CONFIG] myroom
amoothei-virtroom-reset [--config CONFIG] myroom
```

The argument ```myroom``` is mandatory. It refers to the definition of the virtual room in the configuration.

The following config file locations are used, first match wins:

    * Command line argument
    * ~/.config/amoothei-vdi/amoothei-vm-rollout.conf
    * /etc/amoothei-vdi/amoothei-vm-rollout.conf




## Installation and preparation
To run amoothei-vm-rollout, the system must be prepared first:

1. Setting up [floppy payload mechanism](sftp-floppy-upload.md)



## Configuration
### Config File
### General Settings
### Room definitions
### Logging configuration


## Windows stuff
### Registry keys
### Goldimage - sealing a virtual machine


### Autounattend.xml

### Mako Templating for Autounattend.xml


Goldimage preparation
======================
The Goldimage is the Win7 VM "archetype" that will be cloned later.

Details are described [here](Goldimage.md)


Installing amoothei-vm-rollout
=================================


Configuring amoothei-vm-rollout
===================================





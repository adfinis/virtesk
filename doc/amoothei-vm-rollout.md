# VM rollout tools

Tools for creating and manageing VDI VMs, grouped into virtual rooms.

-------------


## Introduction
amoothei-virtroom-* is a set of tools for creating/cloneing a lot of windows 7 virtual machines.
Those win7 VMs can then be assigned to and displayed on thinclients.

The script creates new VMs based on an existing Ovirt VM Template, and assings hostname, static IP address, ... to it and makes sure the new VM is joined into an Active Directory (or Samba4) domain.

The process is based on Windows Sysprep / Unattended.xml technologies.

See also: [Compatibility](Compatibility.md)

------------------

## Tools
### amoothei-virtroom-show
Parses and validates the room configuration, checks if the VMs exists, and lists their snapshosts.


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

Reset to snapshot state is not supported for stateless VMs.

## Usage
```bash
amoothei-virtroom-show [--config CONFIG] myroom
amoothei-virtroom-rollout [--config CONFIG] myroom
amoothei-virtroom-delete [--config CONFIG] myroom
amoothei-virtroom-reset [--config CONFIG] myroom
```

```myroom``` is the virtual room to act on, e.g. the room to show/rollout/delete/reset. 

The following config file locations are used, first match wins:

* Command line argument (`--config /path/to/amoothei-vm-rollout.conf`)
* `~/.config/amoothei-vdi/amoothei-vm-rollout.conf`
* `/etc/amoothei-vdi/amoothei-vm-rollout.conf`

## Many virtual rooms
When manageing alot of virtual rooms, bash features can be handy:
```
for room in room{01..10}; do amoothei-virtroom-show $room; done
for room in room01 room02 room03; do amoothei-virtroom-show $room; done
for room in $(cat room-list.txt) do amoothei-virtroom-show $room; done
```

## See also
* [Installing amoothei-vm-rollout](amoothei-vm-rollout-install.md)
* [Defining and configuring virtual rooms](amoothei-vm-rollout-config.md)
* [Windows Goldimage](goldimage.md)
* [Windows Unattended Setup](autounattend.md)
* [Quality control after rollout](quality_control.md)




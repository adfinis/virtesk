Amoothei-VDI: Rollout tools for virtual rooms
=============================================

Tools for creating and manageing VDI VMs, grouped into virtual rooms.

--------------

Introduction
------------

| amoothei-virtroom-\* is a set of tools for creating/cloneing a lot of
  windows 7 virtual machines.
| Those win7 VMs can then be assigned to and displayed on thinclients.

The script creates new VMs based on an existing Ovirt VM Template, and
assings hostname, static IP address, ... to it and makes sure the new VM
is joined into an Active Directory (or Samba4) domain.

The process is based on Windows Sysprep / Unattended.xml technologies.

See also: `Compatibility <compatibility.md>`__

--------------

Tools
-----

amoothei-virtroom-show
~~~~~~~~~~~~~~~~~~~~~~

Parses and validates the room configuration, checks if the VMs exists,
and lists their snapshosts.

amoothei-virtroom-rollout
~~~~~~~~~~~~~~~~~~~~~~~~~

Roll out a virtual room.

Prerequisites:

-  VMs of the virtual room shall not exist

How it works:

#. Configuration parsing and validation
#. Create VMs from Ovirt Template
#. Attach Network to VM
#. Create individual Autounattend.xml using a template mechanism
#. Generate payload floppy, containing individual Autounattend.xml
   (filename: A:\\sysprep.inf)
#. Run VM with payload attached. This configures Windows according to
   the settings in Autounattend.xml
#. Wait until all VMs of a virtual room are shut down
#. Postprocess VMs (USB settings, stateless feature, add permissions for
   technical vdi accounts, create snapshots, ...)
#. Start VMs

amoothei-virtroom-delete
~~~~~~~~~~~~~~~~~~~~~~~~

Deletes all VMs of a virtual room.

amoothei-virtroom-reset
~~~~~~~~~~~~~~~~~~~~~~~

Reset VMs of a virtual room to a snapshot state.

How it works:

#. Configuration parsing and validation
#. Stop VMs if they are running
#. Restore state to snapshot
#. Optional: Start VMs again

Reset to snapshot state is not supported for stateless VMs.

amoothei-virtroom-start
~~~~~~~~~~~~~~~~~~~~~~~

Starts all VMs in a virtual room.

Details:

-  Ignores already running VMs
-  No validation is done - returns as soon as the start signal has been
   sent to all VMs. Does not wait for the VMs to launch.

amoothei-virtroom-shutdown
~~~~~~~~~~~~~~~~~~~~~~~~~~

Shut down all VMs in a virtual room.

Details:

-  Clean shutdown: A signal (ACPI shutdown or guest agent shutdown) is
   sent to the operating system of the VM.
   Assumes that ACPI daemon and/or guest agent is properly configured
   inside the VM and that the VM does a clean shutdown when told to do
   so.
-  Ignores already stopped VMs
-  No validation is done - returns as soon as the shutdown signal has
   been sent to all VMs. Does not wait for the VMs to shut down.

Usage
-----

.. code:: bash

    amoothei-virtroom-show [--config CONFIG] myroom
    amoothei-virtroom-rollout [--config CONFIG] myroom
    amoothei-virtroom-delete [--config CONFIG] myroom
    amoothei-virtroom-reset [--config CONFIG] myroom

``myroom`` is the virtual room to act on, e.g. the room to
show/rollout/delete/reset.

The following config file locations are used, first match wins:

-  Command line argument
   (``--config /path/to/amoothei-vm-rollout.conf``)
-  ``~/.config/amoothei-vdi/amoothei-vm-rollout.conf``
-  ``/etc/amoothei-vdi/amoothei-vm-rollout.conf``

Many virtual rooms
------------------

When manageing alot of virtual rooms, bash features can be handy:

::

    for room in room{01..10}; do amoothei-virtroom-show $room; done
    for room in room01 room02 room03; do amoothei-virtroom-show $room; done
    for room in $(cat room-list.txt); do amoothei-virtroom-show $room; done

See also
--------

-  `Installing amoothei-vm-rollout <amoothei-vm-rollout-install.md>`__
-  `Defining and configuring virtual
   rooms <amoothei-vm-rollout-config.md>`__
-  `Windows Goldimage <goldimage.md>`__
-  `Windows Unattended Setup <autounattend.md>`__
-  `Quality control after rollout <quality_control.md>`__

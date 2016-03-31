Amoothei-VDI: Stateless and snapshot features
=============================================

Features to reset virtual rooms to a well-defined, known state

--------------

Introduction
------------

Situation:

-  Large number of clearly-defined managed workplaces
-  Users and programs might modify workplaces and leave some debris
   after work
-  Workplace modifications and debris shall be avoided
-  Divergence of workplaces shall be avoided

Amoothei-VDI provides two solutions:

-  Snapshots: A snapshot will be created for every VM after initial
   rollout. A cronjob resets the virtual rooms to the snapshot state
   every night.
-  Stateless VMs: A snapshot will be created at VM startup; The VM will
   be reset to snapshot state after shutdown.

The approach using snapshots is the preferred solution.

Snapshots
---------

How it works:

-  Virtual rooms are created using amoothei-virtroom-rollout. After
   rollout, amoothei-virtroom-rollout automatically creates a snapshot
   for every VM.
-  Every night, amoothei-virtroom-reset is run by cronjob. This tool
   will stop the VMs, reset them back to the snapshot that was created
   by amoothei-virtroom-rollout, and starts the VMs again. During the
   reset phase at night, the VMs / Workplaces are unavailable.
-  VMs are statefull, but they will be reset every night

Background: Snapshot operations are expensive, in particular when doing
alot of snapshot operations at once. Snaphosts in RHEV/Ovirt also
sometimes were buggy and problematic in the past. During snapshot
operations, the VM cannot be used, that is, the user has to wait for the
operations to complete.

This solutions avoids those problems:

-  Snapshot creation is only done once, after initial rollout. By
   inserting short breaks where necessary, the tools do avoid situations
   where RHEV/Ovirt is overloaded by to many parallel snapshot
   operations.
-  Reset to snapshot date is done during the night, when workplaces are
   unused.
-  No snapshot operations are done during daytime. Therefore, the users
   do not have to wait for snapshot operations. Statefull VMs start alot
   faster than stateless VMs, and they are also more reliable and less
   ressource-consuming.
-  VM startup is fast, even in peak situations in a classroom where 20
   VMs might start at once.

Configuration: ``amoothei-vm-rollout.conf``:

::

    [room room01]
      [[student_vms]]
      # The snapshot and stateless features are mutually exclusive and cannot be used together.
      stateless = False 

      # Used for snapshot creation after initial rollout
      snapshot_description = "Automatic snapshot after amoothei-vmrollout, IP=${ip}/${netmask_as_suffix}, scripttime=${scripttime}"

      # Used for reset
      reset_to_snapshot_regex = "Automatic snapshot after amoothei-vmrollout, .*"

      # Shall VMs be started after reset?
      reset_startvm = Auto

To use the snapshot feature, ``snapshot_description`` and
``reset_to_snapshot_regex`` must be configured. The first parameter is
used during rollout of virtual rooms, the second is used to identify the
snapshot the VMs to.

``reset_startvm = Always/Auto/Never`` determines if VMs shall be started
after reset. When set to ``Auto``, the VMs will be started if they were
running before reset.

To disable the snapshot feature, set ``snapshot_description = ""`` and
deactivate the reset cronjob.

Automatic reset every night
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cronjob: ``/etc/cron.d/amoothei-vdi-reset-virtrooms``: Runs reset script
at 01:00 AM every night:

::

    SHELL=/bin/sh
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/amoothei-vdi.src/amoothei-vm-rollout/
    # m h  dom mon dow   command
    00 01 * * * root /etc/amoothei-vdi/reset-virtrooms-every-night.sh > /dev/zero

Please make sure to add your amoothei installation directory to
``$PATH``, like ``/opt/amoothei-vdi.src/amoothei-vm-rollout/`` above.

See also: ``man 5 crontab``.

Reset-Script: ``/etc/amoothei-vdi/reset-virtrooms-every-night.sh``:

::

    #!/bin/bash
    # Reset virtual rooms to snapshots

    amoothei-virtroom-reset test01
    amoothei-virtroom-reset test02
    amoothei-virtroom-reset test03
    amoothei-virtroom-reset test04

Please add ``amoothei-virtroom-reset <myroom>`` for every virtual room
that shall be reset.

Making it executable:
``chmod +x /etc/amoothei-vdi/reset-virtrooms-every-night.sh``.

Stateless
---------

Stateless VMs are a built-in feature of RHEV/Ovirt: Before starting a
stateless VM, a snapshot is created. After VM shutdown, the snapshot is
discarded, e.g. the VM is reset to the state before launch.

Amoothei-vdi supports stateless VMs by setting the stateless flag after
rollout. Afterwards, RHEV/Ovirt is responsible for snapshot management.

Advantages:

-  Builtin feature of RHEV/Ovirt

Drawbacks:

-  VM are starting slower (50-80 seconds until a spice session can be
   opened, compared to 15-30 seconds for statefull VMs)
-  Consumes more resources
-  Somewhat error prone (Bugs in snapshot implementation of RHEV/Ovirt)
-  Other amoothei-vdi code (Thinclients, Start/Stop - Management, ...)
   handle stateless VMs like statefull VMs. No special error handling is
   implemented for stateless VMs. This might be necessary in the
   following areas: VM launch time, amoothei-virtroom-delete,
   amoothei-virtroom-start, amoothei-virtroom-shutdown, VM startup upon
   TC startup, VM shutdown upon TC shutdown. In general, stateless VMs
   should run fine, but problems might occour when starting/stopping
   stateless VMs too fast or too often in a row.
-  Peak situations: When starting or stopping alot of stateless VMs at
   once, then RHEV/Ovirt might handle some operations sequentially. For
   example in a classroom situation, if the teacher tells the whole
   class to start their thinclients, startup might take longer than when
   starting a single thinclient.

Configuration: ``amoothei-vm-rollout.conf``:

::

    [room room01]
      [[student_vms]]
      stateless = True

      # The snapshot and stateless features are mutually exclusive and cannot be used together.
      snapshot_description = ""

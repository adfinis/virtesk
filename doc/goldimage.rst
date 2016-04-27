Windows Goldimage
===============================

How to create and seal a Windows Goldimage and use it as a RHEV/Ovirt
VmTemplate.

--------------

Introduction
------------

The goal is to use one master VM (the "Goldimage") as a blueprint for
creating/cloneing alot of VMs.

If a Windows 7 VM is simply cloned directly, all identifiers inside
remain the same. This includes the Active Directory SID and GUID. Those
identifiers should be unique - but cloneing violates the uniqueness
property. Therefore, direct cloneing will cause problems in Active
Directory environments. This can be avoided by using the
Sysprep/Autounattend process described below.

Prerequisites
-------------

This article covers Goldimages based on Windows 7 x64 Professional in an
Active Directory (or Samba4) environment. The Professional Edition of
Windows 7 is nessesary for usage in Active Directory (or Samba4)
domains.

Initial Goldimage
-----------------

Steps:

-  Create VM + Install Win7 x64 Professional

   -  Using a thin-provisioned disk in RHEV/Ovirt is recommended

-  Install virtio + spice drivers, install guest agent
-  Install all Windows Updates
-  Configure as you like, install Programs

Common Settings:
~~~~~~~~~~~~~~~~

Registry Keys:

::

    rem Tell Windows where to find its Unattended Setup Config file. Common values include a:\sysprep.inf,  a:\Autounattend.xml, a:\Unattend.xml. For virtesk-vdi, a:\sysprep.inf should be used.
    rem See also:
    rem     * /etc/ovirt-engine/osinfo.conf.d/ on RHEV/Ovirt Manager
    rem       os.windows_7.sysprepFileName.value = sysprep.inf
    rem       os.windows_7x64.sysprepFileName.value = sysprep.inf
    reg add "HKEY_LOCAL_MACHINE\SYSTEM\SETUP" /v UnattendFile /t REG_SZ /d a:\sysprep.inf /f

    rem Disable TCP Task-Offloading.
    rem Useful to avoid problems with incorrect udp checksums regarding virtio-net + dhcp
    reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\TCPIP\Parameters" /v DisableTaskOffload /t REG_DWORD /d 1 /f

Ovirt OS info settings
----------------------

Virtesk-VDI puts the Unattend Setup Config file into the file
``a:\sysprep.inf`` on a `virtual floppy disk <sftp-floppy-upload.html>`__.
To make sure windows finds the floppy there, setting the windows
registry key as described above is sufficient. However, if you wanna use
the same Goldimage VmTemplate for other purposes (Ovirt UserPortal /
PowerUserPortal, manual creation of VMs, manual creation of Ovirt
VmPools), then the following settings on your RHEV / Ovirt Manager are
needed to make sure that RHEV / Ovirt will put their version of the
Unattended Setup Config file into the right location:

::

    mkdir -p /etc/ovirt-engine/osinfo.conf.d/
    mkdir -p /etc/ovirt-engine/sysprep/
    cp /usr/share/ovirt-engine/conf/sysprep/sysprep.w7x64 /etc/ovirt-engine/sysprep/sysprep.w7x64
    vim /etc/ovirt-engine/sysprep/sysprep.w7x64          # adjust settings

/etc/ovirt-engine/osinfo.conf.d/10-sysprep.properties

::

    os.windows_7x64.sysprepPath.value = /etc/ovirt-engine/sysprep/sysprep.w7x64

    ## Workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1192495
    os.windows_7x64.sysprepFileName.value = sysprep.inf

Restart ovirt-engine:

::

    service ovirt-engine restart

Sysprep
-------

The following step will generalize your Goldimage VM. You will
"partially loose" your Goldimage VM, so might wanna create a VM
snapshot beforehand.
Sysprep can be run as local Administrator or as a Domain
Administrator. Please disconnect all network shares - they might cause
problems when generalizing.

Programm: ``C:\Windows\system32\sysprep\sysprep.exe``

Please choose the following options:

English:

::

        System Cleanup Action: 
            Enter Out-of-Box-Experience (OOBE)
            [X] Generalize
        Shutdown Options:
            Shutdown

German:

::

        Systembereinigungsaktion: 
            Out-of-Box-Experience (OOBE) für System aktivieren
            [X] Veralgemeinern
        Optionen für Herunterfahren
        Herunterfahren

Afterwards, the VM will be generalized and then turned off. Then the VM
is ready to create a RHEV/Ovirt VmTemplate.

RHEV/Ovirt VmTemplate
---------------------

In RHEV/Ovirt WebAdmin, right-click on the VM and create a new
VmTemplate. Then, adjust
`virtesk-vm-rollout.conf <virtesk-vm-rollout-config.html#room-definitions-section-room-room01>`__
to use the new template: ``template_name = myNewVmTemplate``.

Rolling out virtual rooms
-------------------------

Now you can use the `tools for virtual rooms <virtesk-vm-rollout.html>`__
to create VMs based on this Goldimage.

``virtesk-vm-rollout`` will run `Windows Unattended
Setup <autounattend.html>`__.

Re-Use Goldimage
----------------

To Re-Use your Goldimage VM, take the following steps:

-  Restore Goldimage VM to the snapshot that was created before sysprep
-  Install Updates, adjust configuration, install programs as you like
-  Create a fresh Snapshot
-  Run sysprep again to create a new RHEV/Ovirt VmTemplate

Long snapshot chains should be avoided, delete old snapshots from time
to time.

Alternative approach:

-  Roll out a virtual room based on the last Goldimage
-  Take a VM out of this virtual room and use it as new Goldimage
-  Install Updates, adjust configuration, install programs as you like
-  Run sysprep again to create a new RHEV/Ovirt VmTemplate
-  Optional: Delete Goldimage VM

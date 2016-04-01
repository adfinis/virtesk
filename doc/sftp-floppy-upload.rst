.. |br| raw:: html

   <br />

Payload mechanism
===============================

Floppy payloads for VM rollout

--------------

Introduction
------------

The windows sysprep/unattened.xml process requires passing an individual
configuration file (sysprep.inf) to the VM.

This file is passed to the VM inside a floppy image. For passing floppy
images, a few preparations need to be made:

-  `Installing a hook script on all ovirt
   hypervisors <#installing-vdsm-hook-floppy>`__
-  `Configuring an sftp server for hosting floppy
   images <#configuring-an-sftp-server-for-hosting-floppy-images>`__
-  (Installing mtools for floppy image generation)

Please note: the following has only been tested using Ovirt Linux hosts
(RHEL/CentOS 6.x). It never has ben tested on ovirt hypervisor hosts.
SELinux has not been tested.

Installing vdsm-hook-floppy
---------------------------

Floppies are not a standard Ovirt feature. However, floppy support can
be added using a hook script.

Steps done on Ovirt hosts:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Install vdsm-hook-floppy on all your Ovirt hosts:

::

    [root@host ~]# yum install vdsm-hook-floppy

The package ``vdsm-hook-floppy`` might not be available for RHEL 6.x. If
this is the case, simply install the RPM from Ovirt or EPEL
repositories.

Steps done on Ovirt manager:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On the Ovirt manager, we need to add an custom property for floppy
configuration to Ovirt.

::

    # First, take a look at the existing configuration:
    [root@manager ~]# engine-config -g UserDefinedVMProperties
    UserDefinedVMProperties:  version: 3.0
    UserDefinedVMProperties:  version: 3.1
    UserDefinedVMProperties:  version: 3.2
    UserDefinedVMProperties:  version: 3.3
    UserDefinedVMProperties:  version: 3.4
    UserDefinedVMProperties:  version: 3.5

If your output looks like above, e.g. no existing value is set, then you
can simply run the following command to add the floppy custom property:

::

    [root@manager ~]# engine-config -s UserDefinedVMProperties='floppy=^.*$' --cver=3.5

However, if other custom properties exist, then your output will look
similar to this:

::

    [root@manager ~]# engine-config -g UserDefinedVMProperties
    UserDefinedVMProperties:  version: 3.0
    UserDefinedVMProperties:  version: 3.1
    UserDefinedVMProperties:  version: 3.2
    UserDefinedVMProperties:  version: 3.3
    UserDefinedVMProperties:  version: 3.4
    UserDefinedVMProperties: hostusb=^0x[0-9a-fA-F]{4}:0x[0-9a-fA-F]{4}$ version: 3.5

Here, we need to append our custom property to the existing custom
properties. Multiple custom properties are seperated using semicolons:

::

    # appending floppy=^.*$
    [root@manager ~]# engine-config -s UserDefinedVMProperties='hostusb=^0x[0-9a-fA-F]{4}:0x[0-9a-fA-F]{4}$;floppy=^.*$' --cver=3.5

An engine restart is required for the setting to take effect.

::

    [root@manager ~]# service ovirt-engine restart

Verification using Ovirt web interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. log in to Ovirt web interface using an administrator account
#. choose a VM and edit its properties.
#. in the edit dialog, navigate to the *custom properties* tag
#. Now you should be able to add the *floppy* custom property to VMs.
#. click on *Cancel* (we don't want to save our changes).

If you really do want to test that floppies do work, a few more steps
are necessary:

#. Put a floppy image on a file system accessible by your ovirt hosts.
   This can be a local filesystem (then you need to pin your VM to this
   particular host),
   or also an NFS share accessible and mounted by your ovirt host.
   The floppy image needs to be accessible (read-write) by user qemu /
   group kvm,
   and SELinux needs to be disabled/permissive.
#. Adjust the floppy custom property in the VM edit dialog.
   Insert the full path to the floppy image as seen by the ovirt host
   where the VM will be run.
#. Run the VM.
#. Now the image should be accessible as a floppy drive inside the VM.

Configuring an sftp server for hosting floppy images
----------------------------------------------------

The `VM rollout script <amoothei-vm-rollout.md>`__ needs a way to upload floppy images, so that the images are accessible by the ovirt hosts afterwards. The `VM rollout script <amoothei-vm-rollout.md>`__ uses sftp to upload floppy images, and the Ovirt hosts use NFS to access the floppy images.

Choosing a floppy image location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The image location needs to be accessible by all ovirt hosts. You can for example choose a location on an NFS server and then make sure that this NFS share is mounted on all Ovirt hosts. |br|
But we don't need to create a new NFS share for this, we can reuse an
existing one. Here we use the NFS share where the ISO images are stored.

::

    [root@host ~]# mount | grep nfs
    [...]
    nfs-server:/path/to/iso/share on /rhev/data-center/mnt/mountpoint type nfs (rw,soft,nosharecache,timeo=600,retrans=6,nfsvers=4,[...])
    [...]

Now, we simply store our floppy images in a subdirectory of the ISO NFS
share:

::

    [root@host ~]# mkdir /rhev/data-center/mnt/mountpoint/floppy

We will need those paths later, so lets assign a name to them:

::

    # Floppy directory (as seen by all Ovirt Linux hosts)
    $FLOPPY_LOCATION_NFSCLIENT := /rhev/data-center/mnt/mountpoint/floppy

    # Floppy directory (as seen by the NFS-Server and SFTP-Server)
    $FLOPPY_LOCATION_NFSSERVER := /path/to/iso/share/floppy   

Both paths point to the same directory, the directory where the floppy
images shall be stored.

Setting up sftp access to the floppy image location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sftp server can be any linux machine with access to
nfs-server:$FLOPPY\_LOCATION\_NFSSERVER

Here we assume that the nfs-server is running linux and that we choose
the nfs-server as sftp-server.

sftp is built-in into OpenSSH. With a chroot we do lock down sftp
access.

Creating a new user:

::

    [root@sftp-server] adduser -s /bin/false sftp-floppy-upload

No password needs to be configured, we will set up ssh keys later.

Creating a chroot directory:

::

    [root@sftp-server] mkdir -p /srv/floppy_chroot

/etc/ssh/sshd\_config:

::

    Subsystem sftp internal-sftp

    Match User sftp-floppy-upload
            ForceCommand internal-sftp
            ChrootDirectory /srv/floppy_chroot/

This jails the user sftp-floppy-upload into /srv/floppy\_chroot/ and makes sure that sftp-floppy-upload can only use sftp and doesn't have shell access. |br|

Apply changes:

::

    [root@sftp-server] service sshd restart

Setting up ssh-keys:

::

    [root@sftp-server] # mkdir /home/sftp-floppy-upload/.ssh
    [root@sftp-server] # vim /home/sftp-floppy-upload/.ssh/authorized_keys
                            ... copy paste ssh keys...
    [root@sftp-server] # chmod 700 /home/sftp-floppy-upload/.ssh
    [root@sftp-server] # chmod 600 /home/sftp-floppy-upload/.ssh/authorized_keys
    [root@sftp-server] # chown -R sftp-floppy-upload:sftp-floppy-upload /home/sftp-floppy-upload/
    [root@sftp-server] # restorecon -r -v /home/sftp-floppy-upload/.ssh/

OpenSSH has some very restrictive settings regarding the
``ChrootDirectory`` directive. This prevents us from chrooting into
``$FLOPPY_LOCATION_NFSSERVER`` directly, so we have to work with
bind-mounts:

::

    [root@sftp-server] # vim /etc/fstab
    $FLOPPY_LOCATION_NFSSERVER  /srv/floppy_chroot/floppy  none    bind    0 0

    [root@sftp-server] # mount /srv/floppy_chroot/floppy

Of course fstab doesn't knows variables, so you do have to put the
actual path instead of $FLOPPY\_LOCATION\_NFSSERVER into fstab.

Now let's fix the permissions. The qemu process needs read-write access
to all floppy images, and sftp-floppy-upload need to put and to remove
floppy images.

::

    [root@sftp-server] chown sftp-floppy-upload:kvm $FLOPPY_LOCATION_NFSSERVER 
    [root@sftp-server] chmod 770 $FLOPPY_LOCATION_NFSSERVER

This way, both sftp-floppy-upload and qemu (though group kvm) have
access to $FLOPPY\_LOCATION\_NFSSERVER - but nobody else. The `VM
rollout script <amoothei-vm-rollout.md>`__ will then later put floppy
images with permissions 0666, this way qemu gets read-write access to
the floppy images.

Now, you should be able to list/put/remove files using the following
command:

::

     [user@some-client] sftp -i ssh-private-key sftp-floppy-upload@sftp-server

Troubleshooting
---------------

Duplicate floppy drive
^^^^^^^^^^^^^^^^^^^^^^

Ovirt error message:

::

    VM [...] is down with error. Exit message: internal error process exited while connecting to monitor: qemu-kvm: -drive file=[...],if=none,id=drive-fdc0-0-0,format=raw: Duplicate ID 'drive-fdc0-0-0' for drive

Explanation: Two floppies are inserted into the virtual floppy drive.
That doesn't work. This happens if ovirt decides on its own to add
another floppy image, because ovirts wants to run its own version of an
sysprep/autounattend process. A quick workaround is to temporarily
change the operating system of the virtual machine to some non-windows
OS. If ovirt thinks the VM is running linux, then it won't insert
floppies on its own.

VM fails to run
^^^^^^^^^^^^^^^

If a VM with a floppy configured using the custom property fails to run,
carefully check the floppy image:

-  Is the floppy image accessible by the ovirt host on which the VM
   should be started?
-  File permissions of the floppy image:

   -  read-write permissions are required for user qemu (or group kvm)
   -  SELinux must be disabled

-  Is the path to the floppy image correct?

Alternative payload mechanisms
------------------------------

A lot of mechanisms for injecting a payload into an ovirt VM were
evaluated, but all have their problems:

-  Passing Unattended.xml content through API:

   -  length limit of 16KB (our files were larger, after
      xml-in-xml-encoding)
   -  XML(Unattended.xml) inside XML(REST API) caused problems with some
      characters

-  Payload mechanism through API:

   -  similar problems
   -  http://www.ovirt.org/Features/VMPayload

-  CDROM / ISO image for injecting payload:

   | This was our old implementation. Amoothei-vm-rollout had ssh access
     to the NFS
   | server hosting the ISO images, and the ISOs were generated directly
     on the NFS
   | server using genisoimage.

   | The implementation was insecure and suffered from a general security
   | problem:

   | All ISOs are accessible to all PowerUsers. So the users of the
     PowerUserPortal
   | can access the ISOs containing the Unattended.xml file, and extract
     the
   | secret information (Domain Join credentials, ...) from it.
   | Because of this, we couldn't use the self-service features of Ovirt
     if
   | it was running our VDI implementation.
 

-  Floppy image for injecting payload:

   This article. Complicated, but it works.

See also:
---------

-  `Ovirt OSinfo settings <goldimage.html#ovirt-os-info-settings>`__

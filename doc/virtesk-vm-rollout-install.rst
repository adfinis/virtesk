Installing VM rollout tools
=========================================

Overview
--------

To run virtesk-vm-rollout, the system must be prepared first:

-  Installing virtesk-vm-rollout
-  Minimal configuration
-  Setting up `payload injection mechanism <sftp-floppy-upload.html>`__
-  Configuring virtual rooms

Installation
------------

Installation has been tested on CentOS 7. Fedora >= 20 should work as
well. RHEL 6 / CentOS 6 might not work (Code requires python 2.7)

Dependencies:

::

    yum install ovirt-engine-sdk-python python-mako mtools

Cloneing git repository:

::

    cd /opt
    git clone http://path.to.git.repository/virtesk-vdi.src.git

.. raw:: html

   <!---
   FIXME: git path above
   -->

Bash search path: ``/etc/profile.d/virtesk-vm-rollout.sh``

::

    pathmunge /opt/virtesk-vdi.src/virtesk-vm-rollout after

Minimal configuration
---------------------

::

    mkdir /etc/virtesk-vdi/
    mkdir /var/log/virtesk-vdi/

    # SSL Certificyte of Ovirt engine Certificate Authority 
    vim /etc/virtesk-vdi/ca.crt
    # Template File for Windows Unattended Setup configuration file
    vim /etc/virtesk-vdi/Autounattend-production.xml.template
    # Logging settings
    vim /etc/virtesk-vdi/logging.conf
    # Definitions of virtual rooms:
    vim /etc/virtesk-vdi/virtesk-vm-rollout.conf

Details are documented `here <virtesk-vm-rollout-config.html>`__.

Setting up payload injection mechanism
--------------------------------------

For rolling out virtual rooms, a payload injection is necessary.

Payload injection is done by creating floppy images containing
``a:\sysprep.inf``, uploading them using SFTP, and attaching them to
RHEV/Ovirt VMs using vdsm-hook-floppy.

The initial setup is quite complicated, but it has to be done only once,
afterwards it will "just work".

Detailed instructions can be found `here <sftp-floppy-upload.html>`__.

Testing
-------

After initial installation and after the configuration of at least one
virtual room, run the following command to check if the config is valid
and if tools do work in general:

::

    virtesk-virtroom-show room01

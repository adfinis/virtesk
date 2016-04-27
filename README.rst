.. |br| raw:: html

   <br />


Virtesk-VDI
============

Virtesk-VDI is an Open Source VDI solution. It allows to run virtual desktops
in a RHEV/Ovirt environment seamlessly. The virtual desktops are displayed on thin clients
in physical rooms. You can manage both the virtual desktops and the physical thin clients
efficiently using the well-aligned tool collection.


It is well-suited to virtualize workplaces in educational environments.

The technical building blocks are:

* Red Hat Enterprise Virtualization (RHEV) / Ovirt Virtualization
* Spice VDI protocol
* RHEL / CentOS for infrastructure services
* Fedora Linux for thin clients
* Active Directory (or Samba4) for Windows domain services
* Windows VDI desktops


Documentation is available `here <https://docs.adfinis-sygroup.ch/public/virtesk/>`__.

Features
---------

Thin client user experience
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thin clients are very easy to use:

1. Turn thin client on
2. Login directly on virtual Windows desktop
3. Work
4. Turn thin client off

Features:

* Virtual Windows desktop - feels like a native Windows desktop
* USB redirect
* Audio: headphones, loudspeakers, microphones
* One single login - no need to enter credentials twice
* Comfortable thin client devices - small and silent

Thin client administration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Virtesk-VDI features a fully automated network rollout of thin clients.

The following remote administration features for thin clients are available:

* Remote control / remote scripting (Tool tc_ssh)
* Screenshots (Tool tc_screenshot)
* Unattended Upgrades / Re-Installations (Tool tc_rollout_kexec)

Virtual Rooms
~~~~~~~~~~~~~~
Virtesk-VDI features virtual Windows desktops organized in virtual rooms.

Virtual rooms are useful for educational institutions - physical rooms are mapped to virtual rooms. This is useful when combined with 3rd party classroom management and monitoring software like iTalc, UCS\@School, MasterEye, ...

Instant switching of virtual rooms is possible. For example, one set of VMs can be used for normal teaching, and a dedicated set of secure VMs can be assigned for exams.

The 1:1-mapping from thin clients to desktop VMs is controlled through a postgres database.


Application and desktop maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A master VM (the "gold image") is used for application installation and desktop configuration. This master VM can then be cloned as often as necessary.

A set of tools (virtesk-virtroom-rollout and friends) helps to simplify and automate the necessary tasks. Scripting and automation features like automatic Windows domain join are available.


Nightly desktop reset
~~~~~~~~~~~~~~~~~~~~~

For situations where clearly-defined centrally managed workplaces are desired, the nightly desktop reset feature comes in handy:

* A snapshot is created upon VM creation
* Every night, the VMs is set back to snapshot state

This is useful to reduce time and effort spent by your IT support team: Desktops are always in a well defined state, divergence of desktops is avoided, and leftovers from old user sessions are cleaned up.


Requirements
--------------

* Virtualization hardware (~ 4GB Ram per workplace), shared storage attached through iscsi or FibreChannel
* RHEV/oVirt 3.5.x
* Active Directory (or Samba 4) for Windows domain features
* A supported OS for virtual Desktops ( stable: Windows 7; Windows 10 support is underway)
* Thin clients: Any linux compatible (x86 or x86_64, must be supported by Fedora Linux) hardware can be used. Usually, small, silent and low power thin client devices are used; However, it is also possible to re-use old desktop computers as thin clients
* Infrastructure server VM (part of Virtesk-VDI)

Bird's eye view of operation / installation
-------------------------------------------

The steps to introduce Virtesk-VDI are more or less:

* Preparing RHEV/Ovirt for VDI operation
* Thin clients: Seting up Virtesk-VDI infrastructure services, including a Fedora Linux mirror, a network rollout infrastructure, scripts for unattended Fedora installations based on Kickstart, and a postgres database for VM-to-thin-client-mapping.
* Installing virtesk-tc-tools for thin client remote management
* Installing a Windows 7 master VM ("gold image")
* Setting up the Windows unattended setup process for VM creation and for automatic Windows domain join
* Setting up virtesk-virtroom-tools for virtual room management
* Creating a network concept, including naming standards and ip-address conventions



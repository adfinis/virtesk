.. |br| raw:: html

   <br />


Amoothei-VDI
============

Amoothei-VDI is a Open Source VDI solution designed with thinclients and virtual rooms in mind.

It is well-suited to virtualize workplaces in educational environments.

The technical foundation is formed by:

* Red Hat Enterprise Virtualization (RHEV) / Ovirt Virtualization
* Spice VDI protocol
* RHEL / CentOS for infrastructure services
* Fedora Linux for thinclients 
* Active Directory (or Samba4) for Windows Domain Services 
* Windows 7 VDI Desktops


Documentation is available `here <https://docs.adfinis-sygroup.ch/adsy/amoothei/html/>`__.

Features
---------

Thinclient User Experience
~~~~~~~~~~~~~~~~~~~~~~~~~~

Thinclients are very easy to use:

1. Turn thinclient on
2. Login directly on virtual Windows desktop
3. Work
4. Turn thinclient off

Features:

* Virtual Windows desktop - feels like a native Windows desktop
* USB redirect
* Audio: headphones, loudspeakers, microphones
* One single login - no need to enter credentials twice
* Comfortable thinclient devices - small and silent

Thinclient Administration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Amoothei-VDI features a fully automated network rollout of thinclients.

The following remote administration features for thinclients are available:

* Remote control / remote scripting (Tool tc_ssh)
* Screenshots (Tool tc_screenshot)
* Unattended Upgrades / Re-Installations (Tool tc_rollout_kexec)

Virtual Rooms
~~~~~~~~~~~~~~
Amoothei-VDI features virtual Windows desktops organized in virtual rooms.

Virtual rooms are useful for educational institutions - physical rooms are mapped to virtual rooms. This is useful when combined with 3rd party classroom management and monitoring software like iTalc, UCS\@School, MasterEye, ...

Instant switching of virtual rooms is possible. For example, one set of VMs can be used for normal teaching, and a dedicated set of secure VMs can be assigned for exams.

The 1:1-mapping from thinclients to desktop VMs is controlled through a postgres database.


Application and desktop maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A master VM (the "Goldimage") is used for Application installation and desktop configuration. This master VM can then be cloned as often as necessary.

A set of tools (amoothei-virtroom-rollout and friends) helps to simplify and automate the necessary tasks. Scripting and automation features like automatic Windows Domain Join are available.


Nightly desktop reset
~~~~~~~~~~~~~~~~~~~~~

For situations where clearly-defined centrally managed workplaces are desired, the nightly desktop reset feature comes handy:

* A snapshot is created upon VM creation
* Every night, the VMs is set back to snapshot state

This is useful to reduce time and effort spent by your IT support team: Desktops are always in a well defined state, divergence of desktops is avoided, and leftovers from old user sessions are cleaned up.


Requirements
--------------

* Virtualization Hardware (~ 4GB Ram per workplace), shared storage attached through iscsi or FibreChannel
* RHEV/oVirt 3.5.x
* Active Directory (or Samba 4) for Windows Domain features
* A supported OS for virtual Desktops ( stable: Windows 7; Windows 10 support is underway)
* Thinclients: Any linux compatible (x86 or x86_64, must be supported by Fedora Linux) hardware can be used. Usually, small, silent and low power thinclient devices are used; However, it is also possible to re-use old desktop computers as thinclients
* Infrastructure server VM (part of Amoothei-VDI)

Birdeye view of operation / installation
----------------------------------------

The steps to build an Amoothei-VDI thinclient are more or less:

* Preparing RHEV/Ovirt for VDI operation
* Thinclients: Seting up Amoothei-VDI infrastructure services, including a Fedora Linux mirror, a network rollout infrastructure, scripts for unattended Fedora installations based on Kickstart, and a postgres database for VM-to-thinclient-mapping.
* Installing amoothei-tc-tools for thinclient remote management
* Installing a Windows 7 Master VM ("Goldimage")
* Setting up the Windows Unattended Setup process for VM creation and for automatic Windows Domain Join
* Setting up amoothei-virtroom-tools for virtual room management
* Creating a network concept, including nameing standards and ip-address conventions



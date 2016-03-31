.. |br| raw:: html

   <br />

Thinclient-Rollout using Kickstart
==================================


**Goal - perfect rollout experience**


#. Start a thinclient, boot from network
#. Choose what you wanna do in a small graphical boot loader menu
   (optional)
#. The thinclient installation will run completely unattended.
#. After 10 minutes (30 minutes on very old hardware) the installation
   and configuration is completed
#. The thinclient reboots itself
#. The thinclient connects to the virtual machine
   `assigned <tc-vm-mapping.md>`__ to it
#. The thinclient is ready, users can work

The amount of data transferred over the network is quite small (1000M - 2000M, estimated value), so its perfectly possible to roll out several hundred thinclients at a time over a single gigabit uplink. |br|
Everything is completely scripted (no computer images!), therefore, the rollout process and the thinclient system can be flexible adapted for new needs and new features. |br|
Experienced system administrators dont need to be on-site for thinclient rollout, remote rollout using Wake-On-Lan is possible. Instead of PXE network booting, thinclients can also be re-installed using ssh and `kexec <amoothei-tc-tools.html#tc_kexec>`__.


.. warning:: WARNING: DATA LOSS |br| The provided sample kickstart file will ERASE everything on all hard drives and on all usb drives on any computer where a thinclient rollout is attempted. This is indented this way (thinclients dont contain any data, so it's ok).

Background
----------

There are several techiques for fully automated installation of an
operating system:

-  **Unattended Setup** for Microsoft Windows
-  **Preseed** for Debian GNU/Linux
-  **Kickstart** for Red Hat Enterprise Linux, CentOS, Fedora, ...

They all use a configuration file for scripting the installation process. Normally, the goal is to make sure the operating system gets installed without any user or sysadmin interaction. |br|
In amoothei-vdi, a network-based kickstart-installation of Fedora 22 is used to deploy and configure thinclients. |br|
The kickstart script file contains a very large post-section, written in bash. It contains all thinclient configuration files (inlined using bash-here-documents). It also makes sure the minimalistic desktop interface is completely locked down, to make sure that students cannot do anything else besides accessing the assigned virtual machine.


PXE-Setup, Network Boot, Fedora Mirror, ...
-------------------------------------------

Documented `here <amoothei-infrastructure-server.html>`__.

Sample Kickstart File
---------------------

Located at: ``sample_config/tc_rollout.ks``

Alot of adjustment needs to be done to make the kickstart file work in a new environment. |br|
The sections needing adjustmend are marked with ``# ADJUST``.

All references to ``infrastructure-server`` need to be replaced with the
actual FQDN of your infrastructure server.

The thinclient software, *amoothei-tc-connectspice*, needs to be
configured as described `here <amoothei-tc-connectspice.md>`__.

Adapting the sample kickstart file isn't easy, and if you are completely new to kickstart, it is actually quite hard. Don't give up, everyone can learn PXE / network installation / kickstart! |br|
For analyzing kickstart problems, remote logging is useful. On a properly configured `infrastructure server <amoothei-infrastructure-server.md>`__, logfiles are available at ``/var/log/remote``. However, not everything is logged, because remote logging is only done in stage 2 of the Fedora installer.

Kickstart literature
--------------------

Red Hat provides alot of documentation for Red Hat Enterprise Linux
`here <https://access.redhat.com/documentation/en/red-hat-enterprise-linux/>`__.

The *Installation Guide*, the *System Administrator's Guide*, *Networking Guide* provide alot of information about network boot,  network installation, systemd, etc. |br|
Most of the documentation for RHEL7 is also valid for Fedora 22/23.

Kickstart documentation is available
`here <https://github.com/rhinstaller/pykickstart/blob/master/docs/kickstart-docs.rst>`__.

Kickstart boot options are documented
`here <https://rhinstaller.github.io/anaconda/boot-options.html#kickstart>`__.

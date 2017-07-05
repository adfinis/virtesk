.. |br| raw:: html

   <br />

Manageing thinclients efficiently
===============================================


Introduction
------------

virtesk-tc-tools is a collection of utilities for system administrators. |br|
They to help to automate the tasks that occur when managing a lot of thinclients. |br|
|br|
Features:

-  Remote access using SSH
-  Scripting
-  Screenshots
-  Kickstart re-installation using SSH + kexec

Installation
------------

Cloneing git repository:

::

    cd /opt
    git clone http://path.to.git.repository/virtesk-vdi.src.git

.. raw:: html

   <!---
   FIXME: git path above
   -->

Bash search path: ``/etc/profile.d/virtesk-tc-tools.sh``

::

    pathmunge /opt/virtesk-vdi.src/virtesk-tc-tools after

Configuration
-------------

All config file locations are relative to the environment variable ``$VIRTESK_TC_TOOLS_CONF_DIR``. |br|
This variable defaults to ``/etc/virtesk-vdi/``

The config files are sourced by bash scripts, e.g. they have to be valid
bash shell files.

First, the main config file (mandatory) is sourced, and then, the individual config file (optional) is sourced as described below. |br|
This allows to specify default values in the main config file, and to overwrite them later if necessary.

Main Config File
~~~~~~~~~~~~~~~~

``${VIRTESK_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf``:

::

    # DEVELOPER_MODE=0 =====> quiet mode
    # DEVELOPER_MODE=1 =====> verbose debug messages
    DEVELOPER_MODE=0

    # Domain appended to thinclient short names
    TC_DOMAIN=myorganization.mydomain

    # SSH options for tc_ssh
    SSH_GLOBAL_OPTS="-q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=4 -i /etc/virtesk-vdi/virtesk-thinclient-ssh-private-key-id_rsa"

    # Commands to run on a thinclient in order
    # to re-install itself using kexec and kickstart
    # Please adjust the URLs to point to the correct locations
    # on your infrastructure server.
    # Kernel commandline should be the same as when doing PXE rollout.
    ROLLOUT_CMDLINE='rm vmlinuz; rm initrd.img; wget http://infrastructure-server/tftpboot/fedora22-x86_64-pxeboot/vmlinuz; wget http://infrastructure-server/tftpboot/fedora22-x86_64-pxeboot/initrd.img; kexec -l vmlinuz --initrd=initrd.img --reset-vga --append="net.ifnames=0 enforcing=0 inst.ks=http://infrastructure-server/mirror/private/thinclients/kickstart/tc_rollout.ks"; shutdown -r now'

    # Commands to run on a thinclient in order to generate a screenshot
    # and to write it to standart output.
    SCREENSHOT_CMDLINE="DISPLAY=:0 xwd -root | convert  - png:-"

    # Directory where screenshots shall be stored.
    SCREENSHOT_DIR=/screenshot

Sample config file: See ``sample_config/virtesk-tc-tools.conf``.

SSH Key
~~~~~~~

The SSH private key (used by virtesk-tc-tools) and the SSH public key (deployed to thinclients in the kickstart post section) must match. |br|
|br|
A new private/public ssh keypair can be created like this:

::

    [test@testsystem ~]$ ssh-keygen
    Generating public/private rsa key pair.
    Enter file in which to save the key (/home/test/.ssh/id_rsa): virtesk-thinclient-ssh-private-key-id_rsa
    Enter passphrase (empty for no passphrase): 
    Enter same passphrase again: 
    Your identification has been saved in virtesk-thinclient-ssh-private-key-id_rsa.
    Your public key has been saved in virtesk-thinclient-ssh-private-key-id_rsa.pub.
    The key fingerprint is:
    5a:e2:d3:2e:be:dd:b4:ea:f7:bd:7b:a3:52:7f:a5:14 test@testsystem
    The key's randomart image is:
    +--[ RSA 2048]----+
    |                 |
    |                 |
    |                 |
    |              E  |
    |      . S      . |
    |     . =     .. .|
    |      + . . .....|
    |      .+ o.o ..oo|
    |     .o+=oo.o.=+o|
    +-----------------+

Afterwards, copy the private key to ``/etc/virtesk-vdi/virtesk-thinclient-ssh-private-key-id_rsa``, 
and paste the public key into the kickstart post section (search for ``authorized_keys`` in the kickstart file). |br|


Individual config file
~~~~~~~~~~~~~~~~~~~~~~

After sourcing the main config file, the optional individual config file is sourced. Individual configuration will override the main configuration.

This allows you to create custom instances (see
`below <#custom-tool-instances>`__) of the TC tools if nessesary, and to
provide a custom configuration for them.

-  individual config file location:
   ``${VIRTESK_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf.dir/${PROGNAME}.conf``
-  ``PROGNAME=`basename "$BASH_SOURCE"```
-  Examples:

   -  Tool ``tc_ssh`` ---> individual config file:
      ``${VIRTESK_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf.dir/tc_ssh.conf``
   -  Tool ``tc_screenshot`` ---> individual config file:
      ``${VIRTESK_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf.dir/tc_screenshot.conf``
   -  Tool ``tc_rollout_kexec`` ---> individual config file:
      ``${VIRTESK_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf.dir/tc_rollout_kexec.conf``
   -  Custom tool ``tc_my_custom_tool`` ---> individual config file:
      ``${VIRTESK_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf.dir/tc_my_custom_tool.conf``

Tools
-----

tc\_ssh
~~~~~~~

Open an interactive shell on a thinclient, or run commands on a thinclient.

Syntax:

::

    tc_ssh <thinclient> [ssh-args]                     # interactive shell
    tc_ssh <thinclient> [ssh-args] -- remote_command   # execute remote command

``<thinclient>`` can be specified as a short host name (myorganization.mydomain will be appended automatically), as a fully qualified domain name, or as an IPv4 address. |br|
Example: Open interactive root-shell on mytc.myorganization.mydomain:

::

    tc_ssh myTC                               
    # or
    tc_ssh mytc.myorganization.mydomain
    # or
    tc_ssh mytc.myorganization.mydomain -l root
    # or
    tc_ssh 192.0.2.240                              # (myTC has IP 192.0.2.240)

Example: Open interactive shell as user vdiclient:

::

    tc_ssh myTC -l vdiclient 

Example: running command(s):

::

    # single command as root:
    tc_ssh myTC -- uname -a

    # single command as user vdiclient:
    tc_ssh myTC -l vdiclient -- uname -a

    # running multiple commands:
    tc_ssh myTC -- "killall gxmessage && sleep 20; killall remote-viewer && sleep 5; killall gxmessage"

The last example has the following effect on the thinclient: If not yet
connected, it will connect to its assigned VM, then the connection will
be terminated, and then it will connect again to the assigned VM. See
`Tipps and Tricks <#manageing-thinclients-tipps-and-tricks>`__ for
details.

Example: shutdown all thinclients in your organization:

Put all thinclient names into a text-file ``all-thinclients.txt``, one
thinclient name per line:

::

    room01-tc01
    room01-tc02
    [...]
    room02-tc01
    room02-tc02

Run ``tc_ssh`` on all thinclients:

::

    # sequentially
    for TC in $(cat all-thinclients.txt); do tc_ssh $TC -- systemctl poweroff ; done

    # parallel
    for TC in $(cat all-thinclients.txt); do tc_ssh $TC -- systemctl poweroff & done

The sequential and the parallel variant differ by one character only:
``";"`` for the sequential variant, ``"&"`` for the parallel variant.

Security of tc\_ssh: An individual ssh private key is used for
connecting to the thinclients. Only system administrators with access to
this private key will be able to access thinclients. However, the
thinclient identity is not validated, e.g. a man-in-the-middle could
claim to be a thinclient.

tc\_screenshot
~~~~~~~~~~~~~~

Take a screenshot of thinclient ``test01-tc01`` and store it in a PNG
File:

::

    # tc_screenshot test01-tc01 bob-20160315
    Successfully stored a screenshot at /screenshot/bob-20160315/test01-tc01.png.
    -rw-r--r--. 1 root root 236K Mar 15 19:17 /screenshot/bob-20160315/test01-tc01.png

A "session identifier" (here: ``bob-20160315``) is mandatory. It is used to store the screenshots in a well-ordered folder structure.

Taking a lot of screenshots:

::

    for TC in $(cat all_thinclients.txt); do tc_screenshot $TC bob-20160315 & done

Please respect the privacy of your users and don't use this tool for
hidden surveillance.

Screenshots are a valuable tool for quality control: You just deployed a
few hundreds thinclients and you do wanna make sure that every
thinclient is operating correctly. Simply make a screenshot of all of
them. Image viewers like gwenview can display thumbnails of a few
hundreds images at once, and this overview is great for identifying
thinclients with problems.

Diagnostics using thumbnails of alot of TC screenshots:

-  Windows login screen

   -  Thinclient is fine and it is connected to a VM.

-  Gray screen ===> This is the TC user interface.

   -  Try to connect, or reboot the TC.
   -  If the problem persists, inspect logs of virtesk-tc-connectspice.

-  Error / image size is 0 ===> Thinclient is off, so no screenshot
   could be taken.
-  Image resolution wrong, low resolution like 1024x768 ===>

   -  Check monitor cabling
   -  Control xrandr output (using support button on TC)

-  Image resolution correct, but image out of focus ===>

   -  Automatic resolution adjustion using spice-agent didn't work.
   -  This is quite common with freshly deployed windows 7 VMs.
   -  Fix: any of the 3 methods below should help:

      -  fullscreen --> windowed mode --> fullscreen (pressing shift-f11
         twice).
      -  Disconnect and connect again.
      -  Restart thinclient.

   -  If it is a linux VM: The window manager inside the VM needs to
      react to spice resize events. So far only mutter (window manager
      used by GNOME) implements this.

tc\_rollout\_kexec
~~~~~~~~~~~~~~~~~~

Re-Install a thinclient.

Kickstarting a thinclient is so fast that there is no need for a
thinclient upgrade procedure. Instead, we simply re-install thinclients
whenever there is a change to configuration or to
virtesk-tc-connectspice. But we don't want to touch every thinclient by
hand. This tool makes re-installation really easy:

#. make sure TC is running
#. ``tc_rollout_kexec <TC>``

Background: This tools connect to the thinclient and then downloads
kernel/initrd of the fedora installer using http. Then, kexec is used to
load the new kernel/initrd over the running kernel.

Custom tool instances
---------------------

It is often useful to have multiple instances of a tool, each with their
own configuration.

Example situation: You have two kickstart files (The normal one,
``tc_rollout.ks`` and a custom one, ``tc_custom_rollout.ks``). We create
a second rollout tool instance and call it ``tc_custom_rollout``. This
can be done by simply creating a symlink:

::

    ln -s /opt/virtesk-vdi.src/virtesk-tc-tools/tc_rollout_kexec /usr/local/bin/tc_custom_rollout

Now, we can provide a custom configuration in the individual config
file, in
``/etc/virtesk-vdi/virtesk-tc-tools.conf.dir/tc_custom_rollout.conf``:

::

    ROLLOUT_CMDLINE='rm vmlinuz; rm initrd.img; wget http://infrastructure-server/tftpboot/fedora22-x86_64-pxeboot/vmlinuz; wget http://infrastructure-server/tftpboot/fedora22-x86_64-pxeboot/initrd.img; kexec -l vmlinuz --initrd=initrd.img --reset-vga --append="net.ifnames=0 enforcing=0 inst.ks=http://infrastructure-server/mirror/private/thinclients/kickstart/tc_custom_rollout.ks"; shutdown -r now'

The only config change is the name of the kickstart file.

Now we can use our new tool exacly like the normal tool:

::

    tc_custom_rollout test01-tc01

Manageing Thinclients: Tipps and Tricks
---------------------------------------

The following commands are to be run on a TC, using tc\_ssh.

Connect to assigned VM
~~~~~~~~~~~~~~~~~~~~~~

::

    killall gxmessage

If the TC GUI (based on gxmessage) is shown, then this command
terminates the GUI and virtesk-tc-connectspice connects again, that is
it connects to postgres database to determine the assigned VM, it
connects to ovirt manager using REST API to get spice connection
parameters, and then passes them to remote-viewer to initiate a new
spice connection.

If the TC is already connected to a VM, nothing happens.

Disconnect from the VM
~~~~~~~~~~~~~~~~~~~~~~

::

    killall remote-viewer

If remote-viewer is running (that is, the TC is connected), then this
command forces the TC to disconnect. If the TC is not connected, nothing
happens.

Shutdown / Reboot
~~~~~~~~~~~~~~~~~

::

    sudo systemctl poweroff
    sudo systemctl reboot

Initiates a TC shutdown / restart.

X11 Programs
~~~~~~~~~~~~

Create a screenshot:

::

    tc_ssh myTC -l vdiclient -- "DISPLAY=:0 xwd -root | convert  - png:-" > screenshot.png

Run a terminal:

::

    tc_ssh myTC -l vdiclient -- "DISPLAY=:0 xterm &" 

For Developers
~~~~~~~~~~~~~~

Restart X11 + virtesk-tc-connectspice:

::

    tc_ssh myTC -- "systemctl restart lxdm" 

Simulate a network error (or network delay) during startup:

::

    tc_ssh myTC -- "systemctl restart lxdm; iptables -A OUTPUT -p udp -j DROP; sleep 6; iptables -D OUTPUT -p udp -j DROP"

Known issues and workarounds
-----------------------------

Graphics corruption and partial rollout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Situation: During a rollout some systems may end up hanging in an X session with grey screen and frozen mouse pointer.
This was seen somewhat consistently seen on HP Elite Desk 800 G1 SFF desktop systems running Intel Q87 chipset,
Intel i5-4570 processors using the integrated HD Graphics 4600 on Fedora 25 with Linux kernel 4.8.5.

In this case a known-good workaround is to force the Anaconda installer into text-only mode which avoided
graphics corruption and resulted in reliable deployment. Add a line 'text' early in the Kickstart file for this.

Kernel panic during kexec
~~~~~~~~~~~~~~~~~~~~~~~~~

Situation: During a rollout through kexec certain client types may end up with kernel panics.
This was seen consistently on a combination with systems running on Intel H55 chipsets, Intel i5 650 processors
using the integrated HD Graphics on Fedora 25 with Linux kernel 4.8.5.

In this case a known workaround was to append "--real-mode" to the kexec loading parameter (kexec -l).

Inadequate screensaver timeout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Situation: Depending on the used versions of Fluxbox, LXDM and X.org, the
default timeout for screen powerdown may not equal your requirements. - Also
default values do vary in between disttribution versions thus you might want
to adapt it to your needs.

A reliable to customize that timeout is to add the following line in the
kickstart file in the section where /home/vdiclient/.fluxbox/init gets created
and as the last xset command add i.e. "/usr/bin/xset s 3600" which will ensure,
the display gets dark after 1 hour.

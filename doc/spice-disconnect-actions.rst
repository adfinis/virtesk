.. |br| raw:: html

   <br />

Spice disconnect actions
========================


Introduction
------------

What shall happen upon disconnect of a spice connection?

- Lock (default action): The Windows Lockscreen is shown. The user is still logged in, but using the "Switch User" functionality of Windows, other users can work on this desktop.
- Logoff: The user is logged out.
- Shutdown: The virtual machine is shut down.
- Reboot: The virtual machine is rebooted.
- Noop: Nothing happens - The user is still logged in, and the session is accessible directly.

Situation in Ovirt 3.6
----------------------

Spice disconnect actions are a new feature of Ovirt 3.6. Ovirt Hosts must be running RHEL 7.x / CentOS 7.x - because in RHEL 6.x / CentOS 6.x, this feature is not supported.

Amoothei-VDI was not tested with Ovirt 3.6 so far. 


Situation in "official Ovirt 3.5 releases"
------------------------------------------

This feature is not available for Ovirt 3.5.

When a spice connection is disconnected, the desktop is always locked. This cannot be configured.

Situation in "patched Ovirt 3.5"
--------------------------------

The spice disconnect features have been backported to Ovirt 3.5. This article documents this backport.

This backport has been tested with:

- Ovirt Manager: oVirt Engine Version: 3.5.6.2-1
- Ovirt Virtualization Hosts: CentOS 6.x with a patched version of vdsm-4.16.30-0.el6

Not supported are:

- Ovirt Virtualization Hosts running RHEL 6.x (it should work fine - but Red Hat doesn't support inofficial vdsm daemons)
- Ovirt Virtualization Hosts running CentOS 7.x (Then you should upgrade to Ovirt 3.6 and use the official spice disconnect feature)


How does the backport work?
---------------------------

The new vdsm code from Ovirt 3.6 / CentOS 7 has been backported to Ovirt 3.5 / CentOS 6. No code changes are required for the Ovirt Engine itself - custom VM Properties are used to configure the new feature.


How are spice disconnect actions configured?
--------------------------------------------

This section requries that ovirt is patched as described below.

The feature can be configured graphically using custom VM properties:

.. image:: screenshots/spice-disconnect-actions.*

Custom VM properties:

- spice_disconnect_action: Configures the spice disconnect action: noop/lock/logoff/shutdown/reboot 
- spice_disconnect_waittime_seconds: Time in seconds to wait before taking action. Default value: 2 seconds. Values smaller than 2 are not recommended. Values like 30 seconds work fine, larger values have not been tested.


The custom VM properties can also be set on VmTemplates and on VmPools.

Changeing custom VM properties "ad hoc" is not supported, the VM must be stopped and then started again to apply the changes.


**Remark:** Sometimes, Ovirt does not save changes to custom VM properties. After changeing custom VM properties, it is recommended to save the changes (e.g. click on [OK] in the Edit window), and then to edit the VM again to check if the changes were saved.


Spice disconnect actions can be used together with `amoothei-virtroom-rollout <amoothei-vm-rollout.html#amoothei-virtroom-rollout>`__, simply by configuring the appopriate spice disconnect action in the VmTemplate.

Installing the patch
--------------------

Ovirt Manager / Ovirt Engine: enabling custom VM properties:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Case 1:** no other custom VM properties exist:

:: 

    # Step 1: checking old value
    
    [root@ovirt-manager ~]# engine-config -g UserDefinedVMProperties 
    UserDefinedVMProperties:  version: 3.0
    UserDefinedVMProperties:  version: 3.1
    UserDefinedVMProperties:  version: 3.2
    UserDefinedVMProperties:  version: 3.3
    UserDefinedVMProperties:  version: 3.4
    UserDefinedVMProperties:  version: 3.5
    
    # Step 2: setting new value
    
    [root@ovirt-manager ~]# engine-config -s UserDefinedVMProperties='spice_disconnect_action=^(noop|lock|logoff|shutdown|reboot)$;spice_disconnect_waittime_seconds=^[0-9]+$' --cver=3.5
    
    # Step 3: restarting ovirt-engine to let the changes take effect:
    [root@ovirt-manager ~]# service ovirt-engine restart
    

**Case 2:** There are other, pre-existing custom VM properties. In this case, we have to seperate them using ``;`` :

::

    # Step 1: checking old value
    
    [root@ovirt-manager ~]# engine-config -g UserDefinedVMProperties 
    UserDefinedVMProperties:  version: 3.0
    UserDefinedVMProperties:  version: 3.1
    UserDefinedVMProperties:  version: 3.2
    UserDefinedVMProperties:  version: 3.3
    UserDefinedVMProperties:  version: 3.4
    UserDefinedVMProperties: hostusb=^0x[0-9a-fA-F]{4}:0x[0-9a-fA-F]{4}$;floppy=^.*$;spice_disconnect_action=^(noop|lock|logoff|shutdown|reboot)$;spice_disconnect_waittime_seconds=^[0-9]+$ version: 3.5
    
    # Step 2: Append new custom VM properties to existing custom VM properties, seperated using ";"
    
    [root@ovirt-manager ~]# engine-config -s UserDefinedVMProperties='hostusb=^0x[0-9a-fA-F]{4}:0x[0-9a-fA-F]{4}$;floppy=^.*$;spice_disconnect_action=^(noop|lock|logoff|shutdown|reboot)$;spice_disconnect_waittime_seconds=^[0-9]+$' --cver=3.5
    
    # Step 3: restarting ovirt-engine to let the changes take effect:
    [root@ovirt-manager ~]# service ovirt-engine restart


Ovirt Virtualization Hosts: Installing patched vdsm RPMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following steps need to be done on each Ovirt Virtualization Linux Host.

It is recommended to put the Ovirt Virtualization Linux host into maintenance mode first.

Without repository (untested):

::

    yum localinstall vdsm-4.16.30-0.el6.spicedisconnectactionsbackport.906.x86_64.rpm

Other vdsm-RPMs might need upgrades as well to satisfy dependencies.


Using a repository:

::

        cat > /etc/yum.repos.d/customrpms-el6.repo << 'ENDOFREPOFILE'
        [customrpms-el6]
        name=Custom RPMs for EL6
        baseurl=http://hostname-of-your-yum-mirror/mirror/public/el6/customrpms-el6/
        enabled=1
        metadata_expire=10
        gpgcheck=0
        skip_if_unavailable=True

        ENDOFREPOFILE

        [root@ovirt-host ~]# yum upgrade vdsm\*

        [...]

        ==============================================================================================================================
         Package                       Arch        Version                                                  Repository           Size
        ==============================================================================================================================
        Updating:
         vdsm                          x86_64      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6      872 k
         vdsm-cli                      noarch      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6       57 k
         vdsm-jsonrpc                  noarch      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6       93 k
         vdsm-python                   noarch      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6      171 k
         vdsm-python-zombiereaper      noarch      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6      3.9 k
         vdsm-xmlrpc                   noarch      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6       22 k
         vdsm-yajsonrpc                noarch      4.16.30-0.el6.spicedisconnectactionsbackport.904         customrpms-el6       24 k

        [...]



Uninstall instructions (untested): Disable the yum repository (``enabled=0`` in ``customrpms-el6.repo``), and then downgrade vdsm:

::

    yum downgrade vdsm vdsm-cli vdsm-jsonrpc vdsm-python vdsm-python-zombiereaper vdsm-xmlrpc vdsm-yajsonrpc


Developer instructions: building patched vdsm RPMs
-------------------------------------------------- 

On a CentOS 6 machine with Ovirt repositories configured:

Install build tools:

::

    yum install rpm-build gcc make rpmdevtools rpmlint createrepo

Install build dependencies:

::

    yum install python-devel  python-netaddr  mom  python-inotify  python-ioprocess  python-pthreading  python-cpopen libnl3  libvirt-python  genisoimage  python-simplejson

Setting up a build user (recommended):

::

    useradd rpmbuild
    su - rpmbuild

Setting up the build environment and install vdsm RPM sources:

::

    [rpmbuild@build-host ~]$ mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    [rpmbuild@build-host ~]$ echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros
    [rpmbuild@build-host ~]$ yumdownloader --source vdsm
    [rpmbuild@build-host ~]$ rpm -i vdsm-4.16.30-0.el6.src.rpm
    warning: user jenkins does not exist - using root
    warning: group jenkins does not exist - using root
    warning: user jenkins does not exist - using root
    warning: group jenkins does not exist - using root
    
The last command places the vdsm sources into ``~/rpmbuild/{SOURCES,SPECS}/``.

The following adjustments need to be done to the vdsm spec file. For your convenience, the ajusted file is provided in ``misc/vdsm-spice-disconnect-actions-backport/vdsm.spec`` .

::

        # Edit spec file
        vim ~/rpmbuild/SPECS/vdsm.spec


Change Release field:

::

        # old value:
        Release:        0%{?dist}%{?extra_release}

        # new value
        Release:        0%{?dist}%{?extra_release}.spicedisconnectactionsbackport.904

Context / Location in spec file:

::

        Name:           %{vdsm_name}
        Version:        4.16.30
        Release:        0%{?dist}%{?extra_release}
        Summary:        Virtual Desktop Server Manager

Increment the version number (here 904) whenever you rebuild the RPMs.

Configure where the patch file is located: Insert the following line:

::

        Patch0:         vdsm-spice-disconnect-actions-backport.patch

Context / Location in spec file:

::

        Group:          Applications/System
        License:        GPLv2+
        Url:            http://www.ovirt.org/wiki/Vdsm
        Source0:        %{vdsm_name}-%{version}.tar.gz
        Patch0:         vdsm-spice-disconnect-actions-backport.patch
        BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


Configure that patches shall be applied using ``patch -p1``: Insert the following line:

::

        %patch0 -p1

Context / Location in spec file:

::

        %prep
        %setup -q
        %patch0 -p1
        %if 0%{?rhel} == 6
        sed -i '/ su /d' vdsm/vdsm-logrotate.conf.in
        %endif


Put the patch in a location where rpmbuild expects it:

::

    cp misc/vdsm-spice-disconnect-actions-backport/vdsm-spice-disconnect-actions-backport.patch ~rpmbuild/SOURCES/


Building RPMs; Building repository metadata from RPMs:

::

    [rpmbuild@build-host ~]$ rpmbuild -ba ~/rpmbuild/SPECS/vdsm.spec 
    
    [rpmbuild@build-host ~]$ createrepo ~/rpmbuild/RPMS/
    Spawning worker 0 with 19 pkgs
    Workers Finished
    Gathering worker results
    
    Saving Primary metadata
    Saving file lists metadata
    Saving other metadata
    Generating sqlite DBs
    Sqlite DBs complete

Copy RPM repository to a webserver:

::

    rsync -rv ~/rpmbuild/RPMS/ root@webserver:/var/www/mirror/public/el6/customrpms-el6/

   
Background: Changes to vdsm daemon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full patch can be found in ``misc/vdsm-spice-disconnect-actions-backport/vdsm-spice-disconnect-actions-backport.patch`` .

::

    diff -pru vdsm-4.16.30/vdsm/clientIF.py vdsm-4.16.30-vdsm-spice-disconnect-actions-backport/vdsm/clientIF.py
    --- vdsm-4.16.30/vdsm/clientIF.py 2015-11-23 16:01:24.000000000 +0100
    +++ vdsm-4.16.30-vdsm-spice-disconnect-actions-backport/vdsm/clientIF.py 2016-04-05 11:45:16.000000000 +0200
    @@ -556,9 +556,10 @@ class clientIF(object):
                                 'authScheme %s subject %s',
                                 phase, localAddr, remoteAddr, authScheme, subject)
                     if phase == libvirt.VIR_DOMAIN_EVENT_GRAPHICS_INITIALIZE:
    -                    v.onConnect(remoteAddr['node'])
    +                    v.onConnect(remoteAddr['node'], remoteAddr['service'])
                     elif phase == libvirt.VIR_DOMAIN_EVENT_GRAPHICS_DISCONNECT:
    -                    v.onDisconnect()
    +                    v.onDisconnect(clientIp=remoteAddr['node'],
    +                                   clientPort=remoteAddr['service'])
                 elif eventid == libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG:
                     action, = args[:-1]
                     v._onWatchdogEvent(action)
    diff -pru vdsm-4.16.30/vdsm/virt/vm.py vdsm-4.16.30-vdsm-spice-disconnect-actions-backport/vdsm/virt/vm.py
    --- vdsm-4.16.30/vdsm/virt/vm.py 2015-11-23 16:01:24.000000000 +0100
    +++ vdsm-4.16.30-vdsm-spice-disconnect-actions-backport/vdsm/virt/vm.py 2016-04-05 11:43:31.000000000 +0200
    @@ -1960,6 +1960,7 @@ class Vm(object):
             self._powerDownEvent = threading.Event()
             self._liveMergeCleanupThreads = {}
             self._shutdownReason = None
    +        self._clientPort = ''
     
         def _get_lastStatus(self):
             # note that we don't use _statusLock here. One of the reasons is the
    @@ -2471,15 +2472,51 @@ class Vm(object):
             except Exception:
                 self.log.error("Reboot event failed", exc_info=True)
     
    -    def onConnect(self, clientIp=''):
    +    def onConnect(self, clientIp='', clientPort=''):
             if clientIp:
                 self.conf['clientIp'] = clientIp
    +            self._clientPort = clientPort
     
         def _timedDesktopLock(self):
    -        if not self.conf.get('clientIp', ''):
    -            self.guestAgent.desktopLock()
    +        # This is not a definite fix, we're aware that there is still the
    +        # possibility of a race condition, however this covers more cases
    +        # than before and a quick gain
    +
    +        if not self.conf.get('clientIp', '') and not self.destroyed:
    +            delay = config.get('vars', 'user_shutdown_timeout')
    +            timeout = config.getint('vars', 'sys_shutdown_timeout')
    +            daction = 'undef'
    +
    +            if 'spice_disconnect_action' in self.conf['custom']:
    +                daction = (
    +                    self.conf['custom']['spice_disconnect_action'].lower()
    +                )
    +
    +            if daction == 'lock' or daction == 'undef':
    +                self.guestAgent.desktopLock()
    +            elif daction == 'logoff':
    +                self.guestAgent.desktopLogoff(True)
    +            elif daction == 'reboot':
    +                self.shutdown(delay=delay, reboot=True, timeout=timeout,
    +                              message='Scheduled reboot on disconnect',
    +                              force=True)
    +            elif daction == 'shutdown':
    +                self.shutdown(delay=delay, reboot=False, timeout=timeout,
    +                              message='Scheduled shutdown on disconnect',
    +                              force=True)
    +            elif daction == 'noop':
    +                pass
    +            else:
    +                self.guestAgent.desktopLock()
    +
    +    def onDisconnect(self, detail=None, clientIp='', clientPort=''):
    +        if self.conf['clientIp'] != clientIp:
    +            self.log.debug('Ignoring disconnect event because ip differs')
    +            return
    +        if self._clientPort and self._clientPort != clientPort:
    +            self.log.debug('Ignoring disconnect event because ports differ')
    +            return
     
    -    def onDisconnect(self, detail=None):
             self.conf['clientIp'] = ''
             # This is a hack to mitigate the issue of spice-gtk not respecting the
             # configured secure channels. Spice-gtk is always connecting first to
    @@ -2494,6 +2531,22 @@ class Vm(object):
             # Multiple desktopLock calls won't matter if we're really disconnected
             # It is not harmful. And the threads will exit after 2 seconds anyway.
             _DESKTOP_LOCK_TIMEOUT = 2
    +
    +        if 'spice_disconnect_waittime_seconds' in self.conf['custom']:
    +            try:
    +                _DESKTOP_LOCK_TIMEOUT = int(
    +                    self.conf['custom']['spice_disconnect_waittime_seconds']
    +                )
    +            except ValueError:
    +                self.log.error(
    +                    "Cannot convert spice_disconnect_waittime_seconds={0} to "
    +                    "int. Proceeding with default value.".format(
    +                        self.conf['custom'][
    +                            'spice_disconnect_waittime_seconds'
    +                        ]
    +                    ),
    +                    exc_info=True)
    +
             timer = threading.Timer(_DESKTOP_LOCK_TIMEOUT, self._timedDesktopLock)
             timer.start()
    


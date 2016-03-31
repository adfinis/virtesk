Security considerations
=====================================

--------------

Virtual machine isolation
-------------------------

Virtual machines can be isolated by putting them into different Ovirt
networks and by applying the usual network security principles.

Thinclients
-----------

**Ovirt REST-API**: ``Thinclient ---> Ovirt Manager (tcp/443)``

-  HTTPs connection; Server certificate is verified. Ovirt AAA is used
   to authenticate the technical user ``ovirt.thinclient@domain`` used
   by thinclients.
-  Used to get access parameters to assigned VM. Only VDI-VMs can be
   accessed by thinclients, other VMs are protected by Ovirt access
   control rules.

**Spice**: ``Thinclient ---> qemu-kvm (tcp/5900-6100)``

-  SSL connections; Certificate fingerprint is retrieved using REST-API,
   fingerprint is verified. **Spice Ticketing** is used by ``qemu-kvm``
   to determine if the client may access.

**Postgres Database**:
``Thinclient ---> infrastructure server (tcp/5432)``

-  SSL connection, client verifies server certificate if configured to
   do so.
-  Server verifies client identity using username/password.
-  Thinclients have only limited, read only database access.

**Remote logging**: ``Thinclient ---> infrastructure server (tcp/512)``

-  Remote logging is not secure. All logging is sent in plain-text over
   the network.
-  No authentication and no encryption is done.
-  The thinclients are logging sensitive data over the network.
-  Mitigation strategies:

   -  Put thinclients in a protected network (see below).
   -  Disable remote logging. Thinclients work fine with local logging
      only - however, remote logging is useful for problem analysis.

| Thinclients do need to store credentials. If those credentials leak,
  the security concept will break down.
| The thinclients themself won't leak their credentials (exception:
  remote logging). However, common network boot techiques usually
  require
| all code and configuration to be accessible unauthenticated, where an
  attacker might retrieve them - see below.

PXE Rollout
-----------

**PXE is insecure.**

Network booting is very convinient. However, PXE is completely insecure.

Recommendations for situations where both security and PXE are needed:

-  **Physical network protection:** The network hardware (switches,
   servers, ...) should be physically protected. Only trusted persons
   shall be allowed to administrate switches or to plug cables into
   switches.
-  **Dedicated rollout network:** A dedicated rollout network is used
   for rollout. System administrators need to switch VLANs (or cables)
   for rollouts. Only devices in the rollout network are allowed to
   access sensitive data on the infrastructure server.
-  **Mixed network, locked-down:** A mixed (trusted and untrusted
   devices, some switch ports accessible by users) is used for both
   daily operation and for rollout. Techiques like private VLANs,
   MAC-to-Swichport binding, physical protection of cables and
   switchports used by thinclients, static ARP table entries and static
   IP adresses are used for network protection. Then, access to the
   infrastructure server (PXE, kickstart) can be granted based on IP
   access rules.

Kexec Rollout
-------------

In the current implementation of ``tc_kexec``, many mechanisms used for
PXE boot are re-used. Therefore, ``tc_kexec`` is affected by the same
security problems.

A secure variant of ``tc_kexec`` could be engineered upon request. The
kernel and initramfs can be transported in a secure way; the kickstart
file, GnuPG keys and SSL CA certificates can be appended to the
initramfs.

Multiple thinclient environments
--------------------------------

If only some, but not all thinclients need to be protected, then the
security recommendations listed above can be applied only for those
thinclients. Please make sure that for this usecase, a dedicated
technical user ``ovirt.secure-thinclients@domain`` is used for the
thinclients that need protection.

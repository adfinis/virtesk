# Introduction
amoothei-vdi is a vdi solution built around Ovirt / Spice / KVM.

amoothei-vdi consists of the following parts:

* [amoothei-tc-connectspice](doc/amoothei-tc-connectspice.md)
    * VDI Software running on thinclients
* [amoothei-tc-kickstart](doc/amoothei-tc-kickstart.md)
    * Automatic thinclient network deployment
    * Based on Fedora Linux
* [amoothei-tc-tools](doc/amoothei-tc-tools.md)
    * Tools for TC remote management
    * tc_screenshot: Take a screenshot of a thinclient
    * tc_kexec: Re-install a thinclient using kexec
    * tc_ssh: open a ssh connection to a thinclient
* [amoothei-infrastructure-server](doc/amoothei-infrastructure-server.md)
    * Infrastructure services for VDI
* [amoothei-vm-rollout](doc/amoothei-vm-rollout.md)
    * Generates VMs for VDI 


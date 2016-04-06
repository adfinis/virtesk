Amoothei-VDI
============

Amoothei-VDI is a collection of tools to build and operate a VDI solution based
on RHEV/oVirt.

Documentation is available [here](https://docs.adfinis-sygroup.ch/adsy/amoothei/html/).


Features
========

Amoothei-VDI covers the following use cases / features:

* amoothei-tc-connectspice: client part running on the thinclient - connects to RHEV/oVirt manager and initiates the spice session
* amoothei-vm-rollout: let's you create a set of Windows VMs to be used by the VDI clients
* amoothei-tc-tools: utilities to mass manage VDI VMs (e.g. take screenshot of every VM, kickstart re-installation using SSH+kexec, etc.)

Intended use case
=================

Amoothei is not restriced to any use case, however we mostly use the following
setup:

* Low-Power Thinclients runinng GNU/Linux (e.g. Fedora, Debian, etc.)
* RHEV/oVirt backend infrastructure providing Windows VDI VMs
* 1:1 matching of Thinclient <-> VM

Requirements:

* RHEV/oVirt 3.4
* GNU/Linux based thinclient with an up to date "remote-viewer" package (with spice support) and Python 2.x

Birdeye view of operation / installation
========================================

Amoothei-VDI doesn't require a study of rocket science, the steps to build an
Amoothei-VDI environment is more or less:

* Setup a thinclient with your prefered GNU/Linux distribution
* Install amoothei-tc-connectspice on the thinclient
* Prepare a VDI VM on your RHEV/oVirt cluster
* Have fun :)
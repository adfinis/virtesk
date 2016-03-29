# Amoothei-VDI: Installing VM rollout tools


------------------
## Overview
To run amoothei-vm-rollout, the system must be prepared first:

* Installing amoothei-vm-rollout
* Minimal configuration
* Setting up [payload injection mechanism](sftp-floppy-upload.md)
* Configuring virtual rooms



## Installation
Installation has been tested on CentOS 7. Fedora >= 20 should work as well. RHEL 6 / CentOS 6 might not work (Code requires python 2.7)

Dependencies:

```
yum install ovirt-engine-sdk-python python-mako mtools
```

Cloneing git repository:

```
cd /opt
git clone http://path.to.git.repository/amoothei-vdi.src.git
```

<!---
FIXME: git path above
-->

Bash search path: `/etc/profile.d/amoothei-vm-rollout.sh`
```
pathmunge /opt/amoothei-vdi.src/amoothei-vm-rollout after
```

## Minimal configuration
```
mkdir /etc/amoothei-vdi/

# SSL Certificyte of Ovirt engine Certificate Authority 
vim /etc/amoothei-vdi/ca.crt
# Template File for Windows Unattended Setup configuration file
vim /etc/amoothei-vdi/Autounattend-production.xml.template
# Logging settings
vim /etc/amoothei-vdi/logging.conf
# Definitions of virtual rooms:
vim /etc/amoothei-vdi/amoothei-vm-rollout.conf
```

Details are documented [here](amoothei-vm-rollout-config.md)

## Setting up payload injection mechanism
For rolling out virtual rooms, a payload injection is necessary.

Payload injection is done by creating floppy images containing `a:\sysprep.inf`, uploading them using SFTP, and attaching them to RHEV/Ovirt VMs using vdsm-hook-floppy.

The initial setup is quite complicated, but it has to be done only once, afterwards it will "just work".

Detailed instructions can be found [here](sftp-floppy-upload.md)

## Testing
After initial installation and after the configuration of at least one virtual room, run the following command to check if the config is valid and if tools do work in general:
```
amoothei-virtroom-show room01
```






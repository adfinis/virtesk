Introduction
==============
A lot of infrastructure services are needed for VDI:

* TFTP / HTTP / NFS4 for thinclients:

    (Network installation using PXE + Fedora Kickstart)

* Fedora mirror

* Syslog server, accessible to LAN:

    Thinclients use syslog remote logging during kickstart
    installation and normal operation. This way problems
    can be analyzed even if thinclients are off.

* Postgres database:

    Used by thinclients to determine which VM is displayed on which TC.


This article explains how to set up an infrastructure server based on EL 7
hosting all those services.


Enterprise Linux 7 installation
===============================
Normal RHEL 7 / CentOS 7 / Scientific Linux 7 installation, as documented here: 
https://access.redhat.com/documentation/en/red-hat-enterprise-linux/
    
This article is based on experience with a CentOS 7 infrastructure server.

Requirements:

* 1-2 vCPUs
* 1-2GB Ram
* 100GB Diskspace (only one mirror: fedora 22 x86_64)
* 150-200GB (and more) Diskspace (for mirroring multiple distributions / multiple versions)

LVM is recommended for disk space management, with the following 
file systems on seperate logical volumes:

| fs                     | size       | comment                                       |
| ---------------------- | ---------- | --------------------------------------------- |
| /boot (not on LVM)     | 200-500 MB |                                               |
| /                      | 10 GB      |                                               |
| /tmp			 | 1 GB       |                                               |
| /var                   | 4 GB       |                                               |
| /var/log		 | 4 GB       |                                               |
| /var/log/remote        | 2 GB       | more for large installations                  |
| /var/www/mirror        | 68 GB      | more for mirroring more than one distribution |


Installing and configuring services
===================================

Additional repositories and standard packets:
 
```
yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el7.rf.x86_64.rpm
yum groupinstall Base
yum install atd openssh-clients openssh-server bzip2 mc tcpdump iptraf vim \
 nmap acl rsync wget mutt postfix strace make tar iptables iproute screen \
 hdparm ntpdate elinks bind-utils less psmisc lftp ftp mailx util-linux lvm2 \
 pciutils lsof sysstat man cronie dmidecode mlocate at \
 ngrep pwgen yum-utils yum-plugin-downloadonly vim-enhanced

```


### NFS Server
Installing and starting nfs server:

```
yum install nfs-utils

systemctl enable nfs-server
systemctl enable rpcbind
systemctl start rpcbind
systemctl start nfs-server
```

/etc/exports:

```
/var/www/mirror/public/    *(ro,all_squash,insecure)
```

The option "insecure" is necessary for NFS clients behind NAT.

Apply with:

```
    exportfs -a
```

### Network boot
#### Setting up boot files
We do want our network bootloader to be accessible by TFTP (for PXE) 
and by HTTP (for advanced network boatloaders like iPXE). 

However, existing SELinux rules makes it difficult for httpd to access the
files in the standard location /var/lib/tftpboot/ .

So we create a new directory, /srv/tftpboot/ , and we adjust SELinux rules to
make sure that both in.tftpd and httpd are able to access it:

```
yum install syslinux-tftpboot policycoreutils-python-2.2.5-15

mkdir -p /srv/tftpboot/pxelinux
cp -r /var/lib/tftpboot/* /srv/tftpboot/pxelinux/

semanage fcontext -a -t public_content_t '/srv/tftpboot(/.*)?'
restorecon -r /srv/tftpboot/
```

FIXME: setting up Fedora kernel/initrd, pxelinux config, ..

#### Setting up in.tftpd
```
yum install tftp-server
``` 

/etc/xinetd.d/tftp:

``` 
# default: off
# description: The tftp server serves files using the trivial file transfer \
#	protocol.  The tftp protocol is often used to boot diskless \
#	workstations, download configuration files to network-aware printers, \
#	and to start the installation process for some operating systems.
service tftp
{
	socket_type		= dgram
	protocol		= udp
	wait			= yes
	user			= root
	server			= /usr/sbin/in.tftpd
	server_args		= -v -s /srv/tftpboot/
	disable			= no
	per_source		= 11
	cps			= 100 2
	flags			= IPv4
}
``` 

Enabling and starting xinetd service:

``` 
systemctl enable xinetd.service
systemctl start xinetd.service
``` 

#### Setting up httpd
FIXME

#### Setting up a fedora 22 mirror
First add repository definitions for fedora 22 to our infrastructure server.
By setting ```enabled=0``` we can access those repositories, but they don't
interfere with package installation/update on our infrastructure server.

``` 
cat > /etc/yum.repos.d/fedora22.repo << "EOFEOF"
[fedora22]
name=Fedora 22 - x86_64
failovermethod=priority
#baseurl=http://download.fedoraproject.org/pub/fedora/linux/releases/22/Everything/x86_64/os/
baseurl=http://mirror.switch.ch/ftp/mirror/fedora/linux/releases/22/Everything/x86_64/os/
#metalink=https://mirrors.fedoraproject.org/metalink?repo=fedora-22&arch=x86_64
enabled=0
metadata_expire=7d
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-22-x86_64
skip_if_unavailable=False
EOFEOF

cat > /etc/yum.repos.d/fedora22-updates.repo << "EOFEOF"
[fedora22-updates]
name=Fedora 22 - x86_64 - Updates
failovermethod=priority
#baseurl=http://download.fedoraproject.org/pub/fedora/linux/updates/22/x86_64/
baseurl=http://mirror.switch.ch/ftp/mirror/fedora/linux/updates/22/x86_64/
#metalink=https://mirrors.fedoraproject.org/metalink?repo=updates-released-f22&arch=x86_64
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-22-x86_64
skip_if_unavailable=False

[fedora22-updates-debuginfo]
name=Fedora 22 - x86_64 - Updates - Debug
failovermethod=priority
#baseurl=http://download.fedoraproject.org/pub/fedora/linux/updates/22/x86_64/debug/
metalink=https://mirrors.fedoraproject.org/metalink?repo=updates-released-debug-f22&arch=x86_64
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-22-x86_64
skip_if_unavailable=False

[fedora22-updates-source]
name=Fedora 22 - Updates Source
failovermethod=priority
#baseurl=http://download.fedoraproject.org/pub/fedora/linux/updates/22/SRPMS/
metalink=https://mirrors.fedoraproject.org/metalink?repo=updates-released-source-f22&arch=x86_64
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-22-x86_64
skip_if_unavailable=False

EOFEOF
``` 

Mirroring Fedora 22:

``` 
mkdir -p /var/www/mirror/public/fedora/
cd /var/www/mirror/public/fedora/
for REPO in fedora22 fedora22-updates; do reposync --download-metadata -m -n -l -r $REPO; done
``` 

If reposync shows any errors, like packages that couldn't be downloaded, then repeat those steps
until all packages are fetched successfully.

Creating repository metadata:

``` 
cd /var/www/mirror/public/fedora/fedora22
createrepo --workers=10 -g comps.xml .

cd /var/www/mirror/public/fedora/fedora22-updates
createrepo --workers=10 -g comps.xml .
``` 












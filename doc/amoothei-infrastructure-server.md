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
* Static IP address. Can be a private rfc1918 address. Must be accessible direcly by all thinclients in your LAN. It can be in a different Layer 2 network than you TCs, but must be accessible by layer 3 routing. Technologies that tamper with layer 4 and above (NAT, transparent proxies, ...) will cause problems with TFTP, NFS, kickstart and so on. Those problems can be resolved, but this requires expert knowledge.

    To support TC management features like ssh remote access to thinclients, screenshots of thinclients, pinging thinclients, ..., it is recommended that the infrastructure server is allowed to connect to thinclients using ssh (port 22/tcp) and icmp.

LVM is recommended for disk space management, with the following 
file systems on seperate logical volumes:

| filesystem             | size       | comment                                       |
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

### Firewall
Firewalling is explained in [RHEL7 security guide, chapter 4.5: Using Firewalls][0].

[0]: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Security_Guide/sec-Using_Firewalls.html

Services are described in XML Files residing in ```/usr/lib/firewalld/services/```.

```
# syslogd
firewall-cmd --permanent --add-port=514/tcp

# NFS
firewall-cmd --permanent --add-service=nfs
firewall-cmd --permanent --add-service=rpc-bind
firewall-cmd --permanent --add-service=mountd

# Other services
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=tftp
firewall-cmd --permanent --add-service=postgresql

# apply changes
firewall-cmd --reload
```

For NFS, additional changes might be necessary.

 
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
#### legacy bios versus UEFI
This guide has only been tested with legacy bios. UEFI Thinclients should work fine
as long as the compatibility mode / legacy mode of UEFI is used.

EFI installation of TCs has not been implemented and is not supported. This feature could be engineered, but so far there hasn't been any need for it.

#### Setting up dhcp service
We assume that there is already an existing dhcp service, so there is no
need to install a new one.

Configure your existing dhcp server to allow PXE boot from our infrastructure
server. Instructions for that can be found in the [RHEL7 Installation Guide, Chapter 21, Preparing for a Network Installation][1]

[1]: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/chap-installation-server-setup.html

Example configuration of isc-dhcp-server:

```
option space pxelinux;
option pxelinux.magic code 208 = string;
option pxelinux.configfile code 209 = text;
option pxelinux.pathprefix code 210 = text;
option pxelinux.reboottime code 211 = unsigned integer 32;
option architecture-type code 93 = unsigned integer 16;

subnet 10.0.0.0 netmask 255.255.255.0 {
  option routers 10.0.0.254;
  range 10.0.0.2 10.0.0.253;

  class "pxeclients" {
      match if substring (option vendor-class-identifier, 0, 9) = "PXEClient";
      next-server 10.0.0.1;

      if option architecture-type = 00:07 {
        filename "uefi/shim.efi";
      } else {
        filename "pxelinux/pxelinux.0";
      }
  }
}
```

Please make sure that ```next-server 10.0.0.1;``` points to the IP address of your infrastructure server.

#### Setting up boot files
We do want our network bootloader to be accessible by both TFTP (for PXE) 
and HTTP (for advanced network boatloaders like iPXE). 

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

### Setting up a remote syslog server
The thinclients use our infrastructure server for remote logging,
both during kickstart installation and normal operation.

Please note: remote logging is insecure (no authentication, no verification,
no encryption, could be flooded with messages, ...). Make sure your syslog server is accessible only by trusted clients.

It is recommended to put /var/log/remote/ on a seperate file system, so that no other services are harmed if /var/log/remote/ runs out of diskspace. Setting it up on a LVM logical volume is recommended so you can enlarge it on demand.

/etc/rsyslog.d/tcp-listening.conf:
``` 
# Define templates before the rules that use them

### Per-Host Templates for Remote Systems ###

$template LoggingFormat,"%timereported:::date-rfc3339% %timegenerated:::date-rfc3339% %HOSTNAME% %syslogpriority%,%syslogfacility% %syslogtag%%msg:::drop-last-lf%\n"
$template TmplMsg, "/var/log/remote/%fromhost-ip%.log"


# Provides TCP syslog reception
$ModLoad imtcp
$ModLoad imrelp # more reliable remote logging

# Adding this ruleset to process remote messages
$RuleSet remote1

kern.*,authpriv.*,*.info;mail.none;authpriv.none;cron.none;user.*   ?TmplMsg;LoggingFormat

$RuleSet RSYSLOG_DefaultRuleset   #End the rule set by switching back to the default rule set

$InputTCPServerBindRuleset remote1  #Define a new input and bind it to the "remote1" rule set
$InputTCPServerRun 514
# $InputRELPServerBindRuleSet remote1
# $InputRELPServerRun 20514
``` 

If you use ports other than 514/tcp, you might need to adjust your SELinux settings.

Apply changes:

``` 
service rsyslog restart
``` 

#### Setting up syslog clients
Your syslog clients need to be configured to forward messages to infrasturcture-server:514.

/etc/rsyslog.d/remote-logging.conf:

``` 
*.* @@infrastructure-server:514
``` 

On thinclients, this configuration will be automatically done in the kickstart post section.

Known limitation: The syslog client will only forward messages that are logged *after* rsyslog is started. Boot messages (including kernel boot messages) are logged before rsyslog starts, so those messages are not forwarded to our infrastructure server.

### Setting up postgres database
#### Installation
Postgres: installation, initalization, enable service, starting service:

``` 
yum install postgresql-server
postgresql-setup initdb
systemctl enable postgresql
systemctl start postgresql
``` 

#### Creating database user
We create two users, vdi-dbadmin and vdi-readonly:

``` 
# su - postgres         ## change to user postgres
-bash-4.2$ createuser --connection-limit=10 --no-createdb --login --pwprompt --no-createrole --no-superuser vdi-dbadmin
Enter password for new role: 
Enter it again: 
-bash-4.2$ createuser --connection-limit=10 --no-createdb --login --pwprompt --no-createrole --no-superuser vdi-readonly
Enter password for new role: 
Enter it again: 
-bash-4.2$ exit
``` 

The user vdi-dbadmin will be used by the system administrator (you!) to administer the database and to change the VM-to-TC-mapping.
The password for the user vdi-readonly needs to be configured in amoothei-tc-connectspice. It is used to determine the VM that should be displayed on a TC.

#### Creating database, grant permissions.

``` 
# su - postgres
Last login: Thu Oct 15 17:42:31 CEST 2015 on pts/3
-bash-4.2$ psql
psql (9.2.13)
Type "help" for help.

postgres=# create database vdi;
CREATE DATABASE
postgres=# grant all on database vdi to "vdi-dbadmin";
GRANT
postgres=# \quit
-bash-4.2$ exit
``` 

#### Setting up SSL
For our purposes, a self-signed certificate is sufficent. Put it on the server and then tell postgres where to find it:


/var/lib/pgsql/data/postgresql.conf:

``` 
ssl = on
ssl_cert_file = '/etc/pki/postgres/postgres_ssl.crt'
ssl_key_file = '/etc/pki/postgres/postgres_ssl.key'
``` 

Permissions: The key shall only be accessible by postgres:

``` 
chown postges:root /etc/pki/postgres/postgres_ssl.key
chown 600 /etc/pki/postgres/postgres_ssl.key
``` 

Restart your database to let the changes take effect.

The certificate, /etc/pki/postgres/postgres_ssl.crt , should also be installed
on all thinclients for secure database access. This is done in the kickstart post-section.

#### Allow network access
/var/lib/pgsql/data/pg_hba.conf:

``` 
hostssl    all             all          0.0.0.0/0               md5
``` 

This line allows password-based authentication, protected with TLS/SSL, from everywhere.

Restart your database to let the changes take effect.

#### Create database layout for amoothei-vdi:
FIXME


#### Accessing database
There are alot of postgres shells, both console shells and graphical tools.

For console access, we do recommend ```psql```, for GUI access we do recommend ```pgadmin3```.

A list of postgres shells / tools can be found here:
https://wiki.postgresql.org/wiki/Community_Guide_to_PostgreSQL_GUI_Tools

Troubleshooting
===============

### TFTP
Logfiles:

``` 
journalctl _COMM=in.tftpd 
# or
journalctl -u xinetd.service
``` 

Testing:

``` 
# tftp 127.0.0.1
tftp> get pxelinux/pxelinux.cfg/default
tftp> quit
# cat default 
``` 







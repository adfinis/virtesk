# Copyright (c) 2013-2016, Adfinis SyGroup AG
#
# This file is part of Amoothei-VDI.
#
# Amoothei-VDI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Amoothei-VDI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Amoothei-VDI.  If not, see <http://www.gnu.org/licenses/>.

###################################################################################################
###################################################################################################
#
# Kickstart Main Section - Configures how the base system is installed.
# * File Format: Answer-File for Anaconda-Installer
#
###################################################################################################
###################################################################################################

# Syslog logging
# ADJUST
logging --host=infrastructure-server --port 514 --level=debug

auth --enableshadow --passalgo=sha512

#
# Netzwork location of Anaconda stage 2
# Point to the Fedora Installer DVD
# Can be nfs or http
#

#liveimg --url=http://infrastructure-server/mirror/public/fedora/Fedora-20-i386-DVD_ISO/LiveOS/squashfs.img

#url --url=http://infrastructure-server/mirror/public/fedora/Fedora-Server-DVD-x86_64-22_ISO

# ADJUST
nfs --server=infrastructure-server --dir=/var/www/mirror/public/fedora/Fedora-Server-DVD-x86_64-22_ISO

#
# Additional repositories used during the installation process
#

# ADJUST
repo --name=local-fedora22 --cost=200 --baseurl=http://infrastructure-server/mirror/public/fedora/fedora22/
repo --name=local-fedora22-updates --cost=200 --baseurl=http://infrastructure-server/mirror/public/fedora/fedora22-updates/
repo --name=customrpms-fc22 --cost=200 --baseurl=http://infrastructure-server/mirror/public/fedora/customrpms-fc22/


# Run the Setup Agent on first boot
firstboot --enable

# Keyboard layouts
keyboard --vckeymap=ch --xlayouts='ch'

# System language
lang de_CH.UTF-8

network --bootproto=dhcp --ipv6=auto --activate

# Root password 
# (SSH-Password-Login and system consoles will be disabled in the post section)
# The root-password is only configured because it is required by anaconda. 
# ADJUST
rootpw PASSWORD

# System timezone
# ADJUST
timezone Europe/Zurich --ntpservers=your-ntp-server1.site,your-ntp-server2.site

# System bootloader configuration
bootloader --location=mbr --append="loglevel=0 net.ifnames=0 i915.i915_enable_rc6=0 i915preliminary_hw_support=1 clocksource=acpi_pm systemd.journald.forward_to_kmsg=no systemd.journald.forward_to_console=no systemd.journald.forward_to_wall=no enable_msi=0"

# Partitioning
autopart --type=lvm

# All disks - including usb devices - will be wiped!
clearpart --all --initlabel
zerombr


# Reboot after installation is complete
reboot 


###################################################################################################
###################################################################################################
#
# Packages Section - configures the packages to be installed into this system
# * For mirror configuration: see "repo" above.
#
###################################################################################################
###################################################################################################

# While experimenting with new packages, "--ignoremissing" might be usefull.
# But make sure to remove it afterwards for production setups!
# %packages --ignoremissing


%packages
@core
@standard
@base-x
@fonts
@hardware-support
@guest-desktop-agents

xterm
virt-viewer
dmidecode
ovirt-engine-sdk-python
plymouth-theme-spinner
vim-enhanced
kexec-tools
fluxbox
gxmessage
strace
gnome-icon-theme
alsa-utils
pulseaudio
htop
iftop
python-psycopg2
intel-gpu-tools
psmisc
ccze
xdotool
lldpad
# Display Manager with autologin
lxdm 

# GTK 3.0 Theme for remote-viewer
adwaita-gtk3-theme
# GTK 2.0 Theme for gxmessage
adwaita-gtk2-theme


# Taking Remote-Screenshots using ssh:
# ssh -o StrictHostKeyChecking=no -i ssh-key-thinclients-id_rsa.private_key vdiclient@thinclient "DISPLAY=:0 xwd -root | convert  - png:-"  > filename.png
# requires xws from xorg-x11-apps and convert from ImageMagick
ImageMagick
xorg-x11-apps

# for debugging time related problems...
ntpdate

# Audio tools...
pulseaudio-utils
pulseaudio-module-x11
pavucontrol
dbus-x11


# midnight commander
mc

# Desktop notifications
xfce4-notifyd
libnotify

# for development and debugging
python-ipython-console

# remote logging
rsyslog-relp

%end

###################################################################################################
###################################################################################################
#
# First Post-Section (no chroot)
# * Setup Debug-Bash for Second Post-Section
# * Copy resolv.conf into chroot
#
###################################################################################################
###################################################################################################

# %post
# set -x -v
# 
# cat > /tmp/mybash << 'EOF'
# #!/bin/bash 
# /bin/bash --debugger $1
# EOF
# 
# chmod +x /tmp/mybash
# 
# cp -f /etc/resolv.conf /mnt/sysimage/etc/
# %end

###################################################################################################
###################################################################################################
#
# Second Post-Section
# * runs chrooted into the installed system ( /mnt/sysimage/ )
# * Logging / Output:
# ** to tty8
# ** to /root/ks-post-anaconda.log (in the installed system)
#
###################################################################################################
###################################################################################################

%post

#
# Setup Code
#


# redirect the output to the log file
exec >/root/ks-post-anaconda.log 2>&1

# show the output on the 8th console
tail -f /root/ks-post-anaconda.log >/dev/tty8 &
# changing to VT 8 that we can see what's going on....
/usr/bin/chvt 8
set -x -v
echo "Start Kickstart Postsection...."

#
# show information about available memory...
#
free -m

#
# Avoid time-related problems...
#

echo Time now: $(date)
echo Setting time using ntpdate ......
# ADJUST
ntpdate -b your-ntp-server.site
if [ $? -eq 0 ]; then
        echo Finished setting time. Time now: $(date)
        echo Syncing Time into HWclock...
        hwclock -w
        echo Syncing Time into HWclock... done
else
        echo Failed setting time. Time now: $(date)
fi

#
# Setup SSH-Keys for Root
# Details: see docs/virtesk-tc-tools.rst
#

mkdir /root/.ssh
chmod 700 /root/.ssh
cat > /root/.ssh/authorized_keys << 'EOF'
# SSH-Key for thinclient maintenance
# ADJUST
ssh-rsa AAAA....s5Ix4t thinclient-maintenance@yourdomain.site
EOF

restorecon -R -v /root/.ssh

#
# Disable password login using ssh
#
sed -i 's/^#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^GSSAPIAuthentication yes/GSSAPIAuthentication no/' /etc/ssh/sshd_config

# 
# Rsyslog: set up remote logging
#
cat > /etc/rsyslog.d/remote-logging.conf << 'EOF'
# ADJUST
*.* @@infrastructure-server:514
EOF

# VIM background
echo set background=dark >> /etc/vimrc

# Send dmidecode system information to syslog.
dmidecode -t1 | while read i; do echo dmidecode-t1: $i; done | logger -p user.info

#
# Pulseaudio: disable tsched (timer based sheduling/buffering)
#
sed -r -i 's/load-module module-udev-detect/load-module module-udev-detect tsched=0/' /etc/pulse/default.pa

#
# yum: configuring local Fedora Repositories....
#
#yum-config-manager --quiet --disable "*" > /dev/zero
dnf config-manager --set-disabled "*"

cat > /etc/yum.repos.d/localmirror.repo << 'EOF'
[local-fedora22]
name=Local Mirror: Fedora 22 - x86_64
failovermethod=priority
# ADJUST
baseurl=http://infrastructure-server/mirror/public/fedora/fedora22/
enabled=1
metadata_expire=7d
gpgcheck=1
skip_if_unavailable=True
cost=200
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$releasever-$basearch


[local-fedora22-updates]
name=Local Mirror: Fedora 22 - x86_64 - Updates
failovermethod=priority
# ADJUST
baseurl=http://infrastructure-server/mirror/public/fedora/fedora22-updates/
enabled=1
metadata_expire=7d
gpgcheck=1
skip_if_unavailable=True
cost=200
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$releasever-$basearch

[customrpms-fc22]
name=Customrpms: Fedora22
failovermethod=priority
# ADJUST
baseurl=http://infrastructure-server/mirror/public/fedora/customrpms-fc22/
enabled=1
metadata_expire=7d
gpgcheck=0
skip_if_unavailable=True
cost=200
#gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$releasever-$basearch

EOF

rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-22-x86_64

#
# Setup Sudo - required for system shutdown/reboot
#
cat > /etc/sudoers.d/vdiclient << 'EOF'

# User vdiclient can start all programs as root
# tty is not required
#
# Needed for virtesk-vdi 
vdiclient       ALL=(ALL)       NOPASSWD: ALL
Defaults:vdiclient                      !requiretty
EOF


#
# Plymouth: Splash Screen while booting
#
plymouth-set-default-theme spinner

# changing plymouth theme requires rebuilding initramfs...
for i in $(ls -1 /boot/vmlinuz-* | grep -v rescue | sed -r 's/\/boot\/vmlinuz-(.*)/\1/')
do
        echo rebuilding initramfs for kernel version $i
        dracut --force --kver $i
done

#
# Grub Configuration
# * Please note: kernel cmdline is configured using the "bootloader"-statement in
#   Kickstart main section
#
sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=0/' /etc/default/grub
sed -i 's/GRUB_TERMINAL_OUTPUT="console"/GRUB_TERMINAL_OUTPUT=/' /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg


#
# Policykit / usb redirect for spice
#

cat >  /usr/share/polkit-1/actions/org.spice-space.lowlevelusbaccess.policy << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
         "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
         "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
<policyconfig>

 <vendor>The Spice Project</vendor>
 <vendor_url>http://spice-space.org/</vendor_url>
 <icon_name>spice</icon_name>

 <action id="org.spice-space.lowlevelusbaccess">
   <description>Low level USB device access</description>
   <message>Privileges are required for low level USB device access (for usb device pass through).</message>
   <defaults>
     <allow_inactive>yes</allow_inactive>
     <allow_active>yes</allow_active>
     <allow_any>yes</allow_any>
   </defaults>
 </action>

</policyconfig>
EOF


#
# Disabling screenshot functionality in remote-viewer ausschalten:
# * otherwise, users could overwrite some local files with screenshots.
#

##  <object class="GtkMenuItem" id="menu-file-screenshot">
##                         <property name="visible">True</property>
##                         <property name="can_focus">False</property>
##                         <property name="use_action_appearance">False</property>
##                         <property name="label" translatable="yes">Screenshot</property>
##                         <property name="use_underline">True</property>
##                         <signal name="activate" handler="virt_viewer_window_menu_file_screenshot" swapped="no"/>
##                       </object>
## 

cp -f /usr/share/virt-viewer/ui/virt-viewer.xml /usr/share/virt-viewer/ui/virt-viewer.xml.original-without-remove-screenshot-patch
perl -p0i -e 's|(<object class="GtkMenuItem" id="menu\-file\-screenshot">.*?<property name="visible">)True(</property>.*?</object>)|\1False\2|s' /usr/share/virt-viewer/ui/virt-viewer.xml
diff -puN /usr/share/virt-viewer/ui/virt-viewer.xml.original-without-remove-screenshot-patch  /usr/share/virt-viewer/ui/virt-viewer.xml
if [ "$?" -eq 0 ]; then
        echo "ERROR: Failed to disable Screenshot functionality in /usr/share/virt-viewer/ui/virt-viewer.xml"
fi

#
# Misc systemd settings...
#
sed -i 's/#SystemMaxUse=/SystemMaxUse=100M/'  /etc/systemd/journald.conf
sed -i 's/#DefaultTimeoutStopSec=90s/DefaultTimeoutStopSec=2s/'  /etc/systemd/system.conf

sed -i 's/#NAutoVTs=6/NAutoVTs=0/' /etc/systemd/logind.conf
sed -i 's/#ReserveVT=6/ReserveVT=0/' /etc/systemd/logind.conf
sed -i 's/#HandleSuspendKey=suspend/HandleSuspendKey=poweroff/' /etc/systemd/logind.conf
sed -i 's/#HandleHibernateKey=hibernate/HandleHibernateKey=poweroff/' /etc/systemd/logind.conf
sed -i 's/#HandleLidSwitch=suspend/HandleLidSwitch=poweroff/' /etc/systemd/logind.conf


systemctl disable getty@tty1.service
systemctl mask getty@tty1.service

systemctl set-default graphical.target

#
# lxdm display manager: configuring automatic login
#


sed -i 's/# autologin=.*/autologin=vdiclient/' /etc/lxdm/lxdm.conf
sed -i 's|# session=.*|session=/usr/bin/startfluxbox|' /etc/lxdm/lxdm.conf

#
# Misc Xorg settings...
#
cat > /etc/X11/xorg.conf.d/20-extensions.conf << 'EOF'
Section "Extensions"
    Option         "Composite" "true"
    Option         "DAMAGE" "true"
    Option         "RENDER" "true"
EndSection
EOF

#
# Xorg down-locking...
#
cat > /etc/X11/xorg.conf.d/30-ctrl.conf  << 'EOF'
#Disable CTRL+ALT+F1 ...
Section "ServerFlags"
        Option "DontVTSwitch" "on"
        Option "DontZap" "true"
EndSection
EOF

#
# Xorg Touchpad configuration...
#

cat > /etc/X11/xorg.conf.d/40-touchpad.conf  << 'EOF'
Section "InputClass"
         Identifier      "Touchpad"                      # required
         MatchIsTouchpad "yes"                           # required
         Driver          "synaptics"                     # required
         Option          "MinSpeed"              "0.5"
         Option          "MaxSpeed"              "1.0"
         Option          "AccelFactor"           "0.075"
         Option          "TapButton1"            "1"
         Option          "TapButton2"            "2"     # multitouch
         Option          "TapButton3"            "3"     # multitouch
         Option          "VertTwoFingerScroll"   "1"     # multitouch
         Option          "HorizTwoFingerScroll"  "1"     # multitouch
         Option          "VertEdgeScroll"        "1"
         Option          "CoastingSpeed"         "8"
         Option          "CornerCoasting"        "1"
         Option          "CircularScrolling"     "1"
         Option          "CircScrollTrigger"     "7"
         Option          "EdgeMotionUseAlways"   "1"
         Option          "LBCornerButton"        "8"     # browser "back" btn
         Option          "RBCornerButton"        "9"     # browser "forward" btn
EndSection
EOF



#
# Remove old dhcp leases on startup
# * Reason: thinclient-software malfunctions
#   if stale information is found in leases files
#

cat > /lib/systemd/system/dhcp-leases.service << 'EOF'
# This unit gets pulled automatically into multi-user.target
[Unit]
Description=Remove DHCP Leases
After=local-fs.target
Before=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/removeLeases.sh
TimeoutSec=0
RemainAfterExit=yes
SysVStartPriority=99

[Install]
WantedBy=multi-user.target

EOF

cat > /usr/local/bin/removeLeases.sh << 'EOF'
#!/bin/bash

/usr/bin/rm -f /var/lib/NetworkManager/dhclient-*.lease
/usr/bin/rm -f /var/lib/dhclient/dhclient-*.lease
EOF

chmod +x /usr/local/bin/removeLeases.sh

systemctl enable dhcp-leases.service

#
# Amoothei VDI - Shutdown VM on TC shutdown
#
cat > /etc/systemd/system/shutdownvm.service << 'EOF'
[Unit]
Description=Amoothei VDI - Shutdown VM on TC shutdown
# DefaultDependencies=no
Requires=network-online.target rsyslog.service dbus.service
After=network-online.target rsyslog.service dbus.service
#Requires=rsyslog.service

[Service]
Type=oneshot
TimeoutStopSec=60
RemainAfterExit=true
ExecStart=/bin/true
ExecStop=/usr/local/bin/shutdownvm
User=vdiclient

[Install]
WantedBy=graphical.target
EOF

cat > /usr/local/bin/shutdownvm << 'EOF'
#!/bin/bash

# Amoothei VDI - Shutdown VM on TC shutdown

# Make sure the shutdown logic is triggered only if
# the system halts / is powerin off.

# The shutdown logic SHALL NOT run upon reboot.

/usr/bin/systemctl list-jobs | egrep -q 'halt.target.*start'
HALT_TARGET_ACTIVE=$?
/usr/bin/systemctl list-jobs | egrep -q 'poweroff.target.*start'
POWEROFF_TARGET_ACTIVE=$?
/usr/bin/systemctl list-jobs | egrep -q 'reboot.target.*start'
REBOOT_TARGET_ACTIVE=$?

logger -s -t vmshutdown "HALT_TARGET_ACTIVE=$HALT_TARGET_ACTIVE, POWEROFF_TARGET_ACTIVE=$POWEROFF_TARGET_ACTIVE, REBOOT_TARGET_ACTIVE=$REBOOT_TARGET_ACTIVE"

if [[ $REBOOT_TARGET_ACTIVE -eq 0 ]]; then
        logger -s -t vmshutdown "Rebooting ==> NOT Running VM shutdown code..."
elif [[ $HALT_TARGET_ACTIVE -eq 0 || $POWEROFF_TARGET_ACTIVE -eq 0 ]]; then
        logger -s -t vmshutdown "Running VM shutdown code..."
        /opt/virtesk-tc-connectspice/virtesk-tc-connectspice-shutdown-vm --config /etc/connect_spice_client/connect_spice_client.conf
else
        logger -s -t vmshutdown "Dont know what to do ==> NOT Running VM shutdown code..."
fi
EOF

chmod +x /usr/local/bin/shutdownvm
systemctl enable shutdownvm.service

#
# Enable Wake on LAN on device eth0
#

cat > /lib/systemd/system/wake-on-lan-eth0.service << 'EOF'
# This unit gets pulled automatically into multi-user.target
[Unit]
Description=Activate wake-on-lan on eth0
Wants=network-online.target
After=network-online.target

[Service]
Type=forking
ExecStart=/usr/local/bin/wake-on-lan-eth0.sh
TimeoutSec=0
RemainAfterExit=yes
SysVStartPriority=99

[Install]
WantedBy=multi-user.target

EOF

cat > /usr/local/bin/wake-on-lan-eth0.sh << 'EOF'
#!/bin/bash

ethtool -s eth0 wol g
EOF

chmod +x /usr/local/bin/wake-on-lan-eth0.sh

# execute it in installer too...
/usr/local/bin/wake-on-lan-eth0.sh

systemctl enable wake-on-lan-eth0.service




#
# Config files for connect_spice_client
#

mkdir -p /etc/connect_spice_client/

cat > /etc/connect_spice_client/connect_spice_client.conf << 'EOF'
[general]
log_config_file = connect_spice_client_logging.conf
shutdown_command=/bin/sh -c "sudo shutdown -h now"
reboot_command=/bin/sh -c "sudo shutdown -r now"

# Postgres DB connection string
# ADJUST
postgres_db_connect=host=infrastructure-server sslmode=require connect_timeout=1 dbname=vdi user=vdi-readonly password=PASSWORD

# Desktop notifications
notify_cmd_waiting_for_dhcplease = notify-send -t 3000 -i /usr/share/icons/gnome/48x48/status/network-wired-disconnected.png  "Waiting for network..."
notify_cmd_waiting_for_db_connection = notify-send -t 3000 -i /usr/share/icons/gnome/48x48/status/network-wired-disconnected.png  "Waiting for database..."
notify_cmd_waiting_for_vm_launch = notify-send --hint string:transient:true -t 3000 -i /usr/share/icons/gnome/48x48/apps/preferences-desktop-remote-desktop.png "starting VM... please wait..."

# GUI
dialog_command_with_retry = gxmessage -buttons "neu verbinden:101,Thinclient herunterfahren:102,Thinclient neu starten:103,Support:104" -center -title "Nachricht" -default "neu verbinden" -ontop -noescape -wrap
dialog_command_without_retry = gxmessage -buttons "Thinclient herunterfahren:102,Thinclient neu starten:103,Support:104" -center -title "Nachricht" -ontop -noescape -wrap
dialog_command_support = gxmessage -center -name "Support Informationen" -title "Support Informationen" -wrap -buttons OK:0 -default OK

support_message_file = support_message.txt

config_tags_user_query=ovirt.thinclient*

[connect]
# ADJUST
url=https://your-ovirt-manager.fqdn/api

# ADJUST
username=ovirt.thinclient@your-ovirt-authentication-domain
# ADJUST
password=PASSWORD
ca_file=ovirt-manager.crt


#insecure=True
#filter=True
#filter=False

[spice]
spice_ca_file=ovirt-manager.crt
socket=/tmp/adsy-rhev-tools-spice-control-socket
spice_client_command=/usr/bin/remote-viewer --spice-controller

EOF

# The SSL Certificate for the REST-API is available here:
# curl http://your-ovirt-manager.fqdn/ca.crt
cat > /etc/connect_spice_client/ovirt-manager.crt << 'EOF'
-----BEGIN CERTIFICATE-----
# ADJUST
...
-----END CERTIFICATE-----
EOF


cat > /etc/connect_spice_client/connect_spice_client_logging.conf << 'EOF'
[formatters]
keys=simpleFormatter,logFileFormatter

[loggers]
keys=root

[handlers]
#keys=consoleHandler,timedRotatingFileHandler,syslogDebugHandler
keys=consoleHandler,timedRotatingFileHandler,syslogHandler

[logger_root]
level=DEBUG
handlers=consoleHandler,timedRotatingFileHandler,syslogHandler

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stderr,)

[handler_syslogHandler]
class=handlers.SysLogHandler
level=DEBUG
formatter=simpleFormatter
args=('/dev/log',)

# [handler_syslogDebugHandler]
# class=connect_spice_client.syslog_debug_handler
# level=DEBUG
# formatter=simpleFormatter
# args=('/dev/log',)
# 

[handler_timedRotatingFileHandler]
class=handlers.TimedRotatingFileHandler
level=DEBUG
formatter=logFileFormatter
args=(os.path.expanduser('~/logs/connect_spice_client.log'), 'D', 1, 30)

[formatter_simpleFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
datefmt=

[formatter_logFileFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
datefmt=

EOF

cat > /etc/connect_spice_client/support_message.txt << 'EOF'
===========================================================
    Amoothei-VDI: Support
===========================================================

For support, please call ...

EOF

#
# Adding User vdiclient
# * All VDI stuff is running as vdiclient
#

# create user vdiclient
useradd -G wheel,audio,video,floppy vdiclient

#
# VDI software installation
#

echo Installing virtesk vdi thinclient software...
cd /home/vdiclient
mkdir logs

RELEASE=connect_spice_client


# ADJUST
wget -q --no-check-certificate https://infrastructure-server/mirror/private/thinclients/thinclient-software/$RELEASE.tar.gz
echo wget result: $?

tar -C /opt -xvzf $RELEASE.tar.gz

cat > /etc/profile.d/connect_spice_client_path.sh << 'EOF'
pathmunge /opt/virtesk-tc-connectspice after
EOF

# Remote-Viewer settings...
# * dont ask when closing session:
#
mkdir -p /home/vdiclient/.config/virt-viewer/
cat > /home/vdiclient/.config/virt-viewer/settings << 'EOF'
[virt-viewer]
ask-quit=false
EOF

#
# Xorg Window Manager:
# Fluxbox configuration
#
mkdir -p /home/vdiclient/.fluxbox
touch /home/vdiclient/.fluxbox/menu
touch /home/vdiclient/.fluxbox/keys

cat > /home/vdiclient/.fluxbox/init << 'EOF'
session.menuFile:       ~/.fluxbox/menu
session.keyFile: ~/.fluxbox/keys
session.styleFile: /usr/share/fluxbox/styles/bloe
session.configVersion:  13
session.screen0.toolbar.visible: false
session.screen0.defaultDeco: None
EOF

#
# Fluxbox startup script...
#
cat > /home/vdiclient/.fluxbox/startup << 'EOF'
#!/bin/sh
# xmodmap "$HOME/.Xmodmap"


# Disabling X11 "virtual power off button input device"
# Reason: Key 124 is passed to VM ===> VM shuts down
xinput --disable 6


# Initializing DBUS...
# test for an existing bus daemon, just to be safe
if test -z "$DBUS_SESSION_BUS_ADDRESS" ; then
        # if not found, launch a new one
        eval `dbus-launch --sh-syntax`
        echo "D-Bus per-session daemon address is: $DBUS_SESSION_BUS_ADDRESS"
fi

# starting pulseaudio ..
pulseaudio --start

export PULSE_RUNTIME_PATH="/run/user/`id -u`/pulse/"

# required for seamless switching between
# usb-headphones and internal audio
pacmd load-module module-switch-on-connect

# Dont turn of the screen while idle
/usr/bin/xset s off
/usr/bin/xset -dpms
/usr/bin/xset s noblank

# Set volume
/usr/bin/amixer -c 0 -- sset Master playback 30dB+
/usr/bin/amixer -c 0 -- sset Master playback 30dB+
/usr/bin/amixer -c 0 -- sset Master playback 30dB+
/usr/bin/amixer -c 0 set PCM 50dB+
/usr/bin/amixer -c 0 set Speaker 50dB+
/usr/bin/amixer -c 0 set Mic 50dB+
/usr/bin/amixer -c 0 set "Mic Boost" 50dB+

# Daemon for displaying desktop notifications
/usr/lib64/xfce4/notifyd/xfce4-notifyd &

# starting VDI software

virtesk-tc-connectspice-main --config /etc/connect_spice_client/connect_spice_client.conf &

# uncomment for debugging purposes...
# xterm &
# /usr/bin/gstreamer-properties &


# start window manager
exec fluxbox

EOF

chmod +x /home/vdiclient/.fluxbox/startup

#
# make some ENV-Variables available through
# a script. Not used normally.
# Usefull for remote-debugging using ssh.
#

cat > /home/vdiclient/x11variables.sh << 'EOF'
export DISPLAY=:0
# source .dbus/session-bus/*
# export DBUS_SESSION_BUS_ADDRESS
# export DBUS_SESSION_BUS_PID
# export DBUS_SESSION_BUS_WINDOWID
export PULSE_RUNTIME_PATH="/run/user/`id -u`/pulse/"
EOF

#
# set up ssh keys for user vdiclient
#

mkdir -p /home/vdiclient/.ssh/
chmod 700 /home/vdiclient/.ssh/
cp /root/.ssh/authorized_keys /home/vdiclient/.ssh/
restorecon -R -v /home/vdiclient/.ssh/

#
# Pulseaudio: configure buffering...
#

mkdir -p /home/vdiclient/.config/pulse/
cat > /home/vdiclient/.config/pulse/daemon.conf  << 'EOF'
default-fragments=2
default-fragment-size-msec=125
EOF

# GTK 2.0 Style settings
cat > /home/vdiclient/.gtkrc-2.0 << 'EOF'
style "ponies-window"
{
    #bg[NORMAL] = "#ff69b4"
    #XfceNotifyWindow::border-color = "#ffff00"
    XfceNotifyWindow::border-radius = 10.0
    XfceNotifyWindow::border-width = 6.0
    GtkMisc::yalign = 0.5
    GtkWidget::yalign = 0.5
    XfceNotifyWindow::yalign = 0.5
}
class "XfceNotifyWindow" style "ponies-window"

style "ponies-text"
{
    font_name = "Comic Sans MS 20"
    GtkLabel::yalign = 0.5
    #GtkWidget::text-yalign = 0.5
    GtkMisc::yalign = 0.5
    GtkWidget::yalign = 0.5
    #fg[NORMAL] = "#ffff00"
    #GtkWidget::link-color = "#c17800"
}
widget_class "XfceNotifyWindow.*.<GtkLabel>" style "ponies-text"

style "ponies-misc"
{
    font_name = "Comic Sans MS 20"
    GtkLabel::yalign = 0.5
    #GtkWidget::text-yalign = 0.5
    GtkMisc::yalign = 0.5
    GtkWidget::yalign = 0.5
    #fg[NORMAL] = "#ffff00"
    #GtkWidget::link-color = "#c17800"
}
widget_class "XfceNotifyWindow.*.<GtkMisc>" style "ponies-misc"


style "ponies-btn"
{
    #bg[NORMAL] = "#9400d3"
    #bg[PRELIGHT] = "#5e0086"
}
widget "XfceNotifyWindow.*.GtkButton" style "ponies-btn"
EOF

#
# Print uptime
# * usefull to know how long it takes
#   to roll out some kind of hardware
#

echo uptime:
uptime

#
# Fix file permissions for user vdiclient
# * keep this at the end of this script!
#
restorecon -R -v /home/vdiclient/
chown -R vdiclient:vdiclient /home/vdiclient

echo "Kickstart Postsection ist fertig."
%end

###################################################################################################
###################################################################################################
#
# End of second post-section
#
###################################################################################################
###################################################################################################

%post --nochroot
logger -p user.info "watchdog started..."

exec </dev/null >/dev/null 2>&1
(
for i in {1..2}; do
        sleep 60
        logger -p user.info "Watchdog running since $i minutes"
 done
 logger -p user.info "Watchdog initiates normal reboot..."
 shutdown -r now
 for i in {1..5}; do
        sleep 60
        logger -p user.info "Watchdog2 running since $i minutes"
 done
 logger -p user.info "Watchdog2 initiates forcefull reboot..."
 reboot -f
 while sleep 60; do 
	logger -p user.info "Watchdog: System is still alive, but it shouldn't be..."
 done
) &

%end



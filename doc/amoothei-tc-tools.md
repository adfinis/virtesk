# Amoothei-tc-tools: Manageing TCs efficiently

------------------------------------------------

## Introduction
amoothei-tc-tools is a collection of utilities for system administrators.
They to help to automate the tasks that occur when managing a lot of thinclients.

Features:

* Remote access using SSH
* Scripting
* Screenshots
* Kickstart re-installation using SSH + kexec


## Installation
Cloneing git repository:

```
cd /opt
git clone http://path.to.git.repository/amoothei-vdi.src.git
```

<!---
FIXME: git path above
-->

Bash search path: `/etc/profile.d/amoothei-tc-tools.sh`
```
pathmunge /opt/amoothei-vdi.src/amoothei-tc-tools after
```

## Configuration
All config file locations are relative to the environment variable
`$AMOOTHEI_TC_TOOLS_CONF_DIR`. This variable defaults to `/etc/amoothei-vdi/`

The config files are sourced by bash scripts, e.g. they have to be valid bash shell files.

First, the main config file (mandatory) is sourced, and then, the individual config file (optional) is sourced as described below.
This allows to specify default values in the main config file, and to overwrite them later if necessary. 

### Main Config File
`${AMOOTHEI_TC_TOOLS_CONF_DIR}/amoothei-tc-tools.conf`:
```
FIXME
```

Sample config file: See `sample_config/amoothei-tc-tools.conf`.

### SSH Key
FIXME

### Individual config file
After sourcing the main config file, the optional individual config file is sourced. 
Individual configuration will override the main configuration.

This allows you to create custom instances (see [below](#custom-tool-instances)) of the TC tools if nessesary, and to provide a custom configuration for them.

* individual config file location: `${AMOOTHEI_TC_TOOLS_CONF_DIR}/amoothei-tc-tools.conf.dir/${PROGNAME}.conf`
* ```PROGNAME=`basename "$BASH_SOURCE"` ```
* Examples:
    + Tool `tc_ssh` ---> individual config file: `${AMOOTHEI_TC_TOOLS_CONF_DIR}/amoothei-tc-tools.conf.dir/tc_ssh.conf`
    + Tool `tc_screenshot` ---> individual config file: `${AMOOTHEI_TC_TOOLS_CONF_DIR}/amoothei-tc-tools.conf.dir/tc_screenshot.conf`
    + Tool `tc_rollout_kexec` ---> individual config file: `${AMOOTHEI_TC_TOOLS_CONF_DIR}/amoothei-tc-tools.conf.dir/tc_rollout_kexec.conf`
    + Custom tool `tc_my_custom_tool` ---> individual config file: `${AMOOTHEI_TC_TOOLS_CONF_DIR}/amoothei-tc-tools.conf.dir/tc_my_custom_tool.conf`


FIXME: needs to be implemented.

## Tools

### tc_ssh
Open an interactive shell on a thinclient, or run commands on a thinclient.

Syntax:
```
tc_ssh <thinclient> [ssh-args]                     # interactive shell
tc_ssh <thinclient> [ssh-args] -- remote_command   # execute remote command
```

`<thinclient>` can be specified as a short host name (myorganization.mydomain will be appended automatically),
as a fully qualified domain name, or as an IPv4 address.


Example: Open interactive root-shell on mytc.myorganization.mydomain:
```
tc_ssh myTC                               
# or
tc_ssh mytc.myorganization.mydomain
# or
tc_ssh mytc.myorganization.mydomain -l root
# or
tc_ssh 192.0.2.240                              # (myTC has IP 192.0.2.240)
```

Example: Open interactive shell as user vdiclient:
```
tc_ssh myTC -l vdiclient 
```

Example: running command(s):
```
# single command as root:
tc_ssh myTC -- uname -a

# single command as user vdiclient:
tc_ssh myTC -l vdiclient -- uname -a

# running multiple commands:
tc_ssh myTC -- "killall gxmessage && sleep 20; killall remote-viewer && sleep 5; killall gxmessage"
```

The last example has the following effect on the thinclient: If not yet connected, it will connect to its assigned VM, then the connection will be terminated, and then it will connect again to the assigned VM. See [Tipps and Tricks](#manageing-thinclients-tipps-and-tricks) for details.

Example: shutdown all thinclients in your organization:

Put all thinclient names into a text-file `all-thinclients.txt`, one thinclient name per line:
```
room01-tc01
room01-tc02
[...]
room02-tc01
room02-tc02
```

Run `tc_ssh` on all thinclients:
```
# sequentially
for TC in $(cat all-thinclients.txt); do tc_ssh $TC -- systemctl poweroff ; done

# parallel
for TC in $(cat all-thinclients.txt); do tc_ssh $TC -- systemctl poweroff & done
```

The sequential and the parallel variant differ by one character only: `";"` for the sequential variant, `"&"` for the parallel variant.



Security of tc_ssh: An individual ssh private key is used for connecting to the thinclients. Only system administrators with access to this private key will be able to access thinclients. However, the thinclient identity is not validated, e.g. a man-in-the-middle could claim to be a thinclient.



### tc_screenshot
Take a screenshot of a thinclient and store it in a PNG File.

Please respect the privacy of your users and don't use this tool for hidden surveillance.

Screenshots are a valuable tool for quality control: You just deployed a few hundreds thinclients and you do wanna make sure that every thinclient is operating correctly. Simply make a screenshot of all of them. Image viewers like gwenview can display thumbnails of a few hundreds images at once, and this overview is great for identifying thinclients with problems.

Diagnostics using thumbnails of alot of TC screenshots:

* Windows login screen
    * Thinclient is fine and it is connected to a VM.
* Gray screen ===> This is the TC user interface.
    * Try to connect, or reboot the TC.
    * If the problem persists, inspect logs of amoothei-tc-connectspice.
* Error / image size is 0 ===> Thinclient is off, so no screenshot could be taken.
* Image resolution wrong, low resolution like 1024x768 ===>
    * Check monitor cabling
    * Control xrandr output (using support button on TC)
* Image resolution correct, but image out of focus  ===>
    * Automatic resolution adjustion using spice-agent didn't work.
    * This is quite common with freshly deployed windows 7 VMs.
    * Fix: any of the 3 methods below should help:
        * fullscreen --> windowed mode --> fullscreen (pressing shift-f11 twice).
        * Disconnect and connect again.
        * Restart thinclient.
    * If it is a linux VM: The window manager inside the VM needs to react to spice resize events. So far only mutter (window manager used by GNOME) implements this.
    


FIXME


### tc_rollout_kexec
Re-Install a thinclient. 

Kickstarting a thinclient is so fast that there is no need for a thinclient upgrade procedure. Instead, we simply re-install thinclients whenever there is a change to configuration or to amoothei-tc-connectspice. But we don't want to touch every thinclient by hand. This tool makes re-installation really easy:

1. make sure TC is running
2. ```tc_kexec <TC>```

Background: This tools connect to the thinclient and then downloads kernel/initrd of the fedora installer using http. Then, kexec is used to load the new kernel/initrd over the running kernel.

FIXME

## Custom tool instances

FIXME

## Manageing Thinclients: Tipps and Tricks

The following commands are to be run on a TC, using tc_ssh.

### Connect to assigned VM
```
killall gxmessage
```

If the TC GUI (based on gxmessage) is shown, then this command terminates the GUI and amoothei-tc-connectspice connects again, that is it connects to postgres database to determine the assigned VM, it connects to ovirt manager using REST API to get spice connection parameters, and then passes them to remote-viewer to initiate a new spice connection.

If the TC is already connected to a VM, nothing happens.


### Disconnect from the VM
```
killall remote-viewer
```

If remote-viewer is running (that is, the TC is connected), then this command forces the TC to disconnect. If the TC is not connected, nothing happens.


### Shutdown / Reboot
```
sudo systemctl poweroff
sudo systemctl reboot
```

Initiates a TC shutdown / restart.

### X11 Programs
Create a screenshot:

```
DISPLAY=:0 xwd -root | convert  - png:- > foo.png
```

FIXME: vdiclient

Run a terminal:

```
DISPLAY=:0 xterm
```

FIXME: vdiclient




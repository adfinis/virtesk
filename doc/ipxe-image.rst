iPXE image for cdroms and usb flash drives
========================================================


Introduction
------------

| In some environments, it is not feasible to do a network install of
  thinclients
| using PXE.

For this cases, an iPXE image for cdroms / usb flash drives can be
built.

| The iPXE image contains an embedded configuration file pointing to
  your infrastructure server.
| It will chainload the network bootloader (pxelinux) configured on your
  infrastructure server using http.

Creating an iPXE image:
-----------------------

Upstream documentation: http://ipxe.org/embed

amoothei-vdi.ipxe:

::

    #!ipxe

    echo
    echo Amoothei-VDI thinclient rollout iPXE compatibility image


    echo
    echo Configuring DHCP...
    dhcp

    # Option 209 pxelinux.configfile
    #    Specify the initial PXELINUX configuration file name, 
    #    which may be qualified or unqualified. 

    # Option 210 pxelinux.pathprefix
    #    Specify the PXELINUX common path prefix, instead of deriving 
    #    it from the boot file name. This almost certainly needs to 
    #    end in whatever character the TFTP server OS uses as a 
    #    pathname separator, e.g. slash (/) for Unix. 

    # Path Prefix for PXELINUX:
    # set 210:string tftp://infrastructure-server/pxelinux/
    set 210:string http://infrastructure-server/tftpboot/pxelinux/

    echo
    prompt --key 0x02 --timeout 2000 Press Ctrl-B for the iPXE command line... && shell ||

    echo 
    echo Chainloading pxelinux.0 ...
    chain http://infrastructure-server/tftpboot/pxelinux/pxelinux.0

Fetching source and build the image:

::

    git clone git://git.ipxe.org/ipxe.git
    cd ipxe.git/src
    make bin/ipxe.usb EMBED=/path/to/amoothei-vdi.ipxe
    make bin/ipxe.iso EMBED=/path/to/amoothei-vdi.ipxe

Afterwards, the images will be available at:

::

    ipxe.git/src/bin/ipxe.usb
    ipxe.git/src/bin/ipxe.iso

Writing the images to cdrom / usb flash drive
---------------------------------------------

Burning cdrom:

::

    wodim -dao ipxe.iso

Writing image to usb flash drive

::

    dd if=ipxe.usb of=/dev/sdc bs=1M; sync

Replace ``/dev/sdc`` with the device where the image shall be written
to. Data on ``/dev/sdc`` will be destroyed.

| When using an usb flash drive to roll out thinclients, please make
  sure you remove it
| as soon as the pxelinux menu is displayed. Otherwise, the kickstart
  installation would overwrite
| your usb flash drive.

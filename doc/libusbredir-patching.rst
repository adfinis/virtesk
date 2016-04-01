.. |br| raw:: html

   <br />

USB Redirect: avoiding USB reset
================================

Solution to avoid problems that might occour when redirecting usb devices over spice. |br|
Only few devices are affected, most devices work without the patches below.


Introduction
------------

Spice used libusbredir to redirect usb devices.

Normally, a reset command is issued to the device before it is redirected.
This works fine for 99% of all avaiable usb devices. |br|
However, some problematic devices have issues with usb resets. Redirect fails with the following error message:

::

    Could not redirect Electronics For Imaging, Inc. [hex] 
    Device: error resetting device: LIBUSB_ERROR_NOT_FOUND.

By adding those devices to an internal blacklist of libusbredir, we can prevent usb reset for them. This way, amoothei-vdi can successfully redirect those devices. However, libusbredir must be patched on all thinclients. The following steps explain how the patching is done.


Setting up an rpm build environment
-----------------------------------

Build Machine: A test machine running the same fedora version as your
thinclients.

Installing build-tools:

::

    # dnf install rpm-build gcc make rpmdevtools rpmlint 

Installing build dependencies:

::

    # dnf install libusb1-devel

Setting up rpm build environment

::

    $ mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    $ echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros

Downloading usbredir sources:

::

    $ dnf download --enablerepo=fedora-source --source usbredir

Unpacking sources into your local RPM Build environment:

::

    $ rpm -i usbredir-0.7-3.fc22.src.rpm

The rpm command above will unpack the following files into your rpm
build environment:

-  ~/rpmbuild/SOURCES/usbredir-0.7.tar.bz2
-  ~/rpmbuild/SPECS/usbredir.spec


Patching libusbredir
--------------------

First, we add a patch file, then we tell rpmbuild to apply our patch
before building the package.

~/rpmbuild/SOURCES/usbredir-blacklist.patch

::

    diff -urN usbredir-0.7/usbredirhost/usbredirhost.c foo/usbredirhost/usbredirhost.c
    --- usbredir-0.7/usbredirhost/usbredirhost.c    2013-11-19 13:52:36.000000000 +0100
    +++ foo/usbredirhost/usbredirhost.c 2015-12-21 15:19:16.277973330 +0100
    @@ -139,6 +139,7 @@
     
     static const struct usbredirhost_dev_ids usbredirhost_reset_blacklist[] = {
         { 0x1210, 0x001c },
    +    { 0x2650, 0x1311 },
         { -1, -1 } /* Terminating Entry */
     };

In the Spec-File ``~/rpmbuild/SPECS/usbredir.spec`` we have to add the
following line to make sure that rpmbuild will knows about our patch:

::

    Patch0:     usbredir-blacklist.patch

Context / location in file:

::

    URL:            http://spice-space.org/page/UsbRedir
    Source0:        http://spice-space.org/download/%{name}/%{name}-%{version}.tar.bz2
    Patch0:     usbredir-blacklist.patch
    BuildRequires:  libusb1-devel >= 1.0.9

In the Spec-File ``~/rpmbuild/SPECS/usbredir.spec`` we have to add the
following line to make sure that rpmbuild will apply patches:

::

    %patch0 -p1

Context / location in file:

::

    %prep
    %setup -q

    %patch0 -p1

    %build
    %configure --disable-static
    make %{?_smp_mflags} V=1

Changing the package version: change the spec-file from

::

    Name:           usbredir
    Version:        0.7
    Release:        3%{?dist}

To:

::

    Name:           usbredir
    Version:        0.7
    Release:        99mypackage3%{?dist}



Building the RPM package:
-------------------------

::

    rpmbuild -ba ~/rpmbuild/SPECS/usbredir.spec

Afterwards, the RPMs will be available at:

::

    ~/rpmbuild/RPMS/x86_64/

Testing: Installing RPM manually:
---------------------------------

On a thinclient, run the following command:

::

    # dnf install usbredir-0.7-99mypackage3.fc22.x86_64.rpm

Now the thinclient should be able to redirect the device.

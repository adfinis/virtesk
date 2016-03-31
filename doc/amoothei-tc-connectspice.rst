Amoothei-VDI: VDI Software running on thinclients
=================================================

--------------

Introduction
------------

Amoothei-tc-connectspice is the software running on thinclients.

It connects to the postgres database, determines the assigned VM, starts
it if necessary, determines spice connection parameters, starts a
spice-client (``remote-viewer``), and passes the connection parameters
to the spice client using a unix domain socket (remote-control of
spice-clients using SPICE-XPI API).

Amoothei-tc-connectspice is not designed to run standalone. It needs to
be run on properly configured thinclients. All necessary configuration
is done when rolling out a thinclient using kickstart.

It features a minimalistic GUI, based on gxmessage. The language is
German, other languages are not available.

The former name was ``connect_spice_client``.

Amoothei-tc-connectspice consists of two programs:

-  **amoothei-tc-connectspice-main**: Main program as described above.
-  **amoothei-tc-connectspice-shutdown-vm**: Called by systemd on
   thinclient `shutdown <start-and-stop-management.md>`__. Will shutdown
   the VM asssigned to the thinclient if configured to do so.

Configuration
-------------

Main config file
~~~~~~~~~~~~~~~~

/etc/connect\_spice\_client/connect\_spice\_client.conf

::

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

Technical user for accessing Ovirt REST API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A technical user, ``ovirt.thinclient@your-ovirt-authentication-domain``,
with appropriate permissions, is needed for accessing the Ovirt
REST-API.

Because of REST API limitations regarding unprivileged users, we grant
minimalistic adminstrator permissions to our technical user. However, he
only will be able to access VDI VMs and no other VMs.

New Ovirt Role ``MinimalAdmin``:

::

    Navigation: Ovirt Webadmin ---> top right corner ---> configure ---> Roles ---> New

    Name: MinimalAdmin
    Description: Minimalistic Administrator Role
    Account Type: Admin

    Check Boxes: leave them all unchecked

| For adding new user
  ``ovirt.thinclient@your-ovirt-authentication-domain`` to Ovirt, it
  first needs to be created in ``your-ovirt-authentication-domain``.
| Then, grant him the role ``MinimalAdmin`` using
  ``Ovirt Webadmin ---> top right corner ---> configure ---> System Permissions --> Add``.

New Ovirt Role ``UserRoleWithReconnect``:

::

    Navigation: Ovirt Webadmin ---> top right corner ---> configure ---> Roles ---> New

    Name:         UserRoleWithReconnect
    Description:  Required for Ovirt VDI Thinclients
    Account Type: User

    Checkboxes:
    [X] Login Permissions                 (System --> Configure System)
    [X] Basic Operations                  (VM --> Basic Operations)
    [X] Remote Log In                     (VM --> Basic Operations)
    [X] Override opened console session   (VM --> Administrative Operations)

Amoothei-virtroom-rollout will grant ``UserRoleWithReconnect`` to
``ovirt.thinclient@your-ovirt-authentication-domain`` on freshly created
VMs.

See also: config-option ``tc_user`` in
`amoothei-vm-rollout.conf <amoothei-vm-rollout-config.md>`__.

Ovirt REST API: SSL CA
~~~~~~~~~~~~~~~~~~~~~~

The Ovirt SSL certificate authority needs to be configured for secure
SSL communication.

Fetch the CA file from http://your-ovirt-manager.fqdn/ca.crt, and put it
into ``ovirt-manager.crt``:

/etc/connect\_spice\_client/ovirt-manager.crt

::

    -----BEGIN CERTIFICATE-----
    # ADJUST
    ...
    -----END CERTIFICATE-----

/etc/connect\_spice\_client/connect\_spice\_client\_logging.conf

::

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

Support message
~~~~~~~~~~~~~~~

| The following message is displayed whenever a user clicks
| on the the support-button on a thinclient:

/etc/connect\_spice\_client/support\_message.txt

::

    ===========================================================
        Amoothei-VDI: Support
    ===========================================================

    For support, please call ...

In addition, some system debug information will be displayed.

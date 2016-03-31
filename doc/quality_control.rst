Amoothei-VDI: Quality Control of virtual rooms
==============================================

--------------

Introduction
------------

A lot of problems can occour during Windows Unattended Setup:

-  Network, DNS, DHCP, Firewall-Problems
-  Network adapter: wrong name, wrong Windows-Firewall-Zone, ...
-  Problems with Active Directory SRV-Records
-  Problems with Windows Domain Join
-  Infrastructure overload can occour if many VMs get joined at the same
   time or many CIFS-Shares are accessed at once.
-  ...

| It is important to detect those problems early, so that a solution can
  be found before users are affected.
| A system administrator has to deal with alot of VMs, therefore an
  efficient way for quality control is necessary.

Windows Unattended Setup: Copying logfiles
------------------------------------------

| First, we wanna introduce a ``autounattend-firstlogon.cmd``-Script
  that will be run inside every Win7-VM that is rolled out.
| The script is running in the *Firstlogon-Phase* in Windows Unattended
  Setup. It will be used for mounting shares, copying logfiles, ...

Parameters
~~~~~~~~~~

-  **someserver**: CIFS-Server (Windows or Samba) containing two
   CIFS-Shares:

   -  **scriptshare**: CIFS-Share, where ``autounattend-firstlogon.cmd``
      is located.
   -  **logfileshare**: CIFS-Share for putting logfiles.
   -  **username@windowsdomain*\ \* and **password**: Credentials to
      access those CIFS-Shares

Autounattend-production.xml.template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need to make sure that our new ``autounattend-firstlogon.cmd``-Script
will be called at the right time:

::

    ...
    <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <FirstLogonCommands>
        <SynchronousCommand wcm:action="add">
          <CommandLine>net use Y: \\someserver\scriptshare /persistent:no /user:username@windowsdomain password</CommandLine>
          <RequiresUserInput>false</RequiresUserInput>
          <Order>20</Order>
        </SynchronousCommand>
        <SynchronousCommand wcm:action="add">
          <CommandLine>cmd /c Y:\autounattend-firstlogon.cmd ${scripttime} ${ComputerName} 1> C:\autounattend-firstlogon.log 2>&1 </CommandLine>
          <RequiresUserInput>false</RequiresUserInput>
          <Order>21</Order>
        </SynchronousCommand>
        <SynchronousCommand wcm:action="add">
          <CommandLine>shutdown /p</CommandLine>
          <RequiresUserInput>false</RequiresUserInput>
          <Order>50</Order>
        </SynchronousCommand>
      </FirstLogonCommands>
    </component>
    ...

| ``autounattend-firstlogon.cmd`` will be called with two parameters,
  the *scripttime* and the *ComputerName*. They will be used later for
  storing the logfiles in a well-organized folder structure.
| Output will be redirected to ``C:\autounattend-firstlogon.log``.

\\\\someserver\\scriptshare\\autounattend-firstlogon.cmd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    rem Parameters passed by Autounattend.xml:
    set DATETIME=%1
    set OWSNAME=%2

    net use R: \\someserver\report

    mkdir R:\%DATETIME%-%OWSNAME%


    xcopy C:\windows\Panther\*.* R:\%DATETIME%-%OWSNAME% /K /E /I /H /Y

    copy C:\Windows\debug\NetSetup.LOG R:\%DATETIME%-%OWSNAME%

    copy C:\Windows\Temp\Domainjoin.log R:\%DATETIME%-%OWSNAME%
    copy C:\Windows\Temp\Domainjoin.log.2 R:\%DATETIME%-%OWSNAME%

    echo %COMPUTERNAME% > R:\%DATETIME%-%OWSNAME%\_SELF-FQDN-%OWSNAME%

    copy C:\autounattend-firstlogon.log R:\%DATETIME%-%OWSNAME%

    net use R: /delete /yes 

Remark: ``net use R: ...`` is the second time a CIFS-Share is mounted.
Windows stores Credentials, this is why we do not need to pass
username/password.

Analyzing Logfiles
~~~~~~~~~~~~~~~~~~

Windows Domain Join
^^^^^^^^^^^^^^^^^^^

Logfile: C:\\Windows\\panther\\UnattendGC\\setupact.log

Search terms:

::

    DJOIN
    0x54a
    Unattended Join: NetJoinDomain succeeded

Many VMs: commands to analyze windows domain joins using the logfiles
archived on the *logfile*-CIFS-Share:

Coarse overview:

::

    grep -c "Unattended Join: NetJoinDomain succeeded" 2014-08-04-*/UnattendGC/setupact.log

Result: 1 if joined successfully, 0 otherwise.

How many times did the windows client try to join into the domain?

::

    grep -c  0x54a 2014-08-04-*/UnattendGC/setupact.log

In infrastructure overload situations, the windows client retries 80-85
times and then gives up.

Details for a single windows client:

::

    grep DJOIN 2014-08-04-1216-test05-vd01/UnattendGC/setupact.log

Amoothei-VDI: Windows Unattended Setup
======================================

--------------

Introduction
------------

Amoothei-virtroom-rollout creates several hunderds VMs by cloneing a
single `Goldimage VM <goldimage.md>`__.

However, simply cloneing a windows VM usually isn't enough, it needs to
be generalized/sysprepped and then it must run though the Windows
Unattended Setup phase for setting ComputerName, ip-address and for
joining into the Active Directory Domain.

This article explains the XML-Configuration-File used to configure and
automatize the Windows Unattended Setup phase.

Please note: Windows Unattended Setup is not an easy topic. This article
covers only the aspects important for amoothei-vdi.

Mako Templating
---------------

`Python-mako <http://docs.makotemplates.org/en/latest/syntax.html>`__ is
used for templating and variable substitution.

Variables:

-  ${ip}
-  ${netmask\_as\_suffix}
-  ${default\_gw}
-  ${ComputerName}
-  ${scripttime}

In general, all keys available in the ``vmconfig``-python-dict can be
used as mako template variables. They can be displayed using
``amoothei-virtroom-show``:

::

    $ amoothei-virtroom-show test01
    [...]
    2016-03-03 15:55:08,231 - rhev_manager - DEBUG - {'ComputerName': 'test01-vd01', 'tc_user': '...', 'description': 'LehrerVM', 'rhev_vm_name': 'test01-vd01', 'ip': '...', 'default_gw': '...', 'cluster': 'Default', 'netmask_as_suffix': '21', 'snapshot_description': 'Automatic snapshot after amoothei-vmrollout, IP=${ip}/${netmask_as_suffix}, scripttime=${scripttime}', 'scripttime': '2016-03-03-1555', 'reset_startvm': 'Always', 'timezone': 'W. Europe Standard Time', 'network_name': '...', 'reset_to_snapshot_regex': <_sre.SRE_Pattern object at 0x201d2f0>, 'workaround_os': 'rhel_7x64', 'autounattend_templatefile': '/etc/amoothei-vdi/Autounattend-production.xml.template', 'usb_enabled': True, 'rollout_startvm': True, 'template': '...', 'memory': 4294967296, 'workaround_timezone': 'Etc/GMT', 'os': 'windows_7x64', 'stateless': False}
    [...]

Sample Config File
------------------

A sample config file is available here:
``sample_config/Autounattend-production.xml.template``. It was tested
with Windows 7 Professional, German, SP1
(``de_windows_7_professional_with_sp1_x64_dvd_u_676919.iso``).

If your are using it with a different language (e.g. not German, not
DE-CH, ...), then you'll have to make adjustments. For example, network
adapters have different names in different languages.

The sample config file **will not "just work"**. You'll have to adapt it
to make it work in your environment.

Important Config Sections
-------------------------

Network
~~~~~~~

Works only for German Windows 7:

::

    <Identifier>LAN-Verbindung</Identifier>

Setting IP and gateway...

::

    <Interfaces>
                    <Interface wcm:action="add">
                        <Identifier>LAN-Verbindung</Identifier>
                        <Ipv4Settings>
                            <DhcpEnabled>false</DhcpEnabled>
                            <Metric>10</Metric>
                            <RouterDiscoveryEnabled>false</RouterDiscoveryEnabled>
                        </Ipv4Settings>
                        <UnicastIpAddresses>
                            <IpAddress wcm:action="add" wcm:keyValue="1">${ip}/${netmask_as_suffix}</IpAddress>
                        </UnicastIpAddresses>
                        <Routes>
                            <Route wcm:action="add">
                                <Identifier>0</Identifier>
                                <NextHopAddress>${default_gw}</NextHopAddress>
                                <Prefix>0.0.0.0/0</Prefix>
                            </Route>
                        </Routes>
                    </Interface>
                </Interfaces>

**Adjust**: Setting DNS-Servers and DNS-Searchdomain...

::

    <Interfaces>
                        <Interface wcm:action="add">
                                <Identifier>LAN-Verbindung</Identifier>
                                    <DNSServerSearchOrder>
                                          <IpAddress wcm:action="add" wcm:keyValue="1">192.0.2.220</IpAddress>
                                    </DNSServerSearchOrder>
                                    <DisableDynamicUpdate>false</DisableDynamicUpdate>
                                    <EnableAdapterDomainNameRegistration>true</EnableAdapterDomainNameRegistration>
                                    <DNSDomain>your-dns-domain.tld</DNSDomain>
                        </Interface>
                    </Interfaces>

**Adjust**: more DNS stuff...

::

           <component name="Microsoft-Windows-NetBT" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral"
                            versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                            <Interfaces>
                                    <Interface wcm:action="add">
                                    <NameServerList>
                                            <IpAddress wcm:action="add" wcm:keyValue="1">192.0.2.220</IpAddress>
                                    </NameServerList>
                                    <Identifier>LAN-Verbindung</Identifier>
                                    <NetbiosOptions>1</NetbiosOptions>
                                    </Interface>
                            </Interfaces>
            </component>

Setting the computer name and timezone...

::

            <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <Display>
                    <ColorDepth>32</ColorDepth>
                    <DPI>96</DPI>
                    <HorizontalResolution>1920</HorizontalResolution>
                    <RefreshRate>75</RefreshRate>
                    <VerticalResolution>1080</VerticalResolution>
                </Display>
                <ComputerName>${ComputerName}</ComputerName>
                <TimeZone>W. Europe Standard Time</TimeZone>
            </component>

**Adjust**: Syncing with timeserver (avoids timezone problems during
Windows Domain Join)...

::

     <RunSynchronous>
                    <RunSynchronousCommand wcm:action="add">
                        <Path>w32tm /config  /manualpeerlist:192.0.2.221 /syncfromflags:MANUAL</Path>
                        <Order>1</Order>
                    </RunSynchronousCommand>
                    <RunSynchronousCommand wcm:action="add">
                        <Path>w32tm /resync</Path>
                        <Order>2</Order>
                    </RunSynchronousCommand>
                    <RunSynchronousCommand wcm:action="add">
                        <Path>w32tm /query /peers</Path>
                        <Order>3</Order>
                    </RunSynchronousCommand>
                </RunSynchronous>

**Adjust**: Windows Domain Join...

::

    <component name="Microsoft-Windows-UnattendedJoin" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <Identification>
                    <Credentials>
                        <Domain>YOUR-ACTIVEDIRECTORY-DOMAIN</Domain>
                        <Username>Administrator4Domainjoins</Username>
                        <Password>PASSWORD</Password>
                    </Credentials>
                    <JoinDomain>YOUR-ACTIVEDIRECTORY-DOMAIN</JoinDomain>
                </Identification>
            </component>

**Adjust**: Local Administrator Password, Account for
FirstLogonCommands, ...

::

              <AutoLogon>
                        <Password>
                                <Value>PASSWORD</Value>
                        </Password>
                    <Username>Administrator</Username>
                    <Enabled>true</Enabled>
                    <LogonCount>1</LogonCount>
                </AutoLogon>
                <UserAccounts>
                    <AdministratorPassword>
                        <Value>PASSWORD</Value>
                        <PlainText>true</PlainText>
                    </AdministratorPassword>
                </UserAccounts>

**Adjust**: Run some custization commands as a last step in the Windows
Unattended Setup...

-  see also: `Quality Control: Windows Unattended
   Setup <quality_control.md>`__.

::

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

                    <!-- Do not delete next item -->
                    <SynchronousCommand wcm:action="add">
                         <CommandLine>shutdown /p</CommandLine>
                         <RequiresUserInput>false</RequiresUserInput>
                         <Order>50</Order>
                    </SynchronousCommand>
    </FirstLogonCommands>

IMPORTANT: Last step: VM shutdown
---------------------------------

It is very important, that after all Windows Unattened Setup tasks run
trough, the VM will shut down. If VMs do not shutdown, then
``amoothei-virtroom-rollout`` will wait forever.

::

                    <SynchronousCommand wcm:action="add">
                         <CommandLine>shutdown /p</CommandLine>
                         <RequiresUserInput>false</RequiresUserInput>
                         <Order>50</Order>
                    </SynchronousCommand>

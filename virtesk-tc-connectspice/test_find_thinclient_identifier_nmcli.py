import find_thinclient_identifier_nmcli

MOCK_DATA_NMCLI_DEVICE_SHOW = '''
GENERAL.DEVICE:                         docker0
GENERAL.TYPE:                           bridge
GENERAL.HWADDR:                         8A:7F:3B:20:49:AE
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     docker0
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/0
IP4.ADDRESS[1]:                         172.17.0.1/16
IP4.GATEWAY:
IP4.ROUTE[1]:                           dst = 169.254.0.0/16, nh = 0.0.0.0, mt = 1000
IP6.GATEWAY:

GENERAL.DEVICE:                         wlp3s0
GENERAL.TYPE:                           wifi
GENERAL.HWADDR:                         28:B2:BD:E6:35:7A
GENERAL.MTU:                            0
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     ADSY-EAP
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/7
IP4.ADDRESS[1]:                         10.9.5.185/16
IP4.GATEWAY:                            10.9.1.1
IP4.DNS[1]:                             10.9.2.1
IP4.DNS[2]:                             10.1.2.8
IP4.DNS[3]:                             10.1.2.22
IP4.DOMAIN[1]:                          adfinis-int.ch
IP6.ADDRESS[1]:                         fe80::db41:83ec:a6e7:a7a4/64
IP6.GATEWAY:

GENERAL.DEVICE:                         enp0s25
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         54:EE:75:2C:E4:D5
GENERAL.MTU:                            1500
GENERAL.STATE:                          20 (unavailable)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
WIRED-PROPERTIES.CARRIER:               off

GENERAL.DEVICE:                         lo
GENERAL.TYPE:                           loopback
GENERAL.HWADDR:                         00:00:00:00:00:00
GENERAL.MTU:                            65536
GENERAL.STATE:                          10 (unmanaged)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
IP4.ADDRESS[1]:                         127.0.0.1/8
IP4.GATEWAY:
IP6.ADDRESS[1]:                         ::1/128
IP6.GATEWAY:
'''

MOCK_DATA_NMCLI_CON_SHOW_ADSY_EAP = '''
connection.id:                          ADSY-EAP
connection.uuid:                        f3008792-bd40-4bbe-9b4d-106eac03c9f9
connection.interface-name:              --
connection.type:                        802-11-wireless
connection.autoconnect:                 yes
connection.autoconnect-priority:        0
connection.timestamp:                   1481184404
connection.read-only:                   no
connection.permissions:                 user:andrea
connection.zone:                        --
connection.master:                      --
connection.slave-type:                  --
connection.autoconnect-slaves:          -1 (default)
connection.secondaries:
connection.gateway-ping-timeout:        0
connection.metered:                     unknown
connection.lldp:                        -1 (default)
802-1x.eap:                             ttls
802-1x.identity:                        andreab
802-1x.anonymous-identity:              --
802-1x.pac-file:                        --
802-1x.ca-cert:                         --
802-1x.ca-path:                         --
802-1x.subject-match:                   --
802-1x.altsubject-matches:
802-1x.domain-suffix-match:             --
802-1x.client-cert:                     --
802-1x.phase1-peapver:                  --
802-1x.phase1-peaplabel:                --
802-1x.phase1-fast-provisioning:        --
802-1x.phase2-auth:                     mschapv2
802-1x.phase2-autheap:                  --
802-1x.phase2-ca-cert:                  --
802-1x.phase2-ca-path:                  --
802-1x.phase2-subject-match:            --
802-1x.phase2-altsubject-matches:
802-1x.phase2-domain-suffix-match:      --
802-1x.phase2-client-cert:              --
802-1x.password:                        <hidden>
802-1x.password-flags:                  1 (agent-owned)
802-1x.password-raw:                    <hidden>
802-1x.password-raw-flags:              0 (none)
802-1x.private-key:                     --
802-1x.private-key-password:            <hidden>
802-1x.private-key-password-flags:      0 (none)
802-1x.phase2-private-key:              --
802-1x.phase2-private-key-password:     <hidden>
802-1x.phase2-private-key-password-flags:0 (none)
802-1x.pin:                             <hidden>
802-1x.pin-flags:                       0 (none)
802-1x.system-ca-certs:                 no
802-11-wireless.ssid:                   ADSY-EAP
802-11-wireless.mode:                   infrastructure
802-11-wireless.band:                   --
802-11-wireless.channel:                0
802-11-wireless.bssid:                  --
802-11-wireless.rate:                   0
802-11-wireless.tx-power:               0
802-11-wireless.mac-address:            --
802-11-wireless.cloned-mac-address:     --
802-11-wireless.mac-address-blacklist:
802-11-wireless.mac-address-randomization:default
802-11-wireless.mtu:                    auto
802-11-wireless.seen-bssids:            06:27:22:F1:EE:54
802-11-wireless.hidden:                 no
802-11-wireless.powersave:              default (0)
802-11-wireless-security.key-mgmt:      wpa-eap
802-11-wireless-security.wep-tx-keyidx: 0
802-11-wireless-security.auth-alg:      --
802-11-wireless-security.proto:
802-11-wireless-security.pairwise:
802-11-wireless-security.group:
802-11-wireless-security.leap-username: --
802-11-wireless-security.wep-key0:      <hidden>
802-11-wireless-security.wep-key1:      <hidden>
802-11-wireless-security.wep-key2:      <hidden>
802-11-wireless-security.wep-key3:      <hidden>
802-11-wireless-security.wep-key-flags: 0 (none)
802-11-wireless-security.wep-key-type:  0 (unknown)
802-11-wireless-security.psk:           <hidden>
802-11-wireless-security.psk-flags:     0 (none)
802-11-wireless-security.leap-password: <hidden>
802-11-wireless-security.leap-password-flags:0 (none)
ipv4.method:                            auto
ipv4.dns:
ipv4.dns-search:
ipv4.dns-options:                       (default)
ipv4.addresses:
ipv4.gateway:                           --
ipv4.routes:
ipv4.route-metric:                      -1
ipv4.ignore-auto-routes:                no
ipv4.ignore-auto-dns:                   no
ipv4.dhcp-client-id:                    --
ipv4.dhcp-timeout:                      0
ipv4.dhcp-send-hostname:                yes
ipv4.dhcp-hostname:                     a-hostname-appeared
ipv4.dhcp-fqdn:                         --
ipv4.never-default:                     no
ipv4.may-fail:                          yes
ipv4.dad-timeout:                       -1 (default)
ipv6.method:                            auto
ipv6.dns:
ipv6.dns-search:
ipv6.dns-options:                       (default)
ipv6.addresses:
ipv6.gateway:                           --
ipv6.routes:
ipv6.route-metric:                      -1
ipv6.ignore-auto-routes:                no
ipv6.ignore-auto-dns:                   no
ipv6.never-default:                     no
ipv6.may-fail:                          yes
ipv6.ip6-privacy:                       -1 (unknown)
ipv6.addr-gen-mode:                     stable-privacy
ipv6.dhcp-send-hostname:                yes
ipv6.dhcp-hostname:                     --
GENERAL.NAME:                           ADSY-EAP
GENERAL.UUID:                           f3008792-bd40-4bbe-9b4d-106eac03c9f9
GENERAL.DEVICES:                        wlp3s0
GENERAL.STATE:                          activated
GENERAL.DEFAULT:                        yes
GENERAL.DEFAULT6:                       no
GENERAL.VPN:                            no
GENERAL.ZONE:                           --
GENERAL.DBUS-PATH:                      /org/freedesktop/NetworkManager/ActiveConnection/4
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/Settings/3
GENERAL.SPEC-OBJECT:                    /org/freedesktop/NetworkManager/AccessPoint/12
GENERAL.MASTER-PATH:                    --
IP4.ADDRESS[1]:                         10.9.5.185/16
IP4.GATEWAY:                            10.9.1.1
IP4.DNS[1]:                             10.9.2.1
IP4.DNS[2]:                             10.1.2.8
IP4.DNS[3]:                             10.1.2.22
IP4.DOMAIN[1]:                          adfinis-int.ch
DHCP4.OPTION[1]:                        requested_ms_classless_static_routes = 1
DHCP4.OPTION[2]:                        requested_domain_search = 1
DHCP4.OPTION[3]:                        requested_host_name = 1
DHCP4.OPTION[4]:                        requested_time_offset = 1
DHCP4.OPTION[5]:                        requested_domain_name = 1
DHCP4.OPTION[6]:                        filename = pxelinux.0
DHCP4.OPTION[7]:                        requested_rfc3442_classless_static_routes = 1
DHCP4.OPTION[8]:                        requested_wpad = 1
DHCP4.OPTION[9]:                        requested_broadcast_address = 1
DHCP4.OPTION[10]:                       next_server = 10.9.2.1
DHCP4.OPTION[11]:                       requested_netbios_scope = 1
DHCP4.OPTION[12]:                       requested_interface_mtu = 1
DHCP4.OPTION[13]:                       requested_subnet_mask = 1
DHCP4.OPTION[14]:                       routers = 10.9.1.1
DHCP4.OPTION[15]:                       dhcp_message_type = 5
DHCP4.OPTION[16]:                       ip_address = 10.9.5.185
DHCP4.OPTION[17]:                       requested_static_routes = 1
DHCP4.OPTION[18]:                       expiry = 1481225250
DHCP4.OPTION[19]:                       requested_domain_name_servers = 1
DHCP4.OPTION[20]:                       broadcast_address = 10.9.255.255
DHCP4.OPTION[21]:                       requested_ntp_servers = 1
DHCP4.OPTION[22]:                       domain_name = adfinis-int.ch
DHCP4.OPTION[23]:                       dhcp_lease_time = 43200
DHCP4.OPTION[24]:                       domain_name_servers = 10.9.2.1 10.1.2.8 10.1.2.22
DHCP4.OPTION[25]:                       requested_netbios_name_servers = 1
DHCP4.OPTION[26]:                       subnet_mask = 255.255.0.0
DHCP4.OPTION[27]:                       network_number = 10.9.0.0
DHCP4.OPTION[28]:                       requested_routers = 1
DHCP4.OPTION[29]:                       dhcp_server_identifier = 10.9.2.1
IP6.ADDRESS[1]:                         fe80::db41:83ec:a6e7:a7a4/64
IP6.GATEWAY:
'''
MOCK_DATA_NMCLI_CON_SHOW_ADSY_EAP_EMPTY = '''
connection.id:                          ADSY-EAP
connection.uuid:                        f3008792-bd40-4bbe-9b4d-106eac03c9f9
connection.interface-name:              --
connection.type:                        802-11-wireless
connection.autoconnect:                 yes
connection.autoconnect-priority:        0
connection.timestamp:                   1481184404
connection.read-only:                   no
connection.permissions:                 user:andrea
connection.zone:                        --
connection.master:                      --
connection.slave-type:                  --
connection.autoconnect-slaves:          -1 (default)
connection.secondaries:
connection.gateway-ping-timeout:        0
connection.metered:                     unknown
connection.lldp:                        -1 (default)
802-1x.eap:                             ttls
802-1x.identity:                        andreab
802-1x.anonymous-identity:              --
802-1x.pac-file:                        --
802-1x.ca-cert:                         --
802-1x.ca-path:                         --
802-1x.subject-match:                   --
802-1x.altsubject-matches:
802-1x.domain-suffix-match:             --
802-1x.client-cert:                     --
802-1x.phase1-peapver:                  --
802-1x.phase1-peaplabel:                --
802-1x.phase1-fast-provisioning:        --
802-1x.phase2-auth:                     mschapv2
802-1x.phase2-autheap:                  --
802-1x.phase2-ca-cert:                  --
802-1x.phase2-ca-path:                  --
802-1x.phase2-subject-match:            --
802-1x.phase2-altsubject-matches:
802-1x.phase2-domain-suffix-match:      --
802-1x.phase2-client-cert:              --
802-1x.password:                        <hidden>
802-1x.password-flags:                  1 (agent-owned)
802-1x.password-raw:                    <hidden>
802-1x.password-raw-flags:              0 (none)
802-1x.private-key:                     --
802-1x.private-key-password:            <hidden>
802-1x.private-key-password-flags:      0 (none)
802-1x.phase2-private-key:              --
802-1x.phase2-private-key-password:     <hidden>
802-1x.phase2-private-key-password-flags:0 (none)
802-1x.pin:                             <hidden>
802-1x.pin-flags:                       0 (none)
802-1x.system-ca-certs:                 no
802-11-wireless.ssid:                   ADSY-EAP
802-11-wireless.mode:                   infrastructure
802-11-wireless.band:                   --
802-11-wireless.channel:                0
802-11-wireless.bssid:                  --
802-11-wireless.rate:                   0
802-11-wireless.tx-power:               0
802-11-wireless.mac-address:            --
802-11-wireless.cloned-mac-address:     --
802-11-wireless.mac-address-blacklist:
802-11-wireless.mac-address-randomization:default
802-11-wireless.mtu:                    auto
802-11-wireless.seen-bssids:            06:27:22:F1:EE:54
802-11-wireless.hidden:                 no
802-11-wireless.powersave:              default (0)
802-11-wireless-security.key-mgmt:      wpa-eap
802-11-wireless-security.wep-tx-keyidx: 0
802-11-wireless-security.auth-alg:      --
802-11-wireless-security.proto:
802-11-wireless-security.pairwise:
802-11-wireless-security.group:
802-11-wireless-security.leap-username: --
802-11-wireless-security.wep-key0:      <hidden>
802-11-wireless-security.wep-key1:      <hidden>
802-11-wireless-security.wep-key2:      <hidden>
802-11-wireless-security.wep-key3:      <hidden>
802-11-wireless-security.wep-key-flags: 0 (none)
802-11-wireless-security.wep-key-type:  0 (unknown)
802-11-wireless-security.psk:           <hidden>
802-11-wireless-security.psk-flags:     0 (none)
802-11-wireless-security.leap-password: <hidden>
802-11-wireless-security.leap-password-flags:0 (none)
ipv4.method:                            auto
ipv4.dns:
ipv4.dns-search:
ipv4.dns-options:                       (default)
ipv4.addresses:
ipv4.gateway:                           --
ipv4.routes:
ipv4.route-metric:                      -1
ipv4.ignore-auto-routes:                no
ipv4.ignore-auto-dns:                   no
ipv4.dhcp-client-id:                    --
ipv4.dhcp-timeout:                      0
ipv4.dhcp-send-hostname:                yes
ipv4.dhcp-hostname:                     --
ipv4.dhcp-fqdn:                         --
ipv4.never-default:                     no
ipv4.may-fail:                          yes
ipv4.dad-timeout:                       -1 (default)
ipv6.method:                            auto
ipv6.dns:
ipv6.dns-search:
ipv6.dns-options:                       (default)
ipv6.addresses:
ipv6.gateway:                           --
ipv6.routes:
ipv6.route-metric:                      -1
ipv6.ignore-auto-routes:                no
ipv6.ignore-auto-dns:                   no
ipv6.never-default:                     no
ipv6.may-fail:                          yes
ipv6.ip6-privacy:                       -1 (unknown)
ipv6.addr-gen-mode:                     stable-privacy
ipv6.dhcp-send-hostname:                yes
ipv6.dhcp-hostname:                     --
GENERAL.NAME:                           ADSY-EAP
GENERAL.UUID:                           f3008792-bd40-4bbe-9b4d-106eac03c9f9
GENERAL.DEVICES:                        wlp3s0
GENERAL.STATE:                          activated
GENERAL.DEFAULT:                        yes
GENERAL.DEFAULT6:                       no
GENERAL.VPN:                            no
GENERAL.ZONE:                           --
GENERAL.DBUS-PATH:                      /org/freedesktop/NetworkManager/ActiveConnection/4
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/Settings/3
GENERAL.SPEC-OBJECT:                    /org/freedesktop/NetworkManager/AccessPoint/12
GENERAL.MASTER-PATH:                    --
IP4.ADDRESS[1]:                         10.9.5.185/16
IP4.GATEWAY:                            10.9.1.1
IP4.DNS[1]:                             10.9.2.1
IP4.DNS[2]:                             10.1.2.8
IP4.DNS[3]:                             10.1.2.22
IP4.DOMAIN[1]:                          adfinis-int.ch
DHCP4.OPTION[1]:                        requested_ms_classless_static_routes = 1
DHCP4.OPTION[2]:                        requested_domain_search = 1
DHCP4.OPTION[3]:                        requested_host_name = 1
DHCP4.OPTION[4]:                        requested_time_offset = 1
DHCP4.OPTION[5]:                        requested_domain_name = 1
DHCP4.OPTION[6]:                        filename = pxelinux.0
DHCP4.OPTION[7]:                        requested_rfc3442_classless_static_routes = 1
DHCP4.OPTION[8]:                        requested_wpad = 1
DHCP4.OPTION[9]:                        requested_broadcast_address = 1
DHCP4.OPTION[10]:                       next_server = 10.9.2.1
DHCP4.OPTION[11]:                       requested_netbios_scope = 1
DHCP4.OPTION[12]:                       requested_interface_mtu = 1
DHCP4.OPTION[13]:                       requested_subnet_mask = 1
DHCP4.OPTION[14]:                       routers = 10.9.1.1
DHCP4.OPTION[15]:                       dhcp_message_type = 5
DHCP4.OPTION[16]:                       ip_address = 10.9.5.185
DHCP4.OPTION[17]:                       requested_static_routes = 1
DHCP4.OPTION[18]:                       expiry = 1481225250
DHCP4.OPTION[19]:                       requested_domain_name_servers = 1
DHCP4.OPTION[20]:                       broadcast_address = 10.9.255.255
DHCP4.OPTION[21]:                       requested_ntp_servers = 1
DHCP4.OPTION[22]:                       domain_name = adfinis-int.ch
DHCP4.OPTION[23]:                       dhcp_lease_time = 43200
DHCP4.OPTION[24]:                       domain_name_servers = 10.9.2.1 10.1.2.8 10.1.2.22
DHCP4.OPTION[25]:                       requested_netbios_name_servers = 1
DHCP4.OPTION[26]:                       subnet_mask = 255.255.0.0
DHCP4.OPTION[27]:                       network_number = 10.9.0.0
DHCP4.OPTION[28]:                       requested_routers = 1
DHCP4.OPTION[29]:                       dhcp_server_identifier = 10.9.2.1
IP6.ADDRESS[1]:                         fe80::db41:83ec:a6e7:a7a4/64
IP6.GATEWAY:
'''

MOCK_DATA_SINGLE_LINE = 'IP4.ADDRESS[1]:                         10.9.5.185/16'


def test_extract_identifiers_from_nmcli(mock):
    def my_check_output(cmd, **kwargs):
        if cmd[:4] == ['nmcli', 'con', 'show', 'ADSY-EAP']:
            return MOCK_DATA_NMCLI_CON_SHOW_ADSY_EAP
        elif cmd[:3] == ['nmcli', 'con', 'show']:
            return MOCK_DATA_NMCLI_CON_SHOW_ADSY_EAP_EMPTY
        elif cmd[:3] == ['nmcli', 'device', 'show']:
            return MOCK_DATA_NMCLI_DEVICE_SHOW
    mock.patch('subprocess.check_output', my_check_output)
    return_value = find_thinclient_identifier_nmcli.extract_identifiers_from_nmcli()

    assert return_value == (['a-hostname-appeared'], ['172.17.0.1', '10.9.5.185', '127.0.0.1'])


def test_get_dhcp_hostname_from_connection(mock):
    patched_check_output = mock.patch('subprocess.check_output')
    patched_check_output.return_value = MOCK_DATA_NMCLI_CON_SHOW_ADSY_EAP
    return_value = find_thinclient_identifier_nmcli.get_dhcp_hostname_from_connection('SOME-NAME')
    assert return_value == 'a-hostname-appeared'


def test_get_dhcp_hostname_from_connection_empty(mock):
    patched_check_output = mock.patch('subprocess.check_output')
    patched_check_output.return_value = MOCK_DATA_NMCLI_CON_SHOW_ADSY_EAP_EMPTY
    return_value = find_thinclient_identifier_nmcli.get_dhcp_hostname_from_connection('SOME-NAME')
    assert return_value is None


def test_get_line_key_value():
    return_value = find_thinclient_identifier_nmcli.get_line_key_value(MOCK_DATA_SINGLE_LINE)
    key, value = return_value
    assert key == 'IP4.ADDRESS[1]'
    assert value == '10.9.5.185/16'


def test_get_line_key_value_none():
    return_value = find_thinclient_identifier_nmcli.get_line_key_value('')
    assert return_value is None

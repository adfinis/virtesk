import find_thinclient_identifier_nmcli as find_nmcli


def test_extract_identifiers_from_nmcli(mock, nmcli_device_show, nmcli_con_show, nmcli_con_show_empty, hostnamectl_transient):
    def my_check_output(cmd, **kwargs):
        if cmd[:4] == ['nmcli', 'con', 'show', 'ADSY-EAP']:
            return nmcli_con_show
        elif cmd[:3] == ['nmcli', 'con', 'show']:
            return nmcli_con_show_empty
        elif cmd[:3] == ['nmcli', 'device', 'show']:
            return nmcli_device_show
        elif cmd[:1] == ['hostnamectl']:
            return hostnamectl_transient
    mock.patch('find_thinclient_identifier_nmcli.subprocess.check_output', my_check_output)
    return_value = find_nmcli.extract_identifiers_from_nmcli()

    assert return_value == (['a-hostname-appeared', 'transient-hostname'], ['172.17.0.1', '10.9.5.185', '127.0.0.1'])


def test_get_dhcp_hostname_from_connection(mock, nmcli_con_show):
    patched_check_output = mock.patch('find_thinclient_identifier_nmcli.subprocess.check_output')
    patched_check_output.return_value = nmcli_con_show
    return_value = find_nmcli.get_dhcp_hostname_from_connection('SOME-NAME')
    assert return_value == 'a-hostname-appeared'


def test_get_dhcp_hostname_from_connection_empty(mock, nmcli_con_show_empty):
    patched_check_output = mock.patch('find_thinclient_identifier_nmcli.subprocess.check_output')
    patched_check_output.return_value = nmcli_con_show_empty
    return_value = find_nmcli.get_dhcp_hostname_from_connection('SOME-NAME')
    assert return_value is None


def test_get_line_key_value(nmcli_device_show_single_line):
    return_value = find_nmcli.get_line_key_value(nmcli_device_show_single_line)
    key, value = return_value
    assert key == 'IP4.ADDRESS[1]'
    assert value == '10.9.5.185/16'


def test_get_line_key_value_none():
    return_value = find_nmcli.get_line_key_value('')
    assert return_value is None


def test_get_active_connections(mock, active_connection):
    patched_check_output = mock.patch('find_thinclient_identifier_nmcli.subprocess.check_output')
    patched_check_output.return_value = active_connection
    return_value = find_nmcli.get_active_connections()
    assert return_value == 2


def test_get_hostname_from_hostnamectl(mock, hostnamectl_transient):
    patched_check_output = mock.patch('find_thinclient_identifier_nmcli.subprocess.check_output')
    patched_check_output.return_value = hostnamectl_transient
    return_value = find_nmcli.extract_hostname_from_hostnamectl()
    assert return_value == 'transient-hostname'


def test_get_hostname_from_hostnamectl_empty(mock, hostnamectl_transient_empty):
    patched_check_output = mock.patch('find_thinclient_identifier_nmcli.subprocess.check_output')
    patched_check_output.return_value = hostnamectl_transient_empty
    return_value = find_nmcli.extract_hostname_from_hostnamectl()
    assert return_value == None

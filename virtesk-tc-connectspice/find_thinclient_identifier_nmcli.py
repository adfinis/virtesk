import subprocess
import re


def extract_identifiers_from_nmcli():
    fixedips = []
    hostnames = []
    nmcli_output = subprocess.check_output(['nmcli', 'device', 'show'], env={'LC_ALL': 'C'})
    for line in nmcli_output.splitlines():
        if re.match('^IP4\.ADDRESS.', line):
            key, value = get_line_key_value(line)
            value = value[:value.index("/")].strip()
            fixedips.append(value)
        elif re.match('^GENERAL\.CONNECTION.', line):
            key, value = get_line_key_value(line)
            dhcp_hostname = get_dhcp_hostname_from_connection(value)
            if dhcp_hostname:
                hostnames.append(dhcp_hostname)
    return (hostnames, fixedips)


def get_dhcp_hostname_from_connection(name):
    if name and name != '--':
        nmcli_output = subprocess.check_output(['nmcli', 'con', 'show', name])
        for line in nmcli_output.splitlines():
            if re.match('^ipv4\.dhcp-hostname.', line):
                key, value = get_line_key_value(line)
                if value != '--':
                    return value


def get_line_key_value(line):
    if line:
        values = str(line).split(':')
        if len(values) == 2:
            key, value = values
            value = value.strip()
            return (key, value)


def main():
    print(extract_identifiers_from_nmcli())


if __name__ == "__main__":
    main()


# match on only eth0
# nmcli device show has hostname?

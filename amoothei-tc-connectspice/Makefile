all:
	echo no default make target...

clean:
	rm -f *.pyc

#release: clean
#	tar -C /root -czf /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz connect_spice_client
#	mv -f /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-dev.tar.gz

release: clean
	tar --transform 's,^,amoothei-tc-connectspice/,S' -czf /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz *.py amoothei-tc-connectspice-shutdown-vm amoothei-tc-connectspice-main
	echo mv -f /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-dev.tar.gz

flake8:
	flake8 --ignore=E221,E222,E251,E272,E241,E203 .


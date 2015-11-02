all:
	echo no default make target...

clean:
	rm -f *.pyc

release: clean
	tar -C /root -czf /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz connect_spice_client
	mv -f /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-dev.tar.gz

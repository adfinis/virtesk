all:
	echo no default make target...

clean:
	rm -f *.pyc

#release: clean
#	tar -C /root -czf /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz connect_spice_client
#	mv -f /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-dev.tar.gz

release: clean
	tar --transform 's,^,virtesk-tc-connectspice/,S' -czf /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz *.py virtesk-tc-connectspice-shutdown-vm virtesk-tc-connectspice-main
	echo mv -f /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-new.tar.gz /var/www/mirror/private/thinclients/thinclient-software/connect_spice_client-dev.tar.gz

flake8: 
	flake8 --doctests -j auto --ignore=E221,E222,E251,E272,E241,E203 *.py virtesk-tc-connectspice-*
flake8-strict: 
	flake8 --doctests -j auto *.py virtesk-tc-connectspice-*
indention_report:
	autopep8 . --recursive --select=E101,E121 --diff
indention_fix:
	autopep8 . --recursive --select=E101,E121 --in-place
autopep8_report:
	autopep8 . --recursive --diff



all:
	python rollout.py --configfile /root/tmpconfig_vmrollout/classrooms.conf test01
flake8: 
	flake8 --ignore=E221,E222,E251,E272,E241,E203 .
clean:
	rm -f *.pyc

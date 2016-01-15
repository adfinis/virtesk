rollout:
	python rollout.py --configfile /root/tmpconfig_vmrollout/classrooms.conf test01
reset:
	python reset.py --configfile /root/tmpconfig_vmrollout/classrooms.conf test01
delete_classroom:
	python delete_classroom_vms.py --configfile /root/tmpconfig_vmrollout/classrooms.conf test01
show:
	amoothei-virtroom-show --configfile /root/tmpconfig_vmrollout/classrooms.conf test01
flake8: 
	flake8 --ignore=E221,E222,E251,E272,E241,E203 .
indention_report:
	autopep8 . --recursive --select=E101,E121 --diff
indention_fix:
	autopep8 . --recursive --select=E101,E121 --in-place
clean:
	rm -f *.pyc

all:
	python rollout.py --configfile /root/tmpconfig_vmrollout/classrooms.conf test01
clean:
	rm -f *.pyc

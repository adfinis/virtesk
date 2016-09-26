flake8: 
	flake8 --doctests -j auto --ignore=E221,E222,E251,E272,E241,E203 *.py virtesk-virtroom-*
flake8-strict: 
	flake8 --doctests -j auto . *.py virtesk-virtroom-*
indention_report:
	autopep8 . --recursive --select=E101,E121 --diff
indention_fix:
	autopep8 . --recursive --select=E101,E121 --in-place
autopep8_report:
	autopep8 . --recursive --diff
clean:
	rm -f *.pyc

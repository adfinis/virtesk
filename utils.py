Traceback (most recent call last):
  File "/usr/bin/autopep8", line 9, in <module>
    load_entry_point('autopep8==0.9.1', 'console_scripts', 'autopep8')()
  File "/usr/lib/python2.7/dist-packages/autopep8.py", line 2309, in main
    options))
  File "/usr/lib/python2.7/dist-packages/autopep8.py", line 1849, in fix_string
    return fix_lines(sio.readlines(), options=options)
  File "/usr/lib/python2.7/dist-packages/autopep8.py", line 1854, in fix_lines
    tmp_source = ''.join(normalize_line_endings(source_lines))
  File "/usr/lib/python2.7/dist-packages/autopep8.py", line 1820, in normalize_line_endings
    newline = find_newline(lines)
  File "/usr/lib/python2.7/dist-packages/autopep8.py", line 955, in find_newline
    if s.endswith(CRLF):
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 45: ordinal not in range(128)

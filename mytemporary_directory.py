import shutil
import tempfile

class TemporaryDirectory(object):
    """Context manager for tempfile.mkdtemp() so it's usable with "with" statement."""
    def __init__(self, prefix):
	#	super(object, self).__init__()
	#super().__init__()
	self.prefix = prefix

    def __enter__(self):
        self.name = tempfile.mkdtemp(prefix=self.prefix)
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
	try:
		shutil.rmtree(self.name)
	except OSError as e:
   		# Reraise unless ENOENT: No such file or directory
    		# (ok if directory has already been deleted)
    		if e.errno != errno.ENOENT:
        		raise


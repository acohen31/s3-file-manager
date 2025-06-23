import os
import sys
import threading

class ProgressMonitor(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen += bytes_amount
            percentage = (self._seen * 100) / self._size
            sys.stdout.write(
                "\r%s   %s / %s   (%.2f%%)\n" % (self._filename, self._seen, self._size, percentage)
            )
            sys.stdout.flush()
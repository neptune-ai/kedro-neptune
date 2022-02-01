import logging
import sys


class GrabbableStdoutHandler(logging.StreamHandler):
    """
    This class is like a StreamHandler using sys.stdout, but always uses
    whatever sys.stdout is currently set to rather than the value of
    sys.stderr at handler construction time.
    This enables neptune-client to capture stdout regardless
    of logging configuration time.
    Based on logging._StderrHandler from standard library.
    """
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)

    @property
    def stream(self):
        return sys.stdout

""" fdbutil exceptions  """
import logging


class FdbUtilException(Exception):
    """ Catchall Exception Handler for FdbUtil """

    def __init__(self, message):
        """ Captures message and sends to logger """

        Exception.__init__(self, message)

        # Log messages as raw strings to prevent multiline log messages
        self.logger = logging.getLogger("fdbutil")
        self.logger.error("%r", message)

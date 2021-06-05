# tasklog.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results transaction log functions.
"""

import sys
import os
import traceback
import datetime

from .. import (
    ERROR_LOG,
    APPLICATION_NAME,
    )


def write_error_to_log():
    """Write the exception to the error log with a time stamp."""
    f = open(os.path.join(sys.argv[1], ERROR_LOG), 'a')
    try:
        f.write(
            ''.join(
                ('\n\n\n',
                 ' '.join(
                     (APPLICATION_NAME,
                      'exception report at',
                      datetime.datetime.isoformat(datetime.datetime.today())
                      )),
                 '\n\n',
                 traceback.format_exc(),
                 '\n\n',
                 ))
            )
    finally:
        f.close()

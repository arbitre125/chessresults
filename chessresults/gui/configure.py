# configure.py
# Copyright 2014 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Describe the emails and attachments containing event results.
"""

import os
import tkinter
import tkinter.messagebox

from emailextract.gui.select import Select

from ..core.emailextractor import EmailExtractor


class Configure(Select):
    
    """Define and use an event result's extraction configuration file.
    """

    def __init__(self, emailextractor=None, **kargs):
        """"""
        if emailextractor is None:
            emailextractor = EmailExtractor
        super().__init__(emailextractor=emailextractor, **kargs)

    def read_file(self, filename):
        """"""
        if self._configuration is not None:
            tkinter.messagebox.showinfo(
                parent=self.root,
                title='Result Extraction Rules',
                message='The configuration file has already been read.')
            return
        config_file = os.path.join(self._folder, filename)
        fn = open(config_file, 'r', encoding='utf-8')
        try:
            self.configctrl.delete('1.0', tkinter.END)
            self.configctrl.insert(tkinter.END, fn.read())
        finally:
            fn.close()
        self._configuration = config_file

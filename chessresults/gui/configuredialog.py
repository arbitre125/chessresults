# configuredialog.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""A simple configuration file text editor.

"""

import tkinter
import tkinter.messagebox

from ..core import constants


def get_configuration_item(configuration_file, item):
    """Return configuration value on file for item or builtin default."""
    try:
        of = open(configuration_file)
        try:
            config_text = of.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=parent,
                message="".join(
                    ("Unable to read from\n\n", default, "\n\n", str(exc))
                ),
                title="Read File",
            )
            return ""
        finally:
            of.close()
    except Exception as exc:
        tkinter.messagebox.showinfo(
            parent=parent,
            message="".join(("Unable to open\n\n", default, "\n\n", str(exc))),
            title="Open File",
        )
        return ""
    key = None
    for i in config_text.splitlines():
        i = i.split(maxsplit=1)
        if not i:
            continue
        if i[0].startswith("#"):
            continue
        if i[0] != item:
            continue
        key = item
        if len(i) == 1:
            value = ""
        else:
            value = i[1].strip()
    if key is None:
        for k, v in constants.DEFAULT_URLS:
            if k == item:
                key = item
                value = v
    if key is None:
        value = ""
    return value

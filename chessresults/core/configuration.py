# configuration.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Access and update names of last used database and configuration files.

The initial values are taken from file named in constants.RESULTS_CONF
in the user's home directory if the file exists.

"""

import os

from ..core import constants

try:
    of = open(os.path.expanduser(os.path.join("~", constants.RESULTS_CONF)))
    try:
        config_text = of.read()
    finally:
        of.close()
        del of
except:
    config_text = ""

_items = {
    constants.RECENT_DATABASE: "~",
    constants.RECENT_EMAIL_SELECTION: "~",
    constants.RECENT_EMAIL_EXTRACTION: "~",
}

for item in config_text.splitlines():
    item = item.strip()
    if len(item) == 0:
        continue
    item = item.split(maxsplit=1)
    if len(item) == 1:
        continue
    k, v = item
    if k not in _items:
        continue
    _items[k] = v
del config_text
try:
    del item
except NameError:
    pass
try:
    del k
except NameError:
    pass
try:
    del v
except NameError:
    pass


def get_configuration_value(item):
    """Return value of configuration item or None if item not found."""
    return _items.get(item)


def set_configuration_value(item, value):
    """Set value of configuration item if item exists."""
    if item in _items:
        if _items[item] != value:
            _items[item] = value
            _save_configuration()


def _save_configuration():
    """Save the configuration in file named in constants.RESULTS_CONF."""
    config_text = []
    for k in sorted(_items):
        config_text.append(" ".join((k, _items[k])))
    config_text = "\n".join(config_text)
    try:
        of = open(
            os.path.expanduser(os.path.join("~", constants.RESULTS_CONF)), "w"
        )
        try:
            of.write(config_text)
        finally:
            of.close()
    except:
        pass

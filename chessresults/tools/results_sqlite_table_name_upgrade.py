# results_sqlite_table_name_upgrade.py
# Copyright 2018 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Convert Results table names to convention used in solenrware_base."""


if __name__ == "__main__":

    from solentware_base.tools.sqlite_table_name_upgrade import (
        SqliteTableNameUpgrade,
    )

    from ..core import filespec

    app = SqliteTableNameUpgrade(filespec.FileSpec())
    if app.root:
        app.root.mainloop()

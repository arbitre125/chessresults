# upgrade_from_0_33_7_to_0_34.py
# Copyright 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Upgrade record definitions for ECF reference data files.

Check the tables exist then do the upgrade.

"""

if __name__ == '__main__':

    import os
    import tkinter
    import tkinter.filedialog
    import apsw

    from solentware_base import apswapi
    from ..basecore import upgrade_from_0_33_7_to_0_34

    root = tkinter.Tk()
    directory = tkinter.filedialog.askdirectory(master = root, initialdir='~')
    root.destroy()
    del root
    if directory:
        database = apswapi.Sqlite3api(
            upgrade_from_0_33_7_to_0_34.FileSpec(),
            directory)
        if os.path.exists(database._home):
            database._dbservices = apsw.Connection(database._home)
            for t in upgrade_from_0_33_7_to_0_34.UPGRADE_FIELDS:

                # Raises an exception if the table does not exist.
                database._dbservices.cursor().execute(
                    t.join(('select count(*) from ', ';')))

            database.close_database()

            upgrade_from_0_33_7_to_0_34.do_upgrade(database)

            database._dbservices = apsw.Connection(database._home)
            for t in (upgrade_from_0_33_7_to_0_34.ECFPLAYERDATE_FIELD_DEF,
                      upgrade_from_0_33_7_to_0_34.ECFCLUBDATE_FIELD_DEF,
                      ):
                database._dbservices.cursor().execute(
                    t.join(('drop table ', ';')))
            database.close_database()

# upgrade_results_from_2-1_to_2-2.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Upgrade a results-2.1 database to results-2.2 format.  The reported grading
code, if any, is held for each player in each event.

The number of attributes defined in resultsrecord.ResultsDBvaluePlayer is
increased from 7 to 8.

At Python 3.6 identical python code works for apsw and sqlite3, but earlier
versions of Python must use the sqlite3.Connection commit() and rollback()
methods.
"""

import tkinter, tkinter.messagebox, tkinter.filedialog
import os
import ast
import sys

apsw_imported = False
bsddb3_imported = False
dptdb_imported = False
sqlite3_imported = False

try:
    import apsw
    apsw_imported = True
except:
    pass
try:
    import bsddb3
    bsddb3_imported = True
except:
    pass
try:
    from dptdb import dptapi
    dptdb_imported = True
except:
    pass
try:
    import sqlite3
    sqlite3_imported = True
except:
    pass


def upgrade_apsw(directory, log):
    dbfile = os.path.join(directory, os.path.basename(directory))
    if not os.path.exists(dbfile):
        log.insert(tkinter.END, '\nUnable to open database with apsw.')
        return None
    try:
        conn = apsw.Connection(dbfile)
    except:
        log.insert(tkinter.END, '\nUnable to open database with apsw.')
        return None
    try:
        tcursor = conn.cursor()
        tcursor.execute('begin')
        tcursor.close()
    except:
        log.insert(tkinter.END, '\nStart upgrade transaction failed.')
        conn.close()
        return True
    try:
        wcursor = conn.cursor()
        wstatement = 'update Player set Value = ? where rowid == ?'
        rcursor = conn.cursor()
        rcursor.execute('select * from Player')
        while True:
            r = rcursor.fetchone()
            if not r:
                break
            data = ast.literal_eval(r[1])
            if len(data) != 7:
                log.insert(tkinter.END, '\nWrong number of elements in data.')
                log.insert(tkinter.END, '\nUpgrade database failed.')
                return False
            data.append(None)
            values = (repr(data), r[0])
            wcursor.execute(wstatement, values)
        rcursor.close()
        wcursor.close()
        tcursor = conn.cursor()
        tcursor.execute('commit')
        tcursor.close()
        log.insert(tkinter.END, '\nDatabase upgraded.')
    except:
        log.insert(tkinter.END, '\nUpgrade database failed.')
        try:
            wcursor.close()
        except:
            pass
        try:
            rcursor.close()
        except:
            pass
        tcursor = conn.cursor()
        try:
            tcursor.execute('rollback')
        except:
            pass
        tcursor.close()
    finally:
        conn.close()
    return True


def upgrade_bsddb3(directory, log):
    try:
        dbenv = bsddb3.db.DBEnv()
        dbenv.open(directory,
                   (bsddb3.db.DB_CREATE |
                    bsddb3.db.DB_RECOVER |
                    bsddb3.db.DB_INIT_MPOOL |
                    bsddb3.db.DB_INIT_LOCK |
                    bsddb3.db.DB_INIT_LOG |
                    bsddb3.db.DB_INIT_TXN |
                    bsddb3.db.DB_PRIVATE))
        db = bsddb3.db.DB(dbenv)
    except:
        log.insert(tkinter.END, '\nUnable to open database with bsddb3.')
        return None
    try:
        dbtxn = dbenv.txn_begin()
    except:
        log.insert(tkinter.END, '\nStart transaction failed.')
        return True
    try:
        odb = db.open('Player', 'Player', txn=dbtxn)
    except:
        dbtxn.abort()
        log.insert(tkinter.END, '\nOpen database failed.')
        return None
    commit = False
    try:
        log.insert(tkinter.END, '\nUpgrading Berkeley DB database.')
        cursor = db.cursor(txn=dbtxn)
        while True:
            r = cursor.next()
            if not r:
                break
            data = ast.literal_eval(r[1].decode())
            if len(data) != 7:
                log.insert(tkinter.END, '\nWrong number of elements in data.')
                log.insert(tkinter.END, '\nUpgrade database failed.')
                return False
            data.append(None)
            newdata = repr(data).encode()
            try:
                cursor.put(r[0], newdata, flags=bsddb3.db.DB_CURRENT)
            except:
                log.insert(tkinter.END, '\nUpgrade record data failed.')
                log.insert(tkinter.END, '\nUpgrade database failed.')
                return False
        commit = True
        log.insert(tkinter.END, '\nDatabase upgraded.')
    except:
        dbtxn.abort()
        log.insert(tkinter.END, '\nUpgrade database failed.')
        return True
    finally:
        try:
            cursor.close()
        except:
            pass
        if commit:
            dbtxn.commit()
        else:
            dbtxn.abort()
        try:
            db.close()
        except:
            pass
        try:
            dbenv.close()
        except:
            pass
    return True


def _join_primary_field_occs(record):
    """Concatenate occurrences of field holding primary value."""
    advance = record.AdvanceToNextFVPair
    fieldocc = record.LastAdvancedFieldName
    valueocc = record.LastAdvancedFieldValue
    primary = 'Player'
    v = []
    while advance():
        if fieldocc() == primary:
            v.append(valueocc().ExtractString())
    return ''.join(v)


def upgrade_dptdb(directory, log):
    dptsysfolder = os.path.join(directory, 'dptsys')
    sysprint = 'CONSOLE'
    parms = os.path.join(dptsysfolder, 'parms.ini')
    msgctl = os.path.join(dptsysfolder, 'msgctl.ini')
    audit = os.path.join(dptsysfolder, 'audit.txt')
    username = 'upgrade'
    cwd = os.getcwd()
    os.chdir(dptsysfolder)
    dbserv = dptapi.APIDatabaseServices(sysprint,
                                        username,
                                        parms,
                                        msgctl,
                                        audit)
    os.chdir(cwd)
    dbserv.Allocate('PLAYER',
                    os.path.join(directory, 'player.dpt'),
                    dptapi.FILEDISP_OLD)
    context = dbserv.OpenContext(dptapi.APIContextSpecification('PLAYER'))
    foundset = context.FindRecords(
        dptapi.APIFindSpecification(
            'Player',
            dptapi.FD_ALLRECS,
            dptapi.APIFieldValue('')),
        dptapi.FD_LOCK_EXCL)
    fieldvalue = dptapi.APIFieldValue()

    # DPT_PRIMARY_FIELD_LENGTH is not set in filespec.py
    # SAFE_DPT_FIELD_LENGTH is 63 in solentware_base.core.constants.py
    # See solentware_base.core.constants.py for why safe_length is needed.
    safe_length = 63

    cursor = foundset.OpenCursor()
    
    try:
        while cursor.Accessible():
            record = cursor.AccessCurrentRecordForReadWrite()
            value = _join_primary_field_occs(record)
            data = ast.literal_eval(value)
            if len(data) != 7:
                log.insert(tkinter.END, '\nWrong number of elements in data.')
                log.insert(tkinter.END, '\nUpgrade database failed.')
                dbserv.Backout()
                return False
            data.append(None)
            newdata = repr(data)
            record.DeleteEachOccurrence('Player')
            for i in range(0, len(newdata), safe_length):
                fieldvalue.Assign(newdata[i:i+safe_length])
                record.AddField('Player', fieldvalue)
            cursor.Advance()
        dbserv.Commit()
        log.insert(tkinter.END, '\nDatabase upgraded.')
        return True
    except:
        dbserv.Backout()
        log.insert(tkinter.END, '\nUpgrade database failed.')
        return True

    finally:
        foundset.CloseCursor(cursor)
        context.DestroyAllRecordSets()
        dbserv.CloseContext(context)
        dbserv.Free('PLAYER')
        cwd = os.getcwd()
        os.chdir(dptsysfolder)
        dbserv.Destroy()
        os.chdir(cwd)


def upgrade_sqlite3(directory, log):
    dbfile = os.path.join(directory, os.path.basename(directory))
    if not os.path.exists(dbfile):
        log.insert(tkinter.END, '\nUnable to open database with sqlite3.')
        return None
    try:
        conn = sqlite3.Connection(dbfile)
    except:
        log.insert(tkinter.END, '\nUnable to open database with sqlite3.')
        return None

    # Does not work before Python 3.6 because the later commit or rollback
    # fails stating there is no active transaction.
    if sys.version_info >= (3, 6):
        try:
            tcursor = conn.cursor()
            tcursor.execute('begin')
            tcursor.close()
        except:
            log.insert(tkinter.END, '\nStart upgrade transaction failed.')
            conn.close()
            return True

    try:
        wcursor = conn.cursor()
        wstatement = 'update Player set Value = ? where rowid == ?'
        rcursor = conn.cursor()
        rcursor.execute('select * from Player')
        while True:
            r = rcursor.fetchone()
            if not r:
                break
            data = ast.literal_eval(r[1])
            if len(data) != 7:
                log.insert(tkinter.END, '\nWrong number of elements in data.')
                log.insert(tkinter.END, '\nUpgrade database failed.')
                return False
            data.append(None)
            values = (repr(data), r[0])
            wcursor.execute(wstatement, values)
        rcursor.close()
        wcursor.close()

        # Does not work before Python 3.6: the commit fails stating there is
        # no active transaction and any updates which should have been done
        # remain done.
        # Replacing the tcursor sequence by a 'conn.commit()' statement
        # succeeds and the updates which should have been done remain done.
        if sys.version_info >= (3, 6):
            tcursor = conn.cursor()
            tcursor.execute('commit')
            tcursor.close()
        else:
            conn.commit()

        log.insert(tkinter.END, '\nDatabase upgraded.')
    except:
        log.insert(tkinter.END, '\nUpgrade database failed.')
        try:
            wcursor.close()
        except:
            pass
        try:
            rcursor.close()
        except:
            pass

        # Does not work before Python 3.6: the rollback fails stating there is
        # no active transaction and any updates which should have been undone
        # remain done.
        # Replacing the tcursor sequence by a 'conn.rollback()' statement
        # succeeds but the updates which should have been undone remain done.
        if sys.version_info >= (3, 6):
            tcursor = conn.cursor()
            try:
                tcursor.execute('rollback')
            except:
                pass
            tcursor.close()
        else:
            conn.rollback()

    finally:
        conn.close()
    return True


if __name__ == '__main__':

    root = tkinter.Tk()
    root.wm_title('Upgrade Results Database from 2.1 to 2.2')
    log = tkinter.Text(master=root)
    log.pack()
    if not (bsddb3_imported or dptdb_imported or sqlite3_imported):
        tkinter.messagebox.showinfo(
            master=root,
            title='Upgrade database',
            message='No database interface modules available')
    else:
        directory = tkinter.filedialog.askdirectory(master=root)
        if directory:
            log.insert(tkinter.END,
                       ' '.join(('Directory:', directory)))
            for e, i in enumerate(
                (apsw_imported,
                 bsddb3_imported,
                 dptdb_imported,
                 sqlite3_imported)):
                if i:
                    if e == 0:
                        log.insert(tkinter.END, '\nTrying apsw.')
                        resp = upgrade_apsw(directory, log)
                    elif e == 1:
                        log.insert(tkinter.END, '\nTrying bsddb3.')
                        resp = upgrade_bsddb3(directory, log)
                    elif e == 2:
                        log.insert(tkinter.END, '\nTrying dptdb.')
                        resp = upgrade_dptdb(directory, log)
                    elif e == 3:
                        log.insert(tkinter.END, '\nTrying sqlite3.')
                        resp = upgrade_sqlite3(directory, log)
                    # None - assume wrong database engine used: try another.
                    # False - data problem on particular record using correct
                    #         database engine.
                    # True - operational problem using correct database engine.
                    if resp is not None:
                        log.insert(tkinter.END,
                                   '\nUpgrade action completed.')
                        break
                    else:
                        log.insert(
                            tkinter.END,
                            '\nTry another available database engine.')
            else:
                log.insert(tkinter.END, '\nAll database engines tried.')
                        
            root.mainloop()
    

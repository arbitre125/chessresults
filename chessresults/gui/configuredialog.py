# configuredialog.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""A simple configuration file text editor.
"""

import tkinter
import tkinter.messagebox

from solentware_misc.gui.exceptionhandler import (
    ExceptionHandler,
    DESTROYED_ERROR,
    FOCUS_ERROR,
    )


class ConfigureDialog(ExceptionHandler):

    """Configuration file text editor in a dialogue.

    Update methods are defined but do not change database.  Subclasses must
    override as needed.

    """

    def __init__(
        self,
        parent,
        configuration_file,
        dialog_title='Edit ECF URL Defaults',
        dialog_cancel_hint='Quit without applying changes',
        dialog_update_hint='Apply changes',
        update_message = 'Confirm apply changes to configuration file.',
        cnf=dict(),
        **kargs):
        """Create a configuration file text editor dialogue."""

        super().__init__()
        of = open(configuration_file)
        try:
            config_text = of.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=parent,
                message=''.join(
                    ('Unable to read from\n\n',
                     default,
                     '\n\n',
                     str(exc))),
                title=dialog_title)
            return
        finally:
            of.close()
        self._configuration_file = configuration_file
        self._update_message = update_message
        self.dialog = tkinter.Toplevel(master=parent)
        self.restore_focus = self.dialog.focus_get()
        self.dialog.wm_title(dialog_title)
        self.configuration = tkinter.Text(master=self.dialog)
        self.configuration.insert(tkinter.END, config_text)
        buttons_frame = tkinter.Frame(master=self.dialog)
        buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        buttonrow = buttons_frame.pack_info()['side'] in ('top', 'bottom')
        for i, b in enumerate((
            ('Cancel',
             dialog_cancel_hint,
             True,
             0,
             self.on_cancel),
            ('Update',
             dialog_update_hint,
             True,
             0,
             self.on_update),
            )):
            button = tkinter.Button(
                master=buttons_frame,
                text=b[0],
                underline=b[3],
                command=self.try_command(b[4], buttons_frame))
            if buttonrow:
                buttons_frame.grid_columnconfigure(i*2, weight=1)
                button.grid_configure(column=i*2 + 1, row=0)
            else:
                buttons_frame.grid_rowconfigure(i*2, weight=1)
                button.grid_configure(row=i*2 + 1, column=0)
        if buttonrow:
            buttons_frame.grid_columnconfigure(
                len(b*2), weight=1)
        else:
            buttons_frame.grid_rowconfigure(
                len(b*2), weight=1)

        self.configuration.pack(
            side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE)

        self.dialog.wait_visibility()
        self.dialog.grab_set()
        self.dialog.wait_window()

    def on_cancel(self, event=None):
        """Show dialogue to confirm cancellation of edit."""
        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message='Confirm cancellation of edit',
            title=self.dialog.wm_title()):
            self.dialog.destroy()
        else:

            # Catch application destroyed while askyesno dialogue displayed.
            try:
                self.dialog.tkraise()
            except tkinter.TclError as error:
                if str(error) != 'raise'.join(DESTROYED_ERROR):
                    raise

    def on_update(self, event=None):
        """Extract text from dialog, write to file, and destroy dialog."""
        title = self.dialog.wm_title()
        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message=self._update_message,
            title=title):
            edited_text = self.configuration.get(
                '1.0', ' '.join((tkinter.END, '-1 chars')))
            self.dialog.destroy()
            of = open(self._configuration_file, 'w')
            try:
                of.write(edited_text)
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message=''.join(
                        ('Unable to write to\n\n',
                         self._configuration_file,
                         '\n\n',
                         str(exc))),
                    title=title)
                return
            finally:
                of.close()
        else:

            # Catch application destroyed while askyesno dialogue displayed.
            try:
                self.dialog.tkraise()
            except tkinter.TclError as error:
                if str(error) != 'raise'.join(DESTROYED_ERROR):
                    raise

    def __del__(self):
        """Restore focus to widget with focus before modal interaction."""
        try:
            #restore focus on dismissing dialogue
            self.restore_focus.focus_set()
        except tkinter._tkinter.TclError as error:
            #application destroyed while confirm dialogue exists
            if str(error) != FOCUS_ERROR:
                raise


def get_configuration_item(configuration_file, item):
    """Return configuration value on file for item or builtin default."""
    try:
        of = open(configuration_file)
        try:
            config_text = of.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=parent,
                message=''.join(
                    ('Unable to read from\n\n',
                     default,
                     '\n\n',
                     str(exc))),
                title='Read File')
            return ''
        finally:
            of.close()
    except Exception as exc:
        tkinter.messagebox.showinfo(
            parent=parent,
            message=''.join(
                ('Unable to open\n\n',
                 default,
                 '\n\n',
                 str(exc))),
            title='Open File')
        return ''
    key = None
    for i in config_text.splitlines():
        i = i.split(maxsplit=1)
        if not i:
            continue
        if i[0].startswith('#'):
            continue
        if i[0] != item:
            continue
        key = item
        if len(i) == 1:
            value = ''
        else:
            value = i[1].strip()
    if key is None:
        for k, v in constants.DEFAULT_URLS:
            if k == item:
                key = item
                value = v
    if key is None:
        value = ''
    return value

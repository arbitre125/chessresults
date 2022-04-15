# uploadresults.py
# Copyright 2022 Roger Marsh
# Licence: See LICENSE.txt (BSD licence)

"""Submit results submission files to the ECF.

Based on upload_results in UploadResultsToECF package.
"""

import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import urllib.parse
import subprocess
import os

try:
    if subprocess.run(["curl", "-V"], capture_output=True).returncode:
        curl = False
    else:
        curl = True
except:
    curl = False
try:
    import requests
except ModuleNotFoundError:
    requests = None

from ...core.ecf import feedback_html
from ...core import configuration
from ...core import constants

_AVOID_SCROLLBAR = "avoidscrollbar"
_START_TEXT = " ".join(
    (
        "Fill in all fields then submit to ECF. ",
        "Right-click for menu.",
    )
)
_OPTION_TEXT = " ".join(
    (
        "Submissions will be like browser with just 'Check and report only'",
        "selected.",
    )
)
_NO_EMAIL_TEXT = "Responses are not sent to the grader's email address."
_EMAIL_TEXT = " ".join(
    (
        "Responses are sent to the grader's email address if the",
        "submission is committed.",
    )
)
_DATE_OF_BIRTH_TEXT = " ".join(
    (
        "Dates like yyyy-mm-dd and dd/mm/yyyy in ECF responses",
        "are redacted to hide any dates of birth.",
    )
)
_OTHER_OPTIONS_TEXT = " ".join(
    (
        "Use UploadResultsToECF or a browser if the Tolerate mismatch",
        "or identical game options need to be selected.",
    )
)
_DEFAULT_LIVE_URL = "https://www.ecfrating.org.uk/v2/submit/"
_DEFAULT_TEST_URL = "https://www.ecfrating.org.uk/sandbox/submit/"
_EVENT_DETAILS = "EVENT DETAILS"
_EVENT_CODE = "EVENT CODE"
_SUBMISSION_INDEX = "SUBMISSION INDEX"
_EVENT_NAME = "EVENT NAME"
_RESULTS_OFFICER_ADDRESS = "RESULTS OFFICER ADDRESS"


class UploadResultsError(Exception):
    pass


class _UploadResults:
    """Base class for sending results submission files to the ECF."""

    def __init__(self):
        """Build the user interface."""
        root = tkinter.Toplevel()
        # root.wm_resizable(width=tkinter.FALSE, height=tkinter.FALSE)
        frame = tkinter.ttk.Frame(master=root)
        frame.pack(expand=tkinter.TRUE, fill=tkinter.BOTH)
        frame.grid_rowconfigure(0)
        frame.grid_rowconfigure(1)
        frame.grid_rowconfigure(2)
        frame.grid_rowconfigure(3)
        frame.grid_rowconfigure(8)
        frame.grid_rowconfigure(9, weight=1)
        frame.grid_columnconfigure(0)
        frame.grid_columnconfigure(1, weight=1)
        tkinter.ttk.Label(master=frame, text="ECF URL").grid(
            column=0, row=0, padx=3
        )
        tkinter.ttk.Label(master=frame, text="File Name").grid(
            column=0, row=1, padx=3
        )
        tkinter.ttk.Label(master=frame, text="User Name").grid(
            column=0, row=2, padx=3
        )
        tkinter.ttk.Label(master=frame, text="Password").grid(
            column=0, row=3, padx=3
        )
        urlname = tkinter.StringVar()
        url_entry = tkinter.ttk.Entry(master=frame)
        url_entry["textvariable"] = urlname
        filename = tkinter.StringVar()
        fn_entry = tkinter.ttk.Entry(master=frame)
        fn_entry["textvariable"] = filename
        username = tkinter.StringVar()
        un_entry = tkinter.ttk.Entry(master=frame)
        un_entry["textvariable"] = username
        password = tkinter.StringVar()
        pw_entry = tkinter.ttk.Entry(master=frame, show="*")
        pw_entry["textvariable"] = password
        if isinstance(self, SubmitResultsFromPrincipals):
            create_new_ecf_codes = tkinter.IntVar()
            cnec_option = tkinter.ttk.Checkbutton(
                master=frame, variable=create_new_ecf_codes
            )
        text = tkinter.Text(master=frame, wrap=tkinter.WORD)
        scrollbar = tkinter.ttk.Scrollbar(
            master=text, orient=tkinter.VERTICAL, command=text.yview
        )
        text.configure(yscrollcommand=scrollbar.set)
        text.tag_configure(_AVOID_SCROLLBAR, rmargin=20)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        url_entry.grid(column=1, row=0, sticky=tkinter.NSEW, padx=3, pady=3)
        fn_entry.grid(column=1, row=1, sticky=tkinter.NSEW, padx=3, pady=3)
        un_entry.grid(column=1, row=2, sticky=tkinter.NSEW, padx=3, pady=3)
        pw_entry.grid(column=1, row=3, sticky=tkinter.NSEW, padx=3, pady=3)
        if isinstance(self, SubmitResultsFromPrincipals):
            cnec_option.grid(column=0, row=4)
            tkinter.ttk.Label(
                master=frame,
                text=" ".join(
                    (
                        "Create new ECF codes automatically. (Only users in",
                        "the PRINCIPALS group can do this.)",
                    )
                ),
            ).grid(column=1, row=4, sticky=tkinter.W, padx=3)
        tkinter.ttk.Label(master=frame, text=_START_TEXT).grid(
            column=0, row=4, columnspan=2, pady=3
        )
        tkinter.ttk.Label(master=frame, text=_DATE_OF_BIRTH_TEXT).grid(
            column=0, row=5, columnspan=2, pady=3
        )
        tkinter.ttk.Label(master=frame, text=_OTHER_OPTIONS_TEXT).grid(
            column=0, row=6, columnspan=2, pady=3
        )
        text.grid(
            column=0, row=9, sticky=tkinter.NSEW, columnspan=2, padx=3, pady=3
        )
        menu = tkinter.Menu(master=frame, tearoff=False)
        menu.add_separator()
        menu.add_command(
            label="Set Default Live Upload URL",
            command=self.set_default_live_upload_url,
            accelerator="Alt F3",
        )
        menu.add_command(
            label="Set Default Test Upload URL",
            command=self.set_default_test_upload_url,
            accelerator="Alt F5",
        )
        menu.add_command(
            label="Select Submission File",
            command=self.select_submission_file,
            accelerator="Alt F7",
        )
        menu.add_separator()
        menu.add_command(
            label="Upload Submission File",
            command=self.upload_results_submission,
            accelerator="Alt F9",
        )
        menu.add_separator()

        # See comments just before save_response definition for
        # reason this menu item is here and not in SubmitResults
        # __init__() method.
        menu.add_command(
            label="Save Response",
            command=self.save_response,
            accelerator="Alt F11",
        )
        menu.add_separator()

        self.menu = menu
        self._bind_for_scrolling_only(text)
        for w in (root, frame, text):
            for wc in w.winfo_children():
                wc.bind("<ButtonPress-3>", self.show_menu)
        un_entry.focus_set()
        self.root = root
        self.frame = frame
        self.url_entry = url_entry
        self.fn_entry = fn_entry
        self.un_entry = un_entry
        self.pw_entry = pw_entry
        if isinstance(self, SubmitResultsFromPrincipals):
            self.create_new_ecf_codes = create_new_ecf_codes
            self.cnec_option = cnec_option
        self.text = text
        self.urlname = urlname
        self.filename = filename
        self.username = username
        self.password = password
        self.most_recent_response = None

    # Put the scrollbar next to, not in, the Text widget and lose the tags.
    def insert_text(self, text):
        """Insert text at end of action log widget."""
        self.text.insert(tkinter.END, text, *(_AVOID_SCROLLBAR,))

    def show_menu(self, event=None):
        """Show the popup menu for widget."""
        self.menu.tk_popup(*event.widget.winfo_pointerxy())

    def select_submission_file(self, event=None):
        """Select a results submission file."""
        conf = configuration.Configuration()
        localfilename = tkinter.filedialog.askopenfilename(
            parent=self.text,
            title="Browse Results Submission File",
            initialdir=conf.get_configuration_value(
                constants.RECENT_SUBMISSION
            ),
        )
        if not localfilename:
            return
        conf.set_configuration_value(
            constants.RECENT_SUBMISSION,
            conf.convert_home_directory_to_tilde(
                os.path.dirname(localfilename)
            ),
        )
        self.filename.set(localfilename)
        try:
            rft = open(localfilename).read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                title="Open Submission File", message=str(exc)
            )
            return
        if not self.is_results_file_text_sane(rft):
            message = "".join(
                (localfilename, " cannot be a valid submission file")
            )
            self.insert_text(message + ".\n\n")
            tkinter.messagebox.showinfo(
                title="Submission File", message=message
            )
        else:
            self.insert_text(
                "".join(
                    (
                        localfilename,
                        " may be a valid submission file: a few mandatory items",
                        " are present.\n\n",
                    )
                )
            )

    def set_default_live_upload_url(self, event=None):
        """Open or download a zip file by URL."""
        self.urlname.set(_DEFAULT_LIVE_URL)

    def set_default_test_upload_url(self, event=None):
        """Open or download a zip file by URL."""
        self.urlname.set(_DEFAULT_TEST_URL)

    def set_email_graders_option(self, options):
        """Raise exception, calller must use a subclass."""
        raise UploadResultsError(
            "Use a subclass which implements 'set_email_graders_option'"
        )

    def set_report_only_option(self, options):
        """Raise exception, calller must use a subclass."""
        raise UploadResultsError(
            "Use a subclass which implements 'set_report_only_option'"
        )

    def set_create_new_ecf_codes_option(self, options):
        """Raise exception, calller must use a subclass."""
        raise UploadResultsError(
            "Use a subclass which implements 'set_create_new_ecf_codes_option'"
        )

    def upload_results_submission(self, event=None):
        """Upload a file of results with curl or Requests package.

        curl, if available, is run by subprocess.run and the code snippet
        from Steve Bush is used if Requests package has to be used.

        """
        try:
            urlp = urllib.parse.urlparse(self.urlname.get())
        except ValueError as exc:
            tkinter.messagebox.showinfo(title="Invalid URL", message=str(exc))
            return
        if not urlp.scheme and not urlp.netloc and not urlp.path:
            tkinter.messagebox.showinfo(
                title="Invalid URL",
                message="".join(
                    (
                        "URL not present ",
                        "(eg: https://www.ecfrating.org.uk/v2/submit/)",
                    )
                ),
            )
            return
        if not urlp.scheme:
            tkinter.messagebox.showinfo(
                title="Incomplete URL",
                message="URL scheme missing (eg: https)",
            )
            return
        if not urlp.netloc:
            tkinter.messagebox.showinfo(
                title="Incomplete URL",
                message="URL address missing (eg: www.ecfrating.org.uk)",
            )
            return
        if not urlp.path:
            tkinter.messagebox.showinfo(
                title="Incomplete URL",
                message="URL path missing (eg: /v2/submit/)",
            )
            return
        localfilename = self.filename.get()
        try:
            rft = open(localfilename).read()
        except Exception as exc:
            self.insert_text(str(exc) + ".\n\n")
            tkinter.messagebox.showinfo(
                title="Open Submission File", message=str(exc)
            )
            return
        if not self.is_results_file_text_sane(rft):
            message = "".join(
                (localfilename, " cannot be a valid submission file")
            )
            self.insert_text(message + ".\n\n")
            tkinter.messagebox.showinfo(
                title="Submission File", message=message
            )
            return
        if not self.username.get():
            message = "No user name supplied"
            self.insert_text(message + ".\n\n")
            tkinter.messagebox.showinfo(title="User Name", message=message)
            return
        if not self.password.get():
            message = "No password supplied"
            self.insert_text(message + ".\n\n")
            tkinter.messagebox.showinfo(title="Password", message=message)
            return
        if not curl and not requests:
            message = "No method of submitting results is available"
            self.insert_text(
                "".join(
                    (
                        message,
                        ".\n\nThe 'curl' utility is not available on your ",
                        "system and the 'Requests' package (from Python ",
                        "Packages) is not installed.  One of these is ",
                        "required.\n\n",
                    )
                )
            )
            tkinter.messagebox.showinfo(title="Upload Method", message=message)
            return
        if self.urlname.get() == _DEFAULT_LIVE_URL:
            if not tkinter.messagebox.askyesno(
                title="Upload Results File",
                message="Do you want to upload to the live ECF database?",
            ):
                return
        if curl:
            args = ["curl", "-k", "-L"]
            args.append("-F username=" + self.username.get())
            args.append("-F password=" + self.password.get())
            args.append("-F uploaded_file=@" + self.filename.get())
            self.set_email_graders_option(args)
            self.set_report_only_option(args)
            self.set_create_new_ecf_codes_option(args)
            args.append(self.urlname.get())
            cp = subprocess.run(args, capture_output=True)
            if cp.returncode:
                message = "".join(
                    (
                        "'curl' exited with non-zero returncode '",
                        str(cp.returncode),
                        "'",
                    )
                )
                self.insert_text(
                    "".join(
                        (
                            message,
                            ".\nAssume upload of ",
                            self.filename.get(),
                            " failed.\n\nError output:\n",
                        )
                    )
                )
                self.insert_text(cp.stderr)
                tkinter.messagebox.showinfo(
                    title="Upload Error", message=message
                )
                self.password.set("")
                return
            message = "".join(
                ("'curl' exited with returncode '", str(cp.returncode), "'")
            )
            self.insert_text(
                "".join(
                    (
                        message,
                        ".\n\nResponse to upload of ",
                        self.filename.get(),
                        " is:\n",
                    )
                )
            )
            try:
                text = cp.stdout.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text = cp.stdout.decode("ascii")
                except UnicodeDecodeError:
                    text = cp.stdout.decode("iso-8859-1")
            self.most_recent_response = self.process_response(text)
            tkinter.messagebox.showinfo(
                title="Upload Response", message=message
            )
            self.password.set("")
            return
        if requests:
            postdata = {
                "username": self.username.get(),
                "password": self.password.get(),
            }
            self.set_email_graders_option(postdata)
            self.set_report_only_option(postdata)
            self.set_create_new_ecf_codes_option(postdata)
            filename = self.filename.get()
            try:
                of = open(filename, "rb")
            except Exception as exc:
                self.insert_text(str(exc) + ".\n\n")
                tkinter.messagebox.showinfo(
                    title="Submit Results File", message=str(exc)
                )
                self.password.set("")
                return
            filedata = {"uploaded_file": (filename, of)}
            try:
                response = requests.post(
                    self.urlname.get(), data=postdata, files=filedata
                )
            except Exception as exc:
                self.insert_text(str(exc) + ".\n\n")
                tkinter.messagebox.showinfo(
                    title="Submit Results File", message=str(exc)
                )
                self.password.set("")
                return
            message = "".join(
                (
                    "Response to upload request is status_code '",
                    str(response.status_code),
                    "'",
                )
            )
            self.insert_text(
                "".join(
                    (
                        message,
                        ".\n\nResponse to upload of ",
                        self.filename.get(),
                        " is:\n",
                    )
                )
            )
            self.most_recent_response = self.process_response(response.text)
            tkinter.messagebox.showinfo(
                title="Upload Response", message=message
            )
            self.password.set("")
            return
        self.password.set("")

    def is_results_file_text_sane(self, text):
        """Return True if text could be a valid ECF results submission.

        Verify a few mandatory fields are present.

        """
        te = [e.strip() for e in text.split("#")]
        event_details = False
        event_code = False
        submission_index = False
        event_name = False
        results_officer_address = False
        for t in te:
            t = t.split("=", 1)[0]
            if t == _EVENT_DETAILS:
                event_details = True
            elif t == _EVENT_CODE:
                event_code = True
            elif t == _SUBMISSION_INDEX:
                submission_index = True
            elif t == _EVENT_NAME:
                event_name = True
            elif t == _RESULTS_OFFICER_ADDRESS:
                results_officer_address = True
            else:
                continue
            if (
                event_details
                and event_code
                and submission_index
                and event_name
                and results_officer_address
            ):
                return True
        return False

    def process_response(self, response):
        fb = feedback_html.FeedbackHTML()
        fb.submission_file_name = self.filename.get()
        fb.responsestring = response
        fb.feed(response)
        fb.insert_whitespace_and_redact_dates()
        fb.find_player_lists()
        self.insert_text("\n\n")
        if (
            fb.feedbacknumbers is None
            or fb.feedbackplayers is None
            or fb.submissionpins is None
            or fb.submissionplayers is None
        ):
            message = "".join(
                (
                    "The upload is assumed to have failed because the player ",
                    "lists cannot be found",
                )
            )
            self.insert_text(message + ".\n\n")
            tkinter.messagebox.showinfo(
                title="Upload Response", message=message
            )
            return fb
        self.insert_text(
            "List of players generated in response to submission\n\n"
        )
        self.insert_text(fb.feedbackplayers[0])
        self.insert_text("\n")
        for n, p in zip(fb.feedbacknumbers, fb.feedbackplayers[1:]):
            self.insert_text("".join((n, p, "\n")))
        self.insert_text("\n\nList of players in the submission\n\n")
        self.insert_text(fb.submissionplayers[0])
        for n, p in zip(fb.submissionpins, fb.submissionplayers[1:]):
            self.insert_text("".join((n, p)))
        self.insert_text(
            "".join(
                (
                    "\n\nThe submission PINs and feedback players in display order ",
                    "match up as follows:\n\n",
                )
            )
        )
        for n, s, p in zip(
            fb.feedbacknumbers, fb.submissionpins, fb.feedbackplayers[1:]
        ):
            self.insert_text(
                "".join((n.strip(), "\t", s[1:], "\t\t", p, "\n"))
            )
        self.insert_text("\n\n")
        return fb

    def _bind_for_scrolling_only(self, widget):
        widget.bind("<KeyPress>", "break")
        widget.bind("<Home>", "continue")
        widget.bind("<Left>", "continue")
        widget.bind("<Up>", "continue")
        widget.bind("<Right>", "continue")
        widget.bind("<Down>", "continue")
        widget.bind("<Prior>", "continue")
        widget.bind("<Next>", "continue")
        widget.bind("<End>", "continue")

    # Moved from SubmitResults because ECF responses do not happen as
    # expected from description.  It seems necessary to be able to save
    # responses to 'check and report' submissions to get new ECF codes
    # reported in a response for applying feedback.
    # Steps are:
    #      1. Do a submission in a browser and request new ECF codes.
    #      2. Do a 'submit and commit' submission in this application.
    #         The response says the ECF codes will be allocated on
    #         commit, but the commit seems to have been done already
    #         because nothing is available to commit (pending?) when
    #         accessed via browser and resubmitting the file gets the
    #         response 'submission number already committed'.
    #      3. Do a 'check and report' submission in this application.
    #         The response says the 'new' players have been matched to
    #         ECF codes; which appears to be true because the ECF code
    #         download is able to retrieve the records.
    #         Feedback processing will pick up the 'matches' and apply
    #         them, saving quite a lot of fiddly effort.
    #
    # The responses given appear to be a step behind where the process
    # has got to!
    #
    def save_response(self, event=None):
        """Save response to a successful upload."""
        if self.most_recent_response is None:
            tkinter.messagebox.showinfo(
                title="Save Response", message="No response available to save"
            )
            return
        if self.most_recent_response.responsestring is None:
            tkinter.messagebox.showinfo(
                title="Save Response",
                message="No data available in response to save",
            )
            return
        if self.most_recent_response.issues_exist:
            tkinter.messagebox.showinfo(
                title="Save Response",
                message="".join(
                    (
                        "Cannot save response because upload was not ",
                        "committed by ECF",
                    )
                ),
            )
            return
        if (
            self.most_recent_response.submission_file_name
            != self.filename.get()
        ):
            if not tkinter.messagebox.askyesno(
                title="Save Response",
                message="".join(
                    (
                        "The current response is for\n\n",
                        self.most_recent_response.submission_file_name,
                        "\n\nnot the one shown in 'File Name'.\n\n",
                        "Do you want to save the current response?",
                    )
                ),
            ):
                return
        title = " ".join(
            (
                "Save Response for",
                os.path.basename(
                    self.most_recent_response.submission_file_name
                ),
            )
        )
        conf = configuration.Configuration()
        filename = tkinter.filedialog.asksaveasfilename(
            parent=self.text,
            title=title,
            initialdir=conf.get_configuration_value(constants.RECENT_FEEDBACK),
        )
        if not filename:
            return
        conf.set_configuration_value(
            constants.RECENT_FEEDBACK,
            conf.convert_home_directory_to_tilde(os.path.dirname(filename)),
        )
        of = open(filename, mode="w")
        try:
            of.write(self.most_recent_response.responsestring)
        except Exception as exc:
            message = "Error while saving response"
            self.insert_text(
                "".join(
                    (
                        message,
                        " for ",
                        self.most_recent_response.submission_file_name,
                        ".\n\nReported exception is:\n",
                        str(exc),
                    )
                )
            )
            tkinter.messagebox.showinfo(title=title, message=message)
            return
        finally:
            of.close()
        self.insert_text(
            "".join(
                (
                    "Response for ",
                    self.most_recent_response.submission_file_name,
                    " saved in ",
                    filename,
                    ".\n\n",
                )
            )
        )


class SubmitResults(_UploadResults):
    """Submit and commit results file to the ECF."""

    def __init__(self):
        """Build the user interface."""
        super().__init__()
        self.root.wm_title("Submit ECF Results Submission File")
        tkinter.ttk.Label(master=self.frame, text=_EMAIL_TEXT).grid(
            column=0, row=7, columnspan=2, pady=3
        )

    def set_email_graders_option(self, options):
        """Send response to grader by email."""
        if curl:
            options.append("-F email_graders=")
        elif requests:
            options["email_graders"] = "on"

    def set_report_only_option(self, options):
        """Do nothing.

        Default action is commit submission if it passes validation.

        """

    def set_create_new_ecf_codes_option(self, options):
        """Do nothing.

        Only submitters in the PRINCIPALS group are able to do this.

        """


# This is a guess at how to emulate the webpage 'Create new ECF codes' option
# for PRINCIPAL users.  It is either wrong or not supported in the API at
# https://www.ecfrating.org.uk/v2/submit/ after tests at 'sandbox' version
# where the behaviour is same as seen in SubmitResults class.
class SubmitResultsFromPrincipals(SubmitResults):
    """Submit and commit results file to the ECF.

    Submitters in the PRINCIPALS group are able to do this in the web
    interface.

    """

    def set_create_new_ecf_codes_option(self, options):
        """Create new ECF codes when requested if submission file is valid."""
        if self.create_new_ecf_codes.get():
            if curl:
                options.append("-F auto_create_players=")
            elif requests:
                options["auto_create_players"] = "on"


class CheckAndReportResults(_UploadResults):
    """Check and Report only results file submission to the ECF."""

    def __init__(self):
        """Build the user interface."""
        super().__init__()
        self.root.wm_title("Check and Report ECF Results Submission File")
        tkinter.ttk.Label(master=self.frame, text=_NO_EMAIL_TEXT).grid(
            column=0, row=7, columnspan=2, pady=3
        )
        tkinter.ttk.Label(master=self.frame, text=_OPTION_TEXT).grid(
            column=0, row=8, columnspan=2, pady=3
        )

    def set_email_graders_option(self, options):
        """Do nothing.

        Output for check and report is not sent to graders by email.

        """

    def set_report_only_option(self, options):
        """Validate submission but do not commit."""
        if curl:
            options.append("-F report_only=")
        elif requests:
            options["report_only"] = "on"

    def set_create_new_ecf_codes_option(self, options):
        """Do nothing.

        The submission file is not being committed.

        """

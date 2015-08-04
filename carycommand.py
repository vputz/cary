from abc import abstractmethod, ABCMeta, abstractproperty
import tempfile
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import shutil


class CaryCommand(metaclass=ABCMeta):
    """
    Abstract class for Cary commands--basically a registerable
    factory for Actions
    """

    @abstractproperty
    def name(self):
        return "name"

    @abstractproperty
    def description(self):
        return "description"

    @abstractproperty
    def required_attachments(self):
        return ["required attachment filenames"]

    @abstractmethod
    def _create_action(self, parsed_message):
        """create an action object and return it; redefine!"""
        return None

    def create_action(self, parsed_message):
        action = self._create_action(parsed_message)
        self.configure_action(action)
        return action

    def configure_action(self, action):
        action.set_config(self.config)

    def set_config(self, new_config, **kwargs):
        if kwargs is not None:
            self.config = dict(new_config, **kwargs)
        else:
            self.config = dict(new_config)


class CaryAction(metaclass=ABCMeta):
    """
    Abstract Cary action; this is what is associated with a message
    and actually executes something useful.  Often you will just have
    to redefine "action"
    """
    def __init__(self, parsed_message):
        self._message = parsed_message

    def set_config(self, config, **kwargs):
        self.config = dict(config, **kwargs)

    def execute(self):
        """
        Actually performs the action -- don't redefine this; call directly
        """
        self.make_working_directories()
        self.save_message_text()
        self.save_attachments()
        self.validate_command()
        if self.command_is_valid:
            self.execute_action()
            self.write_response(self.response_body, self.response_body_html)
        else:
            self.write_response(self.invalid_command_response, None)

    def make_working_directories(self):
        self.working_dir = tempfile.mkdtemp(
            dir=os.path.join(self.config['WORKSPACE_DIR'], 'transactions'))
        self.input_dir = os.path.join(self.working_dir, 'input')
        os.mkdir(self.input_dir)
        self.output_dir = os.path.join(self.working_dir, 'output')
        os.mkdir(self.output_dir)
        logging.log(logging.INFO, "Began transaction in "+self.working_dir)

    def save_message_text(self):
        msg_filename = os.path.join(self.input_dir, "message.txt")
        with open(msg_filename, 'w') as f:
            f.write(self._message.message_text)

    def save_attachments(self):
        self._attachments = []
        for attachment in self._message.attachments:
            fnam = CaryAction.safe_filename(self.input_dir, attachment['name'])
            self._attachments.append(fnam)
            with open(fnam, "wb") as f:
                f.write(attachment['data'])

    @abstractmethod
    def validate_command(self):
        """Redefine this; this is where you do your error checking to
        make sure the command is valid.  This should do two things:

        first, it must set self.command_is_valid to be True or False;

        second, if command_is_valid is False, it should set
          self.invalid_command_response to
          a useful message body that can be returned.
        """
        pass

    @abstractmethod
    def execute_action(self):
        """
        Redefine this.  Actually executes the action, with the message
        body and attachments saved to disk.

        This should write the outgoing attachments as required;
        it should then set self._output_filenames to an array of the outgoing
        attachments
        """
        pass

    def write_response(self, body, html_body=None):
        """
        Template method for writing the response; the parts should be redefined
        """
        outer = MIMEMultipart() if html_body is None\
          else MIMEMultipart("alternative")
        outer['Subject'] = self.response_subject
        outer['To'] = self._message.from_address
        outer['From'] = self.config['FROM_ADDRESS']
        outer.attach(MIMEText(body, 'plain'))
        if html_body is not None:
            outer.attach(MIMEText(html_body, 'html'))
        self.attach_files(outer, self._output_filenames)
        with open(os.path.join(self.output_dir, 'message.txt'), "w") as f:
            s = outer.as_string()
            f.write(s)

    def response(self):
        result = None
        with open(os.path.join(self.output_dir, 'message.txt')) as f:
            result = f.read()
        return result

    @property
    @abstractmethod
    def response_subject(self):
        """What the return subject line should say; redefine"""
        return ""

    @property
    @abstractmethod
    def response_body(self):
        """what the body of the response method should say; redefine"""
        return ""

    @property
    def response_body_html(self):
        """What the body of the response method should say--in HTML.
        Usually this simply returns None, but redefine if you wish an
        HTML version of the message"""
        return None

    @staticmethod
    def safe_filename(dir, fnam):
        """
        Takes a string and returns a "safe" temporary filename that bears
        some resemblance to the original
        """
        name, extension = os.path.splitext(fnam)
        snam = "".join(x for x in name if (x.isalnum() or x == "_"))
        return os.path.join(dir, snam+extension)

    @staticmethod
    def attach_files(outer, filenames):
        for fnam in filenames:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(fnam, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="{0}"'.format(
                                os.path.split(fnam)[1]))
            outer.attach(part)

    def clean_up(self):
        """
        Removes the working dir; use with some caution!
        """
        shutil.rmtree(self.working_dir)

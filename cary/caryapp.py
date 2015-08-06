import fnmatch
from cary.parsed_email import ParsedEmail
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class CaryApp():

    def __init__(self):
        self.command_table = {}
        self.allowed_addresses = []
        self.should_respond = False
        self.should_clean_up = False

    def add_command(self, command_name, command):
        self.command_table[command_name] = command

    def is_valid_address(self, address):
        result = False
        for pattern in self.allowed_addresses:
            if fnmatch.fnmatch(address.lower(), pattern.lower()):
                result = True
        return result

    def process_message(self, msg):
        p = ParsedEmail(msg)
        logging.info("Message from {0}:{1}".format(p.from_address, p.subject))
        if self.is_valid_address(p.from_address):
            self.dispatch_command(p)

    def dispatch_command(self, parsed_msg):
        if parsed_msg.subject in self.command_table:
            command = self.command_table[parsed_msg.subject]
            action = command.create_action(parsed_msg)
            action.execute()
            self.last_subject = action.response_subject
            self.last_response = action.response()
        else:
            self.last_subject = "I'm sorry, I didn't understand"
            self.last_response = self.help_response(
                self.last_subject,
                parsed_msg.from_address)

        if self.should_respond:
            self.send_response(self.last_response, parsed_msg.from_address, self.last_response)

        if self.should_clean_up:
            action.clean_up()

    @property
    def help(self):
        return "Hi!  I'm Cary.  Send me a message with one of the following " \
          "in the title, and I'll do my best to respond usefully:\n\n\t""" \
          + "\n\t".join("{0} - {1}".format(name, self.command_table[name].description)
                        for name in self.command_table.keys())

    def help_response(self, subject, to_address):
        """
        This should probably be a separate command that is matched when nothing else is, but
        I'm putting it here because it needs knowledge of other commands.
        """
        outer = MIMEMultipart()
        outer['Subject'] = subject
        outer['To'] = to_address
        outer['From'] = self.return_address
        outer.attach(MIMEText(self.help))
        return outer.as_string()
        

    @property
    def allowed_addresses(self):
        return self._allowed_addresses

    @allowed_addresses.setter
    def allowed_addresses(self, value):
        self._allowed_addresses = value

    @property
    def workspace(self):
        return self._workspace

    @workspace.setter
    def workspace(self, value):
        self._workspace = value

    @property
    def should_clean_up(self):
        return self._should_clean_up

    @should_clean_up.setter
    def should_clean_up(self, value):
        self._should_clean_up = value

    @property
    def smtp_host(self):
        return self._smtp_host

    @smtp_host.setter
    def smtp_host(self, value):
        self._smtp_host = value

    @property
    def return_address(self):
        return self._return_address

    @return_address.setter
    def return_address(self, value):
        self._return_address = value

    @property
    def should_respond(self):
        return self._should_respond

    @should_respond.setter
    def should_respond(self, value):
        self._should_respond = value

    def send_response(self, subject, to_address, response):
        """
        Sends the response; this sends the tempdir/output/message.txt to
        the from: in the input message
        """
        
        logging.debug(
            "Sending mail using SMTP host {0}, return {1}, to {2}".format(
                self.smtp_host, self.return_address, to_address))
        logging.debug("Response:\n{0}".format(response))
        s = smtplib.SMTP(self.smtp_host)
        logging.debug("Types: {0}, {1}, {2}".format(
            type(self.return_address),
            type(to_address),
            type(response)))
        s.sendmail(self.return_address, to_address, response)

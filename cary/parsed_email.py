import re
import email


class ParsedEmail(object):

    def __init__(self, message_text):
        self._message_text = message_text
        self._message = email.message_from_string(message_text)
        self.parse_attachments()

    @property
    def message_text(self):
        return self._message_text

    @property
    def from_address(self):
        return re.search("<(.*)>", self._message['From']).group(1)

    @property
    def subject(self):
        return self._message['Subject']

    @property
    def body(self):
        result = ""
        for part in self._message.walk():
            if part.get_content_type() == "text/plain":
                result += part.get_payload(
                    decode=True).decode('utf-8','replace')
        return result

    def parse_attachments(self):
        self._attachments = [ParsedEmail.attachment_from_part(p)
                             for p in self._message.walk()
                             if ParsedEmail.part_has_attachment(p)]

    @property
    def attachments(self):
        return self._attachments

    # from http://www.ianlewis.org/en/parsing-email-attachments-python
    @staticmethod
    def attachment_from_part(part):
        file_data = part.get_payload(decode=True)
        # unsure if decoding is necessary, but in python3 seems to be
        attachment = dict(data=file_data,
                          content_type=part.get_content_type(),
                          size=len(file_data),
                          name=None,
                          create_date=None,
                          mod_date=None,
                          read_date=None)

        dispositions = ParsedEmail.part_dispositions(part)
        for param in dispositions[1:]:
            name, value = param.split("=")
            name = name.lower().strip()
            value = value.strip().strip('"')
            if name == "filename":
                attachment['name'] = value
            elif name == "create-date":
                attachment['create_date'] = value  # TODO: datetime
            elif name == "modification-date":
                attachment['mod_date'] = value  # TODO: datetime
            elif name == "read-date":
                attachment['read_date'] = value  # TODO: datetime
        return attachment

    @staticmethod
    def part_dispositions(part):
        result = []
        content_disposition = part.get("Content-Disposition", None)
        if content_disposition:
            result = content_disposition.strip().split(";")
        return result

    @staticmethod
    def part_has_attachment(part):
        dispositions = ParsedEmail.part_dispositions(part)
        if len(dispositions) > 0 and dispositions[0].lower() == "attachment":
            return True
        else:
            return False

from pytest import fixture
from pytest_bdd import scenario, given, when, then
from cary.parsed_email import ParsedEmail
import email


@scenario('parse_email.feature', 'Parsing an email')
def test_parse_email():
    pass


@given('the text of an email message')
def message_text():
    return """                                                                                                                                                                                                                                                               
MIME-Version: 1.0
Sender: vbputz@gmail.com
Received: by 10.96.179.170 with HTTP; Thu, 2 Jul 2015 02:04:04 -0700 (PDT)
Date: Thu, 2 Jul 2015 09:04:04 +0000
Delivered-To: vbputz@gmail.com
X-Google-Sender-Auth: sJJa-x7wTzckqir8dDyeENlpqKE
Message-ID: <CADsvd-QQVe4QYBW9+168U_qr3tB3TWQsia1C7ci3ioVLFMqvCA@mail.gmail.com>
Subject: Test subject
From: Vic Putz <vputz@nyx.net>
To: Vic Putz <vbputz@gmail.com>
Content-Type: multipart/mixed; boundary=001a113736b49bc7260519e0b89d

--001a113736b49bc7260519e0b89d
Content-Type: text/plain; charset=UTF-8

Test body

--001a113736b49bc7260519e0b89d
Content-Type: application/octet-stream; name=text_1
Content-Disposition: attachment; filename=text_1
Content-Transfer-Encoding: base64
X-Attachment-Id: f_ibm0yd5t0

SGVsbG8sIHRleHQgMSEK
--001a113736b49bc7260519e0b89d
Content-Type: application/octet-stream; name=text_2
Content-Disposition: attachment; filename=text_2
Content-Transfer-Encoding: base64
X-Attachment-Id: f_ibm0ynoc1

SGVsbG8sIHRleHQgMiEK
--001a113736b49bc7260519e0b89d--"""


@given("that is parsed to a message")
def message(message_text):
    return ParsedEmail(message_text)


@then('I should get the from address')
def get_from_address(message):
    assert message.from_address == "vputz@nyx.net"


@then('I should get the subject')
def get_subject(message):
    assert message.subject == 'Test subject'


@then('I should get the body')
def get_body(message):
    assert message.body == 'Test body\n'


@then('a list of attachments')
def get_attachments(message):
    attachments = message.attachments
    assert len(attachments) == 2
    assert attachments[0]["name"] == "text_1"
    assert attachments[0]["data"] == b"Hello, text 1!\n"
    assert attachments[1]["name"] == "text_2"
    assert attachments[1]["data"] == b"Hello, text 2!\n"

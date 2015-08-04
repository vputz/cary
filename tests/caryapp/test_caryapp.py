from pytest_bdd import scenario, given, then, parsers
from cary.caryapp import CaryApp
from cary.echocommand import EchoCommand
from cary.parsed_email import ParsedEmail

@scenario('caryapp.feature', 'Check allowed emails')
def test_allowed_emails():
    pass


@given('A configured app')
def configured_app():
    app = CaryApp()
    app.allowed_addresses = ['vputz@nyx.net']
    app.return_address = "cary@thingotron.com"
    cmd = EchoCommand()
    app.add_command("echo", cmd)
    return app


def ppatterns(p):
    return [s.strip() for s in p.split(",")]


@given('Allowed <patterns> and an <address>')
def patternconfigured_app(configured_app, patterns, address):
    configured_app.allowed_addresses = ppatterns(patterns)
    return configured_app


@then('I should check <validity>')
def should_check_validity(patternconfigured_app, address, validity):
    assert str(patternconfigured_app.is_valid_address(address)) == validity


@scenario('caryapp.feature', 'Check help text')
def test_help_text():
    pass


@given('a valid email with invalid command')
def valid_email_with_invalid_command():
    message_text = """                                                                                                                                                                                                                                                               
MIME-Version: 1.0
Sender: vbputz@gmail.com
Received: by 10.96.179.170 with HTTP; Thu, 2 Jul 2015 02:04:04 -0700 (PDT)
Date: Thu, 2 Jul 2015 09:04:04 +0000
Delivered-To: vbputz@gmail.com
X-Google-Sender-Auth: sJJa-x7wTzckqir8dDyeENlpqKE
Message-ID: <CADsvd-QQVe4QYBW9+168U_qr3tB3TWQsia1C7ci3ioVLFMqvCA@mail.gmail.com>
Subject: INVALIDCOMMAND
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
    return message_text


@then('App should send help text')
def should_send_help(configured_app, valid_email_with_invalid_command):
    configured_app.process_message(valid_email_with_invalid_command)
    p1 = ParsedEmail(configured_app.last_response)
    p2 = ParsedEmail(configured_app.help_response(
        "I'm sorry, I didn't understand",
        "vputz@nyx.net"))

    assert p1.subject == p2.subject
    assert p1.body == p2.body

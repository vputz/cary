from pytest_bdd import scenario, given, then
from cary.echocommand import EchoAction
from cary.parsed_email import ParsedEmail
import tempfile
import os
import shutil

@scenario('echocommand.feature', 'Basic echo command')
def test_echo_command():
    pass


@given('an email message with a body and attachments')
def echoaction(request):
    message_text = """                                                                                                                                                                                                                                                               
MIME-Version: 1.0
Sender: vbputz@gmail.com
Received: by 10.96.179.170 with HTTP; Thu, 2 Jul 2015 02:04:04 -0700 (PDT)
Date: Thu, 2 Jul 2015 09:04:04 +0000
Delivered-To: vbputz@gmail.com
X-Google-Sender-Auth: sJJa-x7wTzckqir8dDyeENlpqKE
Message-ID: <CADsvd-QQVe4QYBW9+168U_qr3tB3TWQsia1C7ci3ioVLFMqvCA@mail.gmail.com>
Subject: echo
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
    tempworkingdir = tempfile.mkdtemp()
    os.mkdir(os.path.join(tempworkingdir, "transactions"))

    def fin():
        print("DELETING {0}".format(tempworkingdir))
        # shutil.rmtree(tempworkingdir)
    request.addfinalizer(fin)
    result = EchoAction(ParsedEmail(message_text))
    result.set_config({},
                      WORKSPACE_DIR=tempworkingdir,
                      FROM_ADDRESS="CaryTest <carytest@carytest.com>"
                      )
    return result



@then('the action should execute')
def execute_action(echoaction):
    echoaction.execute()


@then('make working directories')
def check_working_directories(echoaction):
    assert os.path.isdir(echoaction.working_dir)
    assert os.path.isdir(echoaction.input_dir)
    assert os.path.isdir(echoaction.output_dir)


@then('save the message text')
def check_message_text(echoaction):
    check_attachments(echoaction.input_dir,
                      [('message.txt',
                        echoaction._message.message_text)])


@then('save the attachments')
def check_input_attachments(echoaction):
    check_attachments(echoaction.input_dir, attachments)


@then('copy the attachments')
def check_output_attachments(echoaction):
    check_attachments(echoaction.output_dir, attachments)


@then('write a response')
def check_response(echoaction):
    fnam = os.path.join(echoaction.output_dir, 'message.txt')
    with open(fnam) as f:
        contents = f.read()
        message = ParsedEmail(contents)
        assert message.from_address == "carytest@carytest.com"

attachments = [("text_1", "Hello, text 1!\n"),
               ("text_2", "Hello, text 2!\n")]


def check_attachments(base_path, attachments):
    for attachment in attachments:
        fnam = os.path.join(base_path, attachment[0])
        with open(fnam) as f:
            contents = f.read()
            assert attachment[1] == contents

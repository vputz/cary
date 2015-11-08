import sys
import logging
from importlib.machinery import SourceFileLoader
import argparse
from cary.caryapp import CaryApp
import poplib


def configure_cary(app, config):
    app.allowed_addresses = config.ALLOW_FROM_ADDRESSES

    app.smtp_host = config.SMTP_HOST
    app.smtp_port = config.SMTP_PORT
    app.smtp_security = config.SMTP_SECURITY
    app.smtp_user = config.SMTP_USER
    app.smtp_password = config.SMTP_PASSWORD
    app.return_address = config.SMTP_RETURN_ADDRESS

    app.admin_email = config.ADMIN_EMAIL
    app.send_apologies = config.SEND_APOLOGIES
    app.should_clean_up = config.SHOULD_CLEAN_UP
    app.should_respond = config.SHOULD_RESPOND
    app.workspace = config.WORKSPACE_DIR

    app.pop_host = config.POP_HOST
    app.pop_port = config.POP_PORT
    app.pop_use_ssl = config.POP_USE_SSL
    app.pop_user = config.POP_USER
    app.pop_password = config.POP_PASSWORD
    app.pop_delete_messages = config.POP_DELETE_MESSAGES

    for name, (cmd_class, cmd_config) in config.COMMANDS.items():
        cmd = cmd_class()
        cmd.set_config(cmd_config,
                       WORKSPACE_DIR=config.WORKSPACE_DIR,
                       FROM_ADDRESS=config.FROM_ADDRESS)
        app.add_command(name, cmd)


def setup_logging(config):
    logging.basicConfig(filename=config.LOG_FILE,
                        level=config.LOG_LEVEL,
                        format=config.LOG_FORMAT)


def messages(server, port, use_ssl, user, user_pass):
    conn = poplib.POP3_SSL(server, port) if use_ssl else poplib.POP3
    conn.user( user )
    conn.pass_(user_pass)
    plist = conn.list()
    ids = [int(x.decode('UTF-8').split(' ')[0]) for x in plist[1]]
    responses = [conn.retr(i) for i in range(1, len(plist[1]) + 1)]
    msgs = ["\n".join( [ y.decode('utf-8') for y in x[1]] ) for x in responses]
    conn.quit()
    return msgs, ids

def delete_messages(server, port, use_ssl, user, user_pass, ids):
    conn = poplib.POP3_SSL(server, port) if use_ssl else poplib.POP3
    conn.user( user )
    conn.pass_(user_pass)
    for id in ids:
        logging.info("Deleting message {0}".format(id))
        conn.dele(id)
    conn.quit()

def process_message(app, msg):
    try:
        app.process_message(msg)
    except Exception as e:
        logging.exception("Serious error on initialization/processing")
        try:
            if app.admin_email:
                logging.error("Attempting admin email on exception {0}".format(
                    repr(e)))
                app.send_admin_email(e, msg)
            if app.send_apologies:
                logging.error("Attempting apology email")
                app.send_apology_email(msg)
        except Exception as e:
            logging.exception("Error sending admin/apology emails")
    
def main():
    parser = argparse.ArgumentParser(
        description="process email message as an offline assistant")
    parser.add_argument('--settings', type=str,
                        help='name of the local settings module',
                        default='local_conf.py')
    parser.add_argument('--fetch', action='store_true',
                        help='if true, fetch from pop3 instead of reading from stdin')

    args = parser.parse_args()
    config = SourceFileLoader('local_conf', args.settings).load_module()
    setup_logging(config)
    app = CaryApp()
    configure_cary(app, config)
    if (args.fetch):
        msgs, ids = messages(app.pop_host, app.pop_port, app.pop_use_ssl,
                            app.pop_user, app.pop_password)
        for msg in msgs:
            process_message(app, msg)
        
        if app.pop_delete_messages:
            delete_messages(app.pop_host, app.pop_port, app.pop_use_ssl,
                            app.pop_user, app.pop_password, ids)
    else:
        msg = sys.stdin.read()
        app.process_message(app, msg)


if __name__ == "__main__":
    main()

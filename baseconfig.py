import logging
# Configuration file for Cary -- as sample.  All "None" variables
# should be redefined for production use

# WORKSPACE_DIR is the location under which temporary directories
# will be built; typically this directory tree will be in
# the form WORKSPACE_DIR/transactions/transaction_id/[input|output]
# plus WORKSPACE_DIR/cary.log
WORKSPACE_DIR = None

# Whether or not Cary should actually send the response email;
# if this is False, Cary will write the response message to disk
# but not actually send it (if SHOULD_RESPOND is False and
# SHOULD_CLEANUP is True, there should be no record of action)
SHOULD_RESPOND = False

# Whether or not Cary should clean up temp files after a transaction.
# typically you will want to do this as they add up after a while,
# but they can be useful for debugging.
SHOULD_CLEAN_UP = False

# The email address cary emails are meant to be from
FROM_ADDRESS = None

# Log level
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_FILE = None
LOG_LEVEL = logging.INFO

####
# Commands
from cary.echocommand import EchoCommand
COMMANDS = {"echo": (EchoCommand, {})}

# email addresses to allow on the "from" line of messages sent
# to cary.  Uses "unix filename matching" (so ? and * for
# single- and multiple-character wildcards) and is case-insensitive
ALLOW_FROM_ADDRESSES = None
SMTP_HOST = None
SMTP_RETURN_ADDRESS = None

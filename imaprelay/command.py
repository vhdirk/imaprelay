import logging
import os
import stat
import sys
import argparse

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from . import connection
from . import relay

log = logging.getLogger('imaprelay')

DEFAULT_CONFIG = """\
[relay]
inbox=INBOX
archive=Archive
interval=30
"""

def main():
    parser = argparse.ArgumentParser(prog="imaprelay",
                                    description="An IMAP-to-SMTP relay, for tedious email services that don't allow forwarding (or suck at it)")
    parser.add_argument("-v", "--verbose", action='store_true', default=False, help="Show debug output")
    parser.add_argument("-c", "--config", help="Configuration file location", default=os.path.expanduser('~/.secret/imaprelay.cfg'))
    
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.CRITICAL)

    st = os.stat(args.config)
    if bool(st.st_mode & (stat.S_IRGRP | stat.S_IROTH)):
        raise Exception("Config file (%s) appears to be group- or "
                        "world-readable. Please `chmod 400` or similar."
                        % args.config)

    config = ConfigParser()
    config.readfp(StringIO(DEFAULT_CONFIG))
    config.read([args.config])

    connection.configure(config)

    rly = relay.Relay(config.get('relay', 'to'),
                      config.get('relay', 'inbox'),
                      config.get('relay', 'archive'))

    rly.loop(int(config.get('relay', 'interval')))

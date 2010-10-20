#
# vmail/scripts/base.py
#
# Copyright (C) 2010 @UK Plc, http://www.uk-plc.net
#
# Author:
#   2010 Damien Churchill <damoxc@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA    02110-1301, USA.
#

import os
import sys
import logging
import logging.handlers
import optparse

from twisted.internet import defer
from vmail.client import client, reactor

LEVELS = { 
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'WARN': logging.WARN,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

log = logging.getLogger(__name__)

def argcount(count):
    def deco(func):
        def wrapper(self):
            if not self.args:
                self.log.error('no arguments specified')
                return 1

            if len(self.args) < count:
                self.log.error('incorrect number of arguments specified')
                return 1

            return func(self)
        return wrapper
    return deco


class ScriptBase(object):

    log_filename = None
    log_format = 'short'
    usage = None

    def __init__(self, add_help_option=True):
        self.name = sys.argv[0]
        self.parser = optparse.OptionParser(usage=self.usage,
            add_help_option=add_help_option)
        self.parser.add_option('-L', '--loglevel', dest='loglevel',
            action='store', help='Set the log level', default='info')
        self.parser.add_option('-l', '--log-file', dest='log_file',
            action='store', help='Set the log file', default=None)

    def setup_logging(self, level='INFO'):
        level = LEVELS.get(level.upper(), logging.INFO)

        logger = logging.getLogger('vmail')
        logger.setLevel(level)
        logger.propagate = 1
        logger.disabled = 0

        if self.log_format == 'short':
            formatter = logging.Formatter('%(message)s')
        elif self.log_format == 'full':
            formatter = logging.Formatter(
                '[%(levelname)-8s] %(asctime)s %(name)-30s %(message)s',
                '%a, %d %b %Y %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(self.log_format)

        if self.log_filename and self.options.log_file != '-':
            handler = logging.handlers.WatchedFileHandler(self.log_filename)
        else:
            handler = logging.StreamHandler()

        handler.setLevel(level)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    def run(self):
        return None

    @classmethod
    def main(cls):
        instance = cls()
        instance.log = logging.getLogger(instance.__class__.__module__)
        (instance.options, instance.args) = instance.parser.parse_args()
        instance.setup_logging(instance.options.loglevel)
        cls._run(instance)

    @classmethod
    def _run(cls, instance):
        retval = instance.run()
        if isinstance(retval, int):
            sys.exit(retval)

class DaemonScriptBase(ScriptBase):

    @classmethod
    def _run(cls, instance):
        retval = instance.run()

        if isinstance(retval, defer.Deferred):
            instance._retval = 0
            def exit(retval):
                if reactor.running:
                    reactor.stop()
                instance._retval = retval

            retval.addCallbacks(exit, exit)
            reactor.run()
            sys.exit(instance._retval)

        elif isinstance(retval, int):
            exit(retval)

    def connect(self):
        if not os.path.exists(client.proxy.socket_path):
            self.log.error('vmaild not running')
            return 255

        return client.connect().addCallbacks(self.on_connect, self.on_connect_err)

    def on_connect(self):
        reactor.stop()

    def on_connect_err(self, error):
        reactor.stop()

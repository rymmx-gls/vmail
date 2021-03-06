#
# vmail/scripts/vautoreply.py
#
# Copyright (C) 2010-2012 @UK Plc, http://www.uk-plc.net
#
# Author:
#   2010-2012 Damien Churchill <damoxc@gmail.com>
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

import sys
import rfc822
import smtplib
from email.utils import formatdate

from vmail.common import Address, check_message
from vmail.client import client
from vmail.error import IgnoredMessageError
from vmail.scripts.base import DaemonScriptBase

class VAutoreply(DaemonScriptBase):

    #filename = '/var/self.log/vmail/vacation.self.log'

    def __init__(self):
        super(VAutoreply, self).__init__()
        self.parser.add_option('-f', '--from', dest='sender', action='store')

    def run(self):
        if not self.args:
            self.log.error('no argument provided')
            return 1

        message = rfc822.Message(sys.stdin)

        # Check for the presence of headers that indicate we shouldn't
        # respond to this
        try:
            check_message(message)
        except IgnoredMessageError as e:
            self.log.warning(e[0])
            return 0

        # Since the recipient comes in the form of:
        # user#example.com@autoreply.example.com we need to do some
        # converting of it first.
        recipient = self.args[0].split('@', 1)[0].replace('#', '@')

        if client.core.send_vacation(recipient, self.options.sender).get():
            self.log.info('sent vacation message to %s', recipient)
        else:
            self.log.warning('not sending vacation message')

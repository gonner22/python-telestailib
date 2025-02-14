# Copyright (C) 2013-2015 The python-bitcoinlib developers
#
# This file is part of python-telestailib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-telestailib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from telestai.wallet import CTelestaiSecret
from telestai.signmessage import TelestaiMessage, VerifyMessage, SignMessage
import sys
import os
import json

_bchr = chr
_bord = ord
if sys.version > '3':
    long = int
    def _bchr(x): return bytes([x])
    def _bord(x): return x


def load_test_vectors(name):
    with open(os.path.dirname(__file__) + '/data/' + name, 'r') as fd:
        return json.load(fd)


class Test_SignVerifyMessage(unittest.TestCase):
    def test_verify_message_simple(self):
        address = "RE34JR9zKhCLu4R7JFaDJz8JnypJDmCE14"
        message = address
        signature = "IKUeo59jk2ueeSBDkugZ9PBbteNayMn2FOKAQ1/WvoNzKcd0DeB1ljzTASm2VV8BeP//jF0aU7ztE55LIVVyOr8="

        message = TelestaiMessage(message)

        self.assertTrue(VerifyMessage(address, message, signature))

    def test_verify_message_vectors(self):
        for vector in load_test_vectors('signmessage.json'):
            message = TelestaiMessage(vector['address'])
            self.assertTrue(VerifyMessage(
                vector['address'], message, vector['signature']))

    def test_sign_message_simple(self):
        key = CTelestaiSecret(
            "L1gVQSmAJDnkK1A1V3mJehL9xQbdai9CCx65d29seRFGVVheyngq")
        address = "RL5dKQv7ZZYrqSYXNVgy2HvncjcQf8G6at"
        message = address

        message = TelestaiMessage(message)
        signature = SignMessage(key, message)

        self.assertTrue(signature)
        self.assertTrue(VerifyMessage(address, message, signature))

    def test_sign_message_vectors(self):
        for vector in load_test_vectors('signmessage.json'):
            key = CTelestaiSecret(vector['wif'])
            message = TelestaiMessage(vector['address'])

            signature = SignMessage(key, message)

            self.assertTrue(
                signature, "Failed to sign for [%s]" % vector['address'])
            self.assertTrue(VerifyMessage(
                vector['address'], message, vector['signature']), "Failed to verify signature for [%s]" % vector['address'])


if __name__ == "__main__":
    unittest.main()

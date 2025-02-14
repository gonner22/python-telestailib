# Copyright (C) 2012-2018 The python-bitcoinlib developers
# Copyright (C) 2018-2020 The python-telestailib developers
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

import telestai.core

from version import __version__


class MainParams(telestai.core.CoreMainParams):
    MESSAGE_START = b'\x54\x45\x4c\x45'
    DEFAULT_PORT = 8767
    RPC_PORT = 8766
    DNS_SEEDS = (('dnsseed.telestainodes.xyz', 'telestai.seeds.multicoin.co'),
                 ('seed-telestai.telestai.org'))
    BASE58_PREFIXES = {'PUBKEY_ADDR': 66,
                       'SCRIPT_ADDR': 127,
                       'SECRET_KEY': 128}
    BECH32_HRP = 'ev'


class TestNetParams(telestai.core.CoreTestNetParams):
    MESSAGE_START = b'\x52\x56\x4e\x54'
    DEFAULT_PORT = 18770
    RPC_PORT = 18766
    DNS_SEEDS = (('seed-testnet-telestai.io', 'seed-testnet2-telestai.io'),
                 ('seed-testnet3-telestai.io', ''))
    BASE58_PREFIXES = {'PUBKEY_ADDR': 111,
                       'SCRIPT_ADDR': 196,
                       'SECRET_KEY': 239}
    BECH32_HRP = ''


class RegTestParams(telestai.core.CoreRegTestParams):
    MESSAGE_START = b'\x43\x52\x4f\x57'
    DEFAULT_PORT = 18444
    RPC_PORT = 18443
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR': 111,
                       'SCRIPT_ADDR': 196,
                       'SECRET_KEY': 239}
    BECH32_HRP = ''


"""Master global setting for what chain params we're using.

However, don't set this directly, use SelectParams() instead so as to set the
telestai.core.params correctly too.
"""
# params = telestai.core.coreparams = MainParams()
params = MainParams()


def SelectParams(name):
    """Select the chain parameters to use

    name is one of 'mainnet', 'testnet', or 'regtest'

    Default chain is 'mainnet'
    """
    global params
    telestai.core._SelectCoreParams(name)
    if name == 'mainnet':
        params = telestai.core.coreparams = MainParams()
    elif name == 'testnet':
        params = telestai.core.coreparams = TestNetParams()
    elif name == 'regtest':
        params = telestai.core.coreparams = RegTestParams()
    else:
        raise ValueError('Unknown chain %r' % name)

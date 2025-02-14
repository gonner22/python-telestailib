#!/usr/bin/env python3
# Copyright (C) 2020 The python-telestailib developers
#
# This file is part of python-telestailib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-telestailib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

# Telestai vanity address generator
# This is an example of address generation in python-telestailib
# Note this is not particularly secure as the private keys may remain accessible in (virtual) memory

import argparse
import re
import os
import sys
import time

import telestai.base58
from telestai.wallet import P2PKHTelestaiAddress, CTelestaiSecret

parser = argparse.ArgumentParser(
    description='Telestai vanity address generator')
parser.add_argument('search', metavar='search string',
                    type=str, help='Search string')
parser.add_argument('--anywhere', action="store_true",
                    help="Search for string anywhere in address (default: leading characters only)")
parser.add_argument('--endswith', action="store_true",
                    help="Search for string anywhere in address (default: leading characters only)")
parser.add_argument('--ignorecase', action="store_true",
                    help="Search for string anywhere in address (default: leading characters only)")
args = parser.parse_args()

search_s = args.search
anywhere = args.anywhere
endswith = args.endswith
ignorecase = args.ignorecase

if search_s[0] != "T" and not (anywhere or endswith):
    print("First character of search string must be 'T'")
    sys.exit(1)

if ignorecase:
    case = re.IGNORECASE
else:
    case = 0

try:
    telestai.base58.decode(search_s)
except telestai.base58.InvalidBase58Error as e:
    print("Error: {}".format(e))
    sys.exit(1)

telestai.SelectParams('mainnet')

c = 0
start = time.time()

if endswith:
    pattern = search_s + r'$'
    while True:
        entropy = os.urandom(32)
        privkey = CTelestaiSecret.from_secret_bytes(entropy)
        addr = str(P2PKHTelestaiAddress.from_pubkey(privkey.pub))
        if re.search(pattern, addr, case):
            break
        c += 1
        if c % 10000 == 0:
            sec = time.time()-start
            sys.stdout.write(f'Try {c} ({round(c/sec)} keys/s) ({(time.time()-start) / 60 / 60} hours)      \r')
            sys.stdout.flush()
elif anywhere:
    pattern = search_s
    while True:
        entropy = os.urandom(32)
        privkey = CTelestaiSecret.from_secret_bytes(entropy)
        addr = str(P2PKHTelestaiAddress.from_pubkey(privkey.pub))
        if re.search(pattern, addr, case):
            break
        c += 1
        if c % 10000 == 0:
            sec = time.time()-start
            sys.stdout.write(f'Try {c} ({round(c/sec)} keys/s) ({(time.time()-start) / 60 / 60} hours)      \r')
            sys.stdout.flush()
else:# startswith
    pattern = r'^' + search_s
    while True:
        entropy = os.urandom(32)
        privkey = CTelestaiSecret.from_secret_bytes(entropy)
        addr = str(P2PKHTelestaiAddress.from_pubkey(privkey.pub))
        if re.search(pattern, addr, case):
            break
        c += 1
        if c % 10000 == 0:
            sec = time.time()-start
            sys.stdout.write(f'Try {c} ({round(c/sec)} keys/s) ({(time.time()-start) / 60 / 60} hours)      \r')
            sys.stdout.flush()

print()
print((time.time()-start) / 60 / 60, 'hours')
print(addr, privkey, entropy.hex())
print(entropy)

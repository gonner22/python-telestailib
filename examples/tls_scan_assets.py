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

import sys
import argparse
import telestai
import telestai.core
from telestai.rpc import TelestaiProxy
from telestai.core import COIN
from telestai.core.assets import RvnAssetData
from telestai.core.script import OP_TLS_ASSET, CScriptOp
from telestai.assets import CAssetName

parser = argparse.ArgumentParser(
    description='Scans Telestai blockchain for assets using RPC')
parser.add_argument('--testnet', action="store_true",
                    help="Use testnet (default: mainnet)")
parser.add_argument('--startblock', type=int, default=0,
                    help="Scan starting block")
parser.add_argument('--match', type=str, default="",
                    help="Asset name match string (default: all)")
args = parser.parse_args()

start = args.startblock
if args.testnet:
    telestai.SelectParams("testnet")
else:
    if args.startblock == 0:
        start = telestai.core.coreparams.nAssetActivationHeight
    telestai.SelectParams("mainnet")

r = TelestaiProxy()  # telestai daemon must be running locally with rpc server enabled

try:
    end = r.getblockcount()
except Exception as e:
    print("Error: ".format(e))
    sys.exit(1)

for c in range(start, end):
    blockhash = r.getblockhash(c)
    block = r.getblock(blockhash)
    for tx in block.vtx:
        for v in tx.vout:
            try:
                get_data = False
                data = []
                for x in v.scriptPubKey:
                    if x == OP_TLS_ASSET:
                        get_data = True    # found OP_TLS_ASSET, 1 or more data pushes follow
                        continue
                    if get_data:
                        if type(x) is not CScriptOp:
                            data.append(x)  # collect up the data
                        else:
                            get_data = False
                if len(data) > 0:
                    for d in data:
                        try:
                            # parse tls asset data as python object
                            a = RvnAssetData(d)
                            display = True
                            if args.match != "" and not args.match in a.asset_name:
                                display = False
                            if display:
                                print(a.asset_name, a.asset_type,
                                      int(a.amount/COIN), a.ipfshash)
                            if a.asset_name != "":
                                # check asset name for validity
                                n = CAssetName(a.asset_name)
                        except Exception as e:
                            print(e, d)

            except Exception as e:
                print(e)

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

import unittest

import telestai
from telestai.core.assets import RvnAssetData

telestai.SelectParams("mainnet")


class Test_TLS_ASSET(unittest.TestCase):
    def test_valid(self):
        # standard transfer
        asset_data = RvnAssetData(
            b'tlst\rNUKA/COLA/CAP\x00\xe9\n\xb5\xe2\x00\x00\x00')
        self.assertTrue(asset_data.asset_name == "NUKA/COLA/CAP")
        self.assertTrue(asset_data.asset_type == "transfer")
        asset_data = RvnAssetData('72766e7404234c544300e1f50500000000')
        self.assertTrue(asset_data.asset_type == "transfer")
        # nullassetdata
        asset_data = RvnAssetData(
            '14d4a4a095e02cd6a9b3cf15cf16cc42dc63baf3e006042342544301')
        self.assertTrue(asset_data.asset_type == "nullassetdata")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            asset_data = RvnAssetData(
                b'tlsx\rNUKA/COLA/CAP\x00\xe9\n\xb5\xe2\x00\x00\x00')

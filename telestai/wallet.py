# Copyright (C) 2012-2014 The python-bitcoinlib developers
#
# This file is part of python-telestailib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-telestailib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Wallet-related functionality

Includes things like representing addresses and converting them to/from
scriptPubKeys; currently there is no actual wallet support implemented.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import hashlib
import telestai.core.script as script
import telestai.core.key
import telestai.core
import telestai.bech32
import telestai.base58
import telestai

import array
import sys

from telestai.core.serialize import Hash160
from telestai.blockchain.utils import double_sha256

_bord = ord
def _tobytes(x): return array.array('B', x).tostring()


if sys.version > '3':
    def _bord(x): return x
    _tobytes = bytes


class CTelestaiAddress(object):

    def __new__(cls, s):
        #        try:
        #            return CBech32TelestaiAddress(s)
        #        except telestai.bech32.Bech32Error:
        #            pass

        try:
            return CBase58TelestaiAddress(s)
        except telestai.base58.Base58Error:
            pass

        raise CTelestaiAddressError(
            'Unrecognized encoding for telestai address')

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a subclass of CTelestaiAddress"""
#        try:
#            return CBech32TelestaiAddress.from_scriptPubKey(scriptPubKey)
#        except CTelestaiAddressError:
#            pass

        try:
            return CBase58TelestaiAddress.from_scriptPubKey(scriptPubKey)
        except CTelestaiAddressError:
            pass

        raise CTelestaiAddressError(
            'scriptPubKey is not in a recognized address format')


class CTelestaiAddressError(Exception):
    """Raised when an invalid Telestai address is encountered"""


class CBech32TelestaiAddress(telestai.bech32.CBech32Data, CTelestaiAddress):
    """A Bech32-encoded Telestai address"""

    @classmethod
    def from_bytes(cls, witver, witprog):

        assert witver == 0
        self = super(CBech32TelestaiAddress, cls).from_bytes(
            witver,
            _tobytes(witprog)
        )

        if len(self) == 32:
            self.__class__ = P2WSHTelestaiAddress
        elif len(self) == 20:
            self.__class__ = P2WPKHTelestaiAddress
        else:
            raise CTelestaiAddressError(
                'witness program does not match any known segwit address format')

        return self

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a CBech32TelestaiAddress

        Returns a CBech32TelestaiAddress subclass, either P2WSHTelestaiAddress or
        P2WPKHTelestaiAddress. If the scriptPubKey is not recognized
        CTelestaiAddressError will be raised.
        """
        try:
            return P2WSHTelestaiAddress.from_scriptPubKey(scriptPubKey)
        except CTelestaiAddressError:
            pass

        try:
            return P2WPKHTelestaiAddress.from_scriptPubKey(scriptPubKey)
        except CTelestaiAddressError:
            pass

        raise CTelestaiAddressError(
            'scriptPubKey not a valid bech32-encoded address')


class CBase58TelestaiAddress(telestai.base58.CBase58Data, CTelestaiAddress):
    """A Base58-encoded Telestai address"""

    @classmethod
    def from_bytes(cls, data, nVersion):
        self = super(CBase58TelestaiAddress, cls).from_bytes(data, nVersion)

        if nVersion == telestai.params.BASE58_PREFIXES['SCRIPT_ADDR']:
            self.__class__ = P2SHTelestaiAddress

        elif nVersion == telestai.params.BASE58_PREFIXES['PUBKEY_ADDR']:
            self.__class__ = P2PKHTelestaiAddress

        else:
            raise CTelestaiAddressError(
                'Version %d not a recognized Telestai Address' % nVersion)

        return self

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a CTelestaiAddress

        Returns a CTelestaiAddress subclass, either P2SHTelestaiAddress or
        P2PKHTelestaiAddress. If the scriptPubKey is not recognized
        CTelestaiAddressError will be raised.
        """
        try:
            return P2SHTelestaiAddress.from_scriptPubKey(scriptPubKey)
        except CTelestaiAddressError:
            pass

        try:
            return P2PKHTelestaiAddress.from_scriptPubKey(scriptPubKey)
        except CTelestaiAddressError:
            pass

        raise CTelestaiAddressError(
            'scriptPubKey not a valid base58-encoded address')


class P2SHTelestaiAddress(CBase58TelestaiAddress):
    @classmethod
    def from_bytes(cls, data, nVersion=None):
        if nVersion is None:
            nVersion = telestai.params.BASE58_PREFIXES['SCRIPT_ADDR']

        elif nVersion != telestai.params.BASE58_PREFIXES['SCRIPT_ADDR']:
            raise ValueError('nVersion incorrect for P2SH address: got %d; expected %d' %
                             (nVersion, telestai.params.BASE58_PREFIXES['SCRIPT_ADDR']))

        return super(P2SHTelestaiAddress, cls).from_bytes(data, nVersion)

    @classmethod
    def from_redeemScript(cls, redeemScript):
        """Convert a redeemScript to a P2SH address

        Convenience function: equivalent to P2SHTelestaiAddress.from_scriptPubKey(redeemScript.to_p2sh_scriptPubKey())
        """
        return cls.from_scriptPubKey(redeemScript.to_p2sh_scriptPubKey())

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a P2SH address

        Raises CTelestaiAddressError if the scriptPubKey isn't of the correct
        form.
        """
        if scriptPubKey.is_p2sh():
            return cls.from_bytes(scriptPubKey[2:22], telestai.params.BASE58_PREFIXES['SCRIPT_ADDR'])

        else:
            raise CTelestaiAddressError('not a P2SH scriptPubKey')

    def to_scriptPubKey(self):
        """Convert an address to a scriptPubKey"""
        assert self.nVersion == telestai.params.BASE58_PREFIXES['SCRIPT_ADDR']
        return script.CScript([script.OP_HASH160, self, script.OP_EQUAL])

    def to_redeemScript(self):
        return self.to_scriptPubKey()
    
    def to_scripthash(self):
        """Convert address to a scripthash for ElectrumX compatibility"""
        script_pubkey = self.to_scriptPubKey()
        scripthash = hashlib.sha256(script_pubkey).digest()
        return scripthash[::-1].hex()


class P2PKHTelestaiAddress(CBase58TelestaiAddress):
    @classmethod
    def from_bytes(cls, data, nVersion=None):
        if nVersion is None:
            nVersion = telestai.params.BASE58_PREFIXES['PUBKEY_ADDR']

        elif nVersion != telestai.params.BASE58_PREFIXES['PUBKEY_ADDR']:
            raise ValueError('nVersion incorrect for P2PKH address: got %d; expected %d' %
                                (nVersion, telestai.params.BASE58_PREFIXES['PUBKEY_ADDR']))

        return super(P2PKHTelestaiAddress, cls).from_bytes(data, nVersion)

    @classmethod
    def from_pubkey(cls, pubkey, accept_invalid=False):
        """Create a P2PKH telestai address from a pubkey

        Raises CTelestaiAddressError if pubkey is invalid, unless accept_invalid
        is True.

        The pubkey must be a bytes instance; CECKey instances are not accepted.
        """
        if not isinstance(pubkey, bytes):
            raise TypeError(
                'pubkey must be bytes instance; got %r' % pubkey.__class__)

        if not accept_invalid:
            if not isinstance(pubkey, telestai.core.key.CPubKey):
                pubkey = telestai.core.key.CPubKey(pubkey)
            if not pubkey.is_fullyvalid:
                raise CTelestaiAddressError('invalid pubkey')

        pubkey_hash = telestai.core.Hash160(pubkey)
        return P2PKHTelestaiAddress.from_bytes(pubkey_hash)

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey, accept_non_canonical_pushdata=True, accept_bare_checksig=True):
        """Convert a scriptPubKey to a P2PKH address

        Raises CTelestaiAddressError if the scriptPubKey isn't of the correct
        form.

        accept_non_canonical_pushdata - Allow non-canonical pushes (default True)

        accept_bare_checksig          - Treat bare-checksig as P2PKH scriptPubKeys (default True)
        """
        if accept_non_canonical_pushdata:
            # Canonicalize script pushes
            # in case it's not a CScript instance yet
            scriptPubKey = script.CScript(scriptPubKey)

            try:
                scriptPubKey = script.CScript(
                    tuple(scriptPubKey))  # canonicalize
            except telestai.core.script.CScriptInvalidError:
                raise CTelestaiAddressError(
                    'not a P2PKH scriptPubKey: script is invalid')

        if scriptPubKey.is_witness_v0_keyhash():
            return cls.from_bytes(scriptPubKey[2:22], telestai.params.BASE58_PREFIXES['PUBKEY_ADDR'])
        elif scriptPubKey.is_witness_v0_nested_keyhash():
            return cls.from_bytes(scriptPubKey[3:23], telestai.params.BASE58_PREFIXES['PUBKEY_ADDR'])
        elif (len(scriptPubKey) == 25
                and _bord(scriptPubKey[0]) == script.OP_DUP
                and _bord(scriptPubKey[1]) == script.OP_HASH160
                and _bord(scriptPubKey[2]) == 0x14
                and _bord(scriptPubKey[23]) == script.OP_EQUALVERIFY
                and _bord(scriptPubKey[24]) == script.OP_CHECKSIG):
            return cls.from_bytes(scriptPubKey[3:23], telestai.params.BASE58_PREFIXES['PUBKEY_ADDR'])

        elif accept_bare_checksig:
            pubkey = None

            # We can operate on the raw bytes directly because we've
            # canonicalized everything above.
            if (len(scriptPubKey) == 35  # compressed
                and _bord(scriptPubKey[0]) == 0x21
                    and _bord(scriptPubKey[34]) == script.OP_CHECKSIG):

                pubkey = scriptPubKey[1:34]

            elif (len(scriptPubKey) == 67  # uncompressed
                    and _bord(scriptPubKey[0]) == 0x41
                    and _bord(scriptPubKey[66]) == script.OP_CHECKSIG):

                pubkey = scriptPubKey[1:65]

            if pubkey is not None:
                return cls.from_pubkey(pubkey, accept_invalid=True)

        raise CTelestaiAddressError('not a P2PKH scriptPubKey')

    def to_scriptPubKey(self, nested=False):
        """Convert an address to a scriptPubKey"""
        assert self.nVersion == telestai.params.BASE58_PREFIXES['PUBKEY_ADDR']
        return script.CScript([script.OP_DUP, script.OP_HASH160, self, script.OP_EQUALVERIFY, script.OP_CHECKSIG])

    def to_redeemScript(self):
        return self.to_scriptPubKey()


class P2WSHTelestaiAddress(CBech32TelestaiAddress):

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a P2WSH address

        Raises CTelestaiAddressError if the scriptPubKey isn't of the correct
        form.
        """
        if scriptPubKey.is_witness_v0_scripthash():
            return cls.from_bytes(0, scriptPubKey[2:34])
        else:
            raise CTelestaiAddressError('not a P2WSH scriptPubKey')

    def to_scriptPubKey(self):
        """Convert an address to a scriptPubKey"""
        assert self.witver == 0
        return script.CScript([0, self])

    def to_redeemScript(self):
        return NotImplementedError("not enough data in p2wsh address to reconstruct redeem script")


class P2WPKHTelestaiAddress(CBech32TelestaiAddress):

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a P2WSH address

        Raises CTelestaiAddressError if the scriptPubKey isn't of the correct
        form.
        """
        if scriptPubKey.is_witness_v0_keyhash():
            return cls.from_bytes(0, scriptPubKey[2:22])
        else:
            raise CTelestaiAddressError('not a P2WPKH scriptPubKey')

    def to_scriptPubKey(self):
        """Convert an address to a scriptPubKey"""
        assert self.witver == 0
        return script.CScript([0, self])

    def to_redeemScript(self):
        return script.CScript([script.OP_DUP, script.OP_HASH160, self, script.OP_EQUALVERIFY, script.OP_CHECKSIG])


class CKey(object):
    """An encapsulated private key

    Attributes:

    pub           - The corresponding CPubKey for this private key

    is_compressed - True if compressed

    """

    def __init__(self, secret, compressed=True):
        self._cec_key = telestai.core.key.CECKey()
        self._cec_key.set_secretbytes(secret)
        self._cec_key.set_compressed(compressed)

        self.pub = telestai.core.key.CPubKey(
            self._cec_key.get_pubkey(), self._cec_key)

    @property
    def is_compressed(self):
        return self.pub.is_compressed

    def sign(self, hash):
        return self._cec_key.sign(hash)

    def sign_compact(self, hash):
        return self._cec_key.sign_compact(hash)


class CTelestaiSecretError(telestai.base58.Base58Error):
    pass


class CTelestaiSecret(telestai.base58.CBase58Data, CKey):
    """A base58-encoded secret key"""

    @classmethod
    def from_secret_bytes(cls, secret, compressed=True):
        """Create a secret key from a 32-byte secret"""
        self = cls.from_bytes(secret + (b'\x01' if compressed else b''),
                              telestai.params.BASE58_PREFIXES['SECRET_KEY'])
        self.__init__(None)
        return self

    def __init__(self, s):
        if self.nVersion != telestai.params.BASE58_PREFIXES['SECRET_KEY']:
            raise CTelestaiSecretError('Not a base58-encoded secret key: got nVersion=%d; expected nVersion=%d' %
                                      (self.nVersion, telestai.params.BASE58_PREFIXES['SECRET_KEY']))

        CKey.__init__(self, self[0:32], len(self) >
                      32 and _bord(self[32]) == 1)
        
    def to_wif(self) -> str:
        """Convert this secret key to a WIF (Wallet Import Format) string."""
        payload = self[:]  # Get the internal byte representation of the secret key
        if self.is_compressed:
            payload += b'\x01'  # Add compression flag if the key is compressed

        version_byte = telestai.params.BASE58_PREFIXES['SECRET_KEY']
        payload = bytes([version_byte]) + payload

        # Calculate checksum (double SHA256) and append first 4 bytes as checksum
        checksum = double_sha256(payload)[:4]

        # Concatenate payload and checksum
        final_payload = payload + checksum

        # Base58Check encode the payload
        wif = telestai.base58.encode(final_payload)
        return wif

__all__ = (
    'CTelestaiAddressError',
    'CTelestaiAddress',
    'CBase58TelestaiAddress',
    'CBech32TelestaiAddress',
    'P2SHTelestaiAddress',
    'P2PKHTelestaiAddress',
    'P2WSHTelestaiAddress',
    'P2WPKHTelestaiAddress',
    'CKey',
    'CTelestaiSecretError',
    'CTelestaiSecret',
)

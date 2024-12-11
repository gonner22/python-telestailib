import unittest
from evrmore.core.key import CPubKey, CECKey
import os
import hashlib

from evrmore.core.script import OP_CHECKMULTISIG, CScript, CreateMultisigRedeemScript
from evrmore.crypto import verify_multisig_script, verify_signature
from evrmore.wallet import P2PKHEvrmoreAddress, P2SHEvrmoreAddress
from evrmore.core.transaction import CMultiSigTransaction

class TestP2SHFunctions(unittest.TestCase):
    def setUp(self):
        # Create test keys
        self.private_keys = []
        self.public_keys = []
        for _ in range(3):
            privkey = CECKey()
            privkey.set_secretbytes(os.urandom(32))
            self.private_keys.append(privkey)
            self.public_keys.append(CPubKey(privkey.get_pubkey()))
        # print("Private Keys: ", self.private_keys)
        # print("Public Keys: ", self.public_keys)

    def test_create_multisig_redeem_script(self):
        script = CreateMultisigRedeemScript(2, self.public_keys)
        self.assertIsInstance(script, CScript)
        self.assertEqual(script[-1], OP_CHECKMULTISIG)
        
        # Test invalid parameters
        with self.assertRaises(ValueError):
            CreateMultisigRedeemScript(4, self.public_keys)  # m > n
            
    def test_verify_signature(self):
        msg = b"test message"
        msg_hash = hashlib.sha256(hashlib.sha256(msg).digest()).digest()
        
        # Create signature
        privkey = self.private_keys[0]
        pubkey = self.public_keys[0]
        
        sig = privkey.sign(msg_hash)
        sig_with_hashtype = sig + b'\x01'  # SIGHASH_ALL
        
        # Debug output
        # print(f"Message: {msg}")
        # print(f"Double SHA256 hash: {msg_hash.hex()}")
        # print(f"Raw signature (hex): {sig.hex()}")
        # print(f"Signature with hashtype (hex): {sig_with_hashtype.hex()}")
        print("private key: ", privkey.get_privkey().hex())
        print(f"Public key: {pubkey.hex()}")
        private_key_bytes = bytes.fromhex(privkey.get_privkey().hex())
        print("private key bytes: ", private_key_bytes)
        # print(f"Signature length: {len(sig)}")
        public_key_bytes = bytes.fromhex(pubkey.hex())
        print("public key bytes: ", public_key_bytes)
        p2pkh_address = P2PKHEvrmoreAddress.from_pubkey(public_key_bytes)
        print("p2pkh address: ", p2pkh_address)
        # Verify both signature formats
        result1 = verify_signature(sig, pubkey, msg_hash)
        result2 = verify_signature(sig_with_hashtype, pubkey, msg_hash)
        
        self.assertTrue(result1 or result2)
        
    def test_verify_multisig_script(self):
        msg = b"test message"
        msg_hash = hashlib.sha256(hashlib.sha256(msg).digest()).digest()
        
        # Create redeem script
        script = CreateMultisigRedeemScript(2, self.public_keys)
        print("redeem script: ", script)
        # Create signatures
        signatures = []
        for i in range(2):  # We need 2 signatures
            sig = self.private_keys[i].sign(msg_hash)
            signatures.append(sig + b'\x01')  # Add SIGHASH_ALL
            
            # Verify individual signatures
            result = verify_signature(signatures[-1], self.public_keys[i], msg_hash)
        #     print(f"Individual sig verification: {result}")
        
        # # Debug output
        # print(f"Double SHA256 hash: {msg_hash.hex()}")
        # print(f"Raw Signatures: {[sig.hex() for sig in signatures]}")
        # print(f"Signatures with hashtype: {[sig.hex() for sig in signatures]}")
        # print(f"Public Keys: {[key.hex() for key in self.public_keys]}")
        
        # Verify multisig script
        result1 = verify_multisig_script(script, signatures, self.public_keys, msg_hash)
        result2 = verify_multisig_script(script, [s[:-1] for s in signatures], self.public_keys, msg_hash)
        
        self.assertTrue(result1 or result2)

    def test_create_and_verify_p2sh_address(self):
        try:
            # Create a redeem script
            redeem_script = CreateMultisigRedeemScript(2, self.public_keys)
            # print("Redeem Script Created", redeem_script)

            # Generate P2SH address
            p2sh_address = P2SHEvrmoreAddress.from_redeemScript(redeem_script)
            print("P2SH Address Generated", p2sh_address)

            # Verify the P2SH address is an instance of P2SHEvrmoreAddress
            self.assertIsInstance(p2sh_address, P2SHEvrmoreAddress)
            # print("P2SH Address Verified")

            # Create a P2SH output script
            p2sh_output_script = CScript.to_p2sh_scriptPubKey(redeem_script)
            print("another p2sh output script: ", p2sh_output_script)

            # Verify the output script is a valid P2SH script
            self.assertTrue(p2sh_output_script.is_p2sh())
            # print("P2SH Output Script Verified")

        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    # def test_spend_p2sh_address(self):
    #     # Create a redeem script
    #     redeem_script = CreateMultisigRedeemScript(2, self.public_keys)
        
    #     # Generate P2SH address
    #     p2sh_address = create_p2sh_address(redeem_script)
        
    #     # Create a transaction spending from the P2SH address
    #     tx = CMultiSigTransaction()
    #     # Add inputs and outputs to the transaction
    #     # tx.vin.append(...)  # Add input referencing the P2SH address
    #     # tx.vout.append(...)  # Add output(s) for the transaction
        
    #     # Sign the transaction with the required private keys
    #     signatures = tx.sign_with_multiple_keys(self.private_keys[:2], redeem_script)
        
    #     # Apply the signatures to the transaction
    #     tx.apply_multisig_signatures(signatures, redeem_script)
        
    #     # Verify the transaction is correctly signed
    #     # This might involve checking the scriptSig or using a method to verify the transaction
    #     # self.assertTrue(tx.is_valid())  # Example assertion

    #     # Debug output
    #     print(f"Transaction: {tx}")
        # print(f"Signatures: {[sig.hex() for sig in signatures]}")

if __name__ == '__main__':
    unittest.main()

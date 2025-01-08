from evrmore.core import CTransaction, CMutableTransaction
from evrmore.core.script import OP_0, SIGHASH_ALL, SIGVERSION_BASE, CScript, SignatureHash


class CMultiSigTransaction(CMutableTransaction):
    """Transaction type for multisig operations with proper mutability handling."""
    
    def sign_with_multiple_keys(self, private_keys, redeem_script, sigversion=SIGVERSION_BASE):
        """
        Sign a multisig transaction with multiple private keys.
        
        :param private_keys: List of private keys to sign with
        :param redeem_script: CScript redeem script
        :param sigversion: Signature version
        :return: List of signatures
        """
#<<<<<<< feature/p2sh
        try:
            # Calculate the sighash using the redeem script
            sighash = SignatureHash(redeem_script, self, 0, SIGHASH_ALL, sigversion)
            signatures = []
            
            # Sign with the required number of private keys
            for privkey in private_keys:
                if len(signatures) >= len(redeem_script):  
                    break
                sig = privkey.sign(sighash) + bytes([SIGHASH_ALL])
                signatures.append(sig)
            
            return signatures
        
        except Exception as e:
            raise ValueError(f"Error signing transaction: {e}")

    def apply_multisig_signatures(self, signatures, redeem_script):
        """
        Apply multiple signatures to a multisig transaction correctly for P2SH.

        :param signatures: List of signatures
        :param redeem_script: CScript redeem script
        """
        try:
            if not signatures or not redeem_script:
                raise ValueError("Signatures and redeem script cannot be empty.")

            # Ensure the signatures are sorted correctly according to the public keys in the redeem script
            # The scriptSig must start with OP_0 due to a historical bug with CHECKMULTISIG
            scriptSig = CScript([OP_0] + signatures + [redeem_script])

            # Apply the scriptSig to the first input in the transaction
            self.vin[0].scriptSig = scriptSig

            # Return the modified transaction with the applied signatures
            return self

        except Exception as e:
            raise ValueError(f"Error applying multisig signatures: {e}")
#=======
#        sighash = SignatureHash(redeem_script, self, 0, SIGHASH_ALL, sigversion)
#        signatures = []
#        
#        for privkey in private_keys:
#            if len(signatures) >= len(redeem_script.required):
#                break
#            sig = privkey.sign(sighash) + bytes([SIGHASH_ALL])
#            signatures.append(sig)
#            
#        return signatures
#        
#    def apply_multisig_signatures(self, signatures, redeem_script):
#        """
#        Apply multiple signatures to a multisig transaction.
#        
#        :param signatures: List of signatures
#        :param redeem_script: CScript redeem script
#        """
#        # Create scriptSig with signatures and redeem script
#        scriptSig = CScript([OP_0])  # OP_0 for multisig bug
#        for sig in signatures:
#            scriptSig += CScript([sig])
#        scriptSig += CScript([redeem_script])
#        
#        # Apply to transaction input
#        self.vin[0].scriptSig = scriptSig
#
#__all__ = (
#    'CMultiSigTransaction',
#)
#>>>>>>> master
__all__ = (
    'CMultiSigTransaction',
)


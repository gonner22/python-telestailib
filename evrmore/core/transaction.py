from evrmore.core import CTransaction
from evrmore.core.script import OP_0, SIGHASH_ALL, SIGVERSION_BASE, CScript, SignatureHash


class CMultiSigTransaction(CTransaction):
    """Transaction type for multisig operations"""
    
    def sign_with_multiple_keys(self, private_keys, redeem_script, sigversion=SIGVERSION_BASE):
        """
        Sign a multisig transaction with multiple private keys.
        
        :param private_keys: List of private keys to sign with
        :param redeem_script: CScript redeem script
        :param sigversion: Signature version
        :return: List of signatures
        """
        sighash = SignatureHash(redeem_script, self, 0, SIGHASH_ALL, sigversion)
        signatures = []
        
        for privkey in private_keys:
            if len(signatures) >= len(redeem_script.required):
                break
            sig = privkey.sign(sighash) + bytes([SIGHASH_ALL])
            signatures.append(sig)
            
        return signatures
        
    def apply_multisig_signatures(self, signatures, redeem_script):
        """
        Apply multiple signatures to a multisig transaction.
        
        :param signatures: List of signatures
        :param redeem_script: CScript redeem script
        """
        # Create scriptSig with signatures and redeem script
        scriptSig = CScript([OP_0])  # OP_0 for multisig bug
        for sig in signatures:
            scriptSig += CScript([sig])
        scriptSig += CScript([redeem_script])
        
        # Apply to transaction input
        self.vin[0].scriptSig = scriptSig

__all__ = (
    'CMultiSigTransaction',
)
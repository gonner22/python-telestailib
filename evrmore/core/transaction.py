from evrmore.core import CMutableTransaction, CTransaction
from evrmore.core.script import OP_0, SIGHASH_ALL, SIGVERSION_BASE, CScript, SignatureHash

class CMultiSigTransaction(CMutableTransaction):
    """Transaction type for multisig operations with secure handling."""
    
    def generate_sighash(self, redeem_script, input_index, sigversion=SIGVERSION_BASE):
        """
        Generate the sighash for a multisig transaction.

        :param redeem_script: CScript redeem script
        :param input_index: Index of the input being signed
        :param sigversion: Signature version
        :return: sighash (bytes)
        """
        try:
            if not isinstance(input_index, int):
                raise TypeError("input_index must be an integer")
            sighash = SignatureHash(redeem_script, self, input_index, SIGHASH_ALL, sigversion)
            return sighash
        except Exception as e:
            raise ValueError(f"Error generating sighash: {e}")

    def sign_independently(self, private_key, sighash):
        """
        Sign the transaction independently with a single private key.

        :param private_key: Private key for signing
        :param sighash: sighash generated for the transaction
        :return: Signature (bytes)
        """
        try:
            signature = private_key.sign(sighash) + bytes([SIGHASH_ALL])
            return signature

        except Exception as e:
            raise ValueError(f"Error signing transaction: {e}")

    def apply_multisig_signatures(self, signatures_list, redeem_script):
        """
        Apply multiple collected signatures to a multisig transaction for P2SH.

        :param signatures: List of collected signatures
        :param redeem_script: CScript redeem script
        """
        try:
            if not signatures_list or not redeem_script:
                raise ValueError("Signatures and redeem script cannot be empty.")

            for i,txin in enumerate(self.vin):
                scriptSig = CScript([OP_0] + signatures_list[i] + [redeem_script])
                txin.scriptSig = scriptSig

            return self

        except Exception as e:
            raise ValueError(f"Error applying multisig signatures: {e}")

__all__ = (
    'CMultiSigTransaction',
)

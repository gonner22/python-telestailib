import evrmore


def verify_signature(sig, pubkey, hash):
    """
    Verify a signature against a public key and message hash
    
    :param sig: The signature in DER format (with or without hashtype byte)
    :param pubkey: The public key (bytes or CECKey)
    :param hash: The message hash to verify against
    :return: bool indicating if signature is valid
    """
    try:
        # Safety checks
        if not sig or not pubkey or not hash:
            return False
            
        if len(hash) != 32:
            return False
            
        # Create a copy of the signature to avoid modifying the original
        working_sig = bytes(sig)
        
        # Remove hashtype byte if present
        if len(working_sig) > 70 and working_sig[-1] in (0x01, 0x02, 0x03, 0x81, 0x82, 0x83):
            working_sig = working_sig[:-1]
            
        # Basic DER signature checks
        if len(working_sig) < 68 or len(working_sig) > 72:  # Typical DER sig lengths
            return False
            
        if working_sig[0] != 0x30:  # DER sequence
            return False
            
        # Use the key's verify method directly
        if isinstance(pubkey, bytes):
            try:
                key = evrmore.core.key.CECKey()
                key.set_pubkey(pubkey)
                return key.verify(hash, working_sig)
            except:
                return False
        else:
            try:
                return pubkey.verify(hash, working_sig)
            except:
                return False
                
    except Exception as e:
        print(f"Signature verification failed: {str(e)}")
        return False

def verify_multisig_script(script, signatures, pubkeys, hash):
    """
    Verify a multisig script with given signatures and public keys
    
    :param script: The redeem script (CScript)
    :param signatures: List of signatures
    :param pubkeys: List of public keys
    :param hash: The message hash to verify against
    :return: bool indicating if multisig is valid
    """
    try:
        # Basic parameter validation
        if not isinstance(signatures, list) or not isinstance(pubkeys, list):
            return False
            
        if not signatures or not pubkeys or len(signatures) > len(pubkeys):
            return False
            
        if len(hash) != 32:
            return False
            
        # Extract m value from script
        if len(script) < 1:
            return False
            
        m = script[0] - 80  # OP_1 is 0x51 (81), so subtract 80
        if m < 1 or m > len(pubkeys):
            return False
            
        # Verify signatures
        valid_count = 0
        used_keys = set()
        
        # Try each signature against unused public keys
        for sig in signatures:
            if not sig:  # Skip empty signatures
                continue
                
            for i, pubkey in enumerate(pubkeys):
                if i in used_keys:
                    continue
                    
                try:
                    if verify_signature(sig, pubkey, hash):
                        valid_count += 1
                        used_keys.add(i)
                        break
                except:
                    continue
                    
        # Check if we have enough valid signatures
        return valid_count >= m
        
    except Exception as e:
        print(f"Multisig verification failed: {e}")
        return False

__all__ = (
    'verify_signature',
    'verify_multisig_script',
)
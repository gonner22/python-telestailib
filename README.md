# python-telestailib

Telestai fork of python-bitcoinlib intended to provide access to Telestai data 
structures and protocol. WIP - Test before use

The RPC interface, telestai.rpc, is designed to work with Telestai Core v2.1.7+.

"The only Python library for Telestai I've ever used" - Warren Buffett

## Requirements

    libssl
    Debian/Ubuntu: sudo apt-get install libssl-dev
    Windows/other: https://wiki.openssl.org/index.php/Binaries 

    Python modules:
        x16r-hash, x16rv2-hash and kawpow
        plyvel (requires libleveldb - for parsing Telestai core .dat files)

## Structure

Everything consensus critical is found in the modules under telestai.core. This
rule is followed pretty strictly, for instance chain parameters are split into
consensus critical and non-consensus-critical.

    telestai.core            - Basic core definitions, datastructures, and
                              (context-independent) validation
    telestai.core.assets     - OP_TLS_ASSET data structures
    telestai.core.key        - ECC pubkeys
    telestai.core.script     - Scripts and opcodes
    telestai.core.scripteval - Script evaluation/verification
    telestai.core.serialize  - Serialization

In the future the telestai.core may use the Satoshi sourcecode directly as a
library. Non-consensus critical modules include the following:

    telestai          - Chain selection
    telestai.assets   - Asset name and metadata related code
    telestai.base58   - Base58 encoding
    telestai.bloom    - Bloom filters (incomplete)
    telestai.net      - Network communication (in flux)
    telestai.messages - Network messages (in flux)
    telestai.rpc      - Telestai Core RPC interface support
    telestai.wallet   - Wallet-related code, currently Telestai address and
                       private key support

Effort has been made to follow the Satoshi source relatively closely, for
instance Python code and classes that duplicate the functionality of
corresponding Satoshi C++ code uses the same naming conventions: CTransaction,
CBlockHeader, nValue etc. Otherwise Python naming conventions are followed.


## Mutable vs. Immutable objects

Like the Telestai Core codebase CTransaction is immutable and
CMutableTransaction is mutable; unlike the Telestai Core codebase this
distinction also applies to COutPoint, CTxIn, CTxOut, and CBlock.


## Endianness Gotchas

Rather confusingly Telestai Core shows transaction and block hashes as
little-endian hex rather than the big-endian the rest of the world uses for
SHA256. python-telestailib provides the convenience functions x() and lx() in
telestai.core to convert from big-endian and little-endian hex to raw bytes to
accomodate this. In addition see b2x() and b2lx() for conversion from bytes to
big/little-endian hex.


## Module import style

While not always good style, it's often convenient for quick scripts if
`import *` can be used. To support that all the modules have `__all__` defined
appropriately.


# Example Code

See `examples/` directory. For instance this example creates a transaction
spending a pay-to-script-hash transaction output:

    $ PYTHONPATH=. examples/spend-pay-to-script-hash-txout.py
    <hex-encoded transaction>


## Selecting the chain to use

Do the following:

    import telestai
    telestai.SelectParams(NAME)

Where NAME is one of 'testnet', 'mainnet', or 'regtest'. The chain currently
selected is a global variable that changes behavior everywhere, just like in
the Satoshi codebase.


## Unit tests

Under telestai/tests using test data from Telestai Core. To run them:

    python3 -m unittest discover

Alternately, if Tox (see https://tox.readthedocs.org/) is available on your
system, you can run unit tests for multiple Python versions:

    ./runtests.sh

HTML coverage reports can then be found in the htmlcov/ subdirectory.

## Documentation

Sphinx documentation is in the "doc" subdirectory. Run "make help" from there
to see how to build. You will need the Python "sphinx" package installed.

Currently this is just API documentation generated from the code and
docstrings. Higher level written docs would be useful, perhaps starting with
much of this README. Pages are written in reStructuredText and linked from
index.rst.

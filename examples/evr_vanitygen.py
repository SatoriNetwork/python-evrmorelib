#!/usr/bin/env python3
# Copyright (C) 2020 The python-evrmorelib developers
#
# This file is part of python-evrmorelib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-evrmorelib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

# Evrmore vanity address generator
# This is an example of address generation in python-evrmorelib
# Note this is not particularly secure as the private keys may remain accessible in (virtual) memory

import argparse
import os
import sys
import time

import evrmore.base58
from evrmore.wallet import P2PKHEvrmoreAddress, CEvrmoreSecret

parser = argparse.ArgumentParser(
    description='Evrmore vanity address generator')
parser.add_argument('search', metavar='search string',
                    type=str, help='Search string')
parser.add_argument('--anywhere', action="store_true",
                    help="Search for string anywhere in address (default: leading characters only)")
args = parser.parse_args()

search_s = args.search
anywhere = args.anywhere

if not anywhere and search_s[0] != "R":
    print("First character of search string must be 'R'")
    sys.exit(1)

try:
    evrmore.base58.decode(search_s)
except evrmore.base58.InvalidBase58Error as e:
    print("Error: {}".format(e))
    sys.exit(1)

evrmore.SelectParams('mainnet')

c = 0
start = time.time()
while True:
    privkey = CEvrmoreSecret.from_secret_bytes(os.urandom(32))
    addr = str(P2PKHEvrmoreAddress.from_pubkey(privkey.pub))
    c += 1
    if anywhere:
        if search_s in addr:
            break
    else:
        if addr.startswith(search_s):
            break

    if c % 1000 == 0:
        sec = time.time()-start
        sys.stdout.write(f'Try {c} ({round(c/sec)} keys/s)\r')
        sys.stdout.flush()


print(addr, privkey)

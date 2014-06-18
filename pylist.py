#!/usr/bin/python
import python_sha3
import aes
import os
import sys
import json
import pbkdf2 as PBKDF2
from bitcoin import *

exodus = '1PiX8AWAHTz5X29M2Rra6mKtm2mKH8EZYX' if len(sys.argv) == 1 else sys.argv[1]

def pbkdf2(x):
    return PBKDF2._pbkdf2(x,x,2000)[:16]

outs = history(exodus)

txs = {}

for o in outs:
    if o['output'][65:] == '0':
        h = o['output'][:64]
        try:
            txs[h] = fetchtx(h)
        except:
            txs[h] = blockr_fetchtx(h)

def processtx(txhex):
        tx = deserialize(txhex)
        ethaddr = b58check_to_hex(script_to_address(tx['outs'][1]['script']))
        print "Tx:",h
        print "Value:",tx['outs'][0]['value']
        print "Ethereum address:",ethaddr
    

for h in txs:
    txhex = txs[h]
    try:
        processtx(txhex)
    except:
        pass

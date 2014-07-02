#!/usr/bin/python
import sys
import pbkdf2 as PBKDF2
import bitcoin as b


if len(sys.argv) == 1:
    exodus = sys.argv[1]
else:
    exodus = '1PiX8AWAHTz5X29M2Rra6mKtm2mKH8EZYX'


def pbkdf2(x):
    return PBKDF2._pbkdf2(x, x, 2000)[:16]

outs = b.blockr_unspent(exodus)

txs = {}

for o in outs:
    if o['output'][65:] == '0':
        h = o['output'][:64]
        try:
            txs[h] = b.fetchtx(h)
        except:
            txs[h] = b.blockr_fetchtx(h)


def processtx(txhex):
        txouts = b.deserialize(txhex)['outs']
        ethaddr = b.b58check_to_hex(b.script_to_address(txouts[1]['script']))
        print "Tx:", h
        print "Value:", txouts[0]['value']
        print "Ethereum address:", ethaddr

for h in txs:
    txhex = txs[h]
    try:
        processtx(txhex)
    except:
        pass

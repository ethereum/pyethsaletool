#!/usr/bin/python
import pbkdf2 as PBKDF2
import bitcoin as b
import sys

if len(sys.argv) == 0:
    sys.stderr.write("Must provide your ETH address, eg. python pylist.py"
                     " cd2a3d9f938e13cd947ec05abc7fe734df8dd826")
    sys.exit()

mybtcaddr = b.hex_to_b58check(sys.argv[-1])
exodus = '36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2'


def pbkdf2(x):
    return PBKDF2._pbkdf2(x, x, 2000)[:16]

outs = b.unspent(mybtcaddr)

txs = {}

for o in outs:
    if o['output'][65:] == '1':
        h = o['output'][:64]
        try:
            txs[h] = b.fetchtx(h)
        except:
            txs[h] = b.blockr_fetchtx(h)


for h in txs:
    txhex = txs[h]
    txouts = b.deserialize(txhex)['outs']
    if txouts[0]['value'] >= 970000 and len(txouts) >= 2:
        ethaddr = b.b58check_to_hex(
            b.script_to_address(txouts[1]['script']))
        v = txouts[0]['value'] + 30000
        print "Tx:", h
        print "Satoshis:", v
        print "Estimated ETH (min):", v * 1337 / 10**8
        print "Estimated ETH (max):", v * 2000 / 10**8

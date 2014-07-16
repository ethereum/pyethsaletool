#!/usr/bin/python
import pbkdf2 as PBKDF2
import bitcoin as b

exodus = '3HE73tDm7q6wHMhCxfThDQFpBX9oq14ZaG'


def pbkdf2(x):
    return PBKDF2._pbkdf2(x, x, 2000)[:16]

outs = b.history(exodus)

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
    if txouts[0]['value'] >= 960000 and len(txouts) >= 2:
        ethaddr = b.b58check_to_hex(b.script_to_address(txouts[1]['script']))
        v = txouts[0]['value'] + 40000
        print "Tx:", h
        print "Satoshis:", v
        print "Estimated ETH (min):", v * 1337 / 10**8
        print "Estimated ETH (max):", v * 2000 / 10**8
        print "Ethereum address:", ethaddr

for h in txs:
    txhex = txs[h]
    try:
        processtx(txhex)
    except:
        pass

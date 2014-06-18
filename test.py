import os, json, pyethereum, random, aes
import pbkdf2 as PBKDF2
from bitcoin import *

import python_sha3, aes

def sha3(x): return python_sha3.sha3_256(x).digest()

def pbkdf2(x): return PBKDF2._pbkdf2(x,x,2000)[:16]

for i in range(300):
    seed = ''.join([random.choice('gsyehrct7nbt3q7wrq37trq7324trwu3vnwu4tayw4598cz53w5w39po') for x in range(20)])
    pw = ''.join([random.choice('gsyehrct7nbt3q7wrq37trq7324trwu3vnwu4tayw4598cz53w5w39po') for x in range(20)])
    print os.popen('./pyethsaletool.py genwallet -o yes -s %s -p %s -w /tmp/meimei -b /tmp/meimei2' % (seed,pw)).read()
    w = json.loads(open('/tmp/meimei').read())
    assert aes.decryptData(pbkdf2(pw), w['encseed'].decode('hex')) == seed
    s = os.popen('./pyethsaletool.py getseed -w /tmp/meimei -p %s' % pw).read()
    assert s.strip() == seed
    print "AES seed encoding tests pass"
    btck = os.popen('./pyethsaletool.py getbtcprivkey -w /tmp/meimei -p %s' % pw).read().strip()
    ethk = os.popen('./pyethsaletool.py getethprivkey -w /tmp/meimei -p %s' % pw).read().strip()
    assert privtoaddr(btck) == w['btcaddr']
    assert pyethereum.utils.privtoaddr(ethk) == w['ethaddr']
    print "BTC and ETH addrs and keys are correct"
    r1 = os.popen('./pyethsaletool.py recover -w /tmp/meimei -p %s' % pw).read().strip().split(' ')[-1]
    assert r1 == seed
    r2 = os.popen('./pyethsaletool.py recover -w /tmp/meimei -b /tmp/meimei2').read().strip().split(' ')[-1]
    assert r2 == seed
    r3 = os.popen('./pyethsaletool.py recover -b /tmp/meimei2 -p %s' % pw).read().strip().split(' ')[-1]
    assert r3 == seed
    print "Recovery works"

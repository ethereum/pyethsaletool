#!/usr/bin/python
import python_sha3
import aes
import os
import sys
import json
import getpass
import pbkdf2 as PBKDF2
from bitcoin import *

from optparse import OptionParser

# Arguments

exodus = '1FxkfJQLJTXpW6QmxGT6oF43ZH959ns8Cq'
minimum = 1000000

# Option parsing

parser = OptionParser()
parser.add_option('-p', '--password',
                  default=None, dest='pw')
parser.add_option('-s', '--seed',
                  default=None, dest='seed')
parser.add_option('-w', '--wallet',
                  default='ethwallet.json', dest='wallet')
parser.add_option('-b', '--backup',
                  default='ethwallet.bkp.json', dest='backup')
parser.add_option('-o', '--overwrite',
                  default=False, dest='overwrite')

(options, args) = parser.parse_args()

# Function wrappers


def sha3(x):
    return python_sha3.sha3_256(x).digest()


def pbkdf2(x):
    return PBKDF2._pbkdf2(x, x, 2000)[:16]


# Prefer openssl because it's more well-tested and reviewed; otherwise,
# use pybitcointools' internal ecdsa implementation
try:
    import openssl
except:
    openssl = None


def openssl_tx_sign(tx, priv):
    if len(priv) == 64:
        priv = priv.decode('hex')
    if openssl:
        k = openssl.CKey()
        k.generate(priv)
        u = k.sign(bitcoin.bin_txhash(tx))
        return u.encode('hex')
    else:
        return ecdsa_tx_sign(tx, priv)


def secure_sign(tx, i, priv):
    i = int(i)
    if not re.match('^[0-9a-fA-F]*$', tx):
        return sign(tx.encode('hex'), i, priv).decode('hex')
    if len(priv) <= 33:
        priv = priv.encode('hex')
    pub = privkey_to_pubkey(priv)
    address = pubkey_to_address(pub)
    signing_tx = signature_form(tx, i, mk_pubkey_script(address))
    sig = openssl_tx_sign(signing_tx, priv)
    txobj = deserialize(tx)
    txobj["ins"][i]["script"] = serialize_script([sig, pub])
    return serialize(txobj)


def secure_privtopub(priv):
    if len(priv) == 64:
        return secure_privtopub(priv.decode('hex')).encode('hex')
    if openssl:
        k = openssl.CKey()
        k.generate(priv)
        return k.get_pubkey()
    else:
        return privtopub(priv)


def tryopen(f):
    try:
        assert f
        t = open(f).read()
        try:
            return json.loads(t)
        except:
            raise Exception("Corrupted file: "+f)
    except:
        return None


def eth_privtoaddr(priv):
    pub = encode_pubkey(secure_privtopub(priv), 'bin_electrum')
    return sha3(pub)[12:].encode('hex')


def getseed(encseed, pw, ethaddr):
    seed = aes.decryptData(pw, encseed.decode('hex'))
    ethpriv = sha3(seed)
    if eth_privtoaddr(ethpriv) != ethaddr:
        raise Exception("Ethereum address provided to getseed does not match!")
    return seed


def mkbackup(wallet, pw):
    seed = getseed(wallet['encseed'], pw, wallet['ethaddr'])
    return {
        "withpw": aes.encryptData(pw, seed).encode('hex'),
        "withwallet": aes.encryptData(wallet['bkp'], seed).encode('hex'),
        "ethaddr": wallet['ethaddr']
    }


def genwallet(seed, pw):
    encseed = aes.encryptData(pw, seed)
    ethpriv = sha3(seed)
    btcpriv = sha3(seed + '\x01')
    ethaddr = sha3(secure_privtopub(ethpriv)[1:])[12:].encode('hex')
    btcaddr = privtoaddr(btcpriv)
    bkp = sha3(seed + '\x02').encode('hex')[:32]
    return {
        "encseed": encseed.encode('hex'),
        "bkp": bkp,
        "ethaddr": ethaddr,
        "btcaddr": btcaddr,
    }


def finalize(wallet, unspent, pw):
    seed = getseed(wallet["encseed"], pw, wallet["ethaddr"])
    balance = sum([o["value"] for o in unspent])
    if balance == 0:
        raise Exception("No funds in address")
    if balance < minimum:
        raise Exception("Insufficient funds. Need at least 0.001 BTC")
    outs = [
        exodus+':'+str(balance - 30000),
        hex_to_b58check(wallet["ethaddr"])+':10000'
    ]
    tx = mktx(unspent, outs)
    btcpriv = sha3(seed+'\x01')
    for i in range(len(unspent)):
        tx = secure_sign(tx, i, btcpriv)
    return tx


def recover_bkp_pw(bkp, pw):
    return getseed(bkp['withpw'], pw, bkp['ethaddr'])


def recover_bkp_wallet(bkp, wallet):
    return getseed(bkp['withwallet'], wallet['bkp'], bkp['ethaddr'])


def ask_for_password(twice=False):
    if options.pw:
        return pbkdf2(options.pw)
    pw = getpass.getpass()
    if twice:
        pw2 = getpass.getpass()
        if pw != pw2:
            raise Exception("Passwords do not match")
    return pbkdf2(pw)


def ask_for_seed():
    if options.seed:
        return options.seed
    else:
        # uses pybitcointools' 3-source random generator
        return random_key().decode('hex')


def checkwrite(f, thunk):
    try:
        open(f)
        # File already exists
        if not options.overwrite:
            s = "File %s already exists. Overwrite? (y/n) "
            are_you_sure = raw_input(s % f)
            if are_you_sure not in ['y', 'yes']:
                sys.exit()
    except:
        # File does not already exist, we're fine
        pass
    open(f, 'w').write(thunk())


w = tryopen(options.wallet)
b = tryopen(options.backup)
# Generate new wallet
if not len(args):
    pass
elif args[0] == 'genwallet':
    pw = ask_for_password(True)
    newwal = genwallet(ask_for_seed(), pw)
    checkwrite(options.wallet, lambda: json.dumps(newwal))
    if options.backup:
        checkwrite(options.backup, lambda: json.dumps(mkbackup(newwal, pw)))
    print "Your intermediate Bitcoin address is:", newwal['btcaddr']
# Backup existing wallet
elif args[0] == 'mkbackup':
    if not w:
        print "Must specify wallet with -w"
    if not opts['backup']:
        opts['backup'] = 'ethwallet.bkp.json'
    pw = password()
    checkwrite(opts['backup'], lambda: json.dumps(mkbackup(w, pw)))
# Get wallet Bitcoin address
elif args[0] == 'getbtcaddress':
    if not w:
        print "Must specify wallet with -w"
    print w["btcaddr"]
# Get wallet Ethereum address
elif args[0] == 'getethaddress':
    if not w:
        print "Must specify wallet with -w"
    print w["ethaddr"]
# Get wallet Bitcoin privkey
elif args[0] == 'getbtcprivkey':
    pw = ask_for_password()
    print encode_privkey(sha3(getseed(w['encseed'], pw,
                         w['ethaddr'])+'\x01'), 'wif')
# Get wallet seed
elif args[0] == 'getseed':
    pw = ask_for_password()
    print getseed(w['encseed'], pw, w['ethaddr'])
# Get wallet Ethereum privkey
elif args[0] == 'getethprivkey':
    pw = ask_for_password()
    print encode_privkey(sha3(getseed(w['encseed'], pw, w['ethaddr'])), 'hex')
# Recover wallet seed
elif args[0] == 'recover':
    if not w and not b:
        print "Must have wallet or backup file"
    elif not b:
        pw = ask_for_password()
        print "Your seed is:", getseed(w['encseed'], pw, w['ethaddr'])
    elif not w:
        pw = ask_for_password()
        print "Your seed is:", getseed(b['withpw'], pw, b['ethaddr'])
    else:
        print "Your seed is:", getseed(b['withwallet'], w['bkp'], b['ethaddr'])
# Finalize a wallet
elif args[0] == 'finalize':
    try:
        u = unspent(w["btcaddr"])
    except:
        try:
            u = blockr_unspent(w["btcaddr"])
        except:
            raise Exception("Blockchain.info and Blockr.io both down. Cannot get transaction outputs to finalize. Remember that your funds stored in the intermediate address can always be recovered by running './pyethsaletool.py getbtcprivkey' and importing the output into a Bitcoin wallet like blockchain.info")
    pw = ask_for_password()
    tx = finalize(w, u, pw)
    try:
        print pushtx(tx)
    except:
        try:
            print eligius_pushtx(tx)
        except:
            raise Exception("Blockchain.info and Eligius both down. Cannot send transaction. Remember that your funds stored in the intermediate address can always be recovered by running './pyethsaletool.py getbtcprivkey' and importing the output into a Bitcoin wallet like blockchain.info")
# sha3 calculator
elif args[0] == 'sha3':
    print sha3(sys.argv[2]).encode('hex')
# Help
else:
    print 'Use "pyethsaletool genwallet" to generate a wallet'
    print 'Use "pyethsaletool mkbackup" to make a backup of a wallet (using -w and -b)'
    print 'Use "pyethsaletool getbtcaddress" to output the intermediate Bitcoin address you need to send funds to'
    print 'Use "pyethsaletool getbtcprivkey" to output the private key to your intermediate Bitcoin address'
    print 'Use "pyethsaletool getethaddress" to output the Ethereum address'
    print 'Use "pyethsaletool getethprivkey" to output the Ethereum private key'
    print 'Use "pyethsaletool finalize" to finalize the funding process once you have deposited to the intermediate address'
    print 'Use "pyethsaletool recover" to recover the seed if you are missing either your wallet or your password'
    print 'Use -s to specify a seed, -w to specify a wallet file, -b to specify a backup file and -p to specify a password when creating a wallet. The -w, -b and -p options also work with other commands.'

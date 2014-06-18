# -*- coding: utf-8 -*-

'''

    Copyright 2012 Joe Harris

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''

'''

    Pure Python (>=2.6, 3.x) pbkdf2 library using sha256. Core ported from
    Django 1.5 with Django-isms removed and Python 3.x compatibility added.
    This generates Django compatible pbkdf2_sha256 hashes. Respectably fast
    despite being in pure Python (4x slower than pure C alternatives). See
    Django hashers for additional notes.
    
    This is useful for projects that you want to verify against Django-generated
    hashes without requiring Django itself.
    
    Usage:
        
        my_hash = pbkdf2_hash('derp')
        if pbkdf2_verify('derp', my_hash):
            print 'hash is valid! woop!'

'''

import os
import string
import binascii
from operator import xor
from struct import pack
from hashlib import sha256
from base64 import b64encode, b64decode

_trans_5c = bytearray([(x ^ 0x5C) for x in range(256)])
_trans_36 = bytearray([(x ^ 0x36) for x in range(256)])
_name = 'pbkdf2_sha256'
_digest = sha256

def _tobytes(s):
    try:
        return bytes(s)
    except TypeError:
        return s.encode()

def _hmac(key, msg):
    dig1, dig2 = _digest(), _digest()
    if len(key) > dig1.block_size:
        key = _digest(key).digest()
    key += b'\x00' * (dig1.block_size - len(key))
    dig1.update(key.translate(_trans_36))
    dig1.update(msg)
    dig2.update(key.translate(_trans_5c))
    dig2.update(dig1.digest())
    return dig2

def _pbkdf2(password, salt, iterations, dklen=0):
    assert iterations > 0
    password = _tobytes(password)
    salt = _tobytes(salt)
    hlen = _digest().digest_size
    if not dklen:
        dklen = hlen
    if dklen > (2 ** 32 - 1) * hlen:
        raise OverflowError('dklen too big')
    l = -(-dklen // hlen)
    r = dklen - (l - 1) * hlen
    hex_format_string = '%%0%ix' % (hlen * 2)
    
    def funcf(i):
        def funcu():
            u = salt + pack(b'>I', i)
            for j in range(int(iterations)):
                u = _hmac(password, u).digest()
                yield int(binascii.hexlify(u), 16)
        r = 0
        for a in funcu():
           r = xor(r, a)
        return binascii.unhexlify((hex_format_string % r).encode('ascii'))
    
    t = [funcf(x) for x in range(1, l + 1)]
    return b''.join(t[:-1]) + t[-1][:r]

def randstr(size=16, chars=''):
    if not chars:
        chars = string.ascii_letters + string.digits
    chars = list(chars)
    if '$' in chars:
        raise ValueError('salt cannot contain $')
    nchars = len(chars)
    r = r''
    for c in os.urandom(size):
        if type(c) == str:
            c = ord(c)
        r += chars[c % nchars]
    return r

def pbkdf2_hash(s):
    salt = randstr(16)
    iters = 10000
    h = b64encode(_pbkdf2(password=s, salt=salt, iterations=iters))
    return r'{}${}${}${}'.format(_name, iters, salt, h.decode('ascii'))

def pbkdf2_verify(s, h):
    parts = h.split('$')
    if len(parts) != 4:
        raise ValueError('invalid comparison hash (bad number of parts): {}'.format(h))
    if parts[0] != _name:
        raise ValueError('invalid comparison hash, only {} is supported, got: {}'.format(_name, parts[0]))
    salt = parts[2]
    try:
        iters = int(parts[1])
    except ValueError:
        raise ValueError('invalid comparison hash (bad iter count): {}'.format(h))
    c = _pbkdf2(password=s, salt=salt, iterations=iters)
    return c == b64decode(parts[3].encode())

'''

    eof

'''

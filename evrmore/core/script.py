# Copyright (C) 2012-2015 The python-bitcoinlib developers
#
# This file is part of python-evrmorelib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-evrmoreb, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Scripts

Functionality to build scripts, as well as SignatureHash(). Script evaluation
is in evrmore.core.scripteval
"""

from __future__ import absolute_import, division, print_function
from .serialize import *
import evrmore.core._bignum
import evrmore.core
import struct

import sys
_bchr = chr
_bord = ord
if sys.version > '3':
    long = int
    def _bchr(x): return bytes([x])
    def _bord(x): return x
    from io import BytesIO as _BytesIO
else:
    from cStringIO import StringIO as _BytesIO


MAX_SCRIPT_SIZE = 10000
MAX_SCRIPT_ELEMENT_SIZE = 520
MAX_SCRIPT_OPCODES = 201

OPCODE_NAMES = {}

_opcode_instances = []


class CScriptOp(int):
    """A single script opcode"""
    __slots__ = []

    @staticmethod
    def encode_op_pushdata(d):
        """Encode a PUSHDATA op, returning bytes"""
        if len(d) < 0x4c:
            return b'' + _bchr(len(d)) + d  # OP_PUSHDATA
        elif len(d) <= 0xff:
            return b'\x4c' + _bchr(len(d)) + d  # OP_PUSHDATA1
        elif len(d) <= 0xffff:
            return b'\x4d' + struct.pack(b'<H', len(d)) + d  # OP_PUSHDATA2
        elif len(d) <= 0xffffffff:
            return b'\x4e' + struct.pack(b'<I', len(d)) + d  # OP_PUSHDATA4
        else:
            raise ValueError("Data too long to encode in a PUSHDATA op")

    @staticmethod
    def encode_op_n(n):
        """Encode a small integer op, returning an opcode"""
        if not (0 <= n <= 16):
            raise ValueError(
                'Integer must be in range 0 <= n <= 16, got %d' % n)

        if n == 0:
            return OP_0
        else:
            return CScriptOp(OP_1 + n-1)

    def decode_op_n(self):
        """Decode a small integer opcode, returning an integer"""
        if self == OP_0:
            return 0

        if not (self == OP_0 or OP_1 <= self <= OP_16):
            raise ValueError('op %r is not an OP_N' % self)

        return int(self - OP_1+1)

    def is_small_int(self):
        """Return true if the op pushes a small integer to the stack"""
        if 0x51 <= self <= 0x60 or self == 0:
            return True
        else:
            return False

    def __str__(self):
        return repr(self)

    def __repr__(self):
        if self in OPCODE_NAMES:
            return OPCODE_NAMES[self]
        else:
            return 'CScriptOp(0x%x)' % self

    def __new__(cls, n):
        try:
            return _opcode_instances[n]
        except IndexError:
            assert len(_opcode_instances) == n
            _opcode_instances.append(super(CScriptOp, cls).__new__(cls, n))
            return _opcode_instances[n]


# Populate opcode instance table
for n in range(0xff+1):
    CScriptOp(n)


# push value
OP_0 = CScriptOp(0x00)
OP_FALSE = OP_0
OP_PUSHDATA1 = CScriptOp(0x4c)
OP_PUSHDATA2 = CScriptOp(0x4d)
OP_PUSHDATA4 = CScriptOp(0x4e)
OP_1NEGATE = CScriptOp(0x4f)
OP_RESERVED = CScriptOp(0x50)
OP_1 = CScriptOp(0x51)
OP_TRUE = OP_1
OP_2 = CScriptOp(0x52)
OP_3 = CScriptOp(0x53)
OP_4 = CScriptOp(0x54)
OP_5 = CScriptOp(0x55)
OP_6 = CScriptOp(0x56)
OP_7 = CScriptOp(0x57)
OP_8 = CScriptOp(0x58)
OP_9 = CScriptOp(0x59)
OP_10 = CScriptOp(0x5a)
OP_11 = CScriptOp(0x5b)
OP_12 = CScriptOp(0x5c)
OP_13 = CScriptOp(0x5d)
OP_14 = CScriptOp(0x5e)
OP_15 = CScriptOp(0x5f)
OP_16 = CScriptOp(0x60)

# control
OP_NOP = CScriptOp(0x61)
OP_VER = CScriptOp(0x62)
OP_IF = CScriptOp(0x63)
OP_NOTIF = CScriptOp(0x64)
OP_VERIF = CScriptOp(0x65)
OP_VERNOTIF = CScriptOp(0x66)
OP_ELSE = CScriptOp(0x67)
OP_ENDIF = CScriptOp(0x68)
OP_VERIFY = CScriptOp(0x69)
OP_RETURN = CScriptOp(0x6a)

# stack ops
OP_TOALTSTACK = CScriptOp(0x6b)
OP_FROMALTSTACK = CScriptOp(0x6c)
OP_2DROP = CScriptOp(0x6d)
OP_2DUP = CScriptOp(0x6e)
OP_3DUP = CScriptOp(0x6f)
OP_2OVER = CScriptOp(0x70)
OP_2ROT = CScriptOp(0x71)
OP_2SWAP = CScriptOp(0x72)
OP_IFDUP = CScriptOp(0x73)
OP_DEPTH = CScriptOp(0x74)
OP_DROP = CScriptOp(0x75)
OP_DUP = CScriptOp(0x76)
OP_NIP = CScriptOp(0x77)
OP_OVER = CScriptOp(0x78)
OP_PICK = CScriptOp(0x79)
OP_ROLL = CScriptOp(0x7a)
OP_ROT = CScriptOp(0x7b)
OP_SWAP = CScriptOp(0x7c)
OP_TUCK = CScriptOp(0x7d)

# splice ops
OP_CAT = CScriptOp(0x7e)
OP_SUBSTR = CScriptOp(0x7f)
OP_LEFT = CScriptOp(0x80)
OP_RIGHT = CScriptOp(0x81)
OP_SIZE = CScriptOp(0x82)

# bit logic
OP_INVERT = CScriptOp(0x83)
OP_AND = CScriptOp(0x84)
OP_OR = CScriptOp(0x85)
OP_XOR = CScriptOp(0x86)
OP_EQUAL = CScriptOp(0x87)
OP_EQUALVERIFY = CScriptOp(0x88)
OP_RESERVED1 = CScriptOp(0x89)
OP_RESERVED2 = CScriptOp(0x8a)

# numeric
OP_1ADD = CScriptOp(0x8b)
OP_1SUB = CScriptOp(0x8c)
OP_2MUL = CScriptOp(0x8d)
OP_2DIV = CScriptOp(0x8e)
OP_NEGATE = CScriptOp(0x8f)
OP_ABS = CScriptOp(0x90)
OP_NOT = CScriptOp(0x91)
OP_0NOTEQUAL = CScriptOp(0x92)

OP_ADD = CScriptOp(0x93)
OP_SUB = CScriptOp(0x94)
OP_MUL = CScriptOp(0x95)
OP_DIV = CScriptOp(0x96)
OP_MOD = CScriptOp(0x97)
OP_LSHIFT = CScriptOp(0x98)
OP_RSHIFT = CScriptOp(0x99)

OP_BOOLAND = CScriptOp(0x9a)
OP_BOOLOR = CScriptOp(0x9b)
OP_NUMEQUAL = CScriptOp(0x9c)
OP_NUMEQUALVERIFY = CScriptOp(0x9d)
OP_NUMNOTEQUAL = CScriptOp(0x9e)
OP_LESSTHAN = CScriptOp(0x9f)
OP_GREATERTHAN = CScriptOp(0xa0)
OP_LESSTHANOREQUAL = CScriptOp(0xa1)
OP_GREATERTHANOREQUAL = CScriptOp(0xa2)
OP_MIN = CScriptOp(0xa3)
OP_MAX = CScriptOp(0xa4)

OP_WITHIN = CScriptOp(0xa5)

# crypto
OP_RIPEMD160 = CScriptOp(0xa6)
OP_SHA1 = CScriptOp(0xa7)
OP_SHA256 = CScriptOp(0xa8)
OP_HASH160 = CScriptOp(0xa9)
OP_HASH256 = CScriptOp(0xaa)
OP_CODESEPARATOR = CScriptOp(0xab)
OP_CHECKSIG = CScriptOp(0xac)
OP_CHECKSIGVERIFY = CScriptOp(0xad)
OP_CHECKMULTISIG = CScriptOp(0xae)
OP_CHECKMULTISIGVERIFY = CScriptOp(0xaf)

# expansion
OP_NOP1 = CScriptOp(0xb0)
OP_NOP2 = CScriptOp(0xb1)
OP_CHECKLOCKTIMEVERIFY = OP_NOP2
OP_NOP3 = CScriptOp(0xb2)
OP_CHECKSEQUENCEVERIFY = OP_NOP3
OP_NOP4 = CScriptOp(0xb3)
OP_NOP5 = CScriptOp(0xb4)
OP_NOP6 = CScriptOp(0xb5)
OP_NOP7 = CScriptOp(0xb6)
OP_NOP8 = CScriptOp(0xb7)
OP_NOP9 = CScriptOp(0xb8)
OP_NOP10 = CScriptOp(0xb9)

# template matching params
OP_SMALLINTEGER = CScriptOp(0xfa)
OP_PUBKEYS = CScriptOp(0xfb)
OP_PUBKEYHASH = CScriptOp(0xfd)
OP_PUBKEY = CScriptOp(0xfe)

OP_INVALIDOPCODE = CScriptOp(0xff)

OP_EVR_ASSET = CScriptOp(0xc0)

OPCODE_NAMES.update({
    OP_0: 'OP_0',
    OP_PUSHDATA1: 'OP_PUSHDATA1',
    OP_PUSHDATA2: 'OP_PUSHDATA2',
    OP_PUSHDATA4: 'OP_PUSHDATA4',
    OP_1NEGATE: 'OP_1NEGATE',
    OP_RESERVED: 'OP_RESERVED',
    OP_1: 'OP_1',
    OP_2: 'OP_2',
    OP_3: 'OP_3',
    OP_4: 'OP_4',
    OP_5: 'OP_5',
    OP_6: 'OP_6',
    OP_7: 'OP_7',
    OP_8: 'OP_8',
    OP_9: 'OP_9',
    OP_10: 'OP_10',
    OP_11: 'OP_11',
    OP_12: 'OP_12',
    OP_13: 'OP_13',
    OP_14: 'OP_14',
    OP_15: 'OP_15',
    OP_16: 'OP_16',
    OP_NOP: 'OP_NOP',
    OP_VER: 'OP_VER',
    OP_IF: 'OP_IF',
    OP_NOTIF: 'OP_NOTIF',
    OP_VERIF: 'OP_VERIF',
    OP_VERNOTIF: 'OP_VERNOTIF',
    OP_ELSE: 'OP_ELSE',
    OP_ENDIF: 'OP_ENDIF',
    OP_VERIFY: 'OP_VERIFY',
    OP_RETURN: 'OP_RETURN',
    OP_TOALTSTACK: 'OP_TOALTSTACK',
    OP_FROMALTSTACK: 'OP_FROMALTSTACK',
    OP_2DROP: 'OP_2DROP',
    OP_2DUP: 'OP_2DUP',
    OP_3DUP: 'OP_3DUP',
    OP_2OVER: 'OP_2OVER',
    OP_2ROT: 'OP_2ROT',
    OP_2SWAP: 'OP_2SWAP',
    OP_IFDUP: 'OP_IFDUP',
    OP_DEPTH: 'OP_DEPTH',
    OP_DROP: 'OP_DROP',
    OP_DUP: 'OP_DUP',
    OP_NIP: 'OP_NIP',
    OP_OVER: 'OP_OVER',
    OP_PICK: 'OP_PICK',
    OP_ROLL: 'OP_ROLL',
    OP_ROT: 'OP_ROT',
    OP_SWAP: 'OP_SWAP',
    OP_TUCK: 'OP_TUCK',
    OP_CAT: 'OP_CAT',
    OP_SUBSTR: 'OP_SUBSTR',
    OP_LEFT: 'OP_LEFT',
    OP_RIGHT: 'OP_RIGHT',
    OP_SIZE: 'OP_SIZE',
    OP_INVERT: 'OP_INVERT',
    OP_AND: 'OP_AND',
    OP_OR: 'OP_OR',
    OP_XOR: 'OP_XOR',
    OP_EQUAL: 'OP_EQUAL',
    OP_EQUALVERIFY: 'OP_EQUALVERIFY',
    OP_RESERVED1: 'OP_RESERVED1',
    OP_RESERVED2: 'OP_RESERVED2',
    OP_1ADD: 'OP_1ADD',
    OP_1SUB: 'OP_1SUB',
    OP_2MUL: 'OP_2MUL',
    OP_2DIV: 'OP_2DIV',
    OP_NEGATE: 'OP_NEGATE',
    OP_ABS: 'OP_ABS',
    OP_NOT: 'OP_NOT',
    OP_0NOTEQUAL: 'OP_0NOTEQUAL',
    OP_ADD: 'OP_ADD',
    OP_SUB: 'OP_SUB',
    OP_MUL: 'OP_MUL',
    OP_DIV: 'OP_DIV',
    OP_MOD: 'OP_MOD',
    OP_LSHIFT: 'OP_LSHIFT',
    OP_RSHIFT: 'OP_RSHIFT',
    OP_BOOLAND: 'OP_BOOLAND',
    OP_BOOLOR: 'OP_BOOLOR',
    OP_NUMEQUAL: 'OP_NUMEQUAL',
    OP_NUMEQUALVERIFY: 'OP_NUMEQUALVERIFY',
    OP_NUMNOTEQUAL: 'OP_NUMNOTEQUAL',
    OP_LESSTHAN: 'OP_LESSTHAN',
    OP_GREATERTHAN: 'OP_GREATERTHAN',
    OP_LESSTHANOREQUAL: 'OP_LESSTHANOREQUAL',
    OP_GREATERTHANOREQUAL: 'OP_GREATERTHANOREQUAL',
    OP_MIN: 'OP_MIN',
    OP_MAX: 'OP_MAX',
    OP_WITHIN: 'OP_WITHIN',
    OP_RIPEMD160: 'OP_RIPEMD160',
    OP_SHA1: 'OP_SHA1',
    OP_SHA256: 'OP_SHA256',
    OP_HASH160: 'OP_HASH160',
    OP_HASH256: 'OP_HASH256',
    OP_CODESEPARATOR: 'OP_CODESEPARATOR',
    OP_CHECKSIG: 'OP_CHECKSIG',
    OP_CHECKSIGVERIFY: 'OP_CHECKSIGVERIFY',
    OP_CHECKMULTISIG: 'OP_CHECKMULTISIG',
    OP_CHECKMULTISIGVERIFY: 'OP_CHECKMULTISIGVERIFY',
    OP_NOP1: 'OP_NOP1',
    OP_NOP2: 'OP_NOP2',
    OP_CHECKLOCKTIMEVERIFY: 'OP_CHECKLOCKTIMEVERIFY',
    OP_NOP3: 'OP_NOP3',
    OP_CHECKSEQUENCEVERIFY: 'OP_CHECKSEQUENCEVERIFY',
    OP_NOP4: 'OP_NOP4',
    OP_NOP5: 'OP_NOP5',
    OP_NOP6: 'OP_NOP6',
    OP_NOP7: 'OP_NOP7',
    OP_NOP8: 'OP_NOP8',
    OP_NOP9: 'OP_NOP9',
    OP_NOP10: 'OP_NOP10',
    OP_SMALLINTEGER: 'OP_SMALLINTEGER',
    OP_PUBKEYS: 'OP_PUBKEYS',
    OP_PUBKEYHASH: 'OP_PUBKEYHASH',
    OP_PUBKEY: 'OP_PUBKEY',
    OP_INVALIDOPCODE: 'OP_INVALIDOPCODE',
    OP_EVR_ASSET: 'OP_EVR_ASSET',
})

OPCODES_BY_NAME = {
    'OP_0': OP_0,
    'OP_PUSHDATA1': OP_PUSHDATA1,
    'OP_PUSHDATA2': OP_PUSHDATA2,
    'OP_PUSHDATA4': OP_PUSHDATA4,
    'OP_1NEGATE': OP_1NEGATE,
    'OP_RESERVED': OP_RESERVED,
    'OP_1': OP_1,
    'OP_2': OP_2,
    'OP_3': OP_3,
    'OP_4': OP_4,
    'OP_5': OP_5,
    'OP_6': OP_6,
    'OP_7': OP_7,
    'OP_8': OP_8,
    'OP_9': OP_9,
    'OP_10': OP_10,
    'OP_11': OP_11,
    'OP_12': OP_12,
    'OP_13': OP_13,
    'OP_14': OP_14,
    'OP_15': OP_15,
    'OP_16': OP_16,
    'OP_NOP': OP_NOP,
    'OP_VER': OP_VER,
    'OP_IF': OP_IF,
    'OP_NOTIF': OP_NOTIF,
    'OP_VERIF': OP_VERIF,
    'OP_VERNOTIF': OP_VERNOTIF,
    'OP_ELSE': OP_ELSE,
    'OP_ENDIF': OP_ENDIF,
    'OP_VERIFY': OP_VERIFY,
    'OP_RETURN': OP_RETURN,
    'OP_TOALTSTACK': OP_TOALTSTACK,
    'OP_FROMALTSTACK': OP_FROMALTSTACK,
    'OP_2DROP': OP_2DROP,
    'OP_2DUP': OP_2DUP,
    'OP_3DUP': OP_3DUP,
    'OP_2OVER': OP_2OVER,
    'OP_2ROT': OP_2ROT,
    'OP_2SWAP': OP_2SWAP,
    'OP_IFDUP': OP_IFDUP,
    'OP_DEPTH': OP_DEPTH,
    'OP_DROP': OP_DROP,
    'OP_DUP': OP_DUP,
    'OP_NIP': OP_NIP,
    'OP_OVER': OP_OVER,
    'OP_PICK': OP_PICK,
    'OP_ROLL': OP_ROLL,
    'OP_ROT': OP_ROT,
    'OP_SWAP': OP_SWAP,
    'OP_TUCK': OP_TUCK,
    'OP_CAT': OP_CAT,
    'OP_SUBSTR': OP_SUBSTR,
    'OP_LEFT': OP_LEFT,
    'OP_RIGHT': OP_RIGHT,
    'OP_SIZE': OP_SIZE,
    'OP_INVERT': OP_INVERT,
    'OP_AND': OP_AND,
    'OP_OR': OP_OR,
    'OP_XOR': OP_XOR,
    'OP_EQUAL': OP_EQUAL,
    'OP_EQUALVERIFY': OP_EQUALVERIFY,
    'OP_RESERVED1': OP_RESERVED1,
    'OP_RESERVED2': OP_RESERVED2,
    'OP_1ADD': OP_1ADD,
    'OP_1SUB': OP_1SUB,
    'OP_2MUL': OP_2MUL,
    'OP_2DIV': OP_2DIV,
    'OP_NEGATE': OP_NEGATE,
    'OP_ABS': OP_ABS,
    'OP_NOT': OP_NOT,
    'OP_0NOTEQUAL': OP_0NOTEQUAL,
    'OP_ADD': OP_ADD,
    'OP_SUB': OP_SUB,
    'OP_MUL': OP_MUL,
    'OP_DIV': OP_DIV,
    'OP_MOD': OP_MOD,
    'OP_LSHIFT': OP_LSHIFT,
    'OP_RSHIFT': OP_RSHIFT,
    'OP_BOOLAND': OP_BOOLAND,
    'OP_BOOLOR': OP_BOOLOR,
    'OP_NUMEQUAL': OP_NUMEQUAL,
    'OP_NUMEQUALVERIFY': OP_NUMEQUALVERIFY,
    'OP_NUMNOTEQUAL': OP_NUMNOTEQUAL,
    'OP_LESSTHAN': OP_LESSTHAN,
    'OP_GREATERTHAN': OP_GREATERTHAN,
    'OP_LESSTHANOREQUAL': OP_LESSTHANOREQUAL,
    'OP_GREATERTHANOREQUAL': OP_GREATERTHANOREQUAL,
    'OP_MIN': OP_MIN,
    'OP_MAX': OP_MAX,
    'OP_WITHIN': OP_WITHIN,
    'OP_RIPEMD160': OP_RIPEMD160,
    'OP_SHA1': OP_SHA1,
    'OP_SHA256': OP_SHA256,
    'OP_HASH160': OP_HASH160,
    'OP_HASH256': OP_HASH256,
    'OP_CODESEPARATOR': OP_CODESEPARATOR,
    'OP_CHECKSIG': OP_CHECKSIG,
    'OP_CHECKSIGVERIFY': OP_CHECKSIGVERIFY,
    'OP_CHECKMULTISIG': OP_CHECKMULTISIG,
    'OP_CHECKMULTISIGVERIFY': OP_CHECKMULTISIGVERIFY,
    'OP_NOP1': OP_NOP1,
    'OP_NOP2': OP_NOP2,
    'OP_CHECKLOCKTIMEVERIFY': OP_CHECKLOCKTIMEVERIFY,
    'OP_NOP3': OP_NOP3,
    'OP_CHECKSEQUENCEVERIFY': OP_CHECKSEQUENCEVERIFY,
    'OP_NOP4': OP_NOP4,
    'OP_NOP5': OP_NOP5,
    'OP_NOP6': OP_NOP6,
    'OP_NOP7': OP_NOP7,
    'OP_NOP8': OP_NOP8,
    'OP_NOP9': OP_NOP9,
    'OP_NOP10': OP_NOP10,
    'OP_SMALLINTEGER': OP_SMALLINTEGER,
    'OP_PUBKEYS': OP_PUBKEYS,
    'OP_PUBKEYHASH': OP_PUBKEYHASH,
    'OP_PUBKEY': OP_PUBKEY,
    'OP_EVR_ASSET': OP_EVR_ASSET
}

# Invalid even when occuring in an unexecuted OP_IF branch due to either being
# disabled, or never having been implemented.
DISABLED_OPCODES = frozenset((OP_VERIF, OP_VERNOTIF,
                                OP_CAT, OP_SUBSTR, OP_LEFT, OP_RIGHT, OP_INVERT, OP_AND,
                                OP_OR, OP_XOR, OP_2MUL, OP_2DIV, OP_MUL, OP_DIV, OP_MOD,
                                OP_LSHIFT, OP_RSHIFT))


class CScriptInvalidError(Exception):
    """Base class for CScript exceptions"""
    pass


class CScriptTruncatedPushDataError(CScriptInvalidError):
    """Invalid pushdata due to truncation"""

    def __init__(self, msg, data):
        self.data = data
        super(CScriptTruncatedPushDataError, self).__init__(msg)


class CScript(bytes):
    """Serialized script

    A bytes subclass, so you can use this directly whenever bytes are accepted.
    Note that this means that indexing does *not* work - you'll get an index by
    byte rather than opcode. This format was chosen for efficiency so that the
    general case would not require creating a lot of little CScriptOP objects.

    iter(script) however does iterate by opcode.
    """
    @classmethod
    def __coerce_instance(cls, other):
        # Coerce other into bytes
        if isinstance(other, CScriptOp):
            other = _bchr(other)
        elif isinstance(other, (int, long)):
            if 0 <= other <= 16:
                other = bytes(_bchr(CScriptOp.encode_op_n(other)))
            elif other == -1:
                other = bytes(_bchr(OP_1NEGATE))
            else:
                other = CScriptOp.encode_op_pushdata(
                    evrmore.core._bignum.bn2vch(other))
        elif isinstance(other, (bytes, bytearray)):
            other = CScriptOp.encode_op_pushdata(other)
        return other

    def __add__(self, other):
        # Do the coercion outside of the try block so that errors in it are
        # noticed.
        other = self.__coerce_instance(other)

        try:
            # bytes.__add__ always returns bytes instances unfortunately
            return CScript(super(CScript, self).__add__(other))
        except TypeError:
            raise TypeError(
                'Can not add a %r instance to a CScript' % other.__class__)

    def join(self, iterable):
        # join makes no sense for a CScript()
        raise NotImplementedError

    def __new__(cls, value=b''):
        if isinstance(value, bytes) or isinstance(value, bytearray):
            return super(CScript, cls).__new__(cls, value)
        else:
            def coerce_iterable(iterable):
                for instance in iterable:
                    yield cls.__coerce_instance(instance)
            # Annoyingly on both python2 and python3 bytes.join() always
            # returns a bytes instance even when subclassed.
            return super(CScript, cls).__new__(cls, b''.join(coerce_iterable(value)))

    def raw_iter(self):
        """Raw iteration

        Yields tuples of (opcode, data, sop_idx) so that the different possible
        PUSHDATA encodings can be accurately distinguished, as well as
        determining the exact opcode byte indexes. (sop_idx)
        """
        i = 0
        while i < len(self):
            sop_idx = i
            opcode = _bord(self[i])
            i += 1

            if opcode > OP_PUSHDATA4:
                yield (opcode, None, sop_idx)
            else:
                datasize = None
                pushdata_type = None
                if opcode < OP_PUSHDATA1:
                    pushdata_type = 'PUSHDATA(%d)' % opcode
                    datasize = opcode

                elif opcode == OP_PUSHDATA1:
                    pushdata_type = 'PUSHDATA1'
                    if i >= len(self):
                        raise CScriptInvalidError(
                            'PUSHDATA1: missing data length')
                    datasize = _bord(self[i])
                    i += 1

                elif opcode == OP_PUSHDATA2:
                    pushdata_type = 'PUSHDATA2'
                    if i + 1 >= len(self):
                        raise CScriptInvalidError(
                            'PUSHDATA2: missing data length')
                    datasize = _bord(self[i]) + (_bord(self[i+1]) << 8)
                    i += 2

                elif opcode == OP_PUSHDATA4:
                    pushdata_type = 'PUSHDATA4'
                    if i + 3 >= len(self):
                        raise CScriptInvalidError(
                            'PUSHDATA4: missing data length')
                    datasize = _bord(self[i]) + (_bord(self[i+1]) << 8) + \
                        (_bord(self[i+2]) << 16) + (_bord(self[i+3]) << 24)
                    i += 4

                else:
                    assert False  # shouldn't happen

                data = bytes(self[i:i+datasize])

                # Check for truncation
                if len(data) < datasize:
                    raise CScriptTruncatedPushDataError(
                        '%s: truncated data' % pushdata_type, data)

                i += datasize

                yield (opcode, data, sop_idx)

    def __iter__(self):
        """'Cooked' iteration

        Returns either a CScriptOP instance, an integer, or bytes, as
        appropriate.

        See raw_iter() if you need to distinguish the different possible
        PUSHDATA encodings.
        """
        for (opcode, data, sop_idx) in self.raw_iter():
            if opcode == 0:
                yield 0
            elif data is not None:
                yield data
            else:
                opcode = CScriptOp(opcode)

                if opcode.is_small_int():
                    yield opcode.decode_op_n()
                else:
                    yield CScriptOp(opcode)

    def __repr__(self):
        # For Python3 compatibility add b before strings so testcases don't
        # need to change
        def _repr(o):
            if isinstance(o, bytes):
                return "x('%s')" % evrmore.core.b2x(o)
            else:
                return repr(o)

        ops = []
        i = iter(self)
        while True:
            op = None
            try:
                op = _repr(next(i))
            except CScriptTruncatedPushDataError as err:
                op = '%s...<ERROR: %s>' % (_repr(err.data), err)
                break
            except CScriptInvalidError as err:
                op = '<ERROR: %s>' % err
                break
            except StopIteration:
                break
            finally:
                if op is not None:
                    ops.append(op)

        return "CScript([%s])" % ', '.join(ops)

    def is_p2sh(self):
        """Test if the script is a p2sh scriptPubKey

        Note that this test is consensus-critical.
        """
        return (len(self) == 23 and
                _bord(self[0]) == OP_HASH160 and
                _bord(self[1]) == 0x14 and
                _bord(self[22]) == OP_EQUAL)

    def is_witness_scriptpubkey(self):
        """Returns true if this is a scriptpubkey signaling segregated witness data.

        A witness program is any valid CScript that consists of a 1-byte push opcode
        followed by a data push between 2 and 40 bytes.
        """
        size = len(self)
        if size < 4 or size > 42:
            return False

        head = struct.unpack('<bb', self[:2])
        if not CScriptOp(head[0]).is_small_int():
            return False

        if head[1] + 2 != size:
            return False

        return True

    def witness_version(self):
        """Returns the witness version on [0,16]. """
        return next(iter(self))

    def is_witness_v0_keyhash(self):
        """Returns true if this is a scriptpubkey for V0 P2WPKH. """
        return len(self) == 22 and self[0:2] == b'\x00\x14'

    def is_witness_v0_nested_keyhash(self):
        """Returns true if this is a scriptSig for V0 P2WPKH embedded in P2SH. """
        return len(self) == 23 and self[0:3] == b'\x16\x00\x14'

    def is_witness_v0_scripthash(self):
        """Returns true if this is a scriptpubkey for V0 P2WSH. """
        return len(self) == 34 and self[0:2] == b'\x00\x20'

    def is_witness_v0_nested_scripthash(self):
        """Returns true if this is a scriptSig for V0 P2WSH embedded in P2SH. """
        return len(self) == 35 and self[0:3] == b'\x22\x00\x20'

    def is_push_only(self):
        """Test if the script only contains pushdata ops

        Note that this test is consensus-critical.

        Scripts that contain invalid pushdata ops return False, matching the
        behavior in Evrmore Core.
        """
        try:
            for (op, op_data, idx) in self.raw_iter():
                # Note how OP_RESERVED is considered a pushdata op.
                if op > OP_16:
                    return False

        except CScriptInvalidError:
            return False
        return True

    def has_canonical_pushes(self):
        """Test if script only uses canonical pushes

        Not yet consensus critical; may be in the future.
        """
        try:
            for (op, data, idx) in self.raw_iter():
                if op > OP_16:
                    continue

                elif op < OP_PUSHDATA1 and op > OP_0 and len(data) == 1 and _bord(data[0]) <= 16:
                    # Could have used an OP_n code, rather than a 1-byte push.
                    return False

                elif op == OP_PUSHDATA1 and len(data) < OP_PUSHDATA1:
                    # Could have used a normal n-byte push, rather than OP_PUSHDATA1.
                    return False

                elif op == OP_PUSHDATA2 and len(data) <= 0xFF:
                    # Could have used a OP_PUSHDATA1.
                    return False

                elif op == OP_PUSHDATA4 and len(data) <= 0xFFFF:
                    # Could have used a OP_PUSHDATA2.
                    return False

        except CScriptInvalidError:  # Invalid pushdata
            return False
        return True

    def is_unspendable(self):
        """Test if the script is provably unspendable"""
        return (len(self) > 0 and
                _bord(self[0]) == OP_RETURN)

    def is_valid(self):
        """Return True if the script is valid, False otherwise

        The script is valid if all PUSHDATA's are valid; invalid opcodes do not
        make is_valid() return False.
        """
        try:
            list(self)
        except CScriptInvalidError:
            return False
        return True

    def to_p2sh_scriptPubKey(self, checksize=True):
        """Create P2SH scriptPubKey from this redeemScript

        That is, create the P2SH scriptPubKey that requires this script as a
        redeemScript to spend.

        checksize - Check if the redeemScript is larger than the 520-byte max
        pushdata limit; raise ValueError if limit exceeded.

        Since a >520-byte PUSHDATA makes EvalScript() fail, it's not actually
        possible to redeem P2SH outputs with redeem scripts >520 bytes.
        """
        if checksize and len(self) > MAX_SCRIPT_ELEMENT_SIZE:
            raise ValueError(
                "redeemScript exceeds max allowed size; P2SH output would be unspendable")
        return CScript([OP_HASH160, evrmore.core.Hash160(self), OP_EQUAL])

    def GetSigOpCount(self, fAccurate):
        """Get the SigOp count.

        fAccurate - Accurately count CHECKMULTISIG, see BIP16 for details.

        Note that this is consensus-critical.
        """
        n = 0
        lastOpcode = OP_INVALIDOPCODE
        for (opcode, data, sop_idx) in self.raw_iter():
            if opcode in (OP_CHECKSIG, OP_CHECKSIGVERIFY):
                n += 1
            elif opcode in (OP_CHECKMULTISIG, OP_CHECKMULTISIGVERIFY):
                if fAccurate and (OP_1 <= lastOpcode <= OP_16):
                    n += opcode.decode_op_n()
                else:
                    n += 20
            lastOpcode = opcode
        return n


class CScriptWitness(ImmutableSerializable):
    """An encoding of the data elements on the initial stack for (segregated
        witness)
    """
    __slots__ = ['stack']

    def __init__(self, stack=()):
        object.__setattr__(self, 'stack', stack)

    def __len__(self):
        return len(self.stack)

    def __iter__(self):
        return iter(self.stack)

    def __repr__(self):
        return 'CScriptWitness(' + ','.join("x('%s')" % evrmore.core.b2x(s) for s in self.stack) + ')'

    def is_null(self):
        return len(self.stack) == 0

    @classmethod
    def stream_deserialize(cls, f):
        n = VarIntSerializer.stream_deserialize(f)
        stack = tuple(BytesSerializer.stream_deserialize(f) for i in range(n))
        return cls(stack)

    def stream_serialize(self, f):
        VarIntSerializer.stream_serialize(len(self.stack), f)
        for s in self.stack:
            BytesSerializer.stream_serialize(s, f)


SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
SIGHASH_ANYONECANPAY = 0x80


def FindAndDelete(script, sig):
    """Consensus critical, see FindAndDelete() in Satoshi codebase"""
    r = b''
    last_sop_idx = sop_idx = 0
    skip = True
    for (opcode, data, sop_idx) in script.raw_iter():
        if not skip:
            r += script[last_sop_idx:sop_idx]
        last_sop_idx = sop_idx
        if script[sop_idx:sop_idx + len(sig)] == sig:
            skip = True
        else:
            skip = False
    if not skip:
        r += script[last_sop_idx:]
    return CScript(r)


def IsLowDERSignature(sig):
    """
    Loosely correlates with IsLowDERSignature() from script/interpreter.cpp
    Verifies that the S value in a DER signature is the lowest possible value.
    Used by BIP62 malleability fixes.
    """
    length_r = sig[3]
    if isinstance(length_r, str):
        length_r = int(struct.unpack('B', length_r)[0])
    length_s = sig[5 + length_r]
    if isinstance(length_s, str):
        length_s = int(struct.unpack('B', length_s)[0])
    s_val = list(struct.unpack(str(length_s) + 'B',
                 sig[6 + length_r:6 + length_r + length_s]))

    # If the S value is above the order of the curve divided by two, its
    # complement modulo the order could have been used instead, which is
    # one byte shorter when encoded correctly.
    max_mod_half_order = [
        0x7f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0x5d, 0x57, 0x6e, 0x73, 0x57, 0xa4, 0x50, 0x1d,
        0xdf, 0xe9, 0x2f, 0x46, 0x68, 0x1b, 0x20, 0xa0]

    return CompareBigEndian(s_val, [0]) > 0 and \
        CompareBigEndian(s_val, max_mod_half_order) <= 0


def CompareBigEndian(c1, c2):
    """
    Loosely matches CompareBigEndian() from eccryptoverify.cpp
    Compares two arrays of bytes, and returns a negative value if the first is
    less than the second, 0 if they're equal, and a positive value if the
    first is greater than the second.
    """
    c1 = list(c1)
    c2 = list(c2)

    # Adjust starting positions until remaining lengths of the two arrays match
    while len(c1) > len(c2):
        if c1.pop(0) > 0:
            return 1
    while len(c2) > len(c1):
        if c2.pop(0) > 0:
            return -1

    while len(c1) > 0:
        diff = c1.pop(0) - c2.pop(0)
        if diff != 0:
            return diff

    return 0


def RawSignatureHash(script, txTo, inIdx, hashtype):
    """Consensus-correct SignatureHash

    Returns (hash, err) to precisely match the consensus-critical behavior of
    the SIGHASH_SINGLE bug. (inIdx is *not* checked for validity)

    If you're just writing wallet software you probably want SignatureHash()
    instead.
    """
    HASH_ONE = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    if inIdx >= len(txTo.vin):
        return (HASH_ONE, "inIdx %d out of range (%d)" % (inIdx, len(txTo.vin)))
    txtmp = evrmore.core.CMutableTransaction.from_tx(txTo)

    for txin in txtmp.vin:
        txin.scriptSig = b''
    txtmp.vin[inIdx].scriptSig = FindAndDelete(
        script, CScript([OP_CODESEPARATOR]))

    if (hashtype & 0x1f) == SIGHASH_NONE:
        txtmp.vout = []

        for i in range(len(txtmp.vin)):
            if i != inIdx:
                txtmp.vin[i].nSequence = 0

    elif (hashtype & 0x1f) == SIGHASH_SINGLE:
        outIdx = inIdx
        if outIdx >= len(txtmp.vout):
            return (HASH_ONE, "outIdx %d out of range (%d)" % (outIdx, len(txtmp.vout)))

        tmp = txtmp.vout[outIdx]
        txtmp.vout = []
        for i in range(outIdx):
            txtmp.vout.append(evrmore.core.CTxOut())
        txtmp.vout.append(tmp)

        for i in range(len(txtmp.vin)):
            if i != inIdx:
                txtmp.vin[i].nSequence = 0

    if hashtype & SIGHASH_ANYONECANPAY:
        tmp = txtmp.vin[inIdx]
        txtmp.vin = []
        txtmp.vin.append(tmp)

    txtmp.wit = evrmore.core.CTxWitness()
    s = txtmp.serialize()
    s += struct.pack(b"<i", hashtype)

    hash = evrmore.core.Hash(s)

    return (hash, None)


SIGVERSION_BASE = 0
SIGVERSION_WITNESS_V0 = 1


def SignatureHash(script, txTo, inIdx, hashtype, amount=None, sigversion=SIGVERSION_BASE):
    """Calculate a signature hash

    'Cooked' version that checks if inIdx is out of bounds - this is *not*
    consensus-correct behavior, but is what you probably want for general
    wallet use.
    """

    if sigversion == SIGVERSION_WITNESS_V0:
        hashPrevouts = b'\x00'*32
        hashSequence = b'\x00'*32
        hashOutputs = b'\x00'*32

        if not (hashtype & SIGHASH_ANYONECANPAY):
            serialize_prevouts = bytes()
            for i in txTo.vin:
                serialize_prevouts += i.prevout.serialize()
            hashPrevouts = evrmore.core.Hash(serialize_prevouts)

        if (not (hashtype & SIGHASH_ANYONECANPAY) and (hashtype & 0x1f) != SIGHASH_SINGLE and (hashtype & 0x1f) != SIGHASH_NONE):
            serialize_sequence = bytes()
            for i in txTo.vin:
                serialize_sequence += struct.pack("<I", i.nSequence)
            hashSequence = evrmore.core.Hash(serialize_sequence)

        if ((hashtype & 0x1f) != SIGHASH_SINGLE and (hashtype & 0x1f) != SIGHASH_NONE):
            serialize_outputs = bytes()
            for o in txTo.vout:
                serialize_outputs += o.serialize()
            hashOutputs = evrmore.core.Hash(serialize_outputs)
        elif ((hashtype & 0x1f) == SIGHASH_SINGLE and inIdx < len(txTo.vout)):
            serialize_outputs = txTo.vout[inIdx].serialize()
            hashOutputs = evrmore.core.Hash(serialize_outputs)

        f = _BytesIO()
        f.write(struct.pack("<i", txTo.nVersion))
        f.write(hashPrevouts)
        f.write(hashSequence)
        txTo.vin[inIdx].prevout.stream_serialize(f)
        BytesSerializer.stream_serialize(script, f)
        f.write(struct.pack("<q", amount))
        f.write(struct.pack("<I", txTo.vin[inIdx].nSequence))
        f.write(hashOutputs)
        f.write(struct.pack("<i", txTo.nLockTime))
        f.write(struct.pack("<i", hashtype))

        return evrmore.core.Hash(f.getvalue())

    assert not script.is_witness_scriptpubkey()

    (h, err) = RawSignatureHash(script, txTo, inIdx, hashtype)
    if err is not None:
        raise ValueError(err)
    return h

def CreateMultisigRedeemScript(required, pubkeys):
    """
    Create a redeem script for a m-of-n multisig transaction.
    
    :param required: Number of required signatures (m in m-of-n)
    :param pubkeys: List of public keys (n in m-of-n)
    :return: CScript object representing the redeem script
    """
    if not (0 <= required <= len(pubkeys) <= 16):
        raise ValueError("Invalid number of required signatures or public keys")
    
    script = CScript([required])  # m
    for pubkey in pubkeys:
        script += pubkey  # Add each public key
    script += len(pubkeys)  # n OP_CHECKMULTISIG
    script += OP_CHECKMULTISIG
    return script

__all__ = (
    'MAX_SCRIPT_SIZE',
    'MAX_SCRIPT_ELEMENT_SIZE',
    'MAX_SCRIPT_OPCODES',
    'OPCODE_NAMES',
    'CScriptOp',

    # every opcode
    'OP_0',
    'OP_FALSE',
    'OP_PUSHDATA1',
    'OP_PUSHDATA2',
    'OP_PUSHDATA4',
    'OP_1NEGATE',
    'OP_RESERVED',
    'OP_1',
    'OP_TRUE',
    'OP_2',
    'OP_3',
    'OP_4',
    'OP_5',
    'OP_6',
    'OP_7',
    'OP_8',
    'OP_9',
    'OP_10',
    'OP_11',
    'OP_12',
    'OP_13',
    'OP_14',
    'OP_15',
    'OP_16',
    'OP_NOP',
    'OP_VER',
    'OP_IF',
    'OP_NOTIF',
    'OP_VERIF',
    'OP_VERNOTIF',
    'OP_ELSE',
    'OP_ENDIF',
    'OP_VERIFY',
    'OP_RETURN',
    'OP_TOALTSTACK',
    'OP_FROMALTSTACK',
    'OP_2DROP',
    'OP_2DUP',
    'OP_3DUP',
    'OP_2OVER',
    'OP_2ROT',
    'OP_2SWAP',
    'OP_IFDUP',
    'OP_DEPTH',
    'OP_DROP',
    'OP_DUP',
    'OP_NIP',
    'OP_OVER',
    'OP_PICK',
    'OP_ROLL',
    'OP_ROT',
    'OP_SWAP',
    'OP_TUCK',
    'OP_CAT',
    'OP_SUBSTR',
    'OP_LEFT',
    'OP_RIGHT',
    'OP_SIZE',
    'OP_INVERT',
    'OP_AND',
    'OP_OR',
    'OP_XOR',
    'OP_EQUAL',
    'OP_EQUALVERIFY',
    'OP_RESERVED1',
    'OP_RESERVED2',
    'OP_1ADD',
    'OP_1SUB',
    'OP_2MUL',
    'OP_2DIV',
    'OP_NEGATE',
    'OP_ABS',
    'OP_NOT',
    'OP_0NOTEQUAL',
    'OP_ADD',
    'OP_SUB',
    'OP_MUL',
    'OP_DIV',
    'OP_MOD',
    'OP_LSHIFT',
    'OP_RSHIFT',
    'OP_BOOLAND',
    'OP_BOOLOR',
    'OP_NUMEQUAL',
    'OP_NUMEQUALVERIFY',
    'OP_NUMNOTEQUAL',
    'OP_LESSTHAN',
    'OP_GREATERTHAN',
    'OP_LESSTHANOREQUAL',
    'OP_GREATERTHANOREQUAL',
    'OP_MIN',
    'OP_MAX',
    'OP_WITHIN',
    'OP_RIPEMD160',
    'OP_SHA1',
    'OP_SHA256',
    'OP_HASH160',
    'OP_HASH256',
    'OP_CODESEPARATOR',
    'OP_CHECKSIG',
    'OP_CHECKSIGVERIFY',
    'OP_CHECKMULTISIG',
    'OP_CHECKMULTISIGVERIFY',
    'OP_NOP1',
    'OP_NOP2',
    'OP_CHECKLOCKTIMEVERIFY',
    'OP_NOP3',
    'OP_CHECKSEQUENCEVERIFY',
    'OP_NOP4',
    'OP_NOP5',
    'OP_NOP6',
    'OP_NOP7',
    'OP_NOP8',
    'OP_NOP9',
    'OP_NOP10',
    'OP_SMALLINTEGER',
    'OP_PUBKEYS',
    'OP_PUBKEYHASH',
    'OP_PUBKEY',
    'OP_INVALIDOPCODE',

    'OPCODES_BY_NAME',
    'DISABLED_OPCODES',
    'CScriptInvalidError',
    'CScriptTruncatedPushDataError',
    'CScript',
    'CScriptWitness',
    'SIGHASH_ALL',
    'SIGHASH_NONE',
    'SIGHASH_SINGLE',
    'SIGHASH_ANYONECANPAY',
    'FindAndDelete',
    'RawSignatureHash',
    'SignatureHash',
    'CreateMultisigRedeemScript',
    'IsLowDERSignature',

    'SIGVERSION_BASE',
    'SIGVERSION_WITNESS_V0',
)

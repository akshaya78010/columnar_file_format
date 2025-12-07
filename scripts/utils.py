# scripts/utils.py
import struct
import zlib
from io import BytesIO

MAGIC = b"SCOLFMT\x00"
VERSION = 1

TYPE_INT32 = 1
TYPE_FLOAT64 = 2
TYPE_STRING = 3

INT32_MISSING = -2147483648  # sentinel for missing ints

def pack_u8(x): return struct.pack("<B", x)
def pack_u16(x): return struct.pack("<H", x)
def pack_u64(x): return struct.pack("<Q", x)
def pack_i32(x): return struct.pack("<i", x)
def pack_f64(x): return struct.pack("<d", x)

def unpack_u8(b): return struct.unpack("<B", b)[0]
def unpack_u16(b): return struct.unpack("<H", b)[0]
def unpack_u64(b): return struct.unpack("<Q", b)[0]
def unpack_i32(b): return struct.unpack("<i", b)[0]
def unpack_f64(b): return struct.unpack("<d", b)[0]

def compress_bytes(b: bytes) -> bytes:
    return zlib.compress(b)

def decompress_bytes(b: bytes) -> bytes:
    return zlib.decompress(b)

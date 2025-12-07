import csv
from io import BytesIO
import argparse
import sys, os

# Make utils importable when running from CLI
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import *

def detect_type(values):
    is_int = True
    is_float = True
    for v in values:
        if v == "" or v is None:
            continue
        try:
            int(v)
        except:
            is_int = False
            try:
                float(v)
            except:
                is_float = False
        if not is_int and not is_float:
            return TYPE_STRING
    if is_int:
        return TYPE_INT32
    if is_float:
        return TYPE_FLOAT64
    return TYPE_STRING

def serialize_column(col_vals, col_type):
    num_rows = len(col_vals)

    if col_type == TYPE_INT32:
        buf = BytesIO()
        for v in col_vals:
            if v == "" or v is None:
                buf.write(pack_i32(INT32_MISSING))
            else:
                buf.write(pack_i32(int(v)))
        uncompressed = buf.getvalue()

    elif col_type == TYPE_FLOAT64:
        buf = BytesIO()
        for v in col_vals:
            if v == "" or v is None:
                buf.write(pack_f64(float("nan")))
            else:
                buf.write(pack_f64(float(v)))
        uncompressed = buf.getvalue()

    else:  # STRING
        concat = BytesIO()
        offsets = []
        offs = 0
        for v in col_vals:
            s = (v or "").encode("utf-8")
            offsets.append(offs)
            concat.write(s)
            offs += len(s)
        offsets.append(offs)

        buf = BytesIO()
        buf.write(pack_u64(num_rows))
        for off in offsets:
            buf.write(pack_u64(off))
        buf.write(concat.getvalue())
        uncompressed = buf.getvalue()

    compressed = compress_bytes(uncompressed)
    return uncompressed, compressed

def write_custom(csv_path, out_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        raise ValueError("CSV is empty")

    header = rows[0]
    data = rows[1:]
    num_rows = len(data)

    columns = [[] for _ in header]
    for row in data:
        for i in range(len(header)):
            columns[i].append(row[i] if i < len(row) else "")

    col_meta = []
    col_blocks = []

    for i, name in enumerate(header):
        vals = columns[i]
        t = detect_type(vals)
        uncompressed, compressed = serialize_column(vals, t)

        col_meta.append({
            "name": name,
            "type": t,
            "uncompressed_size": len(uncompressed),
            "compressed_size": len(compressed),
        })
        col_blocks.append(compressed)

    header_buf = BytesIO()
    header_buf.write(pack_u64(num_rows))
    header_buf.write(pack_u16(len(header)))

    for meta in col_meta:
        name_b = meta["name"].encode("utf-8")
        header_buf.write(pack_u16(len(name_b)))
        header_buf.write(name_b)
        header_buf.write(pack_u8(meta["type"]))
        header_buf.write(pack_u64(meta["uncompressed_size"]))
        header_buf.write(pack_u64(meta["compressed_size"]))
        header_buf.write(pack_u64(0))  # placeholder

    header_bytes = header_buf.getvalue()
    header_length = len(header_bytes)

    with open(out_path, "w+b") as out:
        out.write(MAGIC)
        out.write(pack_u8(VERSION))
        out.write(b"\x00" * 7)
        out.write(pack_u64(header_length))
        out.write(header_bytes)

        block_offsets = []
        current_offset = out.tell()

        for blob in col_blocks:
            block_offsets.append(current_offset)
            out.write(blob)
            current_offset += len(blob)

        header_start = 8 + 1 + 7 + 8
        out.seek(header_start)

        _num_rows = unpack_u64(out.read(8))
        _num_cols = unpack_u16(out.read(2))

        for i in range(_num_cols):
            name_len = unpack_u16(out.read(2))
            out.seek(name_len, 1)
            out.seek(1, 1)
            out.seek(16, 1)

            out.write(pack_u64(block_offsets[i]))

    print(f"[OK] Wrote {out_path} with {num_rows} rows and {len(header)} columns")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="input CSV file")
    ap.add_argument("out", help="output SCF file")
    args = ap.parse_args()
    write_custom(args.csv, args.out)

if __name__ == "__main__":
    main()

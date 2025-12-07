import csv
from io import BytesIO
import argparse
from scripts.utils import *

def read_header(f):
    f.seek(0)
    magic = f.read(8)
    if magic != MAGIC:
        raise ValueError("Invalid file format")

    version = unpack_u8(f.read(1))
    f.read(7)  # padding
    header_length = unpack_u64(f.read(8))

    header_bytes = f.read(header_length)
    buf = BytesIO(header_bytes)

    num_rows = unpack_u64(buf.read(8))
    num_cols = unpack_u16(buf.read(2))

    columns = []
    for _ in range(num_cols):
        name_len = unpack_u16(buf.read(2))
        name = buf.read(name_len).decode("utf-8")
        type_code = unpack_u8(buf.read(1))
        un_size = unpack_u64(buf.read(8))
        comp_size = unpack_u64(buf.read(8))
        offset = unpack_u64(buf.read(8))

        columns.append({
            "name": name,
            "type": type_code,
            "uncompressed_size": un_size,
            "compressed_size": comp_size,
            "offset": offset,
        })

    return {
        "num_rows": num_rows,
        "columns": columns
    }

def read_column(f, col):
    f.seek(col["offset"])
    comp = f.read(col["compressed_size"])
    raw = decompress_bytes(comp)

    t = col["type"]
    out = []
    buf = BytesIO(raw)

    if t == TYPE_INT32:
        for i in range(0, len(raw), 4):
            v = unpack_i32(raw[i:i+4])
            out.append("" if v == INT32_MISSING else str(v))

    elif t == TYPE_FLOAT64:
        for i in range(0, len(raw), 8):
            v = unpack_f64(raw[i:i+8])
            out.append("" if v != v else str(v))  # NaN check

    else:  # STRING
        num_strings = unpack_u64(buf.read(8))
        offsets = [unpack_u64(buf.read(8)) for _ in range(num_strings+1)]
        data = buf.read()
        for i in range(num_strings):
            s = data[offsets[i]:offsets[i+1]].decode("utf-8")
            out.append(s)

    return out

def full_read(f):
    header = read_header(f)
    cols = header["columns"]
    num_rows = header["num_rows"]

    table = []
    for col in cols:
        table.append(read_column(f, col))

    rows = []
    rows.append([c["name"] for c in cols])

    for r in range(num_rows):
        rows.append([table[c][r] for c in range(len(cols))])

    return rows

def selective_read(f, selected):
    header = read_header(f)
    cols = header["columns"]
    name_to_col = {c["name"]: c for c in cols}

    final_cols = []
    for key in selected:
        if key.isdigit():
            final_cols.append(cols[int(key)])
        else:
            final_cols.append(name_to_col[key])

    out_data = []
    out_data.append([c["name"] for c in final_cols])

    col_values = [read_column(f, c) for c in final_cols]

    for r in range(header["num_rows"]):
        out_data.append([col_values[c][r] for c in range(len(final_cols))])

    return out_data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scf", help="input custom file")
    ap.add_argument("csv", help="output CSV")
    ap.add_argument("-c", "--columns", nargs="*", help="column names or indices")
    args = ap.parse_args()

    with open(args.scf, "rb") as f:
        if args.columns:
            rows = selective_read(f, args.columns)
        else:
            rows = full_read(f)

    with open(args.csv, "w", newline="", encoding="utf-8") as out:
        csv.writer(out).writerows(rows)

    print(f"[OK] Wrote CSV -> {args.csv}")

if __name__ == "__main__":
    main()

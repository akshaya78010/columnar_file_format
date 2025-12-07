# Simple Columnar Format (SCF) Specification

## 1. Magic Header
SCOLFMT\0 (8 bytes)
version (1 byte)
padding (7 bytes, zero)

## 2. Header Length
uint64 header_length

## 3. Header Layout
uint64 num_rows
uint16 num_columns

Then repeated for each column:
uint16 name_length
<name_length> bytes (UTF-8 column name)
uint8 type_code (1=int32, 2=float64, 3=string)
uint64 uncompressed_size
uint64 compressed_size
uint64 block_file_offset

- `block_file_offset` is the absolute position in the file where the compressed column block begins.

---

## 4. Column Block (Uncompressed Payload)

### Type 1: INT32
num_rows * int32 (little-endian)
missing → INT32_MIN (-2147483648)

### Type 2: FLOAT64
num_rows * float64 (little-endian)
missing → NaN

### Type 3: STRING
uint64 num_rows
uint64 offsets[num_rows + 1]
concatenated UTF-8 bytes

Offsets point into the concatenated string region.

---

## 5. Compression  
Each column’s uncompressed block is compressed using:
zlib.compress()

---

## 6. File Layout
[MAGIC | VERSION | PADDING]
[HEADER_LENGTH]
[HEADER_BYTES]
[COLUMN_BLOCK_1]
[COLUMN_BLOCK_2]

---

## 7. Selective Reading
To read only specific columns:

1. Read the header.
2. Locate the column’s `block_file_offset`.
3. Seek directly to that offset.
4. Read `compressed_size` bytes.
5. Decompress + parse.

This avoids scanning the entire file.



# Columnar File Format (SCF)

A simple custom columnar storage format built for fast selective column reads, similar to a lightweight Parquet.  
This project converts CSV → SCF (columnar, compressed), and SCF → CSV.

---

## 📁 Repository structure

columnar_file_format/
scripts/
csv_to_custom.py
custom_to_csv.py
utils.py
tests/
test_roundtrip.py
test_selective_read.py
examples/
sample.csv
README.md
SPEC.md

---

---

## 🚀 How to run

### Convert CSV → SCF

python scripts/csv_to_custom.py examples/sample.csv examples/sample.scf

### Convert SCF → CSV (full read)

python scripts/custom_to_csv.py examples/sample.scf examples/out.csv

### Selective column read

python scripts/custom_to_csv.py examples/sample.scf examples/age_only.csv -c age

---

## 🧪 Tests

python -m pytest -q

Expected:
2 passed

---

## 📘 What this project demonstrates

- Understanding of binary file format design
- Compression (zlib)
- Columnar storage layout
- Patchable metadata header with offsets
- Fast selective column reads
- Reversible CSV ↔ SCF transformation

---

## 🧩 Features

✔ Columnar storage  
✔ Zlib compression per column  
✔ Offset-based direct access  
✔ String offsets table  
✔ Int/Float/String type detection  
✔ Missing value encodings  
✔ CLI tools  
✔ Full test suite

---

## 👨‍💻 Author

23A91A05G8

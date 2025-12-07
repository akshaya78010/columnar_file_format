import csv
from scripts.csv_to_custom import write_custom
from scripts.custom_to_csv import full_read
from io import StringIO
import os

def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.reader(f))

def test_roundtrip(tmp_path):
    csv_path = tmp_path / "input.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("id,age,name\n")
        f.write("1,30,Alice\n")
        f.write("2,40,Bob\n")

    custom_path = tmp_path / "out.scf"
    write_custom(str(csv_path), str(custom_path))

    with open(custom_path, "rb") as f:
        rows = full_read(f)

    expected = read_csv(csv_path)

    assert rows == expected

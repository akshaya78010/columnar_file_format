from scripts.csv_to_custom import write_custom
from scripts.custom_to_csv import selective_read

def test_selective_read(tmp_path):
    csv_path = tmp_path / "input.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("id,age,name\n")
        f.write("1,30,Alice\n")
        f.write("2,40,Bob\n")
        f.write("3,50,Charlie\n")

    custom_path = tmp_path / "out.scf"
    write_custom(str(csv_path), str(custom_path))

    with open(custom_path, "rb") as f:
        rows = selective_read(f, ["age"])

    assert rows == [
        ["age"],
        ["30"],
        ["40"],
        ["50"]
    ]

from pathlib import Path
import duckdb

IN_DIR = Path("outputs/final")
OUT_DIR = Path("outputs/final/csv")
OUT_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

for p in IN_DIR.glob("*.parquet"):
    out_csv = OUT_DIR / (p.stem + ".csv")
    con.execute(
        f"COPY (SELECT * FROM read_parquet('{p.as_posix()}')) "
        f"TO '{out_csv.as_posix()}' (HEADER, DELIMITER ',');"
    )
    print("Wrote", out_csv)

print("Done.")

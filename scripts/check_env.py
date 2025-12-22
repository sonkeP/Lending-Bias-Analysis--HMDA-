import sys
import os
try:
    import pandas as pd
except Exception as e:
    print("IMPORT_ERROR", repr(e))
    sys.exit(1)
print("PANDAS", pd.__version__)
path = os.path.join(os.path.dirname(__file__), "..", "data", "analytics", "hmda", "fact_loans_2023.parquet")
path = os.path.normpath(path)
print("PATH", path)
print("EXISTS", os.path.exists(path))
try:
    df = pd.read_parquet(path)
    print("READ_OK", df.shape)
except Exception as e:
    print("READ_ERROR", repr(e))
    sys.exit(2)
print("SUCCESS")

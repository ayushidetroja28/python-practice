from typing import Dict, Any
import pandas as pd
import numpy as np

NUMERIC_AGG = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]

def _col_type(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    return "categorical"

def analyze_dataframe(df: pd.DataFrame, top_n: int = 5) -> Dict[str, Any]:
    """Return a dictionary of statistics for the DataFrame.


    For each column return:
    - dtype (inferred)
    - missing (count)
    - unique (count)
    - sample_values (up to 5 non-null samples)
    - if numeric: summary stats (count, mean, std, percentiles)
    - if categorical: top N values with counts
    """
    print("----------",df)
    result = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "columns_stats": {},
    }
    print("-----result------",result)

    for col in df.columns:
        ser = df[col]
        print("------ser------", ser)
        stats = {
            "dtype": str(ser.dtype),
            "inferred_type": _col_type(ser),
            "missing": int(ser.isna().sum()),
            "missing_pct": float(ser.isna().mean()) if len(ser) > 0 else 0.0,
            "unique": int(ser.nunique(dropna=True)),
            "sample_values": ser.dropna().head(5).tolist(),
        }

        print("-----stats------",stats)
        if pd.api.types.is_numeric_dtype(ser):
            descr = ser.describe(percentiles=[0.25, 0.5, 0.75]).to_dict()
            # normalize keys
            numeric = {
                "count": int(descr.get("count", 0)),
                "mean": descr.get("mean", None),
                "std": descr.get("std", None),
                "min": descr.get("min", None),
                "25%": descr.get("25%", None),
                "50%": descr.get("50%", None),
                "75%": descr.get("75%", None),
                "max": descr.get("max", None),
            }
            stats["numeric_summary"] = numeric
        else:
            top = (
                ser.dropna()
                .astype(str)
                .value_counts()
                .head(top_n)
                .to_dict()
            )
            stats["top_values"] = top


        result["columns_stats"][col] = stats


    return result

def analyze_csv(path_or_buffer, **kwargs) -> Dict[str, Any]:
    print("----path_or_buffer-------",path_or_buffer)
    print("----kwargs-------",kwargs)
    """Load CSV with pandas and analyze. Accepts path or file-like object."""
    # sensible defaults; allow overrides
    read_csv_kwargs = {
        "dtype": None,
        "parse_dates": True,
        "infer_datetime_format": True,
        **kwargs,
    }
    df = pd.read_csv(path_or_buffer, **read_csv_kwargs)
    return analyze_dataframe(df)
        

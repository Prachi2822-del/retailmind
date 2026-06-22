"""
validators.py
Five validation rules applied before any data enters the database.
Each function takes a DataFrame, checks it, and returns the clean version.
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationReport:
    table_name: str
    total_rows: int = 0
    passed_rows: int = 0
    failed_rows: int = 0
    issues: List[str] = field(default_factory=list)

    def add_issue(self, message: str):
        self.issues.append(message)

    @property
    def pass_rate(self):
        if self.total_rows == 0:
            return 0
        return round(self.passed_rows / self.total_rows * 100, 1)


def check_nulls(df, required_cols, report):
    """Rule 1 — Drop rows where required columns are missing."""
    before = len(df)
    df = df.dropna(subset=required_cols)
    dropped = before - len(df)
    if dropped:
        report.add_issue(
            f"NULL check: dropped {dropped} rows "
            f"with nulls in {required_cols}"
        )
    return df


def check_types(df, type_map, report):
    """Rule 2 — Cast columns to correct types, drop rows that fail."""
    df = df.copy()
    bad = pd.Series([False] * len(df), index=df.index)

    for col, dtype in type_map.items():
        if col not in df.columns:
            continue
        if dtype in (float, int):
            coerced = pd.to_numeric(df[col], errors="coerce")
            mask = coerced.isna() & df[col].notna()
            if mask.any():
                report.add_issue(
                    f"TYPE check: {mask.sum()} rows "
                    f"have invalid {col} (expected {dtype.__name__})"
                )
            bad = bad | mask
            df[col] = coerced

    return df[~bad]


def check_ranges(df, range_map, report):
    """Rule 3 — Drop rows where numeric values are out of range."""
    df = df.copy()
    bad = pd.Series([False] * len(df), index=df.index)

    for col, (min_val, max_val) in range_map.items():
        if col not in df.columns:
            continue
        mask = pd.Series([False] * len(df), index=df.index)
        if min_val is not None:
            mask = mask | (df[col] < min_val)
        if max_val is not None:
            mask = mask | (df[col] > max_val)
        if mask.any():
            report.add_issue(
                f"RANGE check: {mask.sum()} rows have "
                f"{col} outside [{min_val}, {max_val}]"
            )
        bad = bad | mask

    return df[~bad]


def check_duplicates(df, key_cols, report):
    """Rule 4 — Remove duplicate rows based on key columns."""
    before = len(df)
    df = df.drop_duplicates(subset=key_cols, keep="first")
    dupes = before - len(df)
    if dupes:
        report.add_issue(
            f"DUPLICATE check: removed {dupes} "
            f"duplicate rows on {key_cols}"
        )
    return df


def check_referential_integrity(df, fk_col, valid_ids, report, label=""):
    """Rule 5 — Drop rows whose foreign key doesn't exist in reference table."""
    mask = ~df[fk_col].isin(valid_ids)
    dropped = mask.sum()
    if dropped:
        report.add_issue(
            f"REF INTEGRITY {label}: {dropped} rows "
            f"have unknown {fk_col}"
        )
    return df[~mask]
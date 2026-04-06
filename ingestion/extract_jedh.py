import os
import wbgapi as wb
import pandas as pd
from datetime import datetime
from spark_session import get_spark_session

wb.db = 2

JEDH_SERIES = [
    "DT.DOD.DECT.CD",
    "DT.DOD.DLXF.CD",
    "DT.DOD.DPNG.CD",
    "DT.DOD.MIBR.CD",
    "DT.DOD.DPPG.CD",
    "DT.DOD.DIMF.CD",
    "DT.DOD.PVLX.CD",
    "DT.DOD.MWBG.CD",
    "DT.DOD.MIDA.CD",
]

GCS_BUCKET = os.environ["GCS_BUCKET"]
RUN_DATE = datetime.utcnow().strftime("%Y-%m-%d")


def extract_jedh():
    print("Extracting IDS series from World Bank API source 2...")

    records = []
    for series in JEDH_SERIES:
        print(f"  Fetching: {series}")
        try:
            df = wb.data.DataFrame(
                series,
                time=range(1998, 2026),
                labels=True,
                numericTimeKeys=True,
            )
            df = df.reset_index()
            df["series_code"] = series
            df["extracted_at"] = RUN_DATE
            records.append(df)
        except Exception as e:
            print(f"  Warning: could not fetch {series} — {e}")
            continue

    if not records:
        raise RuntimeError("No IDS data fetched — aborting.")

    combined = pd.concat(records, ignore_index=True)

    combined.columns = [
        f"year_{col}" if str(col).isdigit() else col
        for col in combined.columns
    ]

    print(f"Total rows fetched: {len(combined)}")
    print(f"Columns: {list(combined.columns)}")
    return combined


def load_to_gcs(df: pd.DataFrame):
    spark = get_spark_session("jedh-ingestion")
    sdf = spark.createDataFrame(df.astype(str))

    output_path = f"gs://{GCS_BUCKET}/raw/jedh/extracted_date={RUN_DATE}/"
    print(f"Writing to {output_path}")

    sdf.write.mode("overwrite").parquet(output_path)
    print("JEDH data written to GCS successfully.")
    spark.stop()


if __name__ == "__main__":
    df = extract_jedh()
    load_to_gcs(df)

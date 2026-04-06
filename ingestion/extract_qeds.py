import os
import io
import re
import requests
import pandas as pd
from datetime import datetime
from google.cloud import storage


GCS_BUCKET = os.environ["GCS_BUCKET"]
RUN_DATE = datetime.utcnow().strftime("%Y-%m-%d")

QEDS_EXCEL_URLS = {
    "sdds_table1_net_ext_debt": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-1-5-2025Q2.xlsx",
    "sdds_table3_debt_service": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-3-2025Q2.xlsx",
    "sdds_table3_2_by_instrument": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-3-2-2025Q2.xlsx",
    "sdds_table2_1_foreign_currency": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-2-1-2025Q2.xlsx",
    "sdds_table1_6_reconciliation": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-1-6-2025Q2.xlsx",
}


def clean_column_name(col):
    col = str(col)
    col = re.sub(r'\s*\[.*?\]', '', col)
    col = col.strip()
    col = re.sub(r'[^a-zA-Z0-9_]', '_', col)
    col = re.sub(r'_+', '_', col)
    col = col.strip('_')
    if col and col[0].isdigit():
        col = 'q_' + col
    if not col:
        col = 'unknown'
    return col.lower()


def extract_qeds():
    print("Downloading QEDS SDDS Excel files from World Bank...")
    records = []

    for table_name, url in QEDS_EXCEL_URLS.items():
        print(f"  Downloading: {table_name}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            sheets = pd.read_excel(io.BytesIO(response.content), sheet_name=None)
            for sheet_name, sheet_df in sheets.items():
                sheet_df["source_table"] = table_name
                sheet_df["sheet_name"] = sheet_name
                sheet_df["extracted_at"] = RUN_DATE
                sheet_df.columns = [clean_column_name(c) for c in sheet_df.columns]
                seen = {}
                new_cols = []
                for c in sheet_df.columns:
                    if c in seen:
                        seen[c] += 1
                        new_cols.append(f"{c}_{seen[c]}")
                    else:
                        seen[c] = 0
                        new_cols.append(c)
                sheet_df.columns = new_cols
                records.append(sheet_df.astype(str))
            print(f"    OK — {len(sheets)} sheet(s) loaded")
        except Exception as e:
            print(f"  Warning: could not download {table_name} — {e}")
            continue

    if not records:
        raise RuntimeError("No QEDS data downloaded — aborting.")

    combined = pd.concat(records, ignore_index=True)
    print(f"Total rows fetched: {len(combined)}")
    return combined


def load_to_gcs(df: pd.DataFrame):
    output_path = f"raw/qeds/extracted_date={RUN_DATE}/qeds.parquet"
    print(f"Writing to gs://{GCS_BUCKET}/{output_path}")

    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(output_path)
    blob.upload_from_file(buffer, content_type="application/octet-stream")

    print("QEDS data written to GCS successfully.")


if __name__ == "__main__":
    df = extract_qeds()
    load_to_gcs(df)

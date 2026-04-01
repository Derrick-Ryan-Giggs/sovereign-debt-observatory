import os
import io
import requests
import pandas as pd
from datetime import datetime
from spark_session import get_spark_session


GCS_BUCKET = os.environ["GCS_BUCKET"]
RUN_DATE = datetime.utcnow().strftime("%Y-%m-%d")

QEDS_EXCEL_URLS = {
    "sdds_table1_gross_ext_debt_by_sector": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-1-5-2025Q2.xlsx",
    "sdds_table3_debt_service_schedule":     "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-3-2025Q2.xlsx",
    "sdds_table3_2_debt_service_by_instrument": "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-3-2-2025Q2.xlsx",
    "sdds_table2_1_foreign_currency_debt":   "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-2-1-2025Q2.xlsx",
    "sdds_table1_6_reconciliation":          "https://thedocs.worldbank.org/en/doc/6e72b0ded996306fa01f5db7a0c38b19-0050052021/related/SDDS-Table-1-6-2025Q2.xlsx",
}


def extract_qeds():
    print("Downloading QEDS SDDS Excel files from World Bank...")
    records = []

    for table_name, url in QEDS_EXCEL_URLS.items():
        print(f"  Downloading: {table_name}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            df = pd.read_excel(io.BytesIO(response.content), sheet_name=None)
            for sheet_name, sheet_df in df.items():
                sheet_df["source_table"] = table_name
                sheet_df["sheet_name"] = sheet_name
                sheet_df["extracted_at"] = RUN_DATE
                records.append(sheet_df)
            print(f"    OK — {len(df)} sheet(s) loaded")
        except Exception as e:
            print(f"  Warning: could not download {table_name} — {e}")
            continue

    if not records:
        raise RuntimeError("No QEDS data downloaded — aborting.")

    combined = pd.concat(records, ignore_index=True)
    combined = combined.astype(str)
    print(f"Total rows fetched: {len(combined)}")
    return combined


def load_to_gcs(df: pd.DataFrame):
    spark = get_spark_session("qeds-ingestion")
    sdf = spark.createDataFrame(df)

    output_path = f"gs://{GCS_BUCKET}/raw/qeds/extracted_date={RUN_DATE}/"
    print(f"Writing to {output_path}")

    sdf.write.mode("overwrite").parquet(output_path)
    print("QEDS data written to GCS successfully.")
    spark.stop()


if __name__ == "__main__":
    df = extract_qeds()
    load_to_gcs(df)

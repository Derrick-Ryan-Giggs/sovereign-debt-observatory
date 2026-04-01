output "gcs_bucket_name" {
  description = "GCS data lake bucket name"
  value       = google_storage_bucket.data_lake.name
}

output "gcs_bucket_url" {
  description = "GCS data lake bucket URL"
  value       = google_storage_bucket.data_lake.url
}

output "bq_raw_dataset" {
  description = "BigQuery raw dataset ID"
  value       = google_bigquery_dataset.raw.dataset_id
}

output "bq_staging_dataset" {
  description = "BigQuery staging dataset ID"
  value       = google_bigquery_dataset.staging.dataset_id
}

output "bq_mart_dataset" {
  description = "BigQuery mart dataset ID"
  value       = google_bigquery_dataset.mart.dataset_id
}

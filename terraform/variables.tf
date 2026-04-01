variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "gcs_bucket_name" {
  description = "GCS data lake bucket name"
  type        = string
}

variable "credentials_file" {
  description = "Path to GCP service account key JSON"
  type        = string
}

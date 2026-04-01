terraform {
  required_version = ">= 1.3"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = var.region
}

resource "google_storage_bucket" "data_lake" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_object" "raw_prefix" {
  name    = "raw/.keep"
  bucket  = google_storage_bucket.data_lake.name
  content = "placeholder"
}

resource "google_storage_bucket_object" "staging_prefix" {
  name    = "staging/.keep"
  bucket  = google_storage_bucket.data_lake.name
  content = "placeholder"
}

resource "google_bigquery_dataset" "raw" {
  dataset_id    = "raw"
  friendly_name = "Raw dataset"
  description   = "Raw external tables pointing to GCS Parquet files"
  location      = var.location

  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "staging" {
  dataset_id    = "staging"
  friendly_name = "Staging dataset"
  description   = "Cleaned and cast tables, partitioned and clustered"
  location      = var.location

  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "mart" {
  dataset_id    = "mart"
  friendly_name = "Mart dataset"
  description   = "Analysis-ready aggregated models for Looker Studio"
  location      = var.location

  delete_contents_on_destroy = true
}

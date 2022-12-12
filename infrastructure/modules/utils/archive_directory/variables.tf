variable "source_dir" {
  description = "The directory to be archived"
  type        = string
}

variable "output_path" {
  description = "The path where the zip archive will be saved"
  type        = string
}

variable "bucket_name" {
  description = "The name of the S3 bucket where the object will be created"
  type        = string
}

variable "bucket_key" {
  description = "The key for the object that will be created in the S3 bucket"
  type        = string
}

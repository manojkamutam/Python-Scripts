import boto3
import os
import shutil
import time
import logging

# Configure logging
logging.basicConfig(filename="deploy_s3.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Variables (Update these as needed)
S3_BUCKET = "your-s3-bucket-name"
LOCAL_DIST_PATH = "./dist"  # Path to your local frontend build folder
BACKUP_PATH = "./backup"  # Where to store old files before deletion
CLOUDFRONT_DISTRIBUTION_ID = "your-cloudfront-distribution-id"

# AWS Clients
s3 = boto3.client("s3")
cloudfront = boto3.client("cloudfront")

def backup_existing_files():
    """Backup existing files from S3 before deployment."""
    logging.info("Starting backup of existing S3 files.")
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)
    
    objects = s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", [])
    for obj in objects:
        key = obj["Key"]
        backup_file_path = os.path.join(BACKUP_PATH, key.replace("/", "_"))
        s3.download_file(S3_BUCKET, key, backup_file_path)
    logging.info("Backup completed.")

def delete_existing_files():
    """Delete all files from S3 bucket before uploading new ones."""
    logging.info("Deleting existing files from S3 bucket.")
    objects = s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", [])
    
    if objects:
        s3.delete_objects(Bucket=S3_BUCKET, Delete={"Objects": [{"Key": obj["Key"]} for obj in objects]})
    logging.info("Old files removed from S3.")

def upload_new_files():
    """Upload new dist files to S3."""
    logging.info("Uploading new files to S3 bucket.")
    for root, _, files in os.walk(LOCAL_DIST_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = os.path.relpath(file_path, LOCAL_DIST_PATH)
            s3.upload_file(file_path, S3_BUCKET, s3_key, ExtraArgs={'ACL': 'public-read'})
    logging.info("New files uploaded successfully.")

def invalidate_cloudfront():
    """Invalidate CloudFront cache to reflect new changes."""
    logging.info("Creating CloudFront invalidation request.")
    invalidation = cloudfront.create_invalidation(
        DistributionId=CLOUDFRONT_DISTRIBUTION_ID,
        InvalidationBatch={
            "Paths": {"Quantity": 1, "Items": ["/*"]},
            "CallerReference": str(time.time())
        }
    )
    logging.info(f"CloudFront invalidation created: {invalidation['Invalidation']['Id']}")

def main():
    print("Starting frontend deployment...")
    backup_existing_files()
    delete_existing_files()
    upload_new_files()
    invalidate_cloudfront()
    print("Deployment completed successfully!")

if __name__ == "__main__":
    main()

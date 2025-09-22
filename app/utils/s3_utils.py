import os
import mimetypes
import boto3
from botocore.exceptions import ClientError


def _s3_client():
    return boto3.client(
        's3',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN')
    )


def build_property_media_key(property_id: int, media_id: int, file_name: str | None) -> str:
    # property/{propertyId}/{media_id}/{fileName}
    if not file_name:
        file_name = 'file'
    return f"property/{property_id}/{media_id}/{file_name}"


def upload_file_to_s3(*, file_path: str, key: str, content_type: str | None = None) -> tuple[str, int]:
    bucket = os.getenv('AWS_S3_BUCKET', 'zpc-app')
    client = _s3_client()

    if not content_type:
        guessed, _ = mimetypes.guess_type(file_path)
        content_type = guessed or 'application/octet-stream'

    extra_args = {'ContentType': content_type}

    # Compute size
    size_bytes = os.path.getsize(file_path)

    try:
        # Some buckets disallow ACLs; do not set ACL by default
        client.upload_file(Filename=file_path, Bucket=bucket, Key=key, ExtraArgs=extra_args)
    except ClientError as e:
        # Retry without ExtraArgs if ContentType causes issues
        try:
            client.upload_file(Filename=file_path, Bucket=bucket, Key=key)
        except Exception:
            raise e

    public_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    return public_url, size_bytes



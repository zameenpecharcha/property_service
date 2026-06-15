import os
import hashlib
import hmac
import mimetypes
import time
import urllib.parse

try:
    import boto3
    from botocore.exceptions import ClientError
    _BOTO3_AVAILABLE = True
except ImportError:
    _BOTO3_AVAILABLE = False


# ── helpers ───────────────────────────────────────────────────────────────────

def build_property_media_key(property_id: int, media_id: int, file_name: str | None) -> str:
    if not file_name:
        file_name = 'file'
    return f"property/{property_id}/{media_id}/{file_name}"


# ── Cloudinary upload (no SDK required) ───────────────────────────────────────

def _cloudinary_sign(params: dict, api_secret: str) -> str:
    """SHA-1 signature for Cloudinary signed uploads."""
    sorted_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hashlib.sha1((sorted_str + api_secret).encode()).hexdigest()


def upload_file_to_cloudinary(*, file_path: str, key: str,
                               content_type: str | None = None) -> tuple[str, int]:
    import urllib.request
    import json

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise RuntimeError("Missing CLOUDINARY_CLOUD_NAME / CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET")

    timestamp = str(int(time.time()))
    public_id = key.replace("/", "_").rsplit(".", 1)[0]

    sign_params = {"public_id": public_id, "timestamp": timestamp}
    signature = _cloudinary_sign(sign_params, api_secret)

    size_bytes = os.path.getsize(file_path)

    # multipart/form-data upload via urllib (no requests lib needed)
    boundary = "----ZPCBoundary" + timestamp
    with open(file_path, "rb") as f:
        file_data = f.read()

    if not content_type:
        guessed, _ = mimetypes.guess_type(file_path)
        content_type = guessed or "application/octet-stream"

    def _field(name, value):
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        ).encode()

    body = b""
    for k2, v2 in [("api_key", api_key), ("timestamp", timestamp),
                   ("public_id", public_id), ("signature", signature)]:
        body += _field(k2, v2)

    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + file_data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/auto/upload"
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())

    public_url = result.get("secure_url", result.get("url", ""))
    return public_url, size_bytes


# ── S3 upload ─────────────────────────────────────────────────────────────────

def _s3_client():
    if not _BOTO3_AVAILABLE:
        raise RuntimeError("boto3 is not installed — set STORAGE_BACKEND=cloudinary or pip install boto3")
    return boto3.client(
        's3',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    )


def upload_file_to_s3(*, file_path: str, key: str,
                      content_type: str | None = None) -> tuple[str, int]:
    bucket = os.getenv('AWS_S3_BUCKET', 'zpc-app')
    client = _s3_client()

    if not content_type:
        guessed, _ = mimetypes.guess_type(file_path)
        content_type = guessed or 'application/octet-stream'

    size_bytes = os.path.getsize(file_path)
    try:
        client.upload_file(Filename=file_path, Bucket=bucket, Key=key,
                           ExtraArgs={'ContentType': content_type})
    except ClientError as e:
        try:
            client.upload_file(Filename=file_path, Bucket=bucket, Key=key)
        except Exception:
            raise e

    public_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    return public_url, size_bytes


# ── unified entry point ───────────────────────────────────────────────────────

def upload_file(*, file_path: str, key: str, content_type: str | None = None) -> tuple[str, int]:
    """Upload a file using whichever backend is configured via STORAGE_BACKEND.
    Returns (public_url, size_bytes).

    Switch backends by changing STORAGE_BACKEND in .env:
      cloudinary  — current default (free tier)
      s3          — AWS S3 / Cloudflare R2 / DigitalOcean Spaces
    """
    backend = os.getenv("STORAGE_BACKEND", "cloudinary").lower()
    if backend == "s3":
        return upload_file_to_s3(file_path=file_path, key=key, content_type=content_type)
    return upload_file_to_cloudinary(file_path=file_path, key=key, content_type=content_type)




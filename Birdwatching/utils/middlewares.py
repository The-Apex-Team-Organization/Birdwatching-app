import hashlib
import boto3
from flask import current_app, redirect, request
from Birdwatching.utils.databases import get_ip_address


def is_blacklisted():
    ip_address = request.headers.get("X-Real-IP")
    if not ip_address:
        return
    ip_address_hashed = hashlib.sha256(bytes(ip_address.encode())).hexdigest()

    isExist = get_ip_address(ip_address_hashed)
    if isExist:
        return redirect(current_app.config["BLACKLIST_REDIRECT_URL"], 302)


def create_presigned_url(filename):
    try:
        s3_client = boto3.client(
            "s3",
            region_name=current_app.config["REGION"],
        )
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": current_app.config["BUCKET_NAME"],
                "Key": filename,
            },
            ExpiresIn=86400,  # 1 day
        )
    except Exception as e:
        print(e)
        return None
    return url


def upload_to_s3(file, filename):
    try:
        s3 = boto3.client(
            "s3",
            region_name=current_app.config["REGION"],
        )
        s3.upload_fileobj(file, current_app.config["BUCKET_NAME"], filename)
    except Exception as e:
        print(e)

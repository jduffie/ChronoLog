#!/usr/bin/env bash
set -euo pipefail

# --------- CONFIG ---------
REGION="us-east-1"
BUCKET="my-static-site-$(date +%s)"  # change if you want a fixed name
SITE_DIR="/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/home"
SRC_DIR="$SITE_DIR/resources"
INDEX_DOC="index.html"
ERROR_DOC="404.html"
# --------------------------

command -v aws >/dev/null || { echo "aws CLI not found"; exit 1; }

# Sanity checks
[ -d "$SRC_DIR" ] || { echo "Source dir not found: $SRC_DIR"; exit 1; }
[ -f "$SRC_DIR/$INDEX_DOC" ] || { echo "Missing $INDEX_DOC in $SRC_DIR"; exit 1; }
[ -f "$SRC_DIR/$ERROR_DOC" ] || ERROR_DOC="$INDEX_DOC"

echo "Creating bucket: $BUCKET in $REGION ..."
if [ "$REGION" = "us-east-1" ]; then
  aws s3api create-bucket --bucket "$BUCKET" >/dev/null
else
  aws s3api create-bucket --bucket "$BUCKET" \
    --create-bucket-configuration LocationConstraint="$REGION" \
    --region "$REGION" >/dev/null
fi

echo "Disabling Block Public Access (required for S3 website endpoints)..."
aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
'{"BlockPublicAcls":false,"IgnorePublicAcls":false,"BlockPublicPolicy":false,"RestrictPublicBuckets":false}' >/dev/null

echo "Enabling static website hosting..."
aws s3 website "s3://$BUCKET/" --index-document "$INDEX_DOC" --error-document "$ERROR_DOC"

echo "Applying public-read bucket policy for objects..."
cat > /tmp/site-policy.json <<JSON
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET/*"
  }]
}
JSON
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file:///tmp/site-policy.json >/dev/null

echo "Syncing site files from $SRC_DIR ..."
aws s3 sync "$SRC_DIR/" "s3://$BUCKET/" --delete

SITE_URL="http://$BUCKET.s3-website-$REGION.amazonaws.com"
echo "Done. Website URL:"
echo "$SITE_URL"

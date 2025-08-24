#!/usr/bin/env bash
set -euo pipefail

# --------- CONFIG ---------
REGION="us-east-1"              # your S3 bucket region
BUCKET="chronolog-site-$(date +%s)"  # change if you want a fixed name
SITE_DIR="/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/home"
SRC_DIR="$SITE_DIR/resources"
INDEX_DOC="index.html"

# Custom domain (optional). If you want to add it later, leave empty for now.
CUSTOM_DOMAIN=""                # e.g., "www.duffie.org"
CERT_ARN=""                     # ACM cert in us-east-1 if using custom domain
# --------------------------

command -v aws >/dev/null || { echo "aws CLI not found"; exit 1; }
command -v jq  >/dev/null || { echo "jq not found"; exit 1; }

[ -d "$SRC_DIR" ] || { echo "Source dir not found: $SRC_DIR"; exit 1; }
[ -f "$SRC_DIR/$INDEX_DOC" ] || { echo "Missing $INDEX_DOC in $SRC_DIR"; exit 1; }

echo "Creating PRIVATE bucket: $BUCKET ($REGION) ..."
if [ "$REGION" = "us-east-1" ]; then
  aws s3api create-bucket --bucket "$BUCKET" >/dev/null
else
  aws s3api create-bucket --bucket "$BUCKET" \
    --create-bucket-configuration LocationConstraint="$REGION" \
    --region "$REGION" >/dev/null
fi

echo "Ensuring Block Public Access is ENABLED (default)..."
aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
'{"BlockPublicAcls":true,"IgnorePublicAcls":true,"BlockPublicPolicy":true,"RestrictPublicBuckets":true}' >/dev/null

echo "Uploading site content..."
aws s3 sync "$SRC_DIR/" "s3://$BUCKET/" --delete

echo "Creating CloudFront Origin Access Control (OAC)..."
OAC_ID=$(aws cloudfront create-origin-access-control --origin-access-control-config '{
  "Name": "oac-'"$BUCKET"'",
  "SigningProtocol": "sigv4",
  "SigningBehavior": "always",
  "OriginAccessControlOriginType": "s3"
}' --query 'OriginAccessControl.Id' --output text)
echo "OAC_ID = $OAC_ID"

ORIGIN_DOMAIN="$BUCKET.s3.$REGION.amazonaws.com"

# Build distribution config JSON
echo "Creating CloudFront distribution..."
DIST_JSON=$(cat <<JSON
{
  "CallerReference": "ref-$(date +%s)",
  "Comment": "ChronoLog static site: $BUCKET",
  "Enabled": true,
  "Origins": { "Quantity": 1, "Items": [{
    "Id": "s3-$BUCKET",
    "DomainName": "$ORIGIN_DOMAIN",
    "S3OriginConfig": { "OriginAccessIdentity": "" },
    "OriginAccessControlId": "$OAC_ID"
  }]},
  "DefaultCacheBehavior": {
    "TargetOriginId": "s3-$BUCKET",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": { "Quantity": 2, "Items": ["GET","HEAD"] },
    "CachedMethods": { "Quantity": 2, "Items": ["GET","HEAD"] },
    "Compress": true,
    "ForwardedValues": { "QueryString": false, "Cookies": { "Forward": "none" } },
    "MinTTL": 0, "DefaultTTL": 3600, "MaxTTL": 86400
  },
  "DefaultRootObject": "$INDEX_DOC",
  "Aliases": { "Quantity": 0 }
}
JSON
)

# If custom domain + cert provided, add them
if [[ -n "$CUSTOM_DOMAIN" && -n "$CERT_ARN" ]]; then
  DIST_JSON=$(echo "$DIST_JSON" | \
    jq --arg d "$CUSTOM_DOMAIN" --arg a "$CERT_ARN" '
      .Aliases = {"Quantity":1,"Items":[ $d ]} |
      .ViewerCertificate = {
        "ACMCertificateArn": $a,
        "SSLSupportMethod": "sni-only",
        "MinimumProtocolVersion": "TLSv1.2_2021"
      }')
fi

DIST_CREATE_OUT=$(aws cloudfront create-distribution --distribution-config "$DIST_JSON")
DIST_ID=$(echo "$DIST_CREATE_OUT" | jq -r '.Distribution.Id')
CF_DOMAIN=$(echo "$DIST_CREATE_OUT" | jq -r '.Distribution.DomainName')
CF_ARN=$(echo "$DIST_CREATE_OUT" | jq -r '.Distribution.ARN')
echo "Distribution created:"
echo "  DIST_ID    = $DIST_ID"
echo "  CF_DOMAIN  = $CF_DOMAIN"

echo "$DIST_ID" > "$SITE_DIR/.cloudfront_dist_id"
echo "$CF_DOMAIN" > "$SITE_DIR/.cloudfront_domain"

echo "Granting CloudFront OAC access to bucket objects via bucket policy..."
cat > /tmp/oac-bucket-policy.json <<JSON
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontOACRead",
    "Effect": "Allow",
    "Principal": { "Service": "cloudfront.amazonaws.com" },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET/*",
    "Condition": { "StringEquals": { "AWS:SourceArn": "$CF_ARN" } }
  }]
}
JSON
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file:///tmp/oac-bucket-policy.json >/dev/null

echo
echo "✅ Deployed!"
echo "  Public HTTPS URL (once deployed): https://$CF_DOMAIN"
if [[ -n "$CUSTOM_DOMAIN" && -n "$CERT_ARN" ]]; then
  echo "  Point DNS (A/ALIAS) for $CUSTOM_DOMAIN to $CF_DOMAIN"
fi

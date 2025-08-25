#!/usr/bin/env bash
set -euo pipefail

# --------- CONFIG ---------
REGION="us-east-1"
BUCKET="my-static-site-1756072614"  # set if you want to enforce, else script tries to infer
SITE_DIR="/Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/home"
SRC_DIR="$SITE_DIR/resources"
# --------------------------

command -v aws >/dev/null || { echo "aws CLI not found"; exit 1; }

# Infer bucket from CloudFront origin if DIST_ID present
DIST_ID_FILE="$SITE_DIR/.cloudfront_dist_id"
CF_DOMAIN_FILE="$SITE_DIR/.cloudfront_domain"

if [ -z "${BUCKET}" ] && [ -f "$DIST_ID_FILE" ]; then
  DIST_ID=$(cat "$DIST_ID_FILE")
  ORIGIN=$(aws cloudfront get-distribution --id "$DIST_ID" \
    --query 'Distribution.DistributionConfig.Origins.Items[0].DomainName' --output text)
  # ORIGIN like "bucket.s3.us-east-1.amazonaws.com"
  BUCKET="${ORIGIN%%.s3.*}"
fi

[ -n "$BUCKET" ] || { echo "Bucket not set and not inferable. Set BUCKET in script."; exit 1; }
[ -d "$SRC_DIR" ] || { echo "Source dir not found: $SRC_DIR"; exit 1; }

echo "Syncing $SRC_DIR -> s3://$BUCKET ..."
aws s3 sync "$SRC_DIR/" "s3://$BUCKET/" --delete

# Invalidate CloudFront if present
if [ -f "$DIST_ID_FILE" ]; then
  DIST_ID=$(cat "$DIST_ID_FILE")
  echo "Creating CloudFront invalidation for /* on $DIST_ID ..."
  aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" >/dev/null
  echo "Invalidation requested."
else
  echo "No CloudFront distribution id file found; skipped invalidation."
fi

echo "Done."

# ChronoLog Static Website Deployment

This directory contains the **landing page** for ChronoLog along with helper scripts to deploy it as a static website on AWS S3 (optionally fronted by CloudFront for HTTPS and custom domains).

---

## Website

[http://my-static-site-1756681589.s3-website-us-east-1.amazonaws.com
](http://my-static-site-1756681589.s3-website-us-east-1.amazonaws.com)

## 📂 Directory Structure

```
home/
├── resources/               # All site content (index.html, images, etc.)
│   ├── index.html
│   ├── chronolog_home.html
│   ├── cartridge.png
│   ├── bullets.png
│   ├── kestrel.png
│   ├── garmin_xero.png
│   ├── rifle.png
│   ├── saami.png
│   └── gis.jpg
├── s3_website_quick.sh      # Script for HTTP-only S3 static website hosting
├── s3_cloudfront_https.sh   # Script for HTTPS with CloudFront + OAC
├── sync_site.sh             # Script for re-deploying content
└── README.md
```

---

## 🚀 Workflow

### 1. Prerequisites
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured  
  ```bash
  aws configure
  ```
- [jq](https://stedolan.github.io/jq/) installed (for CloudFront script JSON handling)  
  ```bash
  brew install jq
  ```

### 2. Deploy a Simple HTTP Site (S3 Website Endpoint)
Use this for **fast, public demos** (no HTTPS).
```bash
./s3_website_quick.sh
```
- Creates a new S3 bucket
- Configures it for **static website hosting**
- Sets **public read** access
- Uploads all files from `resources/`

📎 The script prints a URL like:
```
http://<bucket>.s3-website-<region>.amazonaws.com
```

---

### 3. Deploy a Production Site (CloudFront + HTTPS)
Use this for **secure, production-ready hosting**.
```bash
./s3_cloudfront_https.sh
```
- Creates a private S3 bucket
- Uploads all content from `resources/`
- Creates a **CloudFront distribution** with an **Origin Access Control (OAC)**
- Grants CloudFront permission to read bucket objects
- Prints a CloudFront domain such as:
```
https://d123abc.cloudfront.net
```

Optional:
- To use a **custom domain**, set `CUSTOM_DOMAIN` and `CERT_ARN` in the script  
- Update DNS (Route 53 or your registrar) to point to the CloudFront domain

---

### 4. Sync Updates
Whenever you change HTML/images in `resources/`, run:
```bash
./sync_site.sh
```
- Re-syncs files to the S3 bucket
- If CloudFront is used, issues an **invalidation** so new content is served immediately

---

## 🔄 Typical Workflow

1. **Edit site content** in `resources/`  
2. **Deploy site**:  
   - Quick demo → `./s3_website_quick.sh`  
   - Production HTTPS → `./s3_cloudfront_https.sh`  
3. **Share the URL**  
4. **Update site** later with `./sync_site.sh`  

---

## 🌐 Embedding the Live URL into Your Site

Currently, `index.html` links to:
```html
<a href="http://localhost:8501" class="header-launch">Launch App</a>
```

After deployment, replace it with your **live URL**:

```html
<a href="https://d123abc.cloudfront.net" class="header-launch">Launch App</a>
```

or, if you set up a **custom domain**:

```html
<a href="https://www.example.com" class="header-launch">Launch App</a>
```

Update all similar links in your HTML (`Launch App`, `Upload Chronograph Data`, etc.) to point to the deployed Streamlit app or API endpoint rather than `localhost`.

---

## 📝 Notes

- The **S3 website endpoint** (quick script) only supports HTTP.  
- For **HTTPS + custom domains**, always use the CloudFront script.  
- Bucket names must be **globally unique**. Scripts generate unique names by appending a timestamp.  
- If you want a **fixed bucket name**, edit the `BUCKET` variable in the scripts.  
- To delete, remove the CloudFront distribution first, then the S3 bucket:
  ```bash
  aws cloudfront delete-distribution --id DIST_ID --if-match ETAG
  aws s3 rb s3://BUCKET --force
  ```

---

## ✅ Example

```bash
cd /Users/johnduffie/projects/ChronoLog/Streamlit/ChronoLog/home

# Quick site
./s3_website_quick.sh

# Production site
./s3_cloudfront_https.sh

# Update content later
./sync_site.sh
```

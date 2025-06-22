
# Xero Streamlit App

This is a multi-user Streamlit app that allows users to log in with Google (via Auth0), upload Garmin Xero Chronograph Excel files, store structured data in Supabase, and preserve the original uploads.

---

## 🔐 Authentication

- Users log in via **Google** using **Auth0**
- Uploaded files are stored in **Supabase Storage**
- Parsed session and measurement data is saved to **Supabase PostgreSQL**

---

## ✅ Verify Your Supabase Configuration

To verify your Supabase credentials and storage setup, use the included `verify_supabase.py` script.

### 🛠 Prerequisites

- Python 3.8+
- Required packages:
  ```bash
  pip install supabase gotrue postgrest-py realtime-py storage3
  ```

---

## 🔑 Using 1Password CLI for Secrets

If you store your Supabase Service Role Key in **1Password**, follow these steps:

### Step-by-step:

1. **Sign in to 1Password**:
   ```bash
   op account add --address https://my.1password.com --email johnduffie91@gmail.com
   eval $(op signin)
   ```

2. **Export your Supabase key from 1Password**:
   ```bash
   export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")
   ```

3. **Run the script**:
   ```bash
   python verify_supabase.py
   ```

This will:
- Test your database connection to the `sessions` table
- Upload and delete a dummy file in the `uploads` bucket

---

## 🔧 Project Files

- `app.py` – Main Streamlit app
- `.streamlit/secrets.toml` – Configuration template for Auth0 and Supabase
- `requirements.txt` – Python package requirements
- `verify_supabase.py` – Utility script to test Supabase access

---

## 📦 Deployment

See detailed deployment instructions in the [Deployment Guide](#).


---

## 🧪 Setting Up a Virtual Environment

To avoid dependency conflicts, set up a Python virtual environment:

### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Then install dependencies:
```bash
pip install -r requirements.txt
```

You're now ready to run:
```bash
python verify_supabase.py
```

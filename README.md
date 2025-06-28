
# ChronoLog - Garmin Xero Data Processor

A multi-user Streamlit app for processing Garmin Xero Chronograph data. Users authenticate with Google via Auth0, upload Excel files, and store structured ballistics data in Supabase.

## 🔐 Authentication

- Google OAuth via Auth0
- File storage in Supabase Storage
- Structured data in Supabase PostgreSQL

## 🛠 Setup

### Prerequisites
- Python 3.8+
- Streamlit
- Supabase account with service role key
- Auth0 account configured for Google OAuth

### Environment Setup
#### Dependencies and Virtual Env
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### Test Supabase Configuration

##### Test Access to Supabase
```bash
# Set environment variable
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
python verify_supabase.py
```

##### Using 1Password CLI
If you store credentials in 1Password:
```bash
# Add account (one-time setup)
op account add --address https://my.1password.com --email johnduffie91@gmail.com

      source venv/bin/activate
      op account add --address https://my.1password.com --email johnduffie91@gmail.com
      eval $(op signin --account my.1password.com)
      export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")
      python verify_supabase.py
```

#### Download All Files from Supabase Storage

```bash
# Set environment variable
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
python download_uploads.py
```

##### Using 1Password CLI
If you store credentials in 1Password:
```bash
# Add account (one-time setup)
op account add --address https://my.1password.com --email johnduffie91@gmail.com

source venv/bin/activate
eval $(op signin --account my.1password.com)
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")
python download_uploads.py
```

This creates a timestamped `downloads_YYYYMMDD_HHMMSS/` directory with all uploaded files.

#### Reset Entire System

⚠️ **WARNING**: This completely resets the ChronoLog system and cannot be undone!

This script will:
- DELETE ALL uploaded files from storage
- DROP ALL database tables
- RECREATE empty tables with the correct schema

```bash
# Set environment variable
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
python reset_system.py
```

##### Using 1Password CLI
If you store credentials in 1Password:
```bash
# Add account (one-time setup)
op account add --address https://my.1password.com --email johnduffie91@gmail.com

source venv/bin/activate
eval $(op signin --account my.1password.com)
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")
python reset_system.py
```

The script will prompt for confirmation by requiring you to type `RESET EVERYTHING` before proceeding.



## 🚀 Running the Application

### Start the Streamlit App
```bash
source venv/bin/activate
streamlit run app.py
```

## 📁 Project Structure

- `app.py` – Main Streamlit application
- `verify_supabase.py` – Database/storage connectivity test
- `download_uploads.py` – Script to download all files from Supabase storage
- `reset_system.py` – Script to completely reset the system (files + database)
- `.streamlit/secrets.toml` – Auth0 and Supabase configuration
- `requirements.txt` – Python dependencies

## 📊 Data Processing

The app processes Garmin Xero Excel files by:
1. Extracting bullet metadata (type, grain weight)
2. Parsing shot data (velocity, energy, power factor)
3. Storing sessions and measurements in separate tables
4. Preserving original files in user-specific directories

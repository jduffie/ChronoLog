
# ChronoLog - Garmin Xero Data Processor

[![CI/CD Pipeline](https://github.com/jduffie/ChronoLog/actions/workflows/ci.yml/badge.svg)](https://github.com/jduffie/ChronoLog/actions/workflows/ci.yml)
[![Test Coverage](https://github.com/jduffie/ChronoLog/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/jduffie/ChronoLog/actions/workflows/test-coverage.yml)
[![PR Tests](https://github.com/jduffie/ChronoLog/actions/workflows/pr-tests.yml/badge.svg)](https://github.com/jduffie/ChronoLog/actions/workflows/pr-tests.yml)

A multi-user Streamlit app for processing Garmin Xero Chronograph data. Users authenticate with Google via Auth0, upload Excel files, and store structured ballistics data in Supabase.

## 🧪 Testing

The project includes comprehensive automated testing:

- **82 total tests** across all modules
- **Modular test structure** with tests co-located with code
- **GitHub Actions CI/CD** with automated test execution
- **Test coverage reporting** with detailed metrics

### Running Tests Locally

```bash
# Run all tests
python run_all_tests.py

# Run structural validation tests
python test_all_pages.py

# Run module-specific tests
python chronograph/test_chronograph.py
python weather/test_weather.py
python dope/test_dope.py
python ammo/test_ammo.py
python rifles/test_rifles.py
python mapping/test_mapping.py
```

### Test Coverage

- ✅ **Chronograph Module:** 17/17 tests passing (100%)
- ✅ **Page Structure:** 15/15 tests passing (100%)
- ⚠️ **Overall Suite:** 65/82 tests passing (79%)

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
streamlit run ChronoLog.py
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

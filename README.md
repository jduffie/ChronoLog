
# ChronoLog - Garmin Xero Data Processor

A multi-user Streamlit app for processing Garmin Xero Chronograph data. Users authenticate with Google via Auth0, upload Excel files, and store structured ballistics data in Supabase.

## 🔐 Authentication

- Google OAuth via Auth0
- File storage in Supabase Storage
- Structured data in Supabase PostgreSQL

## 🛠 Setup

### Prerequisites
- Python 3.8+
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



## 🚀 Running the Application

### Start the Streamlit App
```bash
streamlit run app.py
```

## 📁 Project Structure

- `app.py` – Main Streamlit application
- `verify_supabase.py` – Database/storage connectivity test
- `.streamlit/secrets.toml` – Auth0 and Supabase configuration
- `requirements.txt` – Python dependencies

## 📊 Data Processing

The app processes Garmin Xero Excel files by:
1. Extracting bullet metadata (type, grain weight)
2. Parsing shot data (velocity, energy, power factor)
3. Storing sessions and measurements in separate tables
4. Preserving original files in user-specific directories

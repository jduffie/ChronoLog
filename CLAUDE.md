# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```



### Testing Supabase Configuration

The application requires a Supabase service role key. Set it as an environment variable:
```bash
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

source venv/bin/activate
python verify_supabase.py
```

If using 1Password CLI (as documented in README):
```bash
# op account add --address https://my.1password.com --email johnduffie91@gmail.com

eval $(op signin)
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")

source venv/bin/activate
python verify_supabase.py
```
### Running the Application
```bash
# Run the main Streamlit app
streamlit run app.py
```

## Architecture Overview

### Core Components
- **app.py**: Main Streamlit application with Auth0 Google authentication and file upload functionality
- **verify_supabase.py**: Utility script to test Supabase database and storage connectivity
- **.streamlit/secrets.toml**: Configuration file containing Auth0 and Supabase credentials

### Authentication Flow
- Uses Auth0 for Google OAuth authentication
- Redirects to authorize endpoint, processes auth code, retrieves user info
- User session maintained in Streamlit session state

### Data Flow
1. User uploads Garmin Xero Chronograph Excel files through Streamlit interface
2. Files are stored in Supabase Storage under user's email directory
3. Excel data is parsed and structured into:
   - **sessions** table: metadata (bullet type, grain, timestamps, file paths)
   - **measurements** table: individual shot data (speed, energy, power factor, etc.)

### Database Schema
- **sessions**: Contains session metadata with bullet information and user email
- **measurements**: Contains individual shot measurements linked to sessions via session_id

### External Dependencies
- **Streamlit**: Web framework for the application interface
- **Supabase**: Backend-as-a-Service for database and file storage
- **Auth0**: Authentication service for Google OAuth
- **pandas/openpyxl**: Excel file processing
- **requests**: HTTP client for Auth0 API calls

### File Processing
- Parses Garmin Xero Excel files with bullet metadata in first row
- Extracts bullet type and grain weight from comma-separated values
- Processes measurement data starting from row 2
- Handles optional fields like Clean Bore, Cold Bore, and Shot Notes
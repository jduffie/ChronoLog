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
streamlit run ChronoLog.py
```

### Testing Commands

**IMPORTANT**: All tests must pass before committing code. Run both unit and integration tests:

```bash
# Run all unit tests
source venv/bin/activate
python run_all_tests.py

# Run integration tests
python run_integration_tests.py

# Both test suites must pass before any commit
```

### Commit Requirements

Before committing any code changes:
1. **Run all tests** - Both unit and integration tests must pass
2. **Verify functionality** - Test the specific features you modified
3. **Check for breaking changes** - Ensure existing functionality still works
4. **Only commit if all tests pass** - Never commit code with failing tests

## Architecture Overview

### Core Components
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
The application uses a comprehensive Supabase database with the following tables and views:

#### Core Tables
- **users**: User profiles and authentication data
- **chrono_sessions**: Chronograph session metadata
- **chrono_measurements**: Individual shot measurements from chronograph
- **dope_sessions**: DOPE (Data On Previous Engagement) session data
- **dope_measurements**: Individual DOPE measurements with ballistic adjustments
- **weather_source**: Weather measurement device configurations
- **weather_measurements**: Environmental conditions data
- **rifles**: User rifle configurations and specifications
- **bullets**: Bullet specifications and ballistic data
- **ranges**: Approved public shooting ranges (admin-managed)
- **ranges_submissions**: User-submitted range data pending approval

### External Dependencies
- **Streamlit**: Web framework for the application interface
- **Supabase**: Backend-as-a-Service for database and file storage
- **Auth0**: Authentication service for Google OAuth
- **pandas/openpyxl**: Excel file processing
- **requests**: HTTP client for Auth0 API calls

## Key Development Patterns

### Service Layer Pattern
All database operations go through service classes:
```python
from feature.service import FeatureService
service = FeatureService(supabase_client)
results = service.get_data_for_user(user_email)
```

### Model Classes
Use dataclasses for data entities with Supabase integration:
```python
@dataclass
class FeatureModel:
    @classmethod
    def from_supabase_record(cls, record: dict):
        # Convert Supabase record to model instance
```

### Streamlit Classes
Isolate user interface code and especially streamlit code in separate classes.  I may elect to re-use the 
non streamlit code using a different UI framework

### User Isolation
All database queries must filter by user['id'] for data isolation:


### Testing Patterns
- Mock Supabase client in tests
- Use `unittest.mock` for external dependencies
- Follow naming convention: `test_*.py`
- Include both unit and integration tests

### Import Structure
Add root directory to path for module imports:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Database Schema Maintenance



# Next Steps


# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
DO NOT use unicode emojis. Use plain text only.

- always check for unused imports before committing
- my ci/cd does test coverage and ensure the number is higher than 70% before commiting
- only use emojis for info messages.
- each page needs its own private session state with specific states nested beneath
- use user["id"] for authorization
- run isort before commit
- use Intellij MCP where possible to accelerate file searching, etc
- all interior processing and storage is based on the metric system.  Only swap at the edge when importing files that use imperial or in the ui if the user preferences require it
# ChronoLog Development Guide

This guide covers how to set up, run, test, and contribute to the ChronoLog ballistics application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.13+** (tested with Python 3.13.3)
- **Git** for version control
- **1Password CLI** (optional, for secure credential management)

### Optional but Recommended
- **Watchdog** for better Streamlit performance: `pip install watchdog`

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/jduffie/ChronoLog.git
cd ChronoLog
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# install dependencies
pip install -r requirements.txt
```

### 3. Setup Configuration

ChronoLog requires Auth0 and Supabase credentials. You need to create configuration files to store these credentials securely.

#### Create Environment Variables File
Generate environment variables from 1Password for development use:

```bash
# Sign in to 1Password CLI (if not already signed in)
# eval $(op signin)

# Export environment variables from 1Password to current shell
source ./export_env_from_1password.sh

# Verify configuration
source venv/bin/activate
python test_env_variables.py
```

#### Create Streamlit Secrets File
Generate a `.streamlit/secrets.toml` file from 1Password:

```bash
# Sign in to 1Password CLI (if not already signed in)
# eval $(op signin)

# Generate secrets.toml from 1Password
# assumes you have access to the "ChronoLog - Dev" item in the "Private" vault
./setup_secrets.sh
```

#### Manual Configuration (Alternative)
If you don't have access to 1Password, create `.streamlit/secrets.toml` manually:

```toml
[auth0]
domain = "your-auth0-domain"
client_id = "your-auth0-client-id"
client_secret = "your-auth0-client-secret"
redirect_uri = "http://localhost:8501"

[supabase]
url = "your-supabase-url"
key = "your-supabase-anon-key"
service_role_key = "your-supabase-service-role-key"
bucket = "uploads"
```


### Verify Configuration

Test that environment variables are set correctly:
```bash
source venv/bin/activate
python test_env_variables.py
```

Test your Supabase connection:
```bash
source venv/bin/activate
python verify_supabase.py
```

## Running the Application

### Development Server
```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
streamlit run ChronoLog.py
```

The application will be available at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://10.1.166.51:8501 (for network access)


## Testing

ChronoLog has comprehensive test coverage with both unit and integration tests.

### Run All Tests
```bash
source venv/bin/activate
python run_all_tests.py
```

### Run Specific Test Modules
```bash
source venv/bin/activate

# Run chronograph tests
python -m pytest chronograph/test_chronograph.py -v

# Run bullets tests
python -m pytest bullets/test_bullets.py -v

# Run DOPE tests
python -m pytest dope/test_dope.py -v

# Run rifles tests
python -m pytest rifles/test_rifles.py -v
```

### Run Integration Tests
```bash
source venv/bin/activate
python run_integration_tests.py
```

### Test Coverage
Generate test coverage reports:
```bash
source venv/bin/activate
python -m pytest --cov=. --cov-report=html
```

View coverage report: `open htmlcov/index.html`

### Test Structure
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Page Structure Tests**: Verify page configuration and imports
- **Service Layer Tests**: Test database operations with mocked clients

## Code Quality

### Pre-Commit Requirements
**IMPORTANT**: All tests must pass before committing code.

```bash
# Verify all tests pass
source venv/bin/activate
python run_all_tests.py

# Only commit if all tests pass
git add .
git commit -m "Your commit message"
```

### Code Formatting
The project uses:
- **Black 25.1.0** for code formatting
- **isort 6.0.1** for import organization

```bash
# Format code
black .
isort .
```

### Linting
Run linting checks:
```bash
# Check for common issues
flake8 .
```

## Contributing

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow existing architectural patterns
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Changes**
   ```bash
   source venv/bin/activate
   python run_all_tests.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Brief description of changes

   Detailed explanation if needed

   🤖 Generated with [Claude Code](https://claude.ai/code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
Follow the existing commit message style:
- **Subject**: Brief description (50 chars max)
- **Body**: Detailed explanation of changes
- **Footer**: Include Claude Code attribution

Example:
```
Add new feature for bullet management

- Implement BulletService for database operations
- Add comprehensive unit tests
- Update UI to use service layer pattern

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Architectural Guidelines

#### Service Layer Pattern
All database operations should go through service classes:
```python
from feature.service import FeatureService

service = FeatureService(supabase_client)
results = service.get_data_for_user(user_email)
```

#### Model Classes
Use dataclasses for data entities:
```python
@dataclass
class FeatureModel:
    @classmethod
    def from_supabase_record(cls, record: dict):
        # Convert Supabase record to model instance
```

#### User Isolation
All database queries must filter by user:
```python
.eq("user_email", user_email)
```

#### Testing Requirements
- Mock Supabase client in tests
- Test both success and error cases
- Include edge cases and validation
- Maintain >80% test coverage

### File Structure
```
feature/
├── models.py          # Data models
├── service.py         # Business logic and database operations
├── create_tab.py      # Create UI component
├── view_tab.py        # View UI component
└── test_feature.py    # Comprehensive tests
```

## Troubleshooting

### Common Issues

#### 1. Missing Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Authentication Errors
```bash
# Verify secrets configuration
source venv/bin/activate
python verify_supabase.py

# Check 1Password CLI
op account list
```

#### 3. Test Failures
```bash
source venv/bin/activate

# Run tests with verbose output
python -m pytest -v -s

# Run specific failing test
python -m pytest path/to/test.py::TestClass::test_method -v
```

#### 4. Database Connection Issues
- Verify Supabase credentials in secrets.toml
- Check network connectivity
- Ensure service role key has proper permissions

#### 5. Import Errors
```bash
# Verify virtual environment is activated
which python
pip list

# Reinstall in development mode
pip install -e .
```

### Performance Tips

1. **Install Watchdog** for faster Streamlit reloads:
   ```bash
   pip install watchdog
   ```

2. **Use Browser Cache** - Clear browser cache if pages aren't updating

3. **Database Connections** - Ensure you're not creating multiple connections

### Getting Help

1. **Check Logs** - Look at Streamlit console output for errors
2. **Review Tests** - Look at similar test implementations
3. **Check Documentation** - Refer to `specifications.md` for system architecture
4. **Database Schema** - Reference the schema documentation in `CLAUDE.md`

## Development Environment Verification

Use this checklist to verify your development environment:

- [ ] Python 3.13+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Secrets configured (1Password CLI or manual)
- [ ] Supabase connection verified (`python verify_supabase.py`)
- [ ] All tests pass (`python run_all_tests.py`)
- [ ] Application runs (`streamlit run ChronoLog.py`)

Once all items are checked, you're ready to develop!
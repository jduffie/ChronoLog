# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the ChronoLog application.

## 🚀 Workflows

### 1. CI/CD Pipeline (`ci.yml`)
**Triggers:** Push to main/map_on_dope/develop, Pull Requests, Manual dispatch

**Features:**
- **Multi-Python Testing:** Tests against Python 3.9, 3.10, 3.11
- **Comprehensive Testing:** Runs both structural and modular test suites
- **Code Coverage:** Generates coverage reports with Codecov integration
- **Dependency Caching:** Speeds up builds with pip cache
- **Test Artifacts:** Uploads test reports and coverage data
- **PR Comments:** Automatically comments test results on pull requests

**Jobs:**
- `test` - Runs complete test suite with coverage
- `lint` - Code quality checks (Black, isort, flake8, mypy)
- `security` - Security scanning (Bandit, Safety)
- `build-status` - Final status summary

### 2. Test Coverage Report (`test-coverage.yml`)
**Triggers:** Push to main/map_on_dope, Daily at 2 AM UTC, Manual dispatch

**Features:**
- **Detailed Coverage:** Comprehensive coverage analysis
- **Coverage Badge:** Generates coverage badge
- **Commit Comments:** Posts coverage percentage on commits
- **Scheduled Reports:** Daily coverage monitoring

### 3. Pull Request Tests (`pr-tests.yml`)
**Triggers:** Pull request events (opened, synchronize, reopened)

**Features:**
- **Fast PR Validation:** Quick test suite for PR validation
- **Detailed PR Comments:** Rich test result comments on PRs
- **Status Checks:** Sets PR status based on test results
- **Test Artifacts:** Uploads test output for debugging

## 🧪 Test Execution

### Local Testing
```bash
# Run all tests locally
python run_all_tests.py

# Run structural tests only
python test_all_pages.py

# Run specific module tests
python chronograph/test_chronograph.py
```

### GitHub Actions Testing
The workflows automatically:
1. Set up Python environment
2. Install dependencies with caching
3. Create mock Streamlit secrets for testing
4. Run modular test suite (82 tests)
5. Generate coverage reports
6. Upload test artifacts
7. Comment results on PRs

## 📊 Test Coverage

Current test coverage includes:
- **Chronograph Module:** Service, models, import functionality
- **Weather Module:** Weather data processing
- **DOPE Module:** Session management and ballistics
- **Ammo Module:** Ammunition management
- **Rifles Module:** Rifle specifications
- **Mapping Module:** Range location management
- **Page Structure:** All page configurations and layouts

## 🔧 Configuration

### Environment Variables
The workflows create mock environment files for testing:
- `.streamlit/secrets.toml` with test credentials
- Supabase test endpoints
- Auth0 test configuration

### Dependencies
- Core application dependencies from `requirements.txt`
- Testing tools: pytest, coverage, pytest-html
- Linting tools: black, isort, flake8, mypy
- Security tools: bandit, safety

## 📈 Monitoring

### Success Metrics
- ✅ **Structural Tests:** 15/15 passing (100%)
- ✅ **Chronograph Tests:** 17/17 passing (100%)
- ⚠️ **Overall Suite:** 65/82 passing (79%)

### Failure Handling
- Failed tests block PR merging
- Coverage drops trigger notifications
- Security issues are flagged but don't block
- Artifacts are preserved for debugging

## 🚨 Alerts

Workflows will alert on:
- Test failures
- Coverage drops below threshold
- Security vulnerabilities
- Linting violations
- Missing dependencies

## 🔄 Maintenance

### Updating Workflows
1. Modify workflow files in `.github/workflows/`
2. Test changes in a feature branch
3. Commit and push to trigger workflows
4. Monitor Actions tab for results

### Adding New Tests
1. Create tests in appropriate module directory
2. Update `run_all_tests.py` if needed
3. Workflows will automatically discover new tests
4. Coverage reports will include new modules
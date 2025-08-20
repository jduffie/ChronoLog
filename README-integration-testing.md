# Integration Testing Guide

This guide explains how to create and run integration tests for ChronoLog.

## Overview

Integration tests verify that different components of the application work together correctly. Unlike unit tests that test individual functions in isolation, integration tests test:

- **End-to-end workflows** (file upload → database storage → retrieval)
- **Cross-module interactions** (chronograph data with ammo/rifle records) 
- **External service integration** (Supabase database, Auth0 authentication)
- **Data consistency** across the entire application

## Test Structure

### Comprehensive Test Suite

ChronoLog now includes **158 tests** organized across multiple modules:

- **Chronograph**: 17 tests - File processing, data validation, session management
- **Weather**: 14 tests - Weather source management, measurement import, data validation  
- **DOPE**: 18 tests - New modular page structure, session creation, analytics
- **Rifles**: 34 tests - Rifle configuration, ballistic calculations, data integrity
- **Mapping**: 61 tests - Range management, geolocation, submission workflow
- **Page Structure**: 14 tests - UI validation, authentication flow, configuration

### Test Categories

Tests are organized by module and functionality:

- **Unit Tests** - Individual function and class testing
- **Integration Tests** - Cross-module interactions and workflows
- **Structural Tests** - Page organization, imports, configuration
- **Database Tests** - Data persistence, relationships, constraints
- **UI Tests** - Streamlit page functionality and user flows

### Test Files

- `test_all_pages.py` - Page structure and configuration validation
- `run_all_tests.py` - Comprehensive test runner for all modules
- `run_integration_tests.py` - Dedicated integration test runner
- `chronograph/test_chronograph.py` - Chronograph module tests
- `weather/test_weather.py` - Weather module tests (re-enabled)
- `dope/test_dope_modules.py` - New DOPE modular page tests
- `rifles/test_rifles.py` - Rifle management tests
- `mapping/test_mapping.py` - Range and mapping tests

## Running Tests

### Comprehensive Test Suite

```bash
# Run all 158 tests across all modules
python run_all_tests.py

# Run specific module tests
python -m pytest chronograph/test_chronograph.py -v
python -m pytest weather/test_weather.py -v
python -m pytest dope/test_dope_modules.py -v
python -m pytest rifles/test_rifles.py -v
python -m pytest mapping/test_mapping.py -v

# Run page structure validation
python test_all_pages.py
```

### Integration Tests

```bash
# Run all integration tests
python run_integration_tests.py

# Run with coverage reporting
python run_integration_tests.py --coverage

# Run only fast integration tests (skip slow ones)
python run_integration_tests.py --fast
```

### CI/CD Test Execution

The GitHub Actions workflows run the complete test suite:

```bash
# Structural validation
python test_all_pages.py

# Modular test suite
python run_all_tests.py

# Coverage testing with pytest
pytest --cov=. --cov-report=xml --cov-report=html \
  chronograph/test_chronograph.py \
  weather/test_weather.py \
  dope/test_dope_modules.py \
  rifles/test_rifles.py \
  mapping/test_mapping.py \
  test_all_pages.py \
  -v
```

### Targeted Testing

```bash
# Only database integration tests
python run_integration_tests.py --database-only

# Only file upload tests  
python run_integration_tests.py --file-upload

# Only authentication tests
python run_integration_tests.py --auth
```

### Using pytest directly

```bash
# Run all integration tests
pytest -m integration test_integration.py

# Run database tests but skip slow ones
pytest -m "integration and database and not slow" test_integration.py

# Run with verbose output
pytest -m integration -vv test_integration.py
```

## Recent Improvements

### DOPE Module Refactoring

The DOPE (Data On Previous Engagement) module was recently refactored from a single tab-based page to separate modular pages:

**Old Structure (Deprecated):**
- `dope/sessions_tab.py`
- `dope/view_session_tab.py`
- `dope/create_session_tab.py`

**New Structure (Current):**
- `dope/create/create_page.py` - DOPE session creation interface
- `dope/view/view_page.py` - Session management and viewing
- `dope/analytics/analytics_page.py` - Data analysis and visualization

**New Test Coverage:**
- `dope/test_dope_modules.py` - 18 comprehensive tests covering:
  - Module structure validation
  - Import functionality
  - Page rendering with mocked Streamlit components
  - Integration with main application pages
  - Backward compatibility with existing models

### Weather Module Re-enablement

Weather tests were previously disabled due to import issues in CI/CD. Recent fixes:

- ✅ Resolved import path issues in CI environment
- ✅ Re-enabled 14 weather tests in `weather/test_weather.py`
- ✅ Updated CI/CD workflows to include weather module
- ✅ Verified all weather functionality works correctly

### Test Suite Growth

The test suite has grown significantly:
- **Before**: 112 tests
- **After**: 158 tests (+46 new tests)
- **Coverage**: All modules now have comprehensive test coverage
- **CI/CD**: All tests run in GitHub Actions with coverage reporting

## Test Scenarios

### 1. DOPE Module Testing (`TestDopeModules`)

Tests the new modular DOPE page structure:

```python
def test_dope_modules_can_be_imported(self):
    # Tests that all new DOPE modules can be imported
    from dope.create.create_page import render_create_page
    from dope.view.view_page import render_view_page  
    from dope.analytics.analytics_page import render_analytics_page
```

**What it tests:**
- Directory structure organization
- Module import functionality
- Page rendering with Streamlit components
- Integration with main application
- Backward compatibility with existing models

### 2. File Upload Integration (`TestFileUploadIntegration`)

Tests the complete workflow from Excel file upload to database storage:

```python
def test_complete_upload_workflow(self):
    # Creates test Excel file with Garmin Xero format
    # Processes bullet metadata and measurement data  
    # Verifies session and measurements are created correctly
```

**What it tests:**
- Excel file parsing (metadata + data rows)
- Bullet type and grain extraction
- Session creation in database
- Measurement batch insertion
- Data integrity throughout the process

### 3. Cross-Module Integration (`TestCrossModuleIntegration`)

Tests how chronograph data integrates with ammo and rifle modules:

```python
def test_chronograph_ammo_rifle_integration(self):
    # Creates ammo record
    # Creates rifle record  
    # Creates chronograph session
    # Verifies data consistency across modules
```

**What it tests:**
- Data relationships between modules
- Caliber consistency (9mm ammo → 9mm rifle → 9mm chronograph)
- Grain weight matching
- User data isolation

### 4. Authentication Integration (`TestAuthenticationIntegration`)

Tests that authentication properly controls data access:

```python
def test_auth_to_data_access_flow(self):
    # Mocks authenticated user session
    # Tests user-scoped data queries
    # Verifies data isolation between users
```

**What it tests:**
- Auth0 login flow integration
- User session state management
- User-scoped database queries
- Data privacy and isolation

### 5. Database Transaction Integration (`TestDatabaseTransactionIntegration`)

Tests transaction handling and rollback scenarios:

```python 
def test_transaction_rollback_on_error(self):
    # Simulates partial operation failure
    # Tests that incomplete data is rolled back
    # Ensures database consistency
```

**What it tests:**
- Transaction atomicity
- Rollback on partial failures
- Data consistency under error conditions
- Database integrity constraints

## Environment Setup

### Test Database Configuration

Integration tests can run in two modes:

1. **Mock Mode** (CI/Testing):
   ```bash
   export SUPABASE_URL="https://test.supabase.co"
   export SUPABASE_KEY="test-key"
   ```

2. **Real Database Mode** (Local Development):
   ```bash  
   export SUPABASE_URL="your-actual-supabase-url"
   export SUPABASE_KEY="your-actual-service-role-key"
   ```

### Test Data Isolation

Integration tests include automatic cleanup:

```python
def tearDown(self):
    # Clean up test sessions and measurements
    for session_id in self.test_session_ids:
        self.supabase.table('sessions').delete().eq('id', session_id).execute()
```

## Writing New Integration Tests

### 1. Inherit from BaseIntegrationTest

```python
@pytest.mark.integration
@pytest.mark.your_category
class TestYourIntegration(BaseIntegrationTest):
    """Test your integration scenario"""
    
    def test_your_workflow(self):
        # Your test logic here
        pass
```

### 2. Add Appropriate Markers

Use pytest markers to categorize your tests:

```python
@pytest.mark.integration      # Required for all integration tests
@pytest.mark.database        # If it touches database
@pytest.mark.slow           # If it takes >2 seconds
@pytest.mark.file_upload     # If it involves files
@pytest.mark.auth           # If it tests authentication
```

### 3. Handle Both Mock and Real Modes

```python
def test_your_feature(self):
    if self.mock_mode:
        # Configure mocks for CI testing
        self.supabase.table.return_value.select.return_value.execute.return_value.data = []
    else:
        # Test with real database
        result = self.service.create_record(data)
        self.test_record_ids.append(result['id'])  # For cleanup
```

### 4. Clean Up Test Data

```python
def tearDown(self):
    """Clean up test data"""
    super().tearDown()  # Call parent cleanup
    
    # Add your specific cleanup
    if not self.mock_mode:
        for record_id in self.test_record_ids:
            self.service.delete_record(record_id)
```

## Common Patterns

### Testing File Operations

```python
def create_test_file(self):
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    # Create test data
    return temp_file.name

def test_file_workflow(self):
    file_path = self.create_test_file()
    try:
        # Test file processing
        result = self.service.process_file(file_path)
        self.assertEqual(result.status, 'success')
    finally:
        os.unlink(file_path)  # Cleanup
```

### Testing Database Transactions

```python
def test_transaction_behavior(self):
    with self.assertRaises(ExpectedError):
        # Test that errors properly rollback
        self.service.complex_operation_that_fails()
    
    # Verify no partial data was left behind
    records = self.service.get_records(self.test_user_email)
    self.assertEqual(len(records), 0)
```

### Testing Cross-Module Data Flow

```python
def test_data_flow(self):
    # Step 1: Create upstream data
    ammo_id = self.ammo_service.create(ammo_data)
    
    # Step 2: Reference in downstream module  
    session_data = {'ammo_id': ammo_id, ...}
    session_id = self.chronograph_service.create_session(session_data)
    
    # Step 3: Verify relationship
    session = self.chronograph_service.get_session(session_id)
    self.assertEqual(session.ammo_id, ammo_id)
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Always clean up test data to avoid pollution
3. **Realistic Data**: Use data that mimics real user inputs
4. **Error Cases**: Test both success and failure scenarios  
5. **Performance**: Mark slow tests with `@pytest.mark.slow`
6. **Documentation**: Clearly document what each test verifies

## CI Integration

Integration tests are automatically run in GitHub Actions:

```yaml
- name: Run integration tests
  run: |
    python run_integration_tests.py --fast
```

The `--fast` flag skips slow tests in CI to keep build times reasonable.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Ensure test credentials are set correctly
2. **Test Data Pollution**: Make sure cleanup is working properly  
3. **Timing Issues**: Use appropriate timeouts for async operations
4. **Mock Configuration**: Verify mocks match real API responses

### Debugging Tests

```bash
# Run with verbose output and no capture
pytest -m integration -vv -s test_integration.py

# Run single test method
pytest -m integration test_integration.py::TestFileUploadIntegration::test_complete_upload_workflow

# Run with pdb debugger
pytest -m integration --pdb test_integration.py
```

This integration testing framework ensures ChronoLog's components work together reliably across different environments and use cases.
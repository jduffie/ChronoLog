# Integration Testing Guide

This guide explains how to create and run integration tests for ChronoLog.

## Overview

Integration tests verify that different components of the application work together correctly. Unlike unit tests that test individual functions in isolation, integration tests test:

- **End-to-end workflows** (file upload → database storage → retrieval)
- **Cross-module interactions** (chronograph data with ammo/rifle records) 
- **External service integration** (Supabase database, Auth0 authentication)
- **Data consistency** across the entire application

## Test Structure

### Test Categories

Integration tests are organized into categories using pytest markers:

- `@pytest.mark.integration` - All integration tests
- `@pytest.mark.database` - Tests that interact with database
- `@pytest.mark.file_upload` - Tests involving file operations  
- `@pytest.mark.auth` - Authentication flow tests
- `@pytest.mark.slow` - Tests that may take several seconds

### Test Files

- `test_integration.py` - Main integration test suite
- `run_integration_tests.py` - Test runner script
- `pytest.ini` - Test configuration with markers

## Running Integration Tests

### Basic Usage

```bash
# Run all integration tests
python run_integration_tests.py

# Run with coverage reporting
python run_integration_tests.py --coverage

# Run only fast integration tests (skip slow ones)
python run_integration_tests.py --fast
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

## Test Scenarios

### 1. File Upload Integration (`TestFileUploadIntegration`)

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

### 2. Cross-Module Integration (`TestCrossModuleIntegration`)

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

### 3. Authentication Integration (`TestAuthenticationIntegration`)

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

### 4. Database Transaction Integration (`TestDatabaseTransactionIntegration`)

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
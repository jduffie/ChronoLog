# Users Module

This module handles all user-related functionality in the ChronoLog application, including authentication, profile management, and user preferences.

## Architecture

The module follows the MVC (Model-View-Controller) pattern:

- **Model** (`user_model.py`): Database operations and data validation
- **View** (`user_view.py`): UI components and form displays
- **Controller** (`user_controller.py`): Business logic and coordination
- **Main Interface** (`user_profile.py`): Public API for the module

## Files

### Core Module Files

- `__init__.py` - Module initialization and exports
- `user_model.py` - Database operations and user data management
- `user_view.py` - Streamlit UI components for user interfaces
- `user_controller.py` - Business logic and coordination between model/view
- `user_profile.py` - Main interface functions for external use

### Database

- `create_users_table.sql` - SQL script to create the users table with proper constraints

### Documentation

- `README.md` - This file

## Database Schema

The users table includes:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    unit_system VARCHAR(20) NOT NULL DEFAULT 'Imperial',
    profile_complete BOOLEAN DEFAULT FALSE,
    auth0_sub VARCHAR(255),
    picture VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Usage

### Basic Integration

```python
from users import handle_user_profile

# In your authentication flow
user_profile = handle_user_profile(auth0_user_data)
if user_profile:
    # User has complete profile, proceed with app
    proceed_to_app(user_profile)
else:
    # User is in profile setup process
    # handle_user_profile will display the setup form
    pass
```

### Admin Functions

```python
from users import display_user_management_page, get_user_statistics

# Display admin user management
display_user_management_page()

# Get user statistics
stats = get_user_statistics()
print(f"Total users: {stats['total_users']}")
```

### Profile Display

```python
from users import display_user_profile_page

# Display user profile page
display_user_profile_page(user_profile)
```

## Features

### User Profile Management
- **Profile Setup**: Required fields validation and setup flow
- **Profile Editing**: Users can update their information
- **Username Validation**: Format checking and uniqueness validation
- **Unit Preferences**: Imperial vs Metric system selection

### Authentication Integration
- **Auth0 Integration**: Seamless integration with existing Auth0 setup
- **Profile Completion**: Automatic redirect to setup if profile incomplete
- **Sidebar Display**: User info displayed in app sidebar

### Admin Features
- **User Management**: Admin interface for viewing/managing users
- **User Statistics**: Dashboard showing user metrics
- **User Deletion**: Admin capability to remove users

### Data Validation
- **Username Rules**: 3-30 characters, alphanumeric plus underscore/hyphen
- **Required Fields**: Email, name, username, state, country
- **Unit System**: Constrained to 'Imperial' or 'Metric'

## User Flow

1. **Sign In**: User signs in with Google via Auth0
2. **Profile Check**: System checks if profile is complete
3. **Profile Setup**: If incomplete, user sees setup form
4. **Validation**: Form validates username availability and format
5. **Save Profile**: Profile saved to database
6. **App Access**: User can access application features
7. **Profile Management**: User can edit profile anytime

## Error Handling

The module includes comprehensive error handling:
- Database connection errors
- Validation errors with user-friendly messages
- Username conflicts and availability checking
- Form submission error feedback

## Security Considerations

- **Email Uniqueness**: Prevents duplicate accounts
- **Username Uniqueness**: Prevents conflicts
- **Input Validation**: SQL injection prevention
- **Auth0 Integration**: Secure authentication flow

## Customization

### Adding New Profile Fields

1. Update the database schema in `create_users_table.sql`
2. Modify the form in `user_view.py`
3. Update validation in `user_controller.py`
4. Add database operations in `user_model.py`

### Changing Unit Systems

Modify the unit system options in `user_view.py` and update the database constraint in the SQL file.

### Adding New Countries

Update the countries list in `user_view.py` `display_profile_setup_form` method.

## Dependencies

- `streamlit` - Web framework
- `supabase` - Database client
- `re` - Regular expressions for validation
- `pandas` - Data handling for admin tables
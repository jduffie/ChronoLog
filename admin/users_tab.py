from datetime import datetime

import pandas as pd
import streamlit as st


def render_users_tab(user, supabase):
    """Render the Users tab for admin management"""
    st.header(" User Management")

    try:
        # Get all users from the database
        response = (
            supabase.table("users")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        if not response.data:
            st.info("📭 No users found in the database.")
            return

        # Convert to DataFrame for better display
        df = pd.DataFrame(response.data)

        # Display summary stats
        st.subheader(" Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Users", len(df))

        with col2:
            # Count users with complete profiles
            complete_profiles = df["profile_complete"].sum() if "profile_complete" in df.columns else 0
            st.metric("Complete Profiles", complete_profiles)

        with col3:
            # Count admin users
            admin_count = 0
            if "roles" in df.columns:
                admin_count = df["roles"].apply(lambda x: "admin" in x if x and isinstance(x, list) else False).sum()
            st.metric("Admin Users", admin_count)

        with col4:
            # Count users by country (most common)
            if "country" in df.columns and not df["country"].empty:
                most_common_country = df["country"].mode().iloc[0] if len(df["country"].mode()) > 0 else "N/A"
                country_count = (df["country"] == most_common_country).sum() if most_common_country != "N/A" else 0
                st.metric(f"Users from {most_common_country}", country_count)
            else:
                st.metric("Countries", "N/A")

        # Add filters
        st.subheader(" Filter Options")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            countries = ["All"] + sorted(df["country"].dropna().unique().tolist()) if "country" in df.columns else ["All"]
            selected_country = st.selectbox("Country:", countries)

        with col2:
            unit_systems = ["All"] + sorted(df["unit_system"].dropna().unique().tolist()) if "unit_system" in df.columns else ["All"]
            selected_unit_system = st.selectbox("Unit System:", unit_systems)

        with col3:
            profile_status = ["All", "Complete", "Incomplete"]
            selected_profile_status = st.selectbox("Profile Status:", profile_status)

        with col4:
            role_filter = ["All", "Admin", "User"]
            selected_role = st.selectbox("Role:", role_filter)

        # Apply filters
        filtered_df = df.copy()
        if selected_country != "All":
            filtered_df = filtered_df[filtered_df["country"] == selected_country]
        if selected_unit_system != "All":
            filtered_df = filtered_df[filtered_df["unit_system"] == selected_unit_system]
        if selected_profile_status != "All":
            if selected_profile_status == "Complete":
                filtered_df = filtered_df[filtered_df["profile_complete"] == True]
            else:  # Incomplete
                filtered_df = filtered_df[filtered_df["profile_complete"] != True]
        if selected_role != "All":
            if selected_role == "Admin":
                filtered_df = filtered_df[filtered_df["roles"].apply(lambda x: "admin" in x if x and isinstance(x, list) else False)]
            else:  # User
                filtered_df = filtered_df[filtered_df["roles"].apply(lambda x: "admin" not in x if x and isinstance(x, list) else True)]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} users")

        # Display the table with selection
        st.subheader(" Users")

        if len(filtered_df) == 0:
            st.warning("No users match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # Format roles for display
        if "roles" in display_df.columns:
            display_df["roles_display"] = display_df["roles"].apply(
                lambda x: ", ".join(x) if x and isinstance(x, list) else "user"
            )

        # Format dates for display
        date_columns = ["created_at", "updated_at"]
        for col in date_columns:
            if col in display_df.columns:
                display_df[f"{col}_display"] = pd.to_datetime(display_df[col]).dt.strftime('%Y-%m-%d %H:%M')

        # Select columns for display
        display_columns = [
            "email", "name", "username", "country", "state", "unit_system", 
            "profile_complete", "roles_display", "created_at_display"
        ]
        
        # Filter to only existing columns
        available_columns = [col for col in display_columns if col in display_df.columns]
        table_df = display_df[available_columns].rename(columns={
            "email": "Email",
            "name": "Name", 
            "username": "Username",
            "country": "Country",
            "state": "State",
            "unit_system": "Unit System",
            "profile_complete": "Profile Complete",
            "roles_display": "Roles",
            "created_at_display": "Created At"
        })

        # Display table with selection
        selected_rows = st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Username": st.column_config.TextColumn("Username", width="small"),
                "Country": st.column_config.TextColumn("Country", width="small"),
                "State": st.column_config.TextColumn("State", width="small"),
                "Unit System": st.column_config.TextColumn("Unit System", width="small"),
                "Profile Complete": st.column_config.CheckboxColumn("Profile Complete", width="small"),
                "Roles": st.column_config.TextColumn("Roles", width="small"),
                "Created At": st.column_config.TextColumn("Created At", width="medium"),
            }
        )

        # Handle user selection for editing
        if selected_rows["selection"]["rows"]:
            selected_row_idx = selected_rows["selection"]["rows"][0]
            selected_user_data = filtered_df.iloc[selected_row_idx]
            
            st.markdown("---")
            
            # Create tabs for Edit and Delete
            edit_tab, delete_tab = st.tabs(["✏️ Edit User", "🗑️ Delete User"])
            
            with edit_tab:
                render_user_edit_form(selected_user_data, supabase)
                
            with delete_tab:
                render_user_delete_form(selected_user_data, supabase)

    except Exception as e:
        st.error(f"❌ Error loading users: {str(e)}")
        st.info("Please check your database connection and try again.")


def render_user_edit_form(user_data, supabase):
    """Render the user editing form"""
    st.markdown(f"**Editing user:** {user_data.get('name', 'Unknown')} ({user_data.get('email', 'Unknown')})")
    
    with st.form(key=f"edit_user_{user_data.get('id')}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Basic information
            st.markdown("**Basic Information**")
            new_name = st.text_input("Name:", value=user_data.get("name", ""))
            new_username = st.text_input("Username:", value=user_data.get("username", ""))
            new_email = st.text_input("Email:", value=user_data.get("email", ""), disabled=True, help="Email cannot be changed")
            
            # Location
            st.markdown("**Location**")
            new_country = st.text_input("Country:", value=user_data.get("country", ""))
            new_state = st.text_input("State:", value=user_data.get("state", ""))
            
        with col2:
            # Settings
            st.markdown("**Settings**")
            unit_system_options = ["Imperial", "Metric"]
            current_unit_system = user_data.get("unit_system", "Imperial")
            new_unit_system = st.selectbox(
                "Unit System:", 
                options=unit_system_options,
                index=unit_system_options.index(current_unit_system) if current_unit_system in unit_system_options else 0
            )
            
            new_profile_complete = st.checkbox(
                "Profile Complete:", 
                value=user_data.get("profile_complete", False)
            )
            
            # Roles management
            st.markdown("**Roles**")
            current_roles = user_data.get("roles", ["user"])
            if not isinstance(current_roles, list):
                current_roles = ["user"]
                
            # Individual role checkboxes
            has_user_role = st.checkbox("User Role", value="user" in current_roles)
            has_admin_role = st.checkbox("Admin Role", value="admin" in current_roles)
            
            # Build new roles list
            new_roles = []
            if has_user_role:
                new_roles.append("user")
            if has_admin_role:
                new_roles.append("admin")
            
            # Ensure at least user role
            if not new_roles:
                new_roles = ["user"]
                st.warning("⚠️ Users must have at least the 'user' role.")

        # Picture URL (if exists)
        new_picture = st.text_input("Picture URL:", value=user_data.get("picture", ""))
        
        # Display current picture if exists
        if user_data.get("picture"):
            try:
                st.image(user_data["picture"], width=100, caption="Current Profile Picture")
            except:
                st.warning("Unable to display current profile picture")

        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        if submitted:
            try:
                # Prepare update data
                update_data = {
                    "name": new_name.strip(),
                    "username": new_username.strip(),
                    "country": new_country.strip(),
                    "state": new_state.strip(),
                    "unit_system": new_unit_system,
                    "profile_complete": new_profile_complete,
                    "roles": new_roles,
                    "picture": new_picture.strip() if new_picture.strip() else None,
                    "updated_at": datetime.now().isoformat(),
                }

                # Update the user in the database
                response = (
                    supabase.table("users")
                    .update(update_data)
                    .eq("id", user_data["id"])
                    .execute()
                )

                if response.data:
                    st.success("✅ User updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update user.")

            except Exception as e:
                st.error(f"❌ Error updating user: {str(e)}")


def render_user_delete_form(user_data, supabase):
    """Render the user deletion form"""
    st.markdown(f"**Delete user:** {user_data.get('name', 'Unknown')} ({user_data.get('email', 'Unknown')})")
    
    # Display user information
    st.markdown("**User Information:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {user_data.get('name', 'N/A')}")
        st.write(f"**Email:** {user_data.get('email', 'N/A')}")
        st.write(f"**Username:** {user_data.get('username', 'N/A')}")
        st.write(f"**Country:** {user_data.get('country', 'N/A')}")
        st.write(f"**State:** {user_data.get('state', 'N/A')}")
        
    with col2:
        st.write(f"**Unit System:** {user_data.get('unit_system', 'N/A')}")
        st.write(f"**Profile Complete:** {user_data.get('profile_complete', False)}")
        roles = user_data.get('roles', ['user'])
        roles_text = ", ".join(roles) if isinstance(roles, list) else str(roles)
        st.write(f"**Roles:** {roles_text}")
        created_at = user_data.get('created_at', '')
        if created_at:
            try:
                formatted_date = pd.to_datetime(created_at).strftime('%Y-%m-%d %H:%M')
                st.write(f"**Created:** {formatted_date}")
            except:
                st.write(f"**Created:** {created_at}")

    # Safety checks
    user_roles = user_data.get('roles', [])
    is_admin = isinstance(user_roles, list) and 'admin' in user_roles
    
    # Warning messages
    st.markdown("---")
    st.error("⚠️ **DANGER ZONE** ⚠️")
    st.warning("This action **CANNOT** be undone. The user and all associated data will be permanently deleted.")
    
    if is_admin:
        st.error("🚨 **WARNING:** This user has admin privileges!")
    
    # Check for related data
    try:
        user_email = user_data.get('email', '')
        
        # Check for user data in various tables
        related_data = []
        
        # Check common tables that might have user data
        tables_to_check = [
            "chrono_sessions", "chrono_measurements", "dope_sessions", "dope_measurements",
            "weather_measurements", "weather_source", "ranges_submissions", "rifles", "bullets"
        ]
        
        for table in tables_to_check:
            try:
                count_response = (
                    supabase.table(table)
                    .select("id", count="exact")
                    .eq("user_email", user_email)
                    .execute()
                )
                if count_response.count and count_response.count > 0:
                    related_data.append(f"{table}: {count_response.count} records")
            except:
                # Table might not exist or might not have user_email column
                continue
        
        if related_data:
            st.warning("**User has associated data that will also be deleted:**")
            for data in related_data:
                st.write(f"• {data}")
                
    except Exception as e:
        st.warning(f"Unable to check for related data: {str(e)}")

    # Confirmation process
    st.markdown("### Confirmation Required")
    st.markdown("Type the user's **email address** to confirm deletion:")
    
    confirmation_email = st.text_input(
        "Confirm email:",
        placeholder="Enter user's email address to confirm deletion",
        key=f"delete_confirmation_{user_data.get('id')}"
    )
    
    # Enable delete button only if confirmation matches
    email_matches = confirmation_email.strip() == user_data.get('email', '')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        delete_button = st.button(
            "🗑️ **DELETE USER PERMANENTLY**",
            type="secondary",
            disabled=not email_matches,
            use_container_width=True,
            key=f"delete_user_button_{user_data.get('id')}"
        )
    
    if not email_matches and confirmation_email.strip():
        st.error("❌ Email confirmation does not match. Please type the exact email address.")
    
    if delete_button and email_matches:
        try:
            # Delete user from database
            delete_response = (
                supabase.table("users")
                .delete()
                .eq("id", user_data["id"])
                .execute()
            )
            
            if delete_response.data:
                st.success(f"✅ User '{user_data.get('name', 'Unknown')}' has been permanently deleted.")
                st.info("🔄 Refreshing page...")
                st.rerun()
            else:
                st.error("❌ Failed to delete user. Please try again.")
                
        except Exception as e:
            st.error(f"❌ Error deleting user: {str(e)}")
            
            # Check if it's a foreign key constraint error
            if "foreign key constraint" in str(e).lower() or "violates foreign key" in str(e).lower():
                st.error("🔗 **Cannot delete user:** This user has associated data in other tables.")
                st.info("💡 **Suggestion:** You may need to delete or transfer the user's data first before deleting the user account.")
            
    if email_matches:
        st.info("✅ Confirmation verified. You can now delete this user.")
    else:
        st.info("⏳ Enter the user's email address above to enable the delete button.")
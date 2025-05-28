import streamlit as st
import pandas as pd
from utils.auth import get_auth_manager

def init_auth_manager():
    """Initialize auth manager"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = get_auth_manager()
    return st.session_state.auth_manager

def main():
    st.set_page_config(page_title="User Management - QRMS", page_icon="👥")
    
    auth_manager = init_auth_manager()
    
    # Check authentication
    if not auth_manager.is_authenticated():
        st.warning("Please login from the main page to access this feature.")
        st.stop()
    
    current_user = auth_manager.get_current_user()
    
    # Check permissions - only Super Admin and Admin can access this page
    if current_user['role'] not in ['super_admin', 'admin']:
        st.error("Access denied. You don't have permission to access User Management.")
        st.stop()
    
    # Show user info in sidebar
    auth_manager.show_user_info()
    
    st.title("👥 User Management")
    st.markdown("---")
    
    # Create tabs for different functions
    if current_user['role'] == 'super_admin':
        tab1, tab2, tab3, tab4 = st.tabs(["Create Users", "Manage Users", "View All Users", "🔐 Credentials View"])
    else:  # admin
        tab1, tab2, tab3 = st.tabs(["Create Users", "Manage Users", "View Users"])
    
    with tab1:
        st.subheader("Create New User")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username", placeholder="Enter unique username")
                new_email = st.text_input("Email", placeholder="user@company.com")
                new_full_name = st.text_input("Full Name", placeholder="Enter full name")
            
            with col2:
                new_password = st.text_input("Password", type="password", placeholder="Enter secure password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                
                # Role selection based on current user's role
                if current_user['role'] == 'super_admin':
                    role_options = ['super_admin', 'admin', 'user']
                    role_labels = ['Super Admin', 'Admin', 'User']
                else:  # admin can only create users
                    role_options = ['user']
                    role_labels = ['User']
                
                new_role = st.selectbox("Role", options=role_options, format_func=lambda x: dict(zip(role_options, role_labels))[x])
            
            department = st.text_input("Department", placeholder="e.g., Manufacturing, Quality Control")
            
            submit_button = st.form_submit_button("Create User", type="primary")
            
            if submit_button:
                # Validation
                if not all([new_username, new_email, new_full_name, new_password, confirm_password]):
                    st.error("Please fill in all required fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif auth_manager.user_exists(new_username):
                    st.error("Username already exists. Please choose a different username.")
                else:
                    # Create the user
                    success = auth_manager.create_user(
                        username=new_username,
                        password=new_password,
                        email=new_email,
                        full_name=new_full_name,
                        role=new_role,
                        department=department,
                        created_by=current_user['username']
                    )
                    
                    if success:
                        st.success(f"User '{new_username}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Please try again.")
    
    with tab2:
        st.subheader("Manage Existing Users")
        
        users_df = auth_manager.get_users_dataframe()
        
        if users_df.empty:
            st.info("No users found.")
        else:
            # Filter users based on permissions
            if current_user['role'] == 'admin':
                # Admins can only see and manage users, not super_admins or other admins
                users_df = users_df[users_df['role'] == 'user']
            
            if not users_df.empty:
                # User selection for management
                selected_user = st.selectbox(
                    "Select User to Manage",
                    options=users_df['username'].tolist(),
                    format_func=lambda x: f"{x} ({users_df[users_df['username']==x]['full_name'].iloc[0]}) - {users_df[users_df['username']==x]['role'].iloc[0].title()}"
                )
                
                if selected_user:
                    user_data = users_df[users_df['username'] == selected_user].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current Information:**")
                        st.write(f"Username: {user_data['username']}")
                        st.write(f"Full Name: {user_data['full_name']}")
                        st.write(f"Email: {user_data['email']}")
                        st.write(f"Role: {user_data['role'].title()}")
                        st.write(f"Department: {user_data.get('department', 'Not specified')}")
                        st.write(f"Created: {user_data.get('created_date', 'Unknown')}")
                    
                    with col2:
                        st.write("**Actions:**")
                        
                        # Reset Password
                        with st.form(f"reset_password_{selected_user}"):
                            st.write("Reset Password:")
                            new_password = st.text_input("New Password", type="password", key=f"new_pass_{selected_user}")
                            confirm_new_password = st.text_input("Confirm New Password", type="password", key=f"confirm_pass_{selected_user}")
                            
                            if st.form_submit_button("Reset Password"):
                                if not new_password or not confirm_new_password:
                                    st.error("Please enter both password fields.")
                                elif new_password != confirm_new_password:
                                    st.error("Passwords do not match.")
                                elif len(new_password) < 6:
                                    st.error("Password must be at least 6 characters long.")
                                else:
                                    if auth_manager.reset_user_password(selected_user, new_password):
                                        st.success("Password reset successfully!")
                                    else:
                                        st.error("Failed to reset password.")
                        
                        # Delete User (only if not the current user)
                        if selected_user != current_user['username']:
                            st.write("---")
                            if st.button(f"Delete User: {selected_user}", type="secondary"):
                                if auth_manager.delete_user(selected_user):
                                    st.success(f"User '{selected_user}' deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete user.")
            else:
                st.info("No users available for management with your current permissions.")
    
    with tab3:
        st.subheader("User List")
        
        users_df = auth_manager.get_users_dataframe()
        
        if users_df.empty:
            st.info("No users found.")
        else:
            # Filter based on role permissions
            if current_user['role'] == 'admin':
                display_df = users_df[users_df['role'].isin(['admin', 'user'])]
            else:  # super_admin
                display_df = users_df
            
            if not display_df.empty:
                # Format the dataframe for display
                display_columns = ['username', 'full_name', 'email', 'role', 'department', 'created_date', 'last_login']
                available_columns = [col for col in display_columns if col in display_df.columns]
                
                formatted_df = display_df[available_columns].copy()
                
                # Format role names
                if 'role' in formatted_df.columns:
                    formatted_df['role'] = formatted_df['role'].str.title().str.replace('_', ' ')
                
                # Format column names
                column_mapping = {
                    'username': 'Username',
                    'full_name': 'Full Name',
                    'email': 'Email',
                    'role': 'Role',
                    'department': 'Department',
                    'created_date': 'Created Date',
                    'last_login': 'Last Login'
                }
                
                formatted_df = formatted_df.rename(columns=column_mapping)
                
                st.dataframe(formatted_df, use_container_width=True)
                
                # Summary statistics
                st.write("**Summary:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Users", len(display_df))
                
                with col2:
                    if current_user['role'] == 'super_admin':
                        admin_count = len(display_df[display_df['role'] == 'super_admin']) + len(display_df[display_df['role'] == 'admin'])
                        st.metric("Admins", admin_count)
                    else:
                        st.metric("Regular Users", len(display_df[display_df['role'] == 'user']))
                
                with col3:
                    active_users = len(display_df[display_df['last_login'].notna()]) if 'last_login' in display_df.columns else 0
                    st.metric("Active Users", active_users)
            else:
                st.info("No users visible with your current permissions.")
    
    # Super Admin only - Credentials View Tab
    if current_user['role'] == 'super_admin':
        with tab4:
            st.subheader("🔐 All User Credentials")
            st.warning("⚠️ **Security Notice**: This view shows all user passwords. This information is highly sensitive and should only be accessed by authorized Super Administrators.")
            
            # Add confirmation checkbox
            show_passwords = st.checkbox("🔓 I understand the security implications and want to view all credentials", key="show_credentials_checkbox")
            
            if show_passwords:
                # Get users with passwords (Super Admin only feature)
                credentials_df = auth_manager.get_users_with_passwords()
                
                if credentials_df.empty:
                    st.info("No user credentials found.")
                else:
                    st.markdown("### 📋 Complete User Credentials List")
                    
                    # Format the dataframe for credentials view
                    display_columns = ['username', 'password', 'full_name', 'email', 'role', 'department', 'created_date', 'last_login']
                    available_columns = [col for col in display_columns if col in credentials_df.columns]
                    
                    formatted_df = credentials_df[available_columns].copy()
                    
                    # Format role names
                    if 'role' in formatted_df.columns:
                        formatted_df['role'] = formatted_df['role'].str.title().str.replace('_', ' ')
                    
                    # Format column names
                    column_mapping = {
                        'username': 'Username',
                        'password': '🔑 Password',
                        'full_name': 'Full Name',
                        'email': 'Email',
                        'role': 'Role',
                        'department': 'Department',
                        'created_date': 'Created Date',
                        'last_login': 'Last Login'
                    }
                    
                    formatted_df = formatted_df.rename(columns=column_mapping)
                    
                    # Display the credentials table
                    st.dataframe(formatted_df, use_container_width=True)
                    
                    # Role-based summary
                    st.markdown("### 📊 Role Distribution")
                    role_counts = credentials_df['role'].value_counts()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        super_admin_count = role_counts.get('super_admin', 0)
                        st.metric("Super Admins", super_admin_count)
                    
                    with col2:
                        admin_count = role_counts.get('admin', 0)
                        st.metric("Admins", admin_count)
                    
                    with col3:
                        user_count = role_counts.get('user', 0)
                        st.metric("Users", user_count)
                    
                    with col4:
                        total_users = len(credentials_df)
                        st.metric("Total Users", total_users)
                    
                    # Export credentials (Super Admin only)
                    st.markdown("### 📥 Export Credentials")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📋 Copy All Credentials to Clipboard", type="secondary"):
                            credentials_text = ""
                            for _, row in credentials_df.iterrows():
                                credentials_text += f"Username: {row['username']}\n"
                                credentials_text += f"Password: {row['password']}\n"
                                credentials_text += f"Role: {row['role']}\n"
                                credentials_text += f"Full Name: {row['full_name']}\n"
                                credentials_text += f"Email: {row['email']}\n"
                                credentials_text += "---\n"
                            
                            st.code(credentials_text, language="text")
                            st.success("✅ Credentials formatted for copying!")
                    
                    with col2:
                        # Download as CSV
                        csv_data = formatted_df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Credentials CSV",
                            data=csv_data,
                            file_name=f"user_credentials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            type="secondary"
                        )
                    
                    # Security reminder
                    st.markdown("---")
                    st.error("🚨 **Security Reminder**: Never share these credentials via email, chat, or unsecured channels. Always use secure methods for credential distribution.")
            
            else:
                st.info("🔒 Check the box above to view sensitive credential information.")

if __name__ == "__main__":
    main()
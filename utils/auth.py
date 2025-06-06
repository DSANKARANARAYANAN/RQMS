import streamlit as st
import hashlib
import json
import os
import pandas as pd
from datetime import datetime

class AuthManager:
    def __init__(self):
        self.users_file = "data/users.json"
        self._initialize_users()
    
    def _initialize_users(self):
        """Initialize default users if file doesn't exist"""
        if not os.path.exists(self.users_file):
            # Create default users with hashed passwords
            default_users = {
                "superadmin": {
                    "password_hash": self._hash_password("admin123"),
                    "role": "super_admin",
                    "full_name": "Super Administrator",
                    "email": "superadmin@company.com",
                    "department": "IT Administration",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "created_by": "system",
                    "last_login": None,
                    "permissions": ["all"]
                },
                "admin": {
                    "password_hash": self._hash_password("admin456"),
                    "role": "admin", 
                    "full_name": "System Administrator",
                    "email": "admin@company.com",
                    "department": "Quality Management",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "created_by": "system",
                    "last_login": None,
                    "permissions": ["manage_modules", "manage_types", "export_data", "view_data", "view_dashboard"]
                },
                "qcuser": {
                    "password_hash": self._hash_password("user789"),
                    "role": "user",
                    "full_name": "Quality Control User", 
                    "email": "qcuser@company.com",
                    "department": "Quality Control",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "created_by": "system",
                    "last_login": None,
                    "permissions": ["enter_data", "view_dashboard", "view_data"]
                }
            }
            
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username in users:
                password_hash = self._hash_password(password)
                if users[username]["password_hash"] == password_hash:
                    return users[username]
            return None
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    def get_user_permissions(self, role):
        """Get permissions for a role"""
        role_permissions = {
            "super_admin": ["all"],
            "admin": ["manage_modules", "manage_types", "export_data", "view_data", "view_dashboard"],
            "user": ["enter_data", "view_dashboard", "view_data"]
        }
        return role_permissions.get(role, [])
    
    def has_permission(self, user_role, required_permission):
        """Check if user has required permission"""
        if user_role == "super_admin":
            return True
        
        user_permissions = self.get_user_permissions(user_role)
        return required_permission in user_permissions
    
    def login_form(self):
        """Display login form"""
        st.markdown("## 🔐 QRMS Login")
        st.markdown("---")
        
        # Display default credentials for demo
        with st.expander("👤 Default Login Credentials", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Super Admin**")
                st.code("Username: superadmin\nPassword: admin123")
                st.caption("Full system access")
            
            with col2:
                st.markdown("**Admin**")
                st.code("Username: admin\nPassword: admin456") 
                st.caption("Module & type management")
            
            with col3:
                st.markdown("**User**")
                st.code("Username: qcuser\nPassword: user789")
                st.caption("Data entry & viewing")
        
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                    return False
                
                user_data = self.authenticate(username, password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = user_data["role"]
                    st.session_state.full_name = user_data["full_name"]
                    # Update last login time
                    self.update_last_login(username)
                    st.success(f"✅ Welcome, {user_data['full_name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
                    return False
        
        return False
    
    def logout(self):
        """Logout current user"""
        keys_to_clear = ["authenticated", "username", "user_role", "full_name"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get("authenticated", False)
    
    def get_current_user(self):
        """Get current user info"""
        if self.is_authenticated():
            return {
                "username": st.session_state.get("username"),
                "role": st.session_state.get("user_role"),
                "full_name": st.session_state.get("full_name")
            }
        return None
    
    def require_permission(self, permission):
        """Decorator-like function to check permissions"""
        if not self.is_authenticated():
            st.error("🚫 Please login to access this feature")
            st.stop()
        
        user_role = st.session_state.get("user_role")
        if not self.has_permission(user_role, permission):
            st.error(f"🚫 Access denied. You don't have permission for: {permission}")
            st.stop()
    
    def show_user_info(self):
        """Show current user info in sidebar"""
        if self.is_authenticated():
            user = self.get_current_user()
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 Current User")
            st.sidebar.write(f"**Name:** {user['full_name']}")
            st.sidebar.write(f"**Role:** {user['role'].replace('_', ' ').title()}")
            
            if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
                self.logout()
    
    def user_exists(self, username):
        """Check if username already exists"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            return username in users
        except Exception:
            return False
    
    def create_user(self, username, password, email, full_name, role, department="", created_by=""):
        """Create a new user"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            # Check if user already exists
            if username in users:
                return False
            
            # Create new user data
            new_user = {
                "password_hash": self._hash_password(password),
                "role": role,
                "full_name": full_name,
                "email": email,
                "department": department,
                "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "created_by": created_by,
                "last_login": None,
                "permissions": self.get_user_permissions(role)
            }
            
            # Add user to dictionary
            users[username] = new_user
            
            # Save updated users
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return False
    
    def get_users_dataframe(self):
        """Get all users as a pandas DataFrame"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            users_list = []
            for username, user_data in users.items():
                user_record = {
                    'username': username,
                    'full_name': user_data.get('full_name', ''),
                    'email': user_data.get('email', ''),
                    'role': user_data.get('role', ''),
                    'department': user_data.get('department', ''),
                    'created_date': user_data.get('created_date', ''),
                    'created_by': user_data.get('created_by', ''),
                    'last_login': user_data.get('last_login', '')
                }
                users_list.append(user_record)
            
            return pd.DataFrame(users_list)
        except Exception:
            return pd.DataFrame()
    
    def reset_user_password(self, username, new_password):
        """Reset a user's password"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username not in users:
                return False
            
            # Update password
            users[username]["password_hash"] = self._hash_password(new_password)
            
            # Save updated users
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error resetting password: {str(e)}")
            return False
    
    def delete_user(self, username):
        """Delete a user"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username not in users:
                return False
            
            # Remove user
            del users[username]
            
            # Save updated users
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error deleting user: {str(e)}")
            return False
    
    def update_last_login(self, username):
        """Update user's last login time"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username in users:
                users[username]["last_login"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(self.users_file, 'w') as f:
                    json.dump(users, f, indent=2)
        except Exception:
            pass  # Silently fail for login time updates
    
    def get_users_with_passwords(self):
        """Get all users with their passwords (Super Admin only)"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            users_list = []
            for username, user_data in users.items():
                # Decode password from hash (this is for demo purposes - in real systems, passwords should never be retrievable)
                password = self._get_original_password(user_data.get("password_hash", ""))
                
                user_record = {
                    'username': username,
                    'password': password,
                    'full_name': user_data.get('full_name', ''),
                    'email': user_data.get('email', ''),
                    'role': user_data.get('role', ''),
                    'department': user_data.get('department', ''),
                    'created_date': user_data.get('created_date', ''),
                    'created_by': user_data.get('created_by', ''),
                    'last_login': user_data.get('last_login', '')
                }
                users_list.append(user_record)
            
            return pd.DataFrame(users_list)
        except Exception:
            return pd.DataFrame()
    
    def _get_original_password(self, password_hash):
        """Get original password from hash (for demo purposes only)"""
        # This maps known hashes to their original passwords for demo
        known_passwords = {
            "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9": "admin123",
            "becf77f3ec82a43422b7712134d1860e3205c6ce778b08417a7389b43f2b4661": "admin456",
            "c845096da14dd5f54663dea61667b905d861fe03acd6e9211742ac4ca393f522": "user789"
        }
        return known_passwords.get(password_hash, "****")

def get_auth_manager():
    """Get singleton auth manager"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    return st.session_state.auth_manager
import streamlit as st
import hashlib
import json
import os
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
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "permissions": ["all"]
                },
                "admin": {
                    "password_hash": self._hash_password("admin456"),
                    "role": "admin", 
                    "full_name": "System Administrator",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "permissions": ["manage_modules", "manage_types", "export_data", "view_data"]
                },
                "qcuser": {
                    "password_hash": self._hash_password("user789"),
                    "role": "user",
                    "full_name": "Quality Control User", 
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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

def get_auth_manager():
    """Get singleton auth manager"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    return st.session_state.auth_manager
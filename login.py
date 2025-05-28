import streamlit as st
from utils.auth import get_auth_manager

def main():
    st.set_page_config(
        page_title="QRMS Login", 
        page_icon="🔐",
        layout="centered"
    )
    
    auth_manager = get_auth_manager()
    
    # Check if already authenticated
    if auth_manager.is_authenticated():
        st.success("✅ You are already logged in!")
        st.info("🔄 Click the button below to go to the main application")
        if st.button("🚀 Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")
        return
    
    # Custom CSS for login page
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .sub-header {
            text-align: center;
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: #ffffff;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">🏭 QRMS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Quality Rejection Management System</div>', unsafe_allow_html=True)
    
    # Login container
    with st.container():
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
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Please Login")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
            with col2:
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
            
            st.markdown("")  # Add some space
            login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    user_data = auth_manager.authenticate(username, password)
                    if user_data:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = user_data["role"]
                        st.session_state.full_name = user_data["full_name"]
                        # Update last login time
                        auth_manager.update_last_login(username)
                        st.success(f"✅ Welcome, {user_data['full_name']}!")
                        st.balloons()
                        
                        # Redirect to main application
                        st.info("🔄 Redirecting to dashboard...")
                        st.switch_page("pages/00_Dashboard.py")
                    else:
                        st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.markdown(
            '<div style="text-align: center; color: #888; font-size: 0.9rem;">'
            '© 2025 Quality Rejection Management System | Secure Manufacturing Solutions'
            '</div>', 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
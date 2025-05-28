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
    
    # Modern CSS for professional login page
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Inter', sans-serif;
        }
        
        .main-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .sub-header {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.2rem;
            font-weight: 400;
            margin-bottom: 3rem;
        }
        
        .login-container {
            max-width: 480px;
            margin: 2rem auto;
            padding: 3rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .credentials-section {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
        }
        
        .credentials-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .credential-item {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }
        
        .credential-item:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        .credential-role {
            font-weight: 600;
            color: #4f46e5;
            font-size: 0.9rem;
        }
        
        .credential-details {
            color: #6b7280;
            font-size: 0.85rem;
            font-family: 'Monaco', 'Menlo', monospace;
            margin-top: 0.25rem;
        }
        
        .stTextInput > div > div > input {
            border-radius: 12px;
            border: 2px solid #e5e7eb;
            padding: 0.875rem 1.25rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 12px;
            padding: 0.875rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1.5rem;
            color: white;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        
        .success-banner {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1.25rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }
        
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
            margin: 2rem 0;
        }
        
        .stAlert > div {
            border-radius: 12px;
            border: none;
            padding: 1rem 1.25rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Modern Header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🏭 QRMS</div>
        <div class="sub-header">Quality Rejection Management System</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern login container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Stylized credentials section
    st.markdown("""
    <div class="credentials-section">
        <div class="credentials-title">🔑 Default Login Credentials</div>
        <div class="credential-item">
            <div class="credential-role">Super Admin</div>
            <div class="credential-details">Username: superadmin | Password: admin123</div>
        </div>
        <div class="credential-item">
            <div class="credential-role">Admin</div>
            <div class="credential-details">Username: admin | Password: admin456</div>
        </div>
        <div class="credential-item">
            <div class="credential-role">User</div>
            <div class="credential-details">Username: qcuser | Password: user789</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    # Login form with modern styling
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
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
import streamlit as st
import os
from utils.email_sender import EmailSender
from utils.scheduler import get_scheduler, start_scheduler

# Page configuration
st.set_page_config(
    page_title="Email Settings - QRMS",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Email Settings & Automated Reports")
st.markdown("Configure email settings for automated daily reports")
st.markdown("---")

# Initialize email sender
email_sender = EmailSender()

# Email Configuration Section
st.subheader("⚙️ Email Configuration")

with st.expander("📋 Current Configuration", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**SMTP Server:**", email_sender.smtp_server)
        st.write("**SMTP Port:**", email_sender.smtp_port)
        st.write("**Email User:**", email_sender.email_user or "Not configured")
    
    with col2:
        st.write("**Password Status:**", "✅ Configured" if email_sender.email_password else "❌ Not configured")
        manager_count = len([e for e in email_sender.manager_emails if e.strip()])
        st.write("**Manager Emails:**", f"{manager_count} configured")
        
        # Show scheduler status
        scheduler = get_scheduler()
        if scheduler and scheduler.is_running:
            st.write("**Scheduler Status:**", "🟢 Running")
        else:
            st.write("**Scheduler Status:**", "🔴 Stopped")

# Configuration Instructions
st.subheader("🔧 Setup Instructions")

with st.expander("📖 How to Configure Email Settings"):
    st.markdown("""
    **Environment Variables Required:**
    
    To enable automated email reports, set these environment variables:
    
    ```bash
    # Email server settings
    SMTP_SERVER=smtp.gmail.com              # Your SMTP server
    SMTP_PORT=587                           # SMTP port (usually 587 for TLS)
    
    # Authentication
    EMAIL_USER=your-email@company.com       # Sender email address
    EMAIL_PASSWORD=your-app-password        # Email password or app password
    
    # Recipients
    MANAGER_EMAILS=manager1@company.com,manager2@company.com
    
    # Schedule (optional)
    DAILY_REPORT_TIME=08:00                 # Time for daily reports (24-hour format)
    ```
    
    **For Gmail Users:**
    - Use your Gmail address for EMAIL_USER
    - Generate an App Password (not your regular password)
    - Enable 2-Factor Authentication first
    - Go to: Google Account → Security → App passwords
    
    **For Other Email Providers:**
    - Check your provider's SMTP settings
    - Use appropriate server and port
    - Some providers require app-specific passwords
    """)

# Test Email Functionality
st.subheader("🧪 Test Email Configuration")

with st.form("test_email"):
    test_email = st.text_input(
        "Test Email Address",
        help="Enter an email address to test the configuration"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        test_submitted = st.form_submit_button("📤 Send Test Email", type="primary")

if test_submitted:
    if not test_email.strip():
        st.error("❌ Please enter a test email address")
    else:
        with st.spinner("Sending test email..."):
            success, message = email_sender.send_test_email(test_email.strip())
        
        if success:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")

# Manual Report Generation
st.subheader("📊 Manual Report Generation")

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("📨 Send Daily Report Now", type="primary"):
        if not email_sender.email_user or not email_sender.email_password:
            st.error("❌ Email credentials not configured")
        elif not any(email.strip() for email in email_sender.manager_emails):
            st.error("❌ Manager emails not configured")
        else:
            with st.spinner("Generating and sending report..."):
                success, message = email_sender.send_daily_report()
            
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

with col2:
    st.info("💡 This will send a report with yesterday's rejection data to all configured manager emails")

# Schedule Configuration
st.subheader("⏰ Report Schedule")

current_time = os.getenv("DAILY_REPORT_TIME", "08:00")
st.write(f"**Current Schedule:** Daily reports at {current_time}")

with st.expander("📅 Schedule Information"):
    st.markdown(f"""
    **Current Configuration:**
    - Daily reports are scheduled to run at **{current_time}** every day
    - Reports include rejection data from the previous 24 hours
    - All configured manager emails will receive the report
    
    **To Change Schedule:**
    - Set the `DAILY_REPORT_TIME` environment variable
    - Use 24-hour format (e.g., "08:00", "14:30")
    - Restart the application after changing
    
    **Report Content:**
    - Summary metrics (total rejections, quantities)
    - Breakdown by module and rejection type
    - Recent rejection records
    - Professional HTML formatting
    """)

# Scheduler Controls
st.subheader("🎛️ Scheduler Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Scheduler"):
        start_scheduler()
        st.success("✅ Scheduler started")
        st.rerun()

with col2:
    if st.button("⏹️ Stop Scheduler"):
        from utils.scheduler import stop_scheduler
        stop_scheduler()
        st.success("✅ Scheduler stopped")
        st.rerun()

with col3:
    if st.button("🔄 Restart Scheduler"):
        from utils.scheduler import stop_scheduler
        stop_scheduler()
        start_scheduler()
        st.success("✅ Scheduler restarted")
        st.rerun()

# Email Preview
st.subheader("👀 Email Preview")

if st.button("📋 Preview Report Content"):
    from utils.data_manager import DataManager
    from datetime import datetime, timedelta
    
    data_manager = DataManager()
    yesterday = datetime.now() - timedelta(days=1)
    start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    summary = data_manager.get_rejection_summary(start_of_yesterday, end_of_yesterday)
    html_content = email_sender.create_daily_report_html(summary)
    
    st.components.v1.html(html_content, height=600, scrolling=True)

st.markdown("---")

# Quick Actions
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Go to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("📝 Data Entry"):
        st.switch_page("pages/01_Data_Entry.py")

with col3:
    if st.button("🔧 Manage Types"):
        st.switch_page("pages/02_Manage_Types.py")

# Status Summary
st.markdown("---")
st.subheader("📊 Configuration Status")

status_items = []

# Check email configuration
if email_sender.email_user and email_sender.email_password:
    status_items.append("✅ Email credentials configured")
else:
    status_items.append("❌ Email credentials missing")

# Check manager emails
if any(email.strip() for email in email_sender.manager_emails):
    manager_count = len([e for e in email_sender.manager_emails if e.strip()])
    status_items.append(f"✅ {manager_count} manager email(s) configured")
else:
    status_items.append("❌ No manager emails configured")

# Check scheduler
scheduler = get_scheduler()
if scheduler and scheduler.is_running:
    status_items.append("✅ Automated scheduler is running")
else:
    status_items.append("❌ Automated scheduler is not running")

for item in status_items:
    st.write(item)

if all("✅" in item for item in status_items):
    st.success("🎉 All email features are properly configured!")
else:
    st.warning("⚠️ Some email features need configuration. Check the setup instructions above.")

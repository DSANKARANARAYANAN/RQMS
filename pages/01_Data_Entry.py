import streamlit as st
from datetime import datetime, time
from utils.data_manager import DataManager

# Page configuration
st.set_page_config(
    page_title="Data Entry - QRMS",
    page_icon="📝",
    layout="wide"
)

# Initialize data manager
@st.cache_resource
def init_data_manager():
    return DataManager()

data_manager = init_data_manager()

st.title("📝 Rejection Data Entry")
st.markdown("Enter new rejection records for manufacturing modules")
st.markdown("---")

# Load available modules and rejection types
modules_df = data_manager.load_modules()
types_df = data_manager.load_rejection_types()

# Check if modules and types are available
if modules_df.empty:
    st.error("⚠️ No modules configured. Please go to 'Manage Types' page to add modules first.")
    st.stop()

if types_df.empty:
    st.error("⚠️ No rejection types configured. Please go to 'Manage Types' page to add rejection types first.")
    st.stop()

# Data entry form
st.subheader("🔧 New Rejection Entry")

with st.form("rejection_entry"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Module selection
        selected_module = st.selectbox(
            "Select Module *",
            options=modules_df['name'].tolist(),
            help="Choose the manufacturing module where rejection occurred"
        )
        
        # Rejection type selection
        selected_type = st.selectbox(
            "Rejection Type *",
            options=types_df['name'].tolist(),
            help="Select the type of rejection"
        )
        
        # Quantity
        quantity = st.number_input(
            "Quantity Rejected *",
            min_value=1,
            value=1,
            help="Number of units rejected"
        )
    
    with col2:
        # Operator name
        operator = st.text_input(
            "Operator Name *",
            help="Name of the operator reporting the rejection"
        )
        
        # Shift
        shift = st.selectbox(
            "Shift *",
            options=["Day", "Evening", "Night"],
            help="Select the working shift"
        )
        
        # Date and time (optional - defaults to current)
        entry_date = st.date_input(
            "Date",
            value=datetime.now().date(),
            help="Date of rejection (defaults to today)"
        )
        
        entry_time = st.time_input(
            "Time",
            value=datetime.now().time(),
            help="Time of rejection (defaults to current time)"
        )
    
    # Reason (full width)
    reason = st.text_area(
        "Reason for Rejection *",
        height=100,
        help="Detailed description of why the rejection occurred"
    )
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submitted = st.form_submit_button("✅ Submit Rejection", type="primary")
    with col2:
        reset = st.form_submit_button("🔄 Reset Form")

# Handle form submission
if submitted:
    # Validate required fields
    if not all([selected_module, selected_type, quantity, operator, reason]):
        st.error("❌ Please fill in all required fields marked with *")
    else:
        # Combine date and time
        entry_datetime = datetime.combine(entry_date, entry_time)
        
        # Add rejection record
        success, message = data_manager.add_rejection(
            module=selected_module,
            rejection_type=selected_type,
            quantity=quantity,
            reason=reason.strip(),
            operator=operator.strip(),
            shift=shift
        )
        
        if success:
            st.success(f"✅ {message}")
            st.balloons()
            # Auto-refresh the form
            st.rerun()
        else:
            st.error(f"❌ {message}")

if reset:
    st.rerun()

st.markdown("---")

# Recent entries section
st.subheader("📋 Recent Rejection Entries")

# Load recent rejections
rejections_df = data_manager.load_rejections()

if not rejections_df.empty:
    # Show last 10 entries
    recent_df = rejections_df.nlargest(10, 'date').copy()
    recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Display in a nice format
    st.dataframe(
        recent_df[['date', 'module', 'rejection_type', 'quantity', 'operator', 'shift', 'reason']],
        use_container_width=True,
        hide_index=True
    )
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        today_rejections = len(rejections_df[rejections_df['date'].dt.date == datetime.now().date()])
        st.metric("Today's Rejections", today_rejections)
    
    with col2:
        total_quantity_today = rejections_df[
            rejections_df['date'].dt.date == datetime.now().date()
        ]['quantity'].sum()
        st.metric("Today's Rejected Quantity", total_quantity_today)
    
    with col3:
        most_common_type = rejections_df['rejection_type'].mode()
        if not most_common_type.empty:
            st.metric("Most Common Type", most_common_type.iloc[0])
        else:
            st.metric("Most Common Type", "N/A")

else:
    st.info("📋 No rejection records found. Enter your first rejection above.")

# Quick actions
st.markdown("---")
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Go to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("📊 Batch Entry"):
        st.switch_page("pages/04_Batch_Entry.py")

with col3:
    if st.button("🔧 Manage Types & Modules"):
        st.switch_page("pages/02_Manage_Types.py")

with col4:
    if st.button("📧 Email Settings"):
        st.switch_page("pages/03_Email_Settings.py")

# Help section
with st.expander("❓ Help & Guidelines"):
    st.markdown("""
    **Data Entry Guidelines:**
    
    1. **Module**: Select the specific manufacturing module where the rejection occurred
    2. **Rejection Type**: Choose the appropriate rejection category
    3. **Quantity**: Enter the number of units rejected (must be at least 1)
    4. **Operator**: Enter the name of the person reporting the rejection
    5. **Shift**: Select the current working shift
    6. **Date/Time**: Defaults to current date and time, but can be adjusted if needed
    7. **Reason**: Provide a detailed explanation of why the rejection occurred
    
    **Tips:**
    - Be specific in your rejection reasons to help with analysis
    - Double-check the module and rejection type before submitting
    - All fields marked with * are required
    """)

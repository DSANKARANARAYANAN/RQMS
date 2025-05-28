import streamlit as st
import pandas as pd
from datetime import datetime, time
from utils.data_manager import DataManager

# Page configuration
st.set_page_config(
    page_title="Batch Entry - QRMS",
    page_icon="📊",
    layout="wide"
)

# Initialize data manager
@st.cache_resource
def init_data_manager():
    return DataManager()

data_manager = init_data_manager()

st.title("📊 Batch Rejection Data Entry")
st.markdown("Enter multiple rejection records efficiently using table format")
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

# Get lists for the table
modules_list = modules_df['name'].tolist()

# Create a function to get applicable types for a module
def get_applicable_types_for_module(module_name):
    if not module_name:
        return []
    return data_manager.get_rejection_types_for_module(module_name)

# Session state for table data
if 'batch_data' not in st.session_state:
    # Create initial empty rows
    st.session_state.batch_data = pd.DataFrame({
        'Module': [''] * 5,
        'Rejection_Type': [''] * 5,
        'Quantity': [0] * 5,
        'Reason': [''] * 5,
        'Operator': [''] * 5,
        'Shift': ['Day'] * 5
    })

# Common fields section
st.subheader("🔧 Common Entry Fields")
col1, col2, col3 = st.columns(3)

with col1:
    common_operator = st.text_input("Default Operator Name", help="Will be applied to empty operator fields")

with col2:
    common_shift = st.selectbox("Default Shift", ["Day", "Evening", "Night"], help="Will be applied to empty shift fields")

with col3:
    entry_date = st.date_input("Entry Date", value=datetime.now().date())

# Batch entry table
st.subheader("📋 Batch Entry Table")

# Create editable dataframe
edited_df = st.data_editor(
    st.session_state.batch_data,
    column_config={
        "Module": st.column_config.SelectboxColumn(
            "Module",
            help="Select the manufacturing module",
            options=modules_list,
            required=True
        ),
        "Rejection_Type": st.column_config.TextColumn(
            "Rejection Type",
            help="Enter rejection type (will be validated against module mapping)",
            max_chars=100
        ),
        "Quantity": st.column_config.NumberColumn(
            "Quantity",
            help="Number of rejected units",
            min_value=0,
            max_value=10000,
            step=1,
            format="%d"
        ),
        "Reason": st.column_config.TextColumn(
            "Reason",
            help="Reason for rejection",
            max_chars=200
        ),
        "Operator": st.column_config.TextColumn(
            "Operator",
            help="Operator name (leave empty to use default)",
            max_chars=50
        ),
        "Shift": st.column_config.SelectboxColumn(
            "Shift",
            help="Working shift",
            options=["Day", "Evening", "Night"]
        )
    },
    num_rows="dynamic",
    use_container_width=True,
    key="batch_entry_table"
)

# Update session state
st.session_state.batch_data = edited_df

# Control buttons
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Add 5 More Rows"):
        new_rows = pd.DataFrame({
            'Module': [''] * 5,
            'Rejection_Type': [''] * 5,
            'Quantity': [0] * 5,
            'Reason': [''] * 5,
            'Operator': [''] * 5,
            'Shift': ['Day'] * 5
        })
        st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_rows], ignore_index=True)
        st.rerun()

with col2:
    if st.button("🔄 Apply Defaults"):
        # Apply default operator and shift to empty fields
        for idx in range(len(st.session_state.batch_data)):
            if not st.session_state.batch_data.loc[idx, 'Operator']:
                st.session_state.batch_data.loc[idx, 'Operator'] = common_operator
            if not st.session_state.batch_data.loc[idx, 'Shift']:
                st.session_state.batch_data.loc[idx, 'Shift'] = common_shift
        st.rerun()

with col3:
    if st.button("🗑️ Clear Table"):
        st.session_state.batch_data = pd.DataFrame({
            'Module': [''] * 5,
            'Rejection_Type': [''] * 5,
            'Quantity': [0] * 5,
            'Reason': [''] * 5,
            'Operator': [''] * 5,
            'Shift': ['Day'] * 5
        })
        st.rerun()

with col4:
    if st.button("✅ Submit All Records", type="primary"):
        # Validate and submit records
        valid_records = []
        errors = []
        
        for idx, row in edited_df.iterrows():
            # Skip empty rows
            if not row['Module'] or not row['Rejection_Type'] or row['Quantity'] <= 0:
                continue
            
            # Validate rejection type is applicable to module
            applicable_types = data_manager.get_rejection_types_for_module(row['Module'])
            if row['Rejection_Type'] not in applicable_types:
                if applicable_types:
                    errors.append(f"Row {idx + 1}: '{row['Rejection_Type']}' is not valid for module '{row['Module']}'. Available types: {', '.join(applicable_types)}")
                else:
                    errors.append(f"Row {idx + 1}: No rejection types configured for module '{row['Module']}'")
                continue
            
            # Validate required fields
            if not row['Reason'].strip():
                errors.append(f"Row {idx + 1}: Reason is required")
                continue
            
            operator = row['Operator'].strip() if row['Operator'] else common_operator
            if not operator:
                errors.append(f"Row {idx + 1}: Operator is required")
                continue
            
            valid_records.append({
                'module': row['Module'],
                'rejection_type': row['Rejection_Type'],
                'quantity': int(row['Quantity']),
                'reason': row['Reason'].strip(),
                'operator': operator,
                'shift': row['Shift']
            })
        
        if errors:
            st.error("❌ Please fix the following errors:\n" + "\n".join(errors))
        elif not valid_records:
            st.warning("⚠️ No valid records to submit. Please fill in at least one complete row.")
        else:
            # Submit all valid records
            success_count = 0
            failed_records = []
            
            for record in valid_records:
                success, message = data_manager.add_rejection(**record)
                if success:
                    success_count += 1
                else:
                    failed_records.append(f"{record['module']} - {record['rejection_type']}: {message}")
            
            if success_count > 0:
                st.success(f"✅ Successfully submitted {success_count} rejection records!")
                st.balloons()
                
                # Clear the table after successful submission
                st.session_state.batch_data = pd.DataFrame({
                    'Module': [''] * 5,
                    'Rejection_Type': [''] * 5,
                    'Quantity': [0] * 5,
                    'Reason': [''] * 5,
                    'Operator': [''] * 5,
                    'Shift': ['Day'] * 5
                })
                st.rerun()
            
            if failed_records:
                st.error("❌ Failed to submit some records:\n" + "\n".join(failed_records))

# Summary section
st.markdown("---")
st.subheader("📊 Current Entry Summary")

if not edited_df.empty:
    # Filter out empty rows for summary
    summary_df = edited_df[
        (edited_df['Module'] != '') & 
        (edited_df['Rejection_Type'] != '') & 
        (edited_df['Quantity'] > 0)
    ]
    
    if not summary_df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_records = len(summary_df)
            st.metric("Records to Submit", total_records)
        
        with col2:
            total_quantity = summary_df['Quantity'].sum()
            st.metric("Total Quantity", total_quantity)
        
        with col3:
            unique_modules = summary_df['Module'].nunique()
            st.metric("Modules Affected", unique_modules)
        
        # Show summary by module
        if len(summary_df) > 0:
            st.subheader("📈 Summary by Module")
            module_summary = summary_df.groupby('Module')['Quantity'].sum().reset_index()
            module_summary.columns = ['Module', 'Total Quantity']
            st.dataframe(module_summary, use_container_width=True, hide_index=True)
    else:
        st.info("📋 No valid records in the table yet. Fill in the table above to see summary.")

# Quick actions
st.markdown("---")
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Go to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("📝 Single Data Entry"):
        st.switch_page("pages/01_Data_Entry.py")

with col3:
    if st.button("🔧 Manage Types"):
        st.switch_page("pages/02_Manage_Types.py")

with col4:
    if st.button("📧 Email Settings"):
        st.switch_page("pages/03_Email_Settings.py")

# Help section
with st.expander("❓ Help & Tips"):
    st.markdown("""
    **Batch Entry Guidelines:**
    
    **How to Use:**
    1. **Set Common Fields**: Enter default operator and shift that will apply to multiple rows
    2. **Fill the Table**: Use dropdowns to select modules and rejection types
    3. **Enter Details**: Add quantity, reason, and specific operator/shift if different
    4. **Apply Defaults**: Click to fill empty operator/shift fields with defaults
    5. **Submit**: Click "Submit All Records" to save all valid entries
    
    **Table Features:**
    - **Dynamic Rows**: Add more rows as needed
    - **Module Selection**: Choose from dropdown of configured modules
    - **Smart Validation**: Rejection types are validated against module mapping
    - **Bulk Operations**: Set common values and apply to multiple rows
    
    **Tips:**
    - Leave operator/shift empty to use defaults
    - Quantity must be greater than 0
    - Reason is required for each entry
    - Only rejection types mapped to the selected module are valid
    - Incomplete rows are automatically skipped
    - Table is cleared after successful submission
    """)
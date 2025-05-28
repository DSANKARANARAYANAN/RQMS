import streamlit as st
import pandas as pd
from utils.data_manager import DataManager

# Page configuration
st.set_page_config(
    page_title="Manage Types - QRMS",
    page_icon="🔧",
    layout="wide"
)

# Initialize data manager
@st.cache_resource
def init_data_manager():
    return DataManager()

data_manager = init_data_manager()

st.title("🔧 Manage Rejection Types & Modules")
st.markdown("Configure and manage rejection types and manufacturing modules")
st.markdown("---")

# Create two main sections
tab1, tab2 = st.tabs(["📦 Modules", "⚠️ Rejection Types"])

# Modules Tab
with tab1:
    st.subheader("Manufacturing Modules")
    
    # Add new module section
    with st.expander("➕ Add New Module", expanded=True):
        with st.form("add_module"):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                module_name = st.text_input(
                    "Module Name *",
                    help="Enter a unique name for the manufacturing module"
                )
            
            with col2:
                module_description = st.text_input(
                    "Description",
                    help="Brief description of the module (optional)"
                )
            
            submitted_module = st.form_submit_button("➕ Add Module", type="primary")
            
            if submitted_module:
                if not module_name.strip():
                    st.error("❌ Module name is required")
                else:
                    success, message = data_manager.add_module(
                        name=module_name.strip(),
                        description=module_description.strip()
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Display existing modules
    st.subheader("📋 Existing Modules")
    modules_df = data_manager.load_modules()
    
    if not modules_df.empty:
        # Display modules in a more user-friendly format
        for idx, module in modules_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 4, 1])
                
                with col1:
                    st.write(f"**{module['name']}**")
                
                with col2:
                    description = module.get('description', 'No description')
                    if pd.isna(description) or description == '':
                        description = 'No description'
                    st.write(description)
                
                with col3:
                    if st.button("🗑️", key=f"del_module_{idx}", help="Delete module"):
                        success, message = data_manager.delete_module(module['name'])
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                st.divider()
        
        # Module statistics
        st.subheader("📊 Module Statistics")
        rejections_df = data_manager.load_rejections()
        
        if not rejections_df.empty:
            module_stats = rejections_df.groupby('module').agg({
                'quantity': 'sum',
                'date': 'count'
            }).rename(columns={'date': 'total_entries'})
            
            module_stats = module_stats.reset_index()
            module_stats.columns = ['Module', 'Total Quantity Rejected', 'Total Entries']
            st.dataframe(module_stats, use_container_width=True, hide_index=True)
        else:
            st.info("📋 No rejection data available for module statistics")
    
    else:
        st.info("📦 No modules configured. Add your first module above.")

# Rejection Types Tab
with tab2:
    st.subheader("Rejection Types")
    
    # Add new rejection type section
    with st.expander("➕ Add New Rejection Type", expanded=True):
        with st.form("add_rejection_type"):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                type_name = st.text_input(
                    "Rejection Type Name *",
                    help="Enter a unique name for the rejection type"
                )
            
            with col2:
                type_description = st.text_input(
                    "Description",
                    help="Brief description of the rejection type (optional)"
                )
            
            # Module mapping section
            st.subheader("📦 Map to Modules *")
            if not modules_df.empty:
                mapped_modules = st.multiselect(
                    "Select applicable modules",
                    options=modules_df['name'].tolist(),
                    help="Choose which modules this rejection type applies to (mandatory)"
                )
            else:
                st.warning("⚠️ No modules available. Please add modules first.")
                mapped_modules = []
            
            submitted_type = st.form_submit_button("➕ Add Rejection Type", type="primary")
            
            if submitted_type:
                if not type_name.strip():
                    st.error("❌ Rejection type name is required")
                elif not mapped_modules:
                    st.error("❌ Please select at least one module for this rejection type")
                else:
                    success, message = data_manager.add_rejection_type(
                        name=type_name.strip(),
                        description=type_description.strip(),
                        mapped_modules=mapped_modules
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Display existing rejection types
    st.subheader("📋 Existing Rejection Types")
    types_df = data_manager.load_rejection_types()
    
    if not types_df.empty:
        # Display types in a more user-friendly format
        for idx, rejection_type in types_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 3, 3, 1])
                
                with col1:
                    st.write(f"**{rejection_type['name']}**")
                
                with col2:
                    description = rejection_type.get('description', 'No description')
                    if pd.isna(description) or description == '':
                        description = 'No description'
                    st.write(description)
                
                with col3:
                    # Show mapped modules
                    mapped_modules = str(rejection_type.get('mapped_modules', '')).split(',')
                    mapped_modules = [m.strip() for m in mapped_modules if m.strip()]
                    if mapped_modules:
                        st.write(f"📦 {', '.join(mapped_modules)}")
                    else:
                        st.write("📦 No modules mapped")
                
                with col4:
                    if st.button("🗑️", key=f"del_type_{rejection_type['name']}_{idx}", help="Delete rejection type"):
                        success, message = data_manager.delete_rejection_type(rejection_type['name'])
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                st.divider()
        
        # Rejection type statistics
        st.subheader("📊 Rejection Type Statistics")
        rejections_df = data_manager.load_rejections()
        
        if not rejections_df.empty:
            type_stats = rejections_df.groupby('rejection_type').agg({
                'quantity': 'sum',
                'date': 'count'
            }).rename(columns={'date': 'total_entries'})
            
            type_stats = type_stats.reset_index()
            type_stats.columns = ['Rejection Type', 'Total Quantity Rejected', 'Total Entries']
            type_stats = type_stats.sort_values('Total Quantity Rejected', ascending=False)
            st.dataframe(type_stats, use_container_width=True, hide_index=True)
        else:
            st.info("📋 No rejection data available for type statistics")
    
    else:
        st.info("⚠️ No rejection types configured. Add your first rejection type above.")

st.markdown("---")

# Quick actions and navigation
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠 Go to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("📝 Single Entry"):
        st.switch_page("pages/01_Data_Entry.py")

with col3:
    if st.button("📊 Batch Entry"):
        st.switch_page("pages/04_Batch_Entry.py")

with col4:
    if st.button("📧 Email Settings"):
        st.switch_page("pages/03_Email_Settings.py")

with col5:
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Help section
with st.expander("❓ Help & Guidelines"):
    st.markdown("""
    **Management Guidelines:**
    
    **Modules:**
    - Modules represent different manufacturing units, production lines, or equipment
    - Use clear, descriptive names (e.g., "Assembly Line 1", "Quality Control Station")
    - Descriptions help operators understand which module to select
    
    **Rejection Types:**
    - Types categorize different kinds of defects or issues
    - Common examples: "Dimensional Error", "Surface Defect", "Material Issue"
    - Use consistent naming conventions across your organization
    
    **Important Notes:**
    - ⚠️ Deleting modules or rejection types cannot be undone
    - ⚠️ Existing rejection records will still reference deleted items
    - 📊 Statistics show usage patterns to help optimize your categories
    
    **Best Practices:**
    - Start with broad categories and refine over time
    - Review usage statistics regularly to identify unused categories
    - Coordinate with your team to ensure consistent naming
    """)



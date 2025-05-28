import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from utils.data_manager import DataManager
from utils.scheduler import start_scheduler

# Initialize data manager
@st.cache_resource
def init_data_manager():
    return DataManager()

# Page configuration
st.set_page_config(
    page_title="QRMS - Quality Rejection Management System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
data_manager = init_data_manager()

# Start scheduler for automated emails
start_scheduler()

# Main dashboard
st.title("🏭 QRMS - Quality Rejection Management System")
st.markdown("---")

# Sidebar filters
st.sidebar.header("📊 Dashboard Filters")

# Date range filter
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=30),
        key="start_date"
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now(),
        key="end_date"
    )

# Load data
rejections_df = data_manager.load_rejections()
modules_df = data_manager.load_modules()
types_df = data_manager.load_rejection_types()

# Filter data by date range
if not rejections_df.empty:
    rejections_df['date'] = pd.to_datetime(rejections_df['date'])
    filtered_df = rejections_df[
        (rejections_df['date'] >= pd.to_datetime(start_date)) &
        (rejections_df['date'] <= pd.to_datetime(end_date))
    ]
else:
    filtered_df = rejections_df

# Module filter
if not modules_df.empty:
    available_modules = ['All'] + modules_df['name'].tolist()
    selected_module = st.sidebar.selectbox("Select Module", available_modules)
    
    if selected_module != 'All':
        filtered_df = filtered_df[filtered_df['module'] == selected_module]

# Rejection type filter
if not types_df.empty:
    available_types = ['All'] + types_df['name'].tolist()
    selected_type = st.sidebar.selectbox("Select Rejection Type", available_types)
    
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['rejection_type'] == selected_type]

# Main dashboard content
if filtered_df.empty:
    st.warning("📋 No rejection data available for the selected filters. Use the Data Entry page to add rejection records.")
    st.info("💡 **Getting Started:**\n- Navigate to 'Data Entry' for single records or 'Batch Entry' for multiple records\n- Visit 'Manage Types' to set up modules and rejection types\n- Configure email settings for automated reports")
else:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rejections = len(filtered_df)
        st.metric("Total Rejections", total_rejections)
    
    with col2:
        total_quantity = filtered_df['quantity'].sum()
        st.metric("Total Quantity Rejected", f"{total_quantity:,}")
    
    with col3:
        avg_daily = total_rejections / max(1, (end_date - start_date).days + 1)
        st.metric("Avg Daily Rejections", f"{avg_daily:.1f}")
    
    with col4:
        unique_modules = filtered_df['module'].nunique()
        st.metric("Modules Affected", unique_modules)

    st.markdown("---")

    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Rejections by Date")
        daily_rejections = filtered_df.groupby('date').agg({
            'quantity': 'sum',
            'date': 'count'
        }).rename(columns={'date': 'count'})
        
        fig_timeline = px.line(
            daily_rejections.reset_index(),
            x='date',
            y='quantity',
            title='Daily Rejection Quantity Trend',
            labels={'quantity': 'Quantity Rejected', 'date': 'Date'}
        )
        fig_timeline.update_layout(showlegend=False)
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    with col2:
        st.subheader("🔧 Rejections by Module")
        module_rejections = filtered_df.groupby('module')['quantity'].sum().sort_values(ascending=False)
        
        fig_modules = px.bar(
            x=module_rejections.values,
            y=module_rejections.index,
            orientation='h',
            title='Rejection Quantity by Module',
            labels={'x': 'Quantity Rejected', 'y': 'Module'}
        )
        st.plotly_chart(fig_modules, use_container_width=True)

    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("⚠️ Rejections by Type")
        type_rejections = filtered_df.groupby('rejection_type')['quantity'].sum().sort_values(ascending=False)
        
        fig_types = px.pie(
            values=type_rejections.values,
            names=type_rejections.index,
            title='Rejection Distribution by Type'
        )
        st.plotly_chart(fig_types, use_container_width=True)
    
    with col4:
        st.subheader("📊 Recent Rejections")
        recent_rejections = filtered_df.nlargest(10, 'date')[['date', 'module', 'rejection_type', 'quantity', 'reason']]
        recent_rejections['date'] = recent_rejections['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent_rejections, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # Detailed data table
    st.subheader("📋 Detailed Rejection Records")
    
    # Export functionality
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"rejections_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Display table
    display_df = filtered_df.copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 10px;'>
    QRMS - Quality Rejection Management System | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

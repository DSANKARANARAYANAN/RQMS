import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.scheduler import start_scheduler
from utils.auth import get_auth_manager

# Page configuration
st.set_page_config(
    page_title="QRMS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS for professional dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stMetric > div {
        background: transparent;
    }
    
    .sidebar .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .sidebar .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    
    .element-container {
        margin-bottom: 1rem;
    }
    
    .user-info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize authentication
auth_manager = get_auth_manager()

# Check authentication
if not auth_manager.is_authenticated():
    st.warning("🔒 Please login to access the QRMS dashboard")
    st.info("🔄 Please go back to the login page to authenticate.")
    st.stop()

# Start scheduler for automated reports
start_scheduler()

def init_data_manager():
    """Initialize data manager"""
    return DataManager()

# Initialize data manager
data_manager = init_data_manager()

# Show user info in sidebar
auth_manager.show_user_info()

# Modern Dashboard Header
st.markdown("""
<div class="main-header">
    <div class="main-title">📊 QRMS Dashboard</div>
    <div class="main-subtitle">Quality Analytics & Rejection Management</div>
</div>
""", unsafe_allow_html=True)

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
    st.warning("📋 No rejection data available for the selected filters.")
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
        unique_modules = filtered_df['module'].nunique()
        st.metric("Modules Affected", unique_modules)
    
    with col4:
        unique_types = filtered_df['rejection_type'].nunique()
        st.metric("Rejection Types", unique_types)

    st.markdown("---")

    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Rejection Trend")
        filtered_df['date_only'] = filtered_df['date'].dt.date
        daily_rejections = filtered_df.groupby('date_only')['quantity'].sum().reset_index()
        
        if len(daily_rejections) > 0:
            fig_timeline = px.line(
                daily_rejections,
                x='date_only',
                y='quantity',
                title="Daily Rejection Quantity Trend",
                markers=True
            )
            fig_timeline.update_layout(
                xaxis_title="Date",
                yaxis_title="Quantity Rejected",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Rejections by Type")
        rejection_counts = filtered_df.groupby('rejection_type')['quantity'].sum().sort_values(ascending=False)
        
        if len(rejection_counts) > 0:
            fig_pie = px.pie(
                values=rejection_counts.values,
                names=rejection_counts.index,
                title="Rejection Distribution by Type"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Additional charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📊 Rejections by Module")
        module_counts = filtered_df.groupby('module')['quantity'].sum().sort_values(ascending=False)
        
        if len(module_counts) > 0:
            fig_bar = px.bar(
                x=module_counts.values,
                y=module_counts.index,
                orientation='h',
                title="Rejection Quantity by Module",
                labels={'x': 'Quantity Rejected', 'y': 'Module'}
            )
            fig_bar.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with col4:
        st.subheader("🔧 Top Rejection Reasons")
        reason_counts = filtered_df.groupby('reason')['quantity'].sum().sort_values(ascending=False).head(10)
        
        if len(reason_counts) > 0:
            fig_reasons = px.bar(
                x=reason_counts.index,
                y=reason_counts.values,
                title="Top 10 Rejection Reasons",
                labels={'x': 'Reason', 'y': 'Quantity'}
            )
            fig_reasons.update_layout(
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig_reasons, use_container_width=True)

    # Pareto Analysis
    st.markdown("---")
    st.subheader("📈 Pareto Analysis - 80/20 Rule")
    
    rejection_totals = filtered_df.groupby('rejection_type')['quantity'].sum().sort_values(ascending=False)
    cumulative_percentage = (rejection_totals.cumsum() / rejection_totals.sum() * 100)
    
    if len(rejection_totals) > 0:
        # Create figure with secondary y-axis
        fig_pareto = go.Figure()
        
        # Add bar chart
        fig_pareto.add_trace(
            go.Bar(
                x=rejection_totals.index,
                y=rejection_totals.values,
                name='Quantity',
                yaxis='y',
                marker_color='lightblue'
            )
        )
        
        # Add cumulative percentage line
        fig_pareto.add_trace(
            go.Scatter(
                x=rejection_totals.index,
                y=cumulative_percentage.values,
                mode='lines+markers',
                name='Cumulative %',
                yaxis='y2',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add 80% reference line
        fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", 
                            annotation_text="80% Line", yref='y2')
        
        fig_pareto.update_layout(
            title='Pareto Chart - Rejection Types (80/20 Analysis)',
            xaxis_title='Rejection Type',
            yaxis=dict(title='Quantity', side='left'),
            yaxis2=dict(title='Cumulative Percentage (%)', side='right', overlaying='y', range=[0, 105]),
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    # Recent rejections table
    st.markdown("---")
    st.subheader("🕒 Recent Rejections")
    if not filtered_df.empty:
        recent_rejections = filtered_df.nlargest(10, 'date')[['date', 'module', 'rejection_type', 'quantity', 'reason', 'operator']]
        recent_rejections['date'] = recent_rejections['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent_rejections, use_container_width=True)

    # Export data functionality (only for admin and super admin)
    if auth_manager.has_permission(st.session_state.get("user_role"), "export_data"):
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📥 Export Data")
            
        with col2:
            if st.button("📊 Download CSV"):
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Filtered Data",
                    data=csv_data,
                    file_name=f"rejection_data_{start_date}_to_{end_date}.csv",
                    mime="text/csv"
                )
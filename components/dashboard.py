import streamlit as st
import pandas as pd
from database.client import SupabaseClient
from components.charts import (
    render_submission_chart, 
    render_customer_pie_chart,
    render_variance_histogram,
    render_top_variance_items,
    render_user_submission_chart,
    render_dashboard_summary
)

def render_admin_dashboard():
    """
    Render the admin dashboard with data visualization and filtering
    """
    st.title("Admin Dashboard")
    
    # Get data from database
    try:
        db_client = SupabaseClient()
        data = db_client.get_all_cycle_counts()
        
        if not data:
            st.info("No data available in the database")
            return
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        
        # Display summary metrics
        render_dashboard_summary(data)
        
        # Filters section
        st.sidebar.header("Filters")
        
        # Get unique values for filters
        customers = ["All"] + sorted(df["customer"].unique().tolist())
        users = ["All"] + sorted(df["uploaded_by"].unique().tolist())
        
        # Add filter widgets
        selected_customer = st.sidebar.selectbox("Customer", customers)
        selected_user = st.sidebar.selectbox("Uploaded By", users)
        date_range = st.sidebar.date_input(
            "Cycle Date Range",
            value=[df["cycle_date"].min(), df["cycle_date"].max()] if len(df) > 0 else None,
            help="Filter by cycle date range"
        )
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_customer != "All":
            filtered_df = filtered_df[filtered_df["customer"] == selected_customer]
            
        if selected_user != "All":
            filtered_df = filtered_df[filtered_df["uploaded_by"] == selected_user]
            
        if date_range and len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df["cycle_date"] >= date_range[0]) & 
                (filtered_df["cycle_date"] <= date_range[1])
            ]
        
        # Show number of records after filtering
        st.sidebar.info(f"Showing {len(filtered_df)} of {len(df)} records")
        
        # Download option
        if not filtered_df.empty:
            st.sidebar.download_button(
                label="Download Filtered Data",
                data=filtered_df.to_csv(index=False).encode('utf-8'),
                file_name=f"cycle_count_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Charts tab layout
        tab1, tab2, tab3 = st.tabs(["Data", "Charts", "Top Variances"])
        
        with tab1:
            st.subheader("Cycle Count Data")
            
            # Display the filtered dataframe
            st.dataframe(filtered_df)
        
        with tab2:
            # Display charts
            col1, col2 = st.columns(2)
            
            with col1:
                render_submission_chart(filtered_df.to_dict('records'))
                render_variance_histogram(filtered_df.to_dict('records'))
                
            with col2:
                render_customer_pie_chart(filtered_df.to_dict('records'))
                render_user_submission_chart(filtered_df.to_dict('records'))
        
        with tab3:
            # Display top variance items
            st.subheader("Items with Highest Variance")
            limit = st.slider("Number of items to show", 5, 30, 10)
            render_top_variance_items(filtered_df.to_dict('records'), limit=limit)
            
            # Display the top variance items table
            st.subheader("Top Items by Absolute Variance")
            filtered_df["abs_variance"] = filtered_df["variance"].abs()
            top_items = filtered_df.sort_values("abs_variance", ascending=False).head(limit)
            st.dataframe(top_items[["item_id", "description", "system_count", "actual_count", "variance", "percent_diff"]])
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.exception(e) 
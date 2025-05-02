import streamlit as st
import os
import pandas as pd
from components.authentication import authenticate, show_authentication_status, logout, check_admin_access, check_permissions
from components.upload import render_upload_form
from components.charts import (
    render_submission_chart, 
    render_customer_pie_chart,
    render_variance_histogram,
    render_top_variance_items,
    render_user_submission_chart,
    render_dashboard_summary
)
from database.client import SupabaseClient
import math
from components.inventory_reconciliation import render_reconciliation_opportunities

# Set page configuration
st.set_page_config(
    page_title="Cycle Count Tracker",
    page_icon="📊",
    layout="wide",
)

# Add custom styles
st.markdown("""
<style>
    .stApp {
        max-width: none;
        margin: 0;
        padding: 0;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Create necessary directories
os.makedirs(".streamlit", exist_ok=True)

# Check if secrets.toml exists, if not create a template
secrets_path = os.path.join(".streamlit", "secrets.toml")

# Initialize session state
if "show_upload_success" not in st.session_state:
    st.session_state["show_upload_success"] = False

# Initialize authentication state if not already done
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# Modified logout function to place at top of page
def logout_top():
    logout()
    st.rerun()

# Dashboard function - moved from Dashboard.py
def render_dashboard():
    try:
        # Get data from database
        db_client = SupabaseClient()
        data = db_client.get_all_cycle_counts()
        
        if not data:
            st.info("No data available in the database")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Get warehouse data for lookups
        warehouses_data = db_client.get_all_warehouses()
        warehouse_map = {w['id']: w['name'] for w in warehouses_data}
        
        # Get user data for lookups
        users_data = db_client.get_all_users()
        user_map = {u['id']: u['name'] for u in users_data}
        
        # Add warehouse name column based on warehouse_id
        if 'warehouse_id' in df.columns:
            df['warehouse'] = df['warehouse_id'].apply(lambda x: warehouse_map.get(x, "Unknown"))
        
        # Add user name column based on uploaded_by UUID
        if 'uploaded_by' in df.columns:
            df['uploader_name'] = df['uploaded_by'].apply(lambda x: user_map.get(x, "Unknown User"))
        
        # Apply role-based filtering
        is_admin = check_admin_access()
        if not is_admin:
            # For managers, only show their own uploads or data from their warehouse
            user_id = st.session_state.get("user_id")
            warehouse_id = st.session_state.get("warehouse_id")
            
            # Filter by user ID if that field exists
            if 'uploaded_by' in df.columns:
                df = df[df["uploaded_by"] == user_id]
            
            # Additional filter by warehouse for managers
            if warehouse_id and 'warehouse_id' in df.columns:
                df = df[df["warehouse_id"] == warehouse_id]
        else:
            
            st.success("Admin view")
            
        # Continue with dashboard display as before
        if df.empty:
            st.warning("No data to display with current filters")
            return
            
        # Convert cycle_date from string to datetime
        df["cycle_date"] = pd.to_datetime(df["cycle_date"]).dt.date
        
        # Display summary metrics for admins
        if is_admin:
            render_dashboard_summary(data)
        
        st.subheader("Filters")
        
        # Create columns for filters
        col1, col2, col3, col4 = st.columns(4)
        
        # Get unique values for filters
        customers = ["All"] + sorted(df["customer"].unique().tolist())
        
        if is_admin:
            users = ["All"] + sorted(df["uploader_name"].unique().tolist())
            warehouses = ["All"] + sorted(df["warehouse"].unique().tolist())

        # Add filter widgets
        with col1:
            selected_customer = st.selectbox("Customer", customers)
        
        with col2:
            if is_admin:
                selected_user = st.selectbox("Uploaded By", users)
                
        with col3:
            if is_admin:
                selected_warehouse = st.selectbox("Warehouse", warehouses)
        
        with col4:
            date_range = st.date_input(
                "Cycle Date Range",
                value=[df["cycle_date"].min(), df["cycle_date"].max()] if len(df) > 0 else None,
                help="Filter by cycle date range"
            )
        
        # Replace selectboxes with text inputs for partial matching
        col5, col6 = st.columns(2)
        with col5:
            search_item = st.text_input("Search Items", "", help="Enter text to search for items")
        with col6:
            search_location = st.text_input("Search Locations", "", help="Enter text to search for locations")
         
        # Apply filters
        filtered_df = df.copy()
        
        if selected_customer != "All":
            filtered_df = filtered_df[filtered_df["customer"] == selected_customer]
            
        if is_admin and selected_user != "All":
            filtered_df = filtered_df[filtered_df["uploader_name"] == selected_user]

        if is_admin and selected_warehouse != "All" and 'warehouse' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["warehouse"] == selected_warehouse]
            
        if date_range and len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df["cycle_date"] >= date_range[0]) & 
                (filtered_df["cycle_date"] <= date_range[1])
            ]
            
        # Apply partial match filters for item and location
        if search_item:
            filtered_df = filtered_df[filtered_df["item_id"].str.contains(search_item, case=False)]
            
        if search_location:
            filtered_df = filtered_df[filtered_df["location"].str.contains(search_location, case=False)]
        
        # Show number of records after filtering
        st.info(f"Showing {len(filtered_df)} of {len(df)} records")
        
        # Download option
        if not filtered_df.empty:
            # Before exporting, ensure warehouse names and user names are included
            export_df = filtered_df.copy()
            if 'warehouse_id' in export_df.columns and 'warehouse' not in export_df.columns:
                export_df['warehouse'] = export_df['warehouse_id'].apply(lambda x: warehouse_map.get(x, "Unknown"))
            if 'uploaded_by' in export_df.columns and 'uploader_name' not in export_df.columns:
                export_df['uploader_name'] = export_df['uploaded_by'].apply(lambda x: user_map.get(x, "Unknown User"))
            
            st.download_button(
                label="Download Filtered Data",
                data=export_df.to_csv(index=False).encode('utf-8'),
                file_name=f"cycle_count_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Format display
        if not filtered_df.empty:
            # Exclude ID column
            if 'id' in filtered_df.columns:
                filtered_df = filtered_df.drop(columns=['id'])
            
            # Capitalize customer names
            if 'customer' in filtered_df.columns:
                filtered_df['customer'] = filtered_df['customer'].str.upper()
            
            # Format date/time columns
            if 'cycle_date' in filtered_df.columns:
                filtered_df['cycle_date'] = pd.to_datetime(filtered_df['cycle_date']).dt.strftime('%b %d, %Y')
            
            if 'uploaded_at' in filtered_df.columns:
                filtered_df['uploaded_at'] = pd.to_datetime(filtered_df['uploaded_at']).dt.strftime('%b %d, %Y %I:%M %p')
        
        # Add warehouse to the displayed fields in dataframe
        display_cols = ['item_id', 'description', 'location', 'warehouse', 'lp', 'lot_number', 'unit', 'status', 'system_count', 
                       'actual_count', 'variance', 'customer', 'cycle_date', 'uploaded_at', 'uploader_name', 'notes', ]

        # Charts tab layout
        tab1, tab2, tab3, tab4 = st.tabs(["Data", "Charts", "Top Variances", "Reconciliation"])
        
        with tab1:
            st.subheader("Cycle Count Data")
            
            # Row count selector and pagination controls
            col1, col2, col3, col4, col5 = st.columns([1, 6, 5, 3, 1])
            
            with col1:
                rows_per_page = st.selectbox(
                    "Rows per page:", 
                    options=[50, 100, 300],
                    index=0  # Default to 50
                )
            

            n_pages = max(1, math.ceil(len(filtered_df) / rows_per_page))
            
            with col5:
                page_number = st.number_input(
                    "Page:", 
                    min_value=1, 
                    max_value=n_pages,
                    step=1
                )
            
            # Show page stats
            with col3:
                start_idx = 1 if len(filtered_df) > 0 else 0
                end_idx = len(filtered_df) if rows_per_page == "All" else min(page_number * rows_per_page, len(filtered_df))
                st.write(f"Showing {start_idx}-{end_idx} of {len(filtered_df)} records")
            
            # Slice the dataframe based on pagination
            if rows_per_page != "All":
                start = (page_number - 1) * rows_per_page
                end = min(start + rows_per_page, len(filtered_df))
                display_df = filtered_df.iloc[start:end]
            else:
                display_df = filtered_df
            
            # Forward/backward buttons
            if n_pages > 1:
                col1, col2 = st.columns(2)
                if col1.button("← Previous", disabled=(page_number == 1)):
                    # This will trigger a rerun with page_number-1
                    st.session_state["page_number"] = max(1, page_number - 1)
                    st.rerun()
                    
                if col2.button("Next →", disabled=(page_number == n_pages)):
                    # This will trigger a rerun with page_number+1
                    st.session_state["page_number"] = min(n_pages, page_number + 1)
                    st.rerun()
            
            # Display the dataframe with width set to fit content
            st.dataframe(
                display_df[display_cols],
                use_container_width=True,
                height=min(600, 35 * len(display_df) + 38)  # Dynamic height based on row count
            )
        
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
            limit = st.number_input("Number of items to show", min_value=5, max_value=30, value=10)
            # show filter by customer
            customers = ["All"] + sorted(filtered_df["customer"].unique().tolist())
            selected_customer = st.selectbox("Customer", customers, key="variance_customer")
            if selected_customer != "All":
                filtered_df = filtered_df[filtered_df["customer"] == selected_customer]
            
            render_top_variance_items(filtered_df.to_dict('records'), limit=limit)
            
            # Display the top variance items table
            st.subheader("Top Items by Absolute Variance")
            filtered_df["abs_variance"] = filtered_df["variance"].abs()
            top_items = filtered_df.sort_values("abs_variance", ascending=False).head(limit)
            st.dataframe(top_items[["item_id", "description", "customer", "location", "system_count", "actual_count", "variance", "percent_diff"]])
        
        with tab4:
            st.subheader("Inventory Reconciliation")
            render_reconciliation_opportunities(filtered_df)
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.exception(e)

# Main function
def main():
    # Call authenticate to handle login form display
    name, auth_status, username = authenticate()
    
    # Different display based on authentication status
    if st.session_state.get("authentication_status"):
        # AUTHENTICATED USER CONTENT
        col1, col2, col3 = st.columns([6, 13, 1])
        with col1:
            welcome_msg = f'Welcome, **{st.session_state["name"]}**'
            
            # Add warehouse info for managers
            if st.session_state.get("role") == "manager" and st.session_state.get("warehouse_id"):
                db_client = SupabaseClient()
                warehouse = db_client.get_warehouse(st.session_state.get("warehouse_id"))
                if warehouse:
                    welcome_msg += f' | Location: **{warehouse["name"]}**'
            
            st.write(welcome_msg)
        
        with col2:
            # Empty column for spacing
            pass
        
        with col3:
            if st.button("Logout"):
                logout_top()
                st.rerun()
                
        # Check for admin access
        is_admin = check_admin_access()
        
        # Create tabs for Data Management and Dashboard
        dashboard_tab, upload_tab = st.tabs(["Dashboard", "Data Management"])
        
        with upload_tab:
            upload_success = render_upload_form()
            if upload_success:
                st.session_state.show_upload_success = True
        
        with dashboard_tab:
            st.title("Dashboard")
            render_dashboard()
            
    else:
        # NON-AUTHENTICATED USER CONTENT
        
        # Show welcome message
        st.markdown("## Cycle Count Tracker")
        st.markdown("""
        Welcome to the Cycle Count Tracker application. Please log in to continue.
        """)


if __name__ == "__main__":
    main() 
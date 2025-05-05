import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_submission_chart(data):
    """
    Render a chart showing submission counts over time
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Convert cycle_date to datetime
    df["cycle_date"] = pd.to_datetime(df["cycle_date"])
    
    # Group by date and count submissions
    counts_by_date = df.groupby(df["cycle_date"].dt.date).size().reset_index(name="count")
    counts_by_date.columns = ["date", "count"]
    
    # Create the chart
    fig = px.line(counts_by_date, x="date", y="count", 
                 title="Cycle Count Submissions Over Time",
                 labels={"date": "Date", "count": "Number of Submissions"})
    
    st.plotly_chart(fig, use_container_width=True)

def render_customer_pie_chart(data):
    """
    Render a pie chart showing submissions by customer
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Group by customer and count submissions
    counts_by_customer = df.groupby("customer").size().reset_index(name="count")
    counts_by_customer.columns = ["customer", "count"]
    
    # Create the chart
    fig = px.pie(counts_by_customer, values="count", names="customer", 
                title="Submissions by Customer")
    
    st.plotly_chart(fig, use_container_width=True)

def render_variance_histogram(data):
    """
    Render a histogram of variances
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create the histogram
    fig = px.histogram(df, x="variance", 
                      title="Distribution of Variances",
                      labels={"variance": "Variance", "count": "Frequency"},
                      nbins=30
                      ) 
    
    st.plotly_chart(fig, use_container_width=True)

def render_top_variance_items(data, limit=10):
    """
    Render a bar chart of items with highest variance
    
    Args:
        data (list): List of cycle count records
        limit (int): Number of items to show
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Get items with highest absolute variance
    df["abs_variance"] = df["variance"].abs()
    top_items = df.sort_values("abs_variance", ascending=False).head(limit)
    
    # Create the chart
    fig = px.bar(top_items, x="item_id", y="variance", 
                title=f"Top {limit} Items by Variance",
                labels={"item_id": "Item ID", "variance": "Variance"},
                hover_data=["description", "system_count", "actual_count"])
    
    st.plotly_chart(fig, use_container_width=True)

def render_user_submission_chart(data):
    """
    Render a bar chart showing submissions by user
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Group by user name and count submissions
    counts_by_user = df.groupby("uploader_name").size().reset_index(name="count")
    counts_by_user.columns = ["user", "count"]
    
    # Create the chart
    fig = px.bar(counts_by_user, x="user", y="count", 
                title="Submissions by User",
                labels={"user": "User", "count": "Number of Submissions"})
    
    st.plotly_chart(fig, use_container_width=True)

def render_admin_dashboard_summary(data):
    """
    Render summary metrics for the dashboard
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Calculate metrics
    total_items = len(df)
    total_customers = df["customer"].nunique()
    total_users = df["uploaded_by"].nunique()
    
    # Create date ranges
    now = datetime.now()
    df["uploaded_at"] = pd.to_datetime(df["uploaded_at"])
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)
    
    # Filter by date ranges
    items_last_week = len(df[df["uploaded_at"] >= last_week])
    items_last_month = len(df[df["uploaded_at"] >= last_month])
    
    # Display metrics only for
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", total_items)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Users", total_users)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Items Last Week", items_last_week)
    col2.metric("Items Last Month", items_last_month)

def render_manager_dashboard_summary(data):
    """
    Render summary metrics for the dashboard
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Filter by warehouse_id if it exists in both dataframe and session state
    warehouse_id = st.session_state.get("warehouse_id")
    if warehouse_id and "warehouse_id" in df.columns:
        df = df[df["warehouse_id"] == warehouse_id]
    
    # Calculate metrics
    total_items = len(df)
    total_customers = df["customer"].nunique() if "customer" in df.columns else 0
    total_users = df["uploaded_by"].nunique() if "uploaded_by" in df.columns else 0   
    
    # Create date ranges
    now = datetime.now()
    if "uploaded_at" in df.columns:
        df["uploaded_at"] = pd.to_datetime(df["uploaded_at"])
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        # Filter by date ranges
        items_last_week = len(df[df["uploaded_at"] >= last_week])
        items_last_month = len(df[df["uploaded_at"] >= last_month])
    else:
        items_last_week = 0
        items_last_month = 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", total_items)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Users", total_users)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Items Last Week", items_last_week)
    col2.metric("Items Last Month", items_last_month)

def render_warehouse_distribution(data):
    """
    Render a chart showing distribution of items across warehouses
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    if 'warehouse' not in df.columns:
        st.info("Warehouse data not available in records")
        return
    
    # Group by warehouse
    counts_by_warehouse = df.groupby("warehouse").size().reset_index(name="count")
    counts_by_warehouse.columns = ["warehouse", "count"]
    
    # Create the chart
    fig = px.bar(counts_by_warehouse, x="warehouse", y="count", 
                title="Items by Warehouse Location",
                labels={"warehouse": "Warehouse", "count": "Number of Items"})
    
    st.plotly_chart(fig, use_container_width=True)

def render_improved_variance_chart(data):
    """
    Render an improved visualization of variances by customer and warehouse
    
    Args:
        data (list): List of cycle count records
    """
    if not data:
        st.info("No data available to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Calculate total variance by warehouse and customer
    pivot = df.pivot_table(
        values="variance", 
        index="warehouse", 
        columns="customer", 
        aggfunc="sum"
    ).fillna(0)
    
    # Create a heatmap
    fig = px.imshow(pivot, 
                    labels=dict(x="Customer", y="Warehouse", color="Total Variance"),
                    title="Variance Heatmap by Warehouse and Customer")
    
    st.plotly_chart(fig, use_container_width=True) 
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
                      labels={"variance": "Variance", "count": "Frequency"})
    
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
    
    # Group by user and count submissions
    counts_by_user = df.groupby("uploaded_by").size().reset_index(name="count")
    counts_by_user.columns = ["user", "count"]
    
    # Create the chart
    fig = px.bar(counts_by_user, x="user", y="count", 
                title="Submissions by User",
                labels={"user": "User", "count": "Number of Submissions"})
    
    st.plotly_chart(fig, use_container_width=True)

def render_dashboard_summary(data):
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
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", total_items)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Users", total_users)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Items Last Week", items_last_week)
    col2.metric("Items Last Month", items_last_month) 
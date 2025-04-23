import streamlit as st
import os
from components.authentication import authenticate, show_authentication_status, logout, check_admin_access
from components.upload import render_upload_form
from database.client import SupabaseClient

# Set page configuration
st.set_page_config(
    page_title="Cycle Count Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS to hide sidebar when not authenticated
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

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
    .stSidebar .sidebar-content {
        background-color: #f8f9fa;
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

# Main function
def main():
    # Call authenticate to handle login form display
    name, auth_status, username = authenticate()
    
    # Different display based on authentication status
    if show_authentication_status():
        # AUTHENTICATED USER CONTENT
                
        # Display logout button
        logout()
        
        # Check for admin access
        is_admin = check_admin_access()
        
        # Display appropriate content based on role
        if is_admin:
            st.sidebar.success("Admin access granted. Please use the Dashboard page.")
            st.markdown("## Welcome to Cycle Count Tracker Admin Panel")
            st.markdown("""
            Please navigate to the Dashboard page using the sidebar to:
            - View all submitted cycle counts
            - Filter data by customer, date, or user
            - View summary charts and statistics
            - Download data as CSV
            """)
        else:
            # Manager view - show upload form
            upload_success = render_upload_form()
            if upload_success:
                st.session_state.show_upload_success = True
    else:
        # NON-AUTHENTICATED USER CONTENT
        
        # Show welcome message
        st.markdown("## Cycle Count Tracker")
        st.markdown("""
        Welcome to the Cycle Count Tracker application. Please log in to continue.
        """)

if __name__ == "__main__":
    main() 
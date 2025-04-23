import streamlit as st
from components.authentication import show_authentication_status, logout
from components.upload import render_upload_form

# Set page configuration
st.set_page_config(
    page_title="Upload Cycle Count",
    page_icon="📊",
    layout="wide"
)

# Add custom styles
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Main function
def main():
    # Display app header
    st.sidebar.title("Cycle Count Tracker")
    st.sidebar.markdown("---")
    
    # Check authentication status
    if show_authentication_status():
        # Display logout button
        logout()
        
        # Show upload form
        render_upload_form()
    else:
        # Not authenticated, redirect to main page
        st.warning("Please log in from the Home page to access this functionality.")
        st.markdown("## Authentication Required")
        st.markdown("""
        You need to be logged in to access the Upload functionality.
        
        Please return to the Home page and log in with your credentials.
        """)

if __name__ == "__main__":
    main() 
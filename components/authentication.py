import streamlit as st
from config.auth_config import get_authenticator, is_admin

import streamlit as st
from config.auth_config import get_authenticator, is_admin

def authenticate():
    """
    Handle authentication using streamlit-authenticator
    
    Returns:
        tuple: (name, authentication_status, username)
            - name: The full name of the authenticated user
            - authentication_status: True if authenticated, False if incorrect, None if not attempted
            - username: The username of the authenticated user
    """
    # Initialize session state for authentication
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "authenticator" not in st.session_state:
        st.session_state["authenticator"] = get_authenticator()
    
    # Get the authenticator from session state
    authenticator = st.session_state["authenticator"]
    
    # Render the login widget and check authentication status
    authentication_status = authenticator.login()

    # If authentication is successful, store user info in session state
    if authentication_status:
        st.session_state["name"] = authenticator.get_user_name()  # Assuming get_user_name() fetches the name
        st.session_state["username"] = authenticator.get_username()  # Assuming get_username() fetches the username
    
    # Return user information from session state
    name = st.session_state["name"]
    username = st.session_state["username"]

    return name, authentication_status, username


def show_authentication_status():
    """
    Display appropriate messages based on authentication status
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    # Check if session state exists first
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    elif st.session_state["authentication_status"] == False:
        st.error("Username/password is incorrect")
        return False
    elif st.session_state["authentication_status"] == None:
        st.warning("Please enter your username and password")
        return False

def logout():
    """
    Handle logout functionality
    """
        
    # Make sure session state is cleared properly on logout
    if st.session_state["authentication_status"] == False:
        st.session_state["authentication_status"] = None

def check_admin_access():
    """
    Check if the current user has admin access
    
    Returns:
        bool: True if user has admin access, False otherwise
    """
    if not st.session_state.get("authentication_status"):
        return False
    
    username = st.session_state.get("username")
    return is_admin(username) 
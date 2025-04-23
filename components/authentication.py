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
    
    # Display the login form with a container to control positioning
    with st.container():
        name, authentication_status, username = authenticator.login("Login", "main")
    
    # Update session state
    if authentication_status is not None:
        st.session_state["authentication_status"] = authentication_status
    if name is not None:
        st.session_state["name"] = name
    if username is not None:
        st.session_state["username"] = username
    
    return name, authentication_status, username

def show_authentication_status():
    """
    Display appropriate messages based on authentication status
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if st.session_state["authentication_status"]:
        st.sidebar.write(f'Welcome *{st.session_state["name"]}*')
        return True
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
    if "authenticator" in st.session_state:
        authenticator = st.session_state["authenticator"]
        authenticator.logout("Logout", "sidebar")
    else:
        # Re-initialize authenticator if needed
        authenticator = get_authenticator()
        authenticator.logout("Logout", "sidebar")
        
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
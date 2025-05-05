import streamlit as st
from database.client import SupabaseClient
import bcrypt
from components.registration import render_registration_form

def authenticate():
    """
    Handle database-based authentication using the users table
    
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
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = None
    if "warehouse_id" not in st.session_state:
        st.session_state["warehouse_id"] = None
    if "show_registration" not in st.session_state:
        st.session_state["show_registration"] = False
    
    # If already authenticated, return current state
    if st.session_state["authentication_status"]:
        return (
            st.session_state["name"],
            st.session_state["authentication_status"],
            st.session_state["username"]
        )
    
    # Toggle between login and registration
    if st.session_state.get("show_registration"):
        # Render registration form
        registration_successful = render_registration_form()
        
        if registration_successful:
            # Switch back to login after successful registration
            st.session_state["show_registration"] = False
            st.rerun()
        
        # Option to go back to login
        if st.button("← Back to Login"):
            st.session_state["show_registration"] = False
            st.rerun()
    else:
        # Create login form
        with st.form("login_form"):
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
        
        if submit:
            # Query user from database
            db_client = SupabaseClient()
            
            # Check if Supabase client is initialized
            if not db_client.supabase:
                st.error("Database connection failed. Check Supabase configuration.")
                return None, False, None
            
            # Get user
            try:
                user = db_client.get_user(username)
                
                if user:
                    # Get password hash from user record
                    stored_hash = user.get("password_hash")
                    
                    # For backward compatibility during development
                    if stored_hash is None:
                        # Temporary: use simple password check if no hash exists
                        if password == "123":
                            st.session_state["authentication_status"] = True
                            st.session_state["username"] = username
                            st.session_state["name"] = user.get("name", username)
                            st.session_state["user_id"] = user.get("id")
                            st.session_state["role"] = user.get("role")
                            st.session_state["warehouse_id"] = user.get("warehouse_id")
                            
                            # Update last login time
                            db_client.update_last_login(user.get("id"))
                            
                            st.rerun()
                    else:
                        # Verify password using bcrypt
                        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                            st.session_state["authentication_status"] = True
                            st.session_state["username"] = username
                            st.session_state["name"] = user.get("name", username)
                            st.session_state["user_id"] = user.get("id")
                            st.session_state["role"] = user.get("role")
                            st.session_state["warehouse_id"] = user.get("warehouse_id")
                            
                            # Update last login time
                            db_client.update_last_login(user.get("id"))
                            
                            st.rerun()
                        else:
                            st.session_state["authentication_status"] = False
                else:
                    st.session_state["authentication_status"] = False
            except Exception as e:
                st.error(f"Error during authentication: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state["authentication_status"] = False
        
        if st.session_state["authentication_status"] == False:
            st.error("Username/password is incorrect")
        
        # Add registration option
        st.write("Don't have an account?")
        if st.button("Register New Account"):
            st.session_state["show_registration"] = True
            st.rerun()
    
    return (
        st.session_state.get("name"),
        st.session_state.get("authentication_status"),
        st.session_state.get("username")
    )

def show_authentication_status():
    """
    Display appropriate messages based on authentication status
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    # Check if session state exists first
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    if st.session_state["authentication_status"] == False:
        st.error("Username/password is incorrect")
        return False
    elif st.session_state["authentication_status"] == None:
        st.warning("Please enter your username and password")
        return False
    return True

def logout(): 
    """Handle logout functionality"""
    # Clear all session state related to authentication
    st.session_state["authentication_status"] = None
    st.session_state["name"] = None
    st.session_state["username"] = None
    st.session_state["user_id"] = None
    st.session_state["role"] = None
    st.session_state["warehouse_id"] = None

def check_admin_access():
    """
    Check if the current user has admin access using their role in the database
    
    Returns:
        bool: True if user has admin role, False otherwise
    """
    if not st.session_state.get("authentication_status"):
        return False
    
    return st.session_state.get("role") == "admin" 

import streamlit as st

# Helper functions for authentication
def get_password_placeholder():
    """
    Return a password placeholder 
    In a real app, you would store hashed passwords in the database
    """
    return "password"  # Default password for testing

def get_role_options():
    """Return valid role options"""
    return ["admin", "manager"]

def check_permissions(required_role="admin"):
    """
    Check if user has required permissions
    
    Args:
        required_role (str): Role required for access
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    # Get user role from session state
    user_role = st.session_state.get("role")
    
    # Admin can access everything
    if user_role == "admin":
        return True
    
    # Otherwise, check if roles match
    return user_role == required_role
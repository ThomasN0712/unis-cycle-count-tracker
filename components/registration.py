import streamlit as st
import bcrypt
from database.client import SupabaseClient

def render_registration_form():
    """
    Render the registration form for new users
    
    Returns:
        bool: True if registration was successful, False otherwise
    """
    st.header("Register New Account")
    
    # Get warehouses for dropdown
    db_client = SupabaseClient()
    warehouses = db_client.get_all_warehouses()
    
    # Create warehouse options for dropdown
    warehouse_options = [(w["id"], w["name"]) for w in warehouses]
    
    # Invitation code (stored in secrets for security)
    invitation_code = st.secrets.get("app_settings", {}).get("invitation_code", "UNIS2023CYCLE")
    
    with st.form("registration_form"):
        username = st.text_input("Username (will be used for login)")
        full_name = st.text_input("Full Name")
        password = st.text_input("Password (6+ characters)", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Warehouse selection
        warehouse_id = None
        if warehouse_options:
            warehouse_names = ["Select Warehouse"] + [w[1] for w in warehouse_options]
            selected_index = st.selectbox("Select Your Warehouse", options=range(len(warehouse_names)), 
                                        format_func=lambda x: warehouse_names[x])
            if selected_index > 0:
                warehouse_id = warehouse_options[selected_index-1][0]
        else:
            st.error("No warehouses available. Please contact administrator.")
        
        # Invitation code field
        user_invitation_code = st.text_input("Invitation Code", help="Enter the company invitation code")
        
        submit = st.form_submit_button("Register")
        
        if submit:
            # Validation
            error = False
            
            # Check invitation code
            if user_invitation_code != invitation_code:
                st.error("Invalid invitation code")
                error = True
            
            # Check username (not empty and unique)
            if not username:
                st.error("Username is required")
                error = True
            else:
                # Check if username already exists
                existing_user = db_client.get_user(username)
                if existing_user:
                    st.error("Username already exists")
                    error = True
            
            # Check full name
            if not full_name:
                st.error("Full name is required")
                error = True
            
            # Check password
            if not password:
                st.error("Password is required")
                error = True
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
                error = True
            elif password != confirm_password:
                st.error("Passwords do not match")
                error = True
            
            # Check warehouse selection
            if not warehouse_id:
                st.error("Please select a warehouse")
                error = True
            
            if not error:
                try:
                    # Hash password
                    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    # Create user
                    user_data = {
                        "username": username,
                        "name": full_name,
                        "role": "manager",  # Default role for new users
                        "warehouse_id": warehouse_id,
                        "password_hash": password_hash
                    }
                    
                    result = db_client.register_user(user_data)
                    
                    if result:
                        st.success("Registration successful! You can now log in.")
                        return True
                    else:
                        st.error("Registration failed. Please try again.")
                except Exception as e:
                    st.error(f"Error during registration: {str(e)}")
    
    return False 
import streamlit as st
import sys
import os
import uuid
import bcrypt
from datetime import datetime

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.client import SupabaseClient

# Initial users to create
INITIAL_USERS = [
    {
        "username": "thomas",
        "name": "Thomas Nguyen",
        "role": "admin",
        "warehouse_id": 1 # Will be assigned if needed
    },
    {
        "username": "brayan",
        "name": "Brayan Escobar",
        "role": "admin",
        "warehouse_id": 1
    },
    {
        "username": "edward",
        "name": "Edward Lampley",
        "role": "manager",
        "warehouse_id": 1
    },
    {
        "username": "marcelino",
        "name": "Marcelino Vazquez",
        "role": "manager",
        "warehouse_id": 1
    }
]

# Default password (you should change this in production)
DEFAULT_PASSWORD = "123"

def main():
    """Initialize the database with user records"""
    print("Initializing users...")
    
    # Connect to database
    db_client = SupabaseClient()
    
    # Get existing users to avoid duplicates
    existing_users = db_client.get_all_users()
    existing_usernames = [user.get("username") for user in existing_users]
    
    # Add users
    for user in INITIAL_USERS:
        if user["username"] in existing_usernames:
            print(f"User {user['username']} already exists, skipping...")
            continue
        
        # Prepare user record
        user_record = {
            "id": str(uuid.uuid4()),
            "username": user["username"],
            "name": user["name"],
            "role": user["role"],
            "warehouse_id": user["warehouse_id"],
            "created_at": datetime.now().isoformat()
        }
        
        # Insert user
        try:
            result = db_client.insert_user(user_record)
            if result:
                print(f"Created user: {user['username']}")
            else:
                print(f"Failed to create user: {user['username']}")
        except Exception as e:
            print(f"Error creating user {user['username']}: {str(e)}")
    
    print("User initialization complete")

if __name__ == "__main__":
    main()

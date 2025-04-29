# import streamlit_authenticator as stauth
# import yaml
# from yaml.loader import SafeLoader
# import streamlit as st
# import os
# import pickle
# import hashlib

# # Define hardcoded user credentials
# credentials = {
#     "usernames": {
#         "thomas": {
#             "name": "Thomas Nguyen",
#             "password": "hashed_password_placeholder",  # Will be hashed
#             "email": "admin@example.com",
#             "role": "admin"
#         },
#         "brayan": {
#             "name": "Brayan Escobar",
#             "password": "hashed_password_placeholder",  # Will be hashed
#             "email": "admin2@example.com",
#             "role": "admin"
#         },
#         "edward": {
#             "name": "Edward Lampley",
#             "password": "hashed_password_placeholder",  # Will be hashed
#             "email": "manager@example.com",
#             "role": "manager"
#         },
#         "marcelino": {
#             "name": "Marcelino Vazquez",
#             "password": "hashed_password_placeholder",  # Will be hashed
#             "email": "manager2@example.com",
#             "role": "manager"
#         }
#     }
# }

# # Placeholder passwords to be hashed (in production, use more secure passwords)
# passwords = {
#     "thomas": "123",
#     "brayan": "123",
#     "edward": "123",
#     "marcelino": "123"
# }

# # Hash passwords and update credentials
# for username, password in passwords.items():
#     credentials["usernames"][username]["password"] = stauth.Hasher().hash(password)

# # Configuration for stauth
# config = {
#     "credentials": credentials,
#     "cookie": {
#         "name": "cycle_count_auth",
#         "key": "cycle_count_key",
#         "expiry_days": 30
#     },
#     "preauthorized": {
#         "emails": []
#     }
# }

# def get_authenticator():
#     """
#     Create and return an authenticator instance
    
#     Returns:
#         stauth.Authenticate: The authenticator instance
#     """
#     return stauth.Authenticate(
#         config["credentials"],
#         config["cookie"]["name"],
#         config["cookie"]["key"],
#         config["cookie"]["expiry_days"],
#         config["preauthorized"]["emails"]
#     )

# def is_admin(username):
#     """
#     Check if the given username has admin role
    
#     Args:
#         username (str): The username to check
        
#     Returns:
#         bool: True if the user is an admin, False otherwise
#     """
#     if not username or username not in credentials["usernames"]:
#         return False
#     return credentials["usernames"][username].get("role") == "admin" 
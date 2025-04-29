# import streamlit as st
# from database.client import SupabaseClient
# from database.schema import CYCLE_COUNTS_TABLE, COLUMNS
# from datetime import datetime, timedelta

# def get_recent_submissions(days=7):
#     """
#     Get submissions from the last N days
    
#     Args:
#         days (int): Number of days to look back
        
#     Returns:
#         list: List of recent cycle count records
#     """
#     try:
#         client = SupabaseClient()
#         date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
#         response = client.supabase.table(CYCLE_COUNTS_TABLE) \
#             .select("*") \
#             .gte(COLUMNS["uploaded_at"], date_from) \
#             .execute()
            
#         if hasattr(response, 'data'):
#             return response.data
#         return []
#     except Exception as e:
#         st.error(f"Error fetching recent submissions: {str(e)}")
#         return []

# def get_customer_submissions(customer):
#     """
#     Get all submissions for a specific customer
    
#     Args:
#         customer (str): Customer name to filter by
        
#     Returns:
#         list: List of cycle count records for the customer
#     """
#     try:
#         client = SupabaseClient()
#         response = client.supabase.table(CYCLE_COUNTS_TABLE) \
#             .select("*") \
#             .eq(COLUMNS["customer"], customer) \
#             .execute()
            
#         if hasattr(response, 'data'):
#             return response.data
#         return []
#     except Exception as e:
#         st.error(f"Error fetching customer submissions: {str(e)}")
#         return []

# def get_user_submissions(username):
#     """
#     Get all submissions by a specific user
    
#     Args:
#         username (str): Username to filter by
        
#     Returns:
#         list: List of cycle count records for the user
#     """
#     try:
#         client = SupabaseClient()
#         response = client.supabase.table(CYCLE_COUNTS_TABLE) \
#             .select("*") \
#             .eq(COLUMNS["uploaded_by"], username) \
#             .execute()
            
#         if hasattr(response, 'data'):
#             return response.data
#         return []
#     except Exception as e:
#         st.error(f"Error fetching user submissions: {str(e)}")
#         return []

# def get_summary_statistics():
#     """
#     Get summary statistics for all cycle count data
    
#     Returns:
#         dict: Dictionary with summary statistics
#     """
#     try:
#         client = SupabaseClient()
#         data = client.get_all_cycle_counts()
        
#         if not data:
#             return {
#                 "total_records": 0,
#                 "total_customers": 0,
#                 "total_users": 0,
#                 "avg_variance": 0,
#                 "avg_percent_diff": 0
#             }
        
#         # Calculate statistics
#         total_records = len(data)
        
#         # Extract unique customers and users
#         customers = set()
#         users = set()
#         total_variance = 0
#         total_percent_diff = 0
        
#         for record in data:
#             customers.add(record["customer"])
#             users.add(record["uploaded_by"])
#             total_variance += record["variance"]
#             total_percent_diff += record["percent_diff"]
        
#         # Calculate averages
#         avg_variance = total_variance / total_records if total_records > 0 else 0
#         avg_percent_diff = total_percent_diff / total_records if total_records > 0 else 0
        
#         return {
#             "total_records": total_records,
#             "total_customers": len(customers),
#             "total_users": len(users),
#             "avg_variance": avg_variance,
#             "avg_percent_diff": avg_percent_diff
#         }
#     except Exception as e:
#         st.error(f"Error calculating summary statistics: {str(e)}")
#         return {
#             "total_records": 0,
#             "total_customers": 0,
#             "total_users": 0,
#             "avg_variance": 0,
#             "avg_percent_diff": 0
#         } 
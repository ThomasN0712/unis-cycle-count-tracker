import streamlit as st
from supabase import create_client
from database.schema import (
    CYCLE_COUNTS_TABLE, WAREHOUSES_TABLE, USERS_TABLE,
    CYCLE_COUNTS_COLUMNS, WAREHOUSES_COLUMNS, USERS_COLUMNS
)

class SupabaseClient:
    _instance = None
    supabase = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            try:
                # Add logging to check if secrets exist
                if "supabase" not in st.secrets:
                    cls._instance.supabase = None
                    return cls._instance
                
                # Check if URL and key exist
                if "url" not in st.secrets["supabase"]:
                    cls._instance.supabase = None
                    return cls._instance
                
                if "key" not in st.secrets["supabase"]:
                    cls._instance.supabase = None
                    return cls._instance
                
                # Log connection attempt
                supabase_url = st.secrets["supabase"]["url"]
                supabase_key = st.secrets["supabase"]["key"]
                
                # Log partial URL (securely)
                url_prefix = supabase_url[:15] if len(supabase_url) > 20 else "..."
                
                # Initialize client
                cls._instance.supabase = create_client(supabase_url, supabase_key)
            except Exception as e:
                import traceback
                st.code(traceback.format_exc())
                cls._instance.supabase = None
        return cls._instance
    
    # Cycle Counts methods
    def insert_cycle_count(self, data):
        """
        Insert cycle count data into the database
        
        Args:
            data (dict): Dictionary containing cycle count data
        
        Returns:
            dict: The inserted record
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return None
            
        try:
            response = self.supabase.table(CYCLE_COUNTS_TABLE).insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            raise
    
    def get_all_cycle_counts(self):
        """
        Get all cycle count records
        
        Returns:
            list: List of cycle count records
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return []
            
        try:
            # Temporarily use simple select without joins until schema is updated
            response = self.supabase.table(CYCLE_COUNTS_TABLE).select("*").execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            raise
    
    def filter_cycle_counts(self, customer=None, date_from=None, date_to=None, warehouse_id=None):
        """
        Filter cycle count records based on criteria
        
        Args:
            customer (str, optional): Customer name to filter by
            date_from (date, optional): Start date for filtering
            date_to (date, optional): End date for filtering
            warehouse_id (str, optional): Warehouse ID to filter by
            
        Returns:
            list: Filtered list of cycle count records
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return []
            
        try:
            # Use simple select without joins for now
            query = self.supabase.table(CYCLE_COUNTS_TABLE).select("*")
            
            # Apply filters if provided
            if customer:
                query = query.eq(CYCLE_COUNTS_COLUMNS["customer"], customer)
                
            if date_from and date_to:
                query = query.gte(CYCLE_COUNTS_COLUMNS["cycle_date"], date_from.isoformat())
                query = query.lte(CYCLE_COUNTS_COLUMNS["cycle_date"], date_to.isoformat())
            elif date_from:
                query = query.gte(CYCLE_COUNTS_COLUMNS["cycle_date"], date_from.isoformat())
            elif date_to:
                query = query.lte(CYCLE_COUNTS_COLUMNS["cycle_date"], date_to.isoformat())
                
            # Use location instead of location_id until schema is updated
            if warehouse_id and 'location' in CYCLE_COUNTS_COLUMNS:
                query = query.eq('location', warehouse_id)
            
            response = query.execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            st.error(f"Error filtering data: {str(e)}")
            raise
    
    def update_cycle_count(self, record_id, data):
        """
        Update an existing cycle count record
        
        Args:
            record_id (str): The ID of the record to update
            data (dict): Dictionary containing updated data
        
        Returns:
            dict: The updated record, or None on error
        """
        try:
            response = self.supabase.table(CYCLE_COUNTS_TABLE).update(data).eq("id", record_id).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")
            return None
    
    def delete_cycle_count(self, record_id):
        """
        Delete a cycle count record
        
        Args:
            record_id (str): The ID of the record to delete
        
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            response = self.supabase.table(CYCLE_COUNTS_TABLE).delete().eq("id", record_id).execute()
            
            if hasattr(response, 'data'):
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting data: {str(e)}")
            return False
    
    # Warehouse methods
    def get_all_warehouses(self):
        """
        Get all warehouses
        
        Returns:
            list: List of warehouses
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return []
            
        try:
            response = self.supabase.table(WAREHOUSES_TABLE).select("*").execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            st.error(f"Error fetching warehouses: {str(e)}")
            raise
    
    def get_warehouse(self, warehouse_id):
        """
        Get warehouse by ID
        
        Args:
            warehouse_id (str): The ID of the warehouse to retrieve
        
        Returns:
            dict: The warehouse record, or None if not found
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
        try:
            response = self.supabase.table(WAREHOUSES_TABLE).select("*").eq("id", warehouse_id).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error fetching warehouse: {str(e)}")
            raise
    
    def insert_warehouse(self, data):
        """Insert new warehouse"""
        if not self.supabase:
            st.error("Supabase client not initialized")
            return None
            
        try:
            response = self.supabase.table(WAREHOUSES_TABLE).insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error inserting warehouse: {str(e)}")
            raise
    
    # User methods
    def get_all_users(self):
        """
        Get all users with warehouse data joined
        
        Returns:
            list: List of users with warehouse data
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return []
            
        try:
            response = self.supabase.table(USERS_TABLE).select("*", f"{WAREHOUSES_TABLE}(*)").execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            raise
    
    def get_user(self, username):
        """
        Get user by username with proper error handling
        
        Args:
            username (str): The username to lookup
        
        Returns:
            dict: User data if found, None otherwise
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return None
        
        try:
            # Simple select for now - add warehouse join when ready
            response = self.supabase.table(USERS_TABLE).select("*").eq("username", username).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error fetching user: {str(e)}")
            return None
    
    def insert_user(self, data):
        """
        Insert new user
        
        Args:
            data (dict): Dictionary containing user data
        
        Returns:
            dict: The inserted user record, or None on error
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
        try:
            response = self.supabase.table(USERS_TABLE).insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error inserting user: {str(e)}")
            raise
    
    def get_warehouse_users(self, warehouse_id):
        """
        Get all users assigned to a specific warehouse
        Args:
            warehouse_id (int): The ID of the warehouse to retrieve users for

        Returns:
            list: List of users assigned to the warehouse
        """
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table(USERS_TABLE).select("*").eq("warehouse_id", warehouse_id).execute()
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            st.error(f"Error fetching warehouse users: {str(e)}")
            return []

    def register_user(self, data):
        """
        Register a new user
        
        Args:
            data (dict): Dictionary containing user data
        
        Returns:
            dict: The created user record, or None on error
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return None
        
        try:
            response = self.supabase.table(USERS_TABLE).insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error registering user: {str(e)}")
            return None

    def update_last_login(self, user_id):
        """
        Update the last login timestamp for a user
        
        Args:
            user_id (str): The ID of the user
        
        Returns:
            bool: True if updated successfully, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            import datetime
            now = datetime.datetime.now().isoformat()
            
            response = self.supabase.table(USERS_TABLE).update(
                {"last_login": now}
            ).eq("id", user_id).execute()
            
            return hasattr(response, 'data') and len(response.data) > 0
        except Exception as e:
            st.error(f"Error updating last login: {str(e)}")
            return False
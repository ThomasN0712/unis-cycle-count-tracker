import streamlit as st
from supabase import create_client
from database.schema import CYCLE_COUNTS_TABLE, COLUMNS, CREATE_CYCLE_COUNTS_TABLE

class SupabaseClient:
    _instance = None
    supabase = None  # Define the attribute at class level
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            # Initialize the Supabase client
            try:
                supabase_url = st.secrets["supabase"]["url"]
                supabase_key = st.secrets["supabase"]["key"]
                cls._instance.supabase = create_client(supabase_url, supabase_key)
            except Exception as e:
                st.error(f"Error initializing Supabase client: {str(e)}")
                # Initialize with None to prevent further errors
                cls._instance.supabase = None
        return cls._instance
    
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
            st.error(f"Error inserting data: {str(e)}")
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
            response = self.supabase.table(CYCLE_COUNTS_TABLE).select("*").execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            raise
    
    def filter_cycle_counts(self, customer=None, date_from=None, date_to=None, uploaded_by=None):
        """
        Filter cycle count records based on criteria
        
        Args:
            customer (str, optional): Customer name to filter by
            date_from (date, optional): Start date for filtering
            date_to (date, optional): End date for filtering
            uploaded_by (str, optional): Username to filter by
            
        Returns:
            list: Filtered list of cycle count records
        """
        if not self.supabase:
            st.error("Supabase client not initialized")
            return []
            
        try:
            query = self.supabase.table(CYCLE_COUNTS_TABLE).select("*")
            
            # Apply filters if provided
            if customer:
                query = query.eq(COLUMNS["customer"], customer)
                
            if date_from and date_to:
                query = query.gte(COLUMNS["cycle_date"], date_from.isoformat())
                query = query.lte(COLUMNS["cycle_date"], date_to.isoformat())
            elif date_from:
                query = query.gte(COLUMNS["cycle_date"], date_from.isoformat())
            elif date_to:
                query = query.lte(COLUMNS["cycle_date"], date_to.isoformat())
                
            if uploaded_by:
                query = query.eq(COLUMNS["uploaded_by"], uploaded_by)
            
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
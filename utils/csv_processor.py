import pandas as pd
import streamlit as st
from datetime import datetime
import uuid

def process_csv(file, metadata):
    """
    Process the uploaded CSV file and combine with metadata
    
    Args:
        file: The uploaded CSV file
        metadata (dict): Additional metadata to include
            - customer: Customer name
            - cycle_date: Date of cycle count
            - notes: Additional notes
            - uploaded_by: Username of uploader
    
    Returns:
        pd.DataFrame: Processed dataframe with all required fields
    """
    try:
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ["Item ID", "Description", "System Count", "Actual Count"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Rename columns to match database schema
        df = df.rename(columns={
            "Item ID": "item_id",
            "Description": "description",
            "System Count": "system_count",
            "Actual Count": "actual_count"
        })
        
        # Calculate variance and percentage difference
        df["variance"] = df["actual_count"] - df["system_count"]
        
        # Handle potential division by zero
        df["percent_diff"] = df.apply(
            lambda row: (row["variance"] / row["system_count"]) * 100 if row["system_count"] != 0 else 0, 
            axis=1
        )
        
        # Add metadata
        df["customer"] = metadata["customer"]
        df["notes"] = metadata["notes"]
        df["cycle_date"] = metadata["cycle_date"]
        df["uploaded_by"] = metadata["uploaded_by"]
        df["uploaded_at"] = datetime.now()
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        
        return df
    
    except Exception as e:
        st.error(f"Error processing CSV: {str(e)}")
        raise

def validate_csv(file):
    """
    Validate that the CSV has the required format
    
    Args:
        file: The uploaded CSV file
        
    Returns:
        bool: True if valid, False otherwise
        str: Error message if invalid
    """
    try:
        # Read first few rows to validate structure
        df = pd.read_csv(file, nrows=5)
        
        # Check required columns
        required_columns = ["Item ID", "Description", "System Count", "Actual Count"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        # Check data types
        try:
            pd.to_numeric(df["System Count"])
            pd.to_numeric(df["Actual Count"])
        except:
            return False, "System Count and Actual Count must be numeric values"
        
        return True, "CSV is valid"
    
    except Exception as e:
        return False, f"Error validating CSV: {str(e)}"

def prepare_for_db(df):
    """
    Convert DataFrame to list of dictionaries for database insertion
    
    Args:
        df (pd.DataFrame): The processed DataFrame
        
    Returns:
        list: List of dictionaries ready for database insertion
    """
    # Convert to dictionaries
    records = df.to_dict(orient="records")
    
    # Ensure numeric types are floats
    for record in records:
        record["system_count"] = float(record["system_count"])
        record["actual_count"] = float(record["actual_count"])
        record["variance"] = float(record["variance"])
        record["percent_diff"] = float(record["percent_diff"])
    
    return records 
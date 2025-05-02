import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime
from database.client import SupabaseClient
import uuid
import io  # For Excel export functionality
import logging  # Add this import
from components.authentication import check_admin_access

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_upload_form():
    """
    Render the interface for cycle count data management
    
    Returns:
        bool: True if data was successfully modified, False otherwise
    """
    st.title("Data Management")
    
    # Check user role from session state 
    is_admin = check_admin_access()
    
    # Initialize Supabase client
    db_client = SupabaseClient()
    
    # Fetch existing data
    with st.spinner("Loading data..."):
        data = db_client.get_all_cycle_counts()
        
    # Convert to DataFrame if data exists
    if data:
        df = pd.DataFrame(data)
        # Sort by most recent first
        if 'uploaded_at' in df.columns:
            df['uploaded_at'] = pd.to_datetime(df['uploaded_at'])
            df = df.sort_values('uploaded_at', ascending=False)
    else:
        df = pd.DataFrame()
    
    # Role based tabs - define tabs based on role
    if is_admin:
        tabs = st.tabs(["Add New Data", "Edit Existing", "Import", "Delete Records"])
        tab1, tab2, tab3, tab4 = tabs
    else:
        tabs = st.tabs(["Add New Data", "Import"])
        tab1, tab3 = tabs  # Note: tab3 here is actually "Import" for non-admins
        st.warning("For editing or deleting records, please contact your administrator.")
    
    # Tab 1: Add new record in table format (available to all roles)
    with tab1:
        st.subheader("Add New Data")
        
        # Add metadata fields at the top
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        
        # Customer metadata field
        customer_meta = meta_col1.text_input("Customer Name")
        
        # Date metadata field
        cycle_date_meta = meta_col2.date_input("Cycle Count Date", 
                                        value=date.today(), 
                                        help="Select the date when the cycle count was performed")
        
        # Warehouse selection - for admins, provide dropdown, for managers use their assigned warehouse
        if is_admin:
            # Get all warehouses
            warehouses = db_client.get_all_warehouses()
            warehouse_options = {w['id']: w['name'] for w in warehouses}
            selected_warehouse = meta_col3.selectbox(
                "Warehouse Location", 
                options=list(warehouse_options.keys()),
                format_func=lambda x: warehouse_options[x],
                help="Select the warehouse where this count was performed"
            )
        else:
            # For managers, use their assigned warehouse
            warehouse_id = st.session_state.get("warehouse_id")
            if warehouse_id:
                warehouse = db_client.get_warehouse(warehouse_id)
                warehouse_name = warehouse.get("name", "Unknown") if warehouse else "Unknown"
                meta_col3.text_input("Warehouse Location", value=warehouse_name, disabled=True)
                selected_warehouse = warehouse_id
            else:
                meta_col3.error("No warehouse assigned to your account")
                selected_warehouse = None
        
        st.markdown("---")
        
        # Table instructions
        st.write("### Item Details")
        
        # Initialize session state for table data if it doesn't exist
        if "table_data" not in st.session_state:
            st.session_state.table_data = [{
                "item_id": "",
                "description": "",
                "lot_number": "",
                "expiration_date": None,
                "unit": "",
                "status": "",
                "lp": "",
                "location": "",
                "system_count": "",
                "actual_count": "",
                "notes": ""
            }]
        
        # Button to add more rows
        if st.button("Add Row"):
            st.session_state.table_data.append({
                "item_id": "",
                "description": "",
                "lot_number": "",
                "expiration_date": None,
                "unit": "",
                "status": "",
                "lp": "",
                "location": "",
                "system_count": "",
                "actual_count": "",
                "notes": ""
            })
        
        # Create a form for the table
        with st.form("table_form"):
            # Create table headers with new fields
            cols = st.columns([1.5, 2, 1.5, 1.5, 1, 1, 1, 1.5, 1.5, 1.5, 2])
            
            # Create a row for each data entry
            for i, row_data in enumerate(st.session_state.table_data):
                cols = st.columns([1.5, 2, 1.5, 1.5, 1, 1, 1, 1.5, 1.5, 1.5, 2])
                
                # Item ID (required)
                row_data["item_id"] = cols[0].text_input(
                    "Item ID*", 
                    value=row_data["item_id"], 
                    key=f"item_id_{i}",
                    help="Enter the item ID"
                )
                
                # Description
                row_data["description"] = cols[1].text_input(
                    "Description*", 
                    value=row_data["description"], 
                    key=f"desc_{i}",
                    help="Enter the item description"
                )
                
                # Lot Number
                row_data["lot_number"] = cols[2].text_input(
                    "Lot Number", 
                    value=row_data["lot_number"], 
                    key=f"lot_{i}",
                    help="Enter the item lot number (optional)"
                )
                
                # Expiration Date
                exp_date = cols[3].date_input(
                    "Expiration Date",
                    value=row_data["expiration_date"] if row_data["expiration_date"] else None,
                    key=f"exp_{i}",
                    help="Enter the item expiration date (optional)"
                )
                row_data["expiration_date"] = exp_date
                
                # Unit
                row_data["unit"] = cols[4].text_input(
                    "Unit",
                    value=row_data["unit"],
                    key=f"unit_{i}",
                    help="Enter the item unit (optional)"
                )
                
                # Status
                row_data["status"] = cols[5].text_input(
                    "Status",
                    value=row_data["status"],
                    key=f"status_{i}",
                    help="Enter the item status (optional)"
                )
                
                # LP
                row_data["lp"] = cols[6].text_input(
                    "LP",
                    value=row_data["lp"],
                    key=f"lp_{i}",
                    help="Enter the item LP (optional)"
                )
                
                # Location
                row_data["location"] = cols[7].text_input(
                    "Location*",
                    value=row_data["location"],
                    key=f"location_{i}",
                    help="Enter the item location"
                )
                
                # System Count
                row_data["system_count"] = cols[8].text_input(
                    "System Count*", 
                    value=row_data["system_count"],
                    key=f"system_{i}",
                    help="Enter the item count from the system"
                )
                
                # Actual Count
                row_data["actual_count"] = cols[9].text_input(
                    "Actual Count*", 
                    value=row_data["actual_count"],
                    key=f"actual_{i}",
                    help="Enter the item count from the actual physical count"
                )
                
                # Notes
                row_data["notes"] = cols[10].text_input(
                    "Notes", 
                    value=row_data["notes"], 
                    key=f"notes_{i}",
                    help="Enter any additional notes about the item"
                )
            
            # Submit button
            submit_btn = st.form_submit_button("Submit All Rows")
            
            if submit_btn:
                # Validate metadata
                if not customer_meta:
                    st.error("Customer name is required")
                else:
                    valid_rows = []
                    errors = []
                    
                    # Validate and prepare each row
                    for i, row_data in enumerate(st.session_state.table_data):
                        if not row_data["item_id"]:
                            errors.append(f"Row {i+1}: Item ID is required")
                            continue
                        
                        # Calculate variance and percent difference
                        try:
                            system_count = float(row_data["system_count"])
                            actual_count = float(row_data["actual_count"])
                            variance = actual_count - system_count
                            percent_diff = (variance / system_count) * 100 if system_count != 0 else 0
                        except ValueError:
                            errors.append(f"Row {i+1}: System Count and Actual Count must be numbers")
                            continue
                        
                        # Prepare record for database - use metadata for customer and cycle_date
                        record = {
                            "id": str(uuid.uuid4()),
                            "item_id": row_data["item_id"],
                            "description": row_data["description"] or "No description",
                            "lot_number": row_data["lot_number"] or "",
                            "expiration_date": row_data["expiration_date"].isoformat() if row_data["expiration_date"] else None,
                            "unit": row_data["unit"] or "",
                            "status": row_data["status"] or "",
                            "lp": row_data["lp"] or "",
                            "location": row_data["location"] or "",
                            "system_count": system_count,
                            "actual_count": actual_count,
                            "variance": variance,
                            "percent_diff": percent_diff,
                            "customer": customer_meta,
                            "notes": row_data["notes"] or "",
                            "cycle_date": cycle_date_meta.isoformat(),
                            "uploaded_by": st.session_state.get("user_id"),
                            "warehouse_id": selected_warehouse,
                            "uploaded_at": datetime.now().isoformat()
                        }
                        
                        # Remove the existing "expiration_date" field if it exists
                        if "expiration_date" in record:
                            del record["expiration_date"]
                        
                        valid_rows.append(record)
                    
                    # Show errors if any
                    if errors:
                        for error in errors:
                            st.error(error)
                    
                    # Process valid rows
                    if valid_rows and not errors:
                        success_count = 0
                        error_count = 0
                        
                        for record in valid_rows:
                            try:
                                db_client.insert_cycle_count(record)
                                success_count += 1
                            except Exception as e:
                                error_count += 1
                                st.error(f"Error adding record: {str(e)}")
                        
                        if success_count > 0:
                            st.success(f"Successfully added {success_count} records for {customer_meta}")
                            # Reset the table data for new entries
                            st.session_state.table_data = [{
                                "item_id": "",
                                "description": "",
                                "lot_number": "",
                                "expiration_date": None,
                                "unit": "",
                                "status": "",
                                "lp": "",
                                "location": "",
                                "system_count": 0.0,
                                "actual_count": 0.0,
                                "notes": ""
                            }]
                            
                            return True
    # Admin-only tabs
    if is_admin:
        # Tab 2: Edit Existing (admin only)
        with tab2:
            st.subheader("Edit Existing Records")
            
            if df.empty:
                st.info("No records to edit.")
            else:
                # Create filters
                if 'customer' in df.columns:
                    customers = ['All'] + sorted(df['customer'].unique().tolist())
                    selected_customer = st.selectbox("Filter by Customer", customers, key="filter_customer")
                    
                    if selected_customer != 'All':
                        filtered_df = df[df['customer'] == selected_customer]
                    else:
                        filtered_df = df
                else:
                    filtered_df = df
                
                # Display records to edit
                if not filtered_df.empty:
                    # Show only relevant columns for selection
                    display_cols = ['item_id', 'description', 'lot_number', 'location', 'system_count', 
                                    'actual_count', 'variance', 'customer', 'cycle_date']
                    selection_df = filtered_df[display_cols].head(100)  # Limit to 100 rows for performance
                    
                    st.write(f"Showing {len(selection_df)} most recent records (up to 100)")
                    st.dataframe(selection_df)
                    
                    # Select record to edit
                    record_indices = [f"{row['item_id']} - {row['description']}" 
                                        for _, row in filtered_df.head(100).iterrows()]
                    
                    if record_indices:
                        selected_record_idx = st.selectbox("Select record to edit:", 
                                                            options=range(len(record_indices)),
                                                            format_func=lambda x: record_indices[x])
                        
                        record_to_edit = filtered_df.iloc[selected_record_idx]
                        record_id = record_to_edit.get('id')
                        
                        # Edit form
                        with st.form("edit_record_form"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                item_id = st.text_input("Item ID*", 
                                                        value=record_to_edit.get('item_id', ''),
                                                        key="edit_item_id")
                                description = st.text_input("Description*", 
                                                            value=record_to_edit.get('description', ''),
                                                            key="edit_desc")
                                lot_number = st.text_input("Lot Number", 
                                                        value=record_to_edit.get('lot_number', ''),
                                                        key="edit_lot")
                                
                                # Handle expiration date
                                default_exp_date = None
                                if 'expiration_date' in record_to_edit and record_to_edit['expiration_date']:
                                    try:
                                        if isinstance(record_to_edit['expiration_date'], str):
                                            default_exp_date = datetime.strptime(
                                                record_to_edit['expiration_date'].split('T')[0], '%Y-%m-%d').date()
                                        else:
                                            default_exp_date = record_to_edit['expiration_date']
                                    except:
                                        pass
                                
                                expiration_date = st.date_input("expiration_date", 
                                                                value=default_exp_date,
                                                                key="edit_exp_date")
                                                                
                            with col2:
                                unit = st.text_input("Unit", 
                                                    value=record_to_edit.get('unit', ''),
                                                    key="edit_unit")
                                status = st.text_input("Status", 
                                                    value=record_to_edit.get('status', ''),
                                                    key="edit_status")
                                lp = st.text_input("LP", 
                                                    value=record_to_edit.get('lp', ''),
                                                    key="edit_lp")
                                location = st.text_input("Location", 
                                                        value=record_to_edit.get('location', ''),
                                                        key="edit_location")
                            
                            with col3:
                                customer = st.text_input("Customer*", 
                                                        value=record_to_edit.get('customer', ''),
                                                        key="edit_customer")
                                system_count = st.number_input("System Count*", 
                                                            value=float(record_to_edit.get('system_count', 0)),
                                                            min_value=0.0, step=1.0,
                                                            key="edit_system")
                                actual_count = st.number_input("Actual Count*", 
                                                            value=float(record_to_edit.get('actual_count', 0)),
                                                            min_value=0.0, step=1.0,
                                                            key="edit_actual")
                                
                                # Handle cycle_date
                                default_date = date.today()
                                if 'cycle_date' in record_to_edit:
                                    try:
                                        if isinstance(record_to_edit['cycle_date'], str):
                                            default_date = datetime.strptime(
                                                record_to_edit['cycle_date'].split('T')[0], '%Y-%m-%d').date()
                                        else:
                                            default_date = record_to_edit['cycle_date']
                                    except:
                                        pass
                                        
                                cycle_date = st.date_input("Cycle Date", 
                                                            value=default_date,
                                                            key="edit_date")
                            
                            # Notes field (full width)
                            notes = st.text_area("Notes", 
                                                value=record_to_edit.get('notes', ''),
                                                key="edit_notes")
                            
                            # Calculated fields
                            variance = actual_count - system_count
                            percent_diff = (variance / system_count) * 100 if system_count != 0 else 0
                                
                            col1, col2 = st.columns(2)
                            col1.metric("Calculated Variance", f"{variance:.2f}")
                            col2.metric("Calculated % Difference", f"{percent_diff:.2f}%")
                            
                            update_btn = st.form_submit_button("Update Record")
                            
                            if update_btn:
                                if not item_id or not description or not customer:
                                    st.error("Required fields must be filled")
                                else:
                                    try:
                                        # Update record with all fields
                                        updated_record = {
                                            "item_id": item_id,
                                            "description": description,
                                            "lot_number": lot_number,
                                            "expiration_date": expiration_date.isoformat() if expiration_date else None,
                                            "unit": unit,
                                            "status": status,
                                            "lp": lp,
                                            "location": location,
                                            "system_count": float(system_count),
                                            "actual_count": float(actual_count),
                                            "variance": float(variance),
                                            "percent_diff": float(percent_diff),
                                            "customer": customer,
                                            "notes": notes,
                                            "cycle_date": cycle_date.isoformat(),
                                            "warehouse_id": selected_warehouse
                                        }
                                        
                                        # Update database
                                        updated = db_client.update_cycle_count(record_id, updated_record)
                                        if updated:
                                            st.success("Record updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to update record.")
                                    except Exception as e:
                                        st.error(f"Error updating record: {str(e)}")
        # Tab 4: Delete Records (admin only)
        with tab4:
            st.subheader("Delete Records")
            st.warning("⚠️ Deletion cannot be undone. Use with caution!")
            
            if df.empty:
                st.info("No records to delete.")
            else:
                # Create filters
                col1, col2 = st.columns(2)
                
                # Customer filter
                if 'customer' in df.columns:
                    customers = ['All'] + sorted(df['customer'].unique().tolist())
                    with col1:
                        delete_customer = st.selectbox("Filter by Customer", customers, key="del_customer")
                
                # Date range filter
                with col2:
                    delete_date_range = st.date_input(
                        "Filter by Cycle Date",
                        value=[],
                        key="del_date_range",
                        help="Select date range for filtering records"
                    )
                
                # Apply filters
                delete_df = df.copy()
                
                if 'customer' in df.columns and delete_customer != 'All':
                    delete_df = delete_df[delete_df['customer'] == delete_customer]
                
                if len(delete_date_range) == 2:
                    start_date, end_date = delete_date_range
                    if 'cycle_date' in delete_df.columns:
                        delete_df['cycle_date'] = pd.to_datetime(delete_df['cycle_date']).dt.date
                        delete_df = delete_df[
                            (delete_df['cycle_date'] >= start_date) & 
                            (delete_df['cycle_date'] <= end_date)
                        ]
                
                # Display records that can be deleted
                if not delete_df.empty:
                    # Show only relevant columns for selection
                    display_cols = ['item_id', 'description', 'system_count', 'actual_count', 
                                    'customer', 'cycle_date']
                    delete_display_df = delete_df[display_cols].head(100)  # Limit for performance
                    
                    st.write(f"Showing {len(delete_display_df)} records (up to 100)")
                    
                    # Initialize session state for selected records if needed
                    if "selected_delete_records" not in st.session_state:
                        st.session_state.selected_delete_records = set()
                    
                    # Select All checkbox
                    select_all = st.checkbox("Select All Records", key="select_all_delete")
                    if select_all:
                        st.session_state.selected_delete_records = set(range(len(delete_display_df)))
                    elif select_all == False and len(st.session_state.selected_delete_records) == len(delete_display_df):
                        st.session_state.selected_delete_records = set()  # Clear if "select all" was unchecked
                    
                    # Display records with checkboxes
                    st.write("### Select Records to Delete")
                    
                    # Show records in a more structured way
                    for i, (idx, row) in enumerate(delete_display_df.iterrows()):
                        col1, col2 = st.columns([1, 20])
                        with col1:
                            # Use session state to maintain checkbox state
                            is_checked = i in st.session_state.selected_delete_records
                            if st.checkbox("Select record", value=is_checked, key=f"del_check_{i}", label_visibility="collapsed"):
                                st.session_state.selected_delete_records.add(i)
                            else:
                                if i in st.session_state.selected_delete_records:
                                    st.session_state.selected_delete_records.remove(i)
                        with col2:
                            # For displaying user information, you might need to join with users
                            # Instead of directly displaying uploaded_by, you might need:
                            user_name = "Unknown"
                            user_id = row.get("uploaded_by")
                            if user_id:
                                user = db_client.get_user_by_id(user_id)
                                if user:
                                    user_name = user.get("name", "Unknown")
                            st.write(f"{row['item_id']} - {row['description']} - {row['customer']} - {row['cycle_date']} - Uploaded by: {user_name}")
                    
                    # Bulk delete action
                    selected_records = list(st.session_state.selected_delete_records)
                    if selected_records:
                        st.warning(f"You've selected {len(selected_records)} record(s) to delete")
                        if st.button("Delete Selected Records", type="primary", key="bulk_delete_btn"):
                            try:
                                success_count = 0
                                for i in selected_records:
                                    record_id = delete_df.iloc[i].get('id')
                                    deleted = db_client.delete_cycle_count(record_id)
                                    if deleted:
                                        success_count += 1
                                
                                if success_count > 0:
                                    st.success(f"Successfully deleted {success_count} record(s)!")
                                    # Clear the selection after successful deletion
                                    st.session_state.selected_delete_records = set()
                                    st.rerun()
                                else:
                                    st.error("Failed to delete records.")
                            except Exception as e:
                                st.error(f"Error deleting records: {str(e)}")
                    else:
                        st.info("Select records to delete")
    
    # Tab 3: Import/Export (available to all, but it's tab2 for non-admins)
    with tab3:
        st.write("### Import Data")
        
        # Upload file
        uploaded_file = st.file_uploader("Upload CSV or Excel file", 
                                        type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                # Process uploaded file - properly use the first row as headers
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)  # Remove header=None
                else:
                    import_df = pd.read_excel(uploaded_file)  # Remove header=None
                
                # Convert all column names to lowercase - handle both string and non-string columns
                import_df.columns = [str(col).lower().strip() if isinstance(col, str) else str(col) for col in import_df.columns]
                
                # Column name mapping dictionary - maps various possible names to our standard fields
                column_mapping = {
                    # Standard name: [list of possible variant names]
                    "item_id": ["item_id", "itemid", "item_number", "itemnumber", "item", "sku", "item code", "itemcode", "part_number", "partnumber", "0"],
                    "description": ["description", "desc", "item_description", "itemdescription", "product_description", "name", "item_name", "product_name", "product", "1"],
                    "lot_number": ["lot_number", "lotnumber", "lot", "lot_no", "lot#", "batch", "batch_number", "batchnumber", "2"],
                    "expiration_date": ["expiration_date", "expirationdate", "expiration", "exp_date", "expdate", "exp", "expiry_date", "expirydate", "expiry", "3"],
                    "unit": ["unit", "uom", "measure", "unit_of_measure", "unitofmeasure", "units", "4"],
                    "status": ["status", "state", "condition", "item_status", "5"],
                    "lp": ["lp", "license_plate", "licenseplate", "pallet_id", "palletid", "6"],
                    "location": ["location", "loc", "storage_location", "storagelocation", "bin", "bin_location", "warehouse_location", "7"],
                    "system_count": ["system_count", "systemcount", "expected_count", "expectedcount", "expected", "system_qty", "qty", "system", "book_count", "bookcount", "8"],
                    "actual_count": ["actual_count", "actualcount", "counted", "physical_count", "physicalcount", "count", "physical", "actual_qty", "actual", "9"],
                    "customer": ["customer", "customer_name", "customername", "client", "client_name", "account", "10"],
                    "notes": ["notes", "note", "comments", "comment", "remarks", "observation", "observations", "details", "11"]
                }
                
                # Check if columns might be numeric indices
                has_numeric_columns = any(col.isdigit() for col in import_df.columns if isinstance(col, str))
                
                # If first row might actually be data (numeric column names), try to fix it
                if has_numeric_columns or all(isinstance(col, int) or (isinstance(col, str) and col.isdigit()) for col in import_df.columns):
                    st.warning("Your file appears to be missing headers. Attempting to infer column meanings...")
                    
                    # Reset the index to make the first row of data become column headers
                    # First read the file again to get a fresh copy
                    if uploaded_file.name.endswith('.csv'):
                        import_df = pd.read_csv(uploaded_file, header=None)
                    else:
                        import_df = pd.read_excel(uploaded_file, header=None)
                    
                    # Map the numeric columns to standard names based on position
                    standard_fields = ["item_id", "description", "lot_number", "expiration_date", 
                                        "unit", "status", "lp", "location", 
                                        "system_count", "actual_count", "customer", "notes"]
                    
                    rename_dict = {}
                    for i, col in enumerate(import_df.columns):
                        if i < len(standard_fields):
                            rename_dict[col] = standard_fields[i]
                    
                    import_df = import_df.rename(columns=rename_dict)
                else:
                    # Create a reverse lookup dictionary
                    reverse_mapping = {}
                    for standard_name, variants in column_mapping.items():
                        for variant in variants:
                            reverse_mapping[variant] = standard_name
                    
                    # Map columns in the imported dataframe to our standard names
                    renamed_columns = {}
                    found_columns = set()
                    
                    for col in import_df.columns:
                        col_str = str(col).lower().strip()
                        if col_str in reverse_mapping:
                            standard_name = reverse_mapping[col_str]
                            renamed_columns[col] = standard_name
                            found_columns.add(standard_name)
                    
                    # Rename columns in dataframe
                    import_df = import_df.rename(columns=renamed_columns)
                
                # Check for and resolve duplicate columns
                if any(import_df.columns.duplicated()):
                    duplicate_cols = import_df.columns[import_df.columns.duplicated()].tolist()
                    st.warning(f"Found duplicate columns: {duplicate_cols}. Keeping only the first occurrence of each.")
                    
                    # Create a new DataFrame with deduplicated columns
                    unique_columns = []
                    for col in import_df.columns:
                        if col not in unique_columns:
                            unique_columns.append(col)
                    
                    # Select only the first occurrence of each column name
                    import_df = import_df[unique_columns]
                
                # Check required columns
                # TODO: FINALIZE WITH BRAYAN WHAT COLUMNS ARE REQUIRED
                required_cols = ["item_id", "system_count", "actual_count", "customer"]
                missing_cols = [col for col in required_cols if col not in import_df.columns]
                
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    st.write("Available columns: ", ", ".join([str(col) for col in import_df.columns]))
                    st.write("Please ensure your file has columns that can be mapped to: item_id, description, system_count, actual_count, and customer")
                else:
                    st.write("Preview of data to import:")
                    st.dataframe(import_df.head(5))
                    
                # Add missing standard columns if necessary
                # if "cycle_date" not in import_df.columns:
                #     import_df["cycle_date"] = date.today().isoformat()
                # if "notes" not in import_df.columns:
                #     import_df["notes"] = ""
                # for field in ["lot_number", "unit", "status", "lp", "location"]:
                #     if field not in import_df.columns:
                #         import_df[field] = ""
                # if "expiration_date" not in import_df.columns:
                #     import_df["expiration_date"] = None
                # Add better file preview to help diagnose issues
                st.write("### File Overview")
                st.write(f"Total rows: {len(import_df)}")
                st.write(f"Columns found: {', '.join(import_df.columns.tolist())}")
                
                
                # Calculate variance and percent_diff
                import_df["variance"] = import_df["actual_count"] - import_df["system_count"]
                import_df["percent_diff"] = import_df.apply(
                    lambda row: (row["variance"] / row["system_count"]) * 100 
                                if row["system_count"] != 0 else 0, 
                    axis=1
                )
                
                # Make sure expiration_date is handled specially since it can't be a default string
                # TODO: THIS MIGHT CAUSING ISSUES
                if "expiration_date" in import_df.columns:
                    import_df["expiration_date"] = import_df["expiration_date"].apply(
                        lambda x: None if pd.isna(x) else x
                    )
                    
                # Add warehouse selection for imports
                st.write("### Select Warehouse")
                warehouse_id = None
                if is_admin:
                    # For admins, provide dropdown
                    warehouses = db_client.get_all_warehouses()
                    warehouse_options = {w['id']: w['name'] for w in warehouses}
                    warehouse_id = st.selectbox(
                        "Import Warehouse", 
                        options=list(warehouse_options.keys()),
                        format_func=lambda x: warehouse_options[x],
                        help="Select the warehouse for these imported records"
                    )
                else:
                    # For managers, use their assigned warehouse
                    warehouse_id = st.session_state.get("warehouse_id")
                    if warehouse_id:
                        warehouse = db_client.get_warehouse(warehouse_id)
                        st.info(f"Importing to warehouse: {warehouse.get('name', 'Unknown')}")
                    else:
                        st.error("No warehouse assigned to your account")
                
                # Add required cycle count date selector
                st.write("### Select Cycle Count Date")
                cycle_count_date = st.date_input(
                    "Cycle Count Date*", 
                    value=date.today(),
                    help="This date will be used for all records in this import"
                )

                # Check for completely empty columns that might cause issues
                empty_cols = [col for col in import_df.columns if import_df[col].isna().all()]

                # Show more rows in preview to help diagnose issues
                with st.expander("Expanded data preview (10 rows)"):
                    st.dataframe(import_df.head(10))

                # Import button
                if st.button("Import Data"):
                    # Validate cycle count date was selected
                    if not cycle_count_date:
                        st.error("Please select a cycle count date before importing")
                    else:
                        with st.spinner("Preparing to import..."):
                            records = import_df.to_dict('records')
                            total_records = len(records)
                            
                            if total_records == 0:
                                st.warning("No records found to import. Please check your file.")
                            else:
                                # Create a progress bar
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                success_count = 0
                                error_count = 0
                                
                                # Process records with progress updates
                                for i, record in enumerate(records):
                                    try:
                                        # Update progress
                                        progress = int((i / total_records) * 100)
                                        progress_bar.progress(progress)
                                        status_text.text(f"Processing: {i+1}/{total_records} records ({progress}%)")
                                        
                                        # Add required fields
                                        record["id"] = str(uuid.uuid4())
                                        record["uploaded_by"] = st.session_state.get("user_id")
                                        record["uploaded_at"] = datetime.now().isoformat()
                                        record["warehouse_id"] = warehouse_id
                                        
                                        # Override any existing cycle_date with the selected date
                                        record["cycle_date"] = cycle_count_date.isoformat()
                                        
                                        # Insert into database
                                        db_client.insert_cycle_count(record)
                                        success_count += 1
                                    except Exception as e:
                                        error_count += 1
                                        st.error(f"Error importing record {i+1}: {str(e)}")
                                
                                # Complete the progress bar
                                progress_bar.progress(100)
                                status_text.text(f"Import complete: {success_count}/{total_records} records processed successfully")
                                
                                st.success(f"Import complete. {success_count} records imported successfully, {error_count} errors.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    return False
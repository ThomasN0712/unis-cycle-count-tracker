import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date
from database.client import SupabaseClient
from database.schema import CYCLE_COUNTS_TABLE
import io

def render_manual_edit():
    """
    Render a UI for manually editing cycle count data
    """
    st.title("Manual Data Entry/Edit")
    
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
        st.info("No existing data found. Add your first record below.")
    
    # Add tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["Add New Record", "Edit Existing", "Bulk Import/Export", "Delete Records"])
    
    # Tab 1: Add new record manually
    with tab1:
        st.subheader("Add New Record")
        
        with st.form("add_record_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_id = st.text_input("Item ID*", key="new_item_id")
                description = st.text_input("Description*", key="new_desc")
                customer = st.text_input("Customer*", key="new_customer")
                notes = st.text_area("Notes", key="new_notes")
                
            with col2:
                system_count = st.number_input("System Count*", min_value=0.0, step=1.0, key="new_system")
                actual_count = st.number_input("Actual Count*", min_value=0.0, step=1.0, key="new_actual")
                cycle_date = st.date_input("Cycle Date", value=date.today(), key="new_date")
                
            # Calculated fields display (read-only)
            if system_count != 0:
                variance = actual_count - system_count
                percent_diff = (variance / system_count) * 100 if system_count != 0 else 0
            else:
                variance = 0
                percent_diff = 0
                
            st.metric("Calculated Variance", f"{variance:.2f}")
            st.metric("Calculated % Difference", f"{percent_diff:.2f}%")
            
            submit_btn = st.form_submit_button("Add Record")
            
            if submit_btn:
                if not item_id or not description or not customer:
                    st.error("Required fields (marked with *) must be filled")
                else:
                    try:
                        # Create new record
                        new_record = {
                            "id": str(uuid.uuid4()),
                            "item_id": item_id,
                            "description": description,
                            "system_count": float(system_count),
                            "actual_count": float(actual_count),
                            "variance": float(variance),
                            "percent_diff": float(percent_diff),
                            "customer": customer,
                            "notes": notes,
                            "cycle_date": cycle_date.isoformat(),
                            "uploaded_by": st.session_state.get("username", "manual_entry"),
                            "uploaded_at": datetime.now().isoformat()
                        }
                        
                        # Insert into database
                        db_client.insert_cycle_count(new_record)
                        st.success("Record added successfully!")
                        
                        # Don't rerun the page, just clear the form inputs using JS
                        st.markdown("""
                        <script>
                        document.querySelectorAll('input[type=text]').forEach(el => el.value = '');
                        document.querySelectorAll('textarea').forEach(el => el.value = '');
                        </script>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error adding record: {str(e)}")
    
    # Tab 2: Edit existing records
    with tab2:
        st.subheader("Edit Existing Records")
        
        if df.empty:
            st.info("No records to edit.")
        else:
            # Create filters
            if 'customer' in df.columns:
                customers = ['All'] + sorted(df['customer'].unique().tolist())
                selected_customer = st.selectbox("Filter by Customer", customers)
                
                if selected_customer != 'All':
                    filtered_df = df[df['customer'] == selected_customer]
                else:
                    filtered_df = df
            else:
                filtered_df = df
            
            # Display records to edit
            if not filtered_df.empty:
                # Show only relevant columns for selection
                display_cols = ['item_id', 'description', 'system_count', 'actual_count', 
                               'variance', 'customer', 'cycle_date']
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
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            item_id = st.text_input("Item ID*", 
                                                  value=record_to_edit.get('item_id', ''),
                                                  key="edit_item_id")
                            description = st.text_input("Description*", 
                                                     value=record_to_edit.get('description', ''),
                                                     key="edit_desc")
                            customer = st.text_input("Customer*", 
                                                   value=record_to_edit.get('customer', ''),
                                                   key="edit_customer")
                            notes = st.text_area("Notes", 
                                               value=record_to_edit.get('notes', ''),
                                               key="edit_notes")
                        
                        with col2:
                            system_count = st.number_input("System Count*", 
                                                        value=float(record_to_edit.get('system_count', 0)),
                                                        min_value=0.0, step=1.0,
                                                        key="edit_system")
                            actual_count = st.number_input("Actual Count*", 
                                                        value=float(record_to_edit.get('actual_count', 0)),
                                                        min_value=0.0, step=1.0,
                                                        key="edit_actual")
                            
                            # Handle date format
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
                        
                        # Calculated fields
                        variance = actual_count - system_count
                        percent_diff = (variance / system_count) * 100 if system_count != 0 else 0
                            
                        st.metric("Calculated Variance", f"{variance:.2f}")
                        st.metric("Calculated % Difference", f"{percent_diff:.2f}%")
                        
                        update_btn = st.form_submit_button("Update Record")
                        
                        if update_btn:
                            if not item_id or not description or not customer:
                                st.error("Required fields must be filled")
                            else:
                                try:
                                    # Update record
                                    updated_record = {
                                        "item_id": item_id,
                                        "description": description,
                                        "system_count": float(system_count),
                                        "actual_count": float(actual_count),
                                        "variance": float(variance),
                                        "percent_diff": float(percent_diff),
                                        "customer": customer,
                                        "notes": notes,
                                        "cycle_date": cycle_date.isoformat()
                                    }
                                    
                                    # Update database
                                    updated = db_client.update_cycle_count(record_id, updated_record)
                                    if updated:
                                        st.success("Record updated successfully!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("Failed to update record.")
                                except Exception as e:
                                    st.error(f"Error updating record: {str(e)}")
    
    # Tab 3: Import/Export
    with tab3:
        st.subheader("Bulk Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Export Data")
            
            # Export options
            export_format = st.radio("Export format:", 
                                   options=["CSV", "Excel"],
                                   horizontal=True)
            
            if not df.empty:
                # Apply date filter for export
                export_date_range = st.date_input(
                    "Date range (optional):",
                    value=[],
                    help="Filter data by cycle date before exporting"
                )
                
                export_df = df.copy()
                
                if len(export_date_range) == 2:
                    start_date, end_date = export_date_range
                    if 'cycle_date' in export_df.columns:
                        export_df['cycle_date'] = pd.to_datetime(export_df['cycle_date']).dt.date
                        export_df = export_df[
                            (export_df['cycle_date'] >= start_date) & 
                            (export_df['cycle_date'] <= end_date)
                        ]
                
                if export_format == "CSV":
                    export_data = export_df.to_csv(index=False).encode('utf-8')
                    file_ext = "csv"
                    mime = "text/csv"
                else:  # Excel
                    buffer = io.BytesIO()
                    export_df.to_excel(buffer, index=False)
                    export_data = buffer.getvalue()
                    file_ext = "xlsx"
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                st.download_button(
                    label=f"Download {export_format}",
                    data=export_data,
                    file_name=f"cycle_count_data_{datetime.now().strftime('%Y%m%d_%H%M')}.{file_ext}",
                    mime=mime
                )
            else:
                st.info("No data available to export.")
        
        with col2:
            st.write("### Import Data")
            
            # Upload file
            uploaded_file = st.file_uploader("Upload CSV or Excel file", 
                                           type=["csv", "xlsx", "xls"])
            
            if uploaded_file is not None:
                try:
                    # Process uploaded file
                    if uploaded_file.name.endswith('.csv'):
                        import_df = pd.read_csv(uploaded_file)
                    else:
                        import_df = pd.read_excel(uploaded_file)
                    
                    # Check required columns
                    required_cols = ["item_id", "description", "system_count", "actual_count", "customer"]
                    missing_cols = [col for col in required_cols if col not in import_df.columns]
                    
                    if missing_cols:
                        st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    else:
                        st.write("Preview of data to import:")
                        st.dataframe(import_df.head(5))
                        
                        # Add missing columns if necessary
                        if "cycle_date" not in import_df.columns:
                            import_df["cycle_date"] = date.today().isoformat()
                        if "notes" not in import_df.columns:
                            import_df["notes"] = ""
                        
                        # Calculate variance and percent_diff
                        import_df["variance"] = import_df["actual_count"] - import_df["system_count"]
                        import_df["percent_diff"] = import_df.apply(
                            lambda row: (row["variance"] / row["system_count"]) * 100 
                                     if row["system_count"] != 0 else 0, 
                            axis=1
                        )
                        
                        # Import button
                        if st.button("Import Data"):
                            with st.spinner("Importing records..."):
                                records = import_df.to_dict('records')
                                success_count = 0
                                error_count = 0
                                
                                for record in records:
                                    try:
                                        # Add required fields
                                        record["id"] = str(uuid.uuid4())
                                        record["uploaded_by"] = st.session_state.get("username", "import")
                                        record["uploaded_at"] = datetime.now().isoformat()
                                        
                                        # Ensure numeric types are float
                                        for field in ["system_count", "actual_count", "variance", "percent_diff"]:
                                            if field in record:
                                                record[field] = float(record[field])
                                        
                                        # Insert into database
                                        db_client.insert_cycle_count(record)
                                        success_count += 1
                                    except Exception as e:
                                        error_count += 1
                                        st.error(f"Error importing record: {str(e)}")
                                
                                st.success(f"Import complete. {success_count} records imported successfully, {error_count} errors.")
                                if success_count > 0:
                                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")

    # Tab 4: Delete Records
    with tab4:
        st.subheader("Delete Records")
        st.warning("⚠️ Deletion cannot be undone. Use with caution!")
        
        if df.empty:
            st.info("No records to delete.")
        else:
            # Create filters
            if 'customer' in df.columns:
                customers = ['All'] + sorted(df['customer'].unique().tolist())
                delete_customer = st.selectbox("Filter by Customer", customers, key="del_customer")
                
                if delete_customer != 'All':
                    delete_df = df[df['customer'] == delete_customer]
                else:
                    delete_df = df
            else:
                delete_df = df
            
            # Display records that can be deleted
            if not delete_df.empty:
                # Show only relevant columns for selection
                display_cols = ['item_id', 'description', 'system_count', 'actual_count', 
                              'customer', 'cycle_date']
                delete_display_df = delete_df[display_cols].head(100)  # Limit for performance
                
                st.write(f"Showing {len(delete_display_df)} most recent records (up to 100)")
                st.dataframe(delete_display_df)
                
                # Select record to delete
                delete_indices = [f"{row['item_id']} - {row['description']} ({row['customer']})" 
                              for _, row in delete_df.head(100).iterrows()]
                
                if delete_indices:
                    selected_delete_idx = st.selectbox("Select record to delete:", 
                                                    options=range(len(delete_indices)),
                                                    format_func=lambda x: delete_indices[x],
                                                    key="del_select")
                    
                    record_to_delete = delete_df.iloc[selected_delete_idx]
                    record_id = record_to_delete.get('id')
                    
                    # Confirmation
                    st.info(f"""
                    You are about to delete:
                    - Item: {record_to_delete.get('item_id')}
                    - Description: {record_to_delete.get('description')}
                    - Customer: {record_to_delete.get('customer')}
                    """)
                    
                    # Required confirmation
                    confirm_text = st.text_input("Type 'DELETE' to confirm:")
                    
                    if confirm_text == "DELETE":
                        if st.button("Delete Record", type="primary"):
                            try:
                                # Delete from database
                                deleted = db_client.delete_cycle_count(record_id)
                                if deleted:
                                    st.success("Record deleted successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete record.")
                            except Exception as e:
                                st.error(f"Error deleting record: {str(e)}")

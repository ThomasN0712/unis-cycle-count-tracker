import streamlit as st

def render_tutorial():
    """
    Render the tutorial page with role-specific content
    """
    # Get user role from session state
    user_role = st.session_state.get("role", "manager")
    
    # Common introduction
    st.write("This guide will help you learn how to use the application effectively.")
    
    # Determine if user is admin
    is_admin = user_role == "admin"
    
    # Create tabs for different tutorial sections
    tutorial_tabs = st.tabs([
        "Getting Started", 
        "Dashboard", 
        "Data Management", 
        "Inventory Reconciliation",
    ])
    
    # Getting Started Tab
    with tutorial_tabs[0]:
        st.markdown("### Getting Started")
        st.write("The Cycle Count Tracker helps you manage inventory counts and identify discrepancies.")
        
        st.markdown("#### Basic Navigation")
        st.write("The application consists of three main sections:")
        st.markdown("""
        1. **Dashboard** - View and analyze cycle count data
        2. **Data Management** - Upload, download, and manage count data
        3. **Tutorial** - This help section
        """)
        
        # Image placeholder
        if not is_admin:
            st.markdown("---")
            st.image("assets/tutorial/dashboard_manager_sc.png")
            st.markdown("---")
        if is_admin:
            st.markdown("---")
            st.image("assets/tutorial/dashboard_admin_sc.png")
            st.markdown("---")
        
        if not is_admin:
            st.write("Your available features:")
            st.markdown("""
            - Upload cycle-count data
            - Access to dashboard and analysis chart
            - Access to reconciliation tool
            """)     
        
        if is_admin:
            st.write("As an administrator, you full access to all features:")
            st.markdown("""
                        
            - Read access to all data across all warehouses
            - Edit or remove cycle count data
            - Access to dashboard and analysis chart
            - Access to reconciliation tool
            """)
            
        # Image placeholder
        st.markdown("---")
            
    
    # Dashboard Tab
    with tutorial_tabs[1]:
        st.markdown("### Using the Dashboard")
        st.write("The dashboard allows you to view and analyze cycle count data.")
        
        st.markdown("#### Dashboard Features")
        
        # Image placeholder
        st.markdown("---")
        st.image("assets/tutorial/charts_sc.png")
        st.markdown("---")
        
        st.markdown("#### Using Filters")
        st.write("Narrow down data using the filters at the top of the dashboard:")
        st.markdown("""
        - **Customer** - Filter by customer name
        - **Date Range** - Select specific date periods
        - **Item Search** - Find specific items (partial matching supported)
        - **Location Search** - Find specific locations (partial matching supported)
        """)
        
        if is_admin:
            st.markdown("""
            Admin can also filter by:
            - **Uploaded By** - Filter by user who entered the data
            - **Warehouse** - Filter by warehouse location
            """)
    
    # Data Management Tab
    with tutorial_tabs[2]:
        st.markdown("### Data Management")
        st.write("This section allows you to upload count data and manage settings.")
        
        st.markdown("#### Uploading Data")
        if not is_admin:
            st.markdown("""
            1. Go to the **Data Management** tab

            2. For uploading data you can either:""")
            st.markdown("### Example of adding new data:")
            st.markdown("""

            Use "Add New Data" to upload individual count records

            1. Select Customer name and cycle count date  
            2. Enter information for each item you are counting  
            3. Click "Add Record"
            """)
            st.image("assets/tutorial/add_new_data_manager_sc.png") 
            st.markdown("### Example of importing data:")
            st.markdown("""
            Use "Import" tab to upload a CSV or Excel file.

            1. Upload a file with the correct format (use template to ensure correct format)  
            2. Select cycle count date  
            3. Click "Import Data"
            """)
            st.image("assets/tutorial/import_manager_sc.png")
        if is_admin:
            st.markdown("""
            1. Go to the **Data Management** tab

            2. For uploading data you can either:
            """)
            st.markdown("### Example of adding new data:")
            st.markdown("""

            Use "Add New Data" to upload individual count records
            
            1. Select Customer name, cycle count date, and warehouse
            2. Enter information for each item you are counting
            3. Click "Add Record"
            """)
            
            st.image("assets/tutorial/add_new_data_admin_sc.png")
            
            st.markdown("### Example of importing data:")
            st.markdown(""" 
            Use "Import" tab to upload a CSV or Excel file.
            
            1. Upload a file with the correct format (use template to ensure correct format)
            2. Select warehouse and cycle count date
            3. Click "Import Data"
            """)
            st.image("assets/tutorial/import_admin_sc.png")
            
        
        st.markdown("#### Required Fields")
        st.markdown("""
        - **Item ID** - Unique identifier for the item
        - **Description** - Item description
        - **Location** - Storage location (e.g. Rack location: "120.03.2.1", Bulk location: "60.123")
        - **System Count** - Expected quantity in system
        - **Actual Count** - Actual physical count
        - **Customer** - Customer name
        """)
        
        if is_admin:
            st.markdown("#### Admin Data Management")
            st.markdown("""
            As an administrator, you can also:
            - View data across all warehouses
            - Edit or remove cycle count data
            """)
    
    # Inventory Reconciliation Tab
    with tutorial_tabs[3]:
        st.markdown("### Inventory Reconciliation")
        st.write("The reconciliation tool helps identify opportunities to resolve inventory discrepancies.")
        
        st.markdown("#### How It Works")
        st.markdown("""
        1. The system identifies items with both overages and shortages across different locations
        2. It suggests matches where items can be moved to resolve variances
        3. You can export a consolidated plan for physical inventory transfers
        """)

        st.markdown("#### Using the Reconciliation Tool")
        st.markdown("""
        1. Go to the **Reconciliation** tab in the dashboard
        2. Adjust the **Look Back Period** to control how far back to search
        3. Set the **Minimum Benefit Threshold** to focus on significant opportunities
        4. Review the suggested matches and export as needed
        """)
        
        st.markdown("---")
        st.image("assets/tutorial/reconciliation_tool_sc.png")
        st.markdown("---")
    
    
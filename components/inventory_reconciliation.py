import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import io

def find_reconciliation_opportunities(df, max_days=7):
    """
    Find reconciliation opportunities for items with overages in some locations
    and shortages in others within the specified time window.
    
    Args:
        df: DataFrame containing cycle count data
        max_days: Maximum number of days to look back for matches (default: 7)
    
    Returns:
        DataFrame with reconciliation opportunities
    """
    # Check if dataframe is empty first
    if df.empty:
        return pd.DataFrame()  # Return empty dataframe if input is empty
    
    # Make a copy of dataframe to avoid modifying the original
    working_df = df.copy()
    
    # Ensure cycle_date is in datetime format
    if 'cycle_date' in working_df.columns:
        # Check if there's data in the dataframe before accessing it
        if len(working_df) > 0:  # This checks if the dataframe has any rows
            # Convert from string format if necessary
            first_value = working_df['cycle_date'].iloc[0]
            if isinstance(first_value, str):
                working_df['cycle_date'] = pd.to_datetime(working_df['cycle_date'])
        else:
            return pd.DataFrame()  # Return empty dataframe if no data
    else:
        # If no cycle_date column, can't perform date filtering
        return pd.DataFrame()
    
    # Filter data to only include the last N days
    today = datetime.now().date()
    cutoff_date = today - timedelta(days=max_days)
    
    # Use datetime comparison - safely handle conversion
    try:
        recent_df = working_df[pd.to_datetime(working_df['cycle_date']).dt.date >= cutoff_date].copy()
    except:
        # If there's an error in date conversion, return empty frame
        return pd.DataFrame()
    
    if recent_df.empty:
        return pd.DataFrame()
    
    # Get only the most recent count for each item-location combination
    recent_df = recent_df.sort_values('cycle_date', ascending=False)
    recent_df = recent_df.drop_duplicates(subset=['item_id', 'location'], keep='first')
    
    opportunities = []
    
    # Group by item_id
    for item_id, item_group in recent_df.groupby('item_id'):
        # Skip if only one location for this item
        if len(item_group['location'].unique()) <= 1:
            continue
        
        # Get overages and shortages by location
        overages = item_group[item_group['variance'] > 0].copy()
        shortages = item_group[item_group['variance'] < 0].copy()
        
        # Skip if no overages or no shortages
        if overages.empty or shortages.empty:
            continue
        
        # Get item description (consistent across all rows)
        description = item_group['description'].iloc[0]
        unit = item_group['unit'].iloc[0] if 'unit' in item_group.columns else ''
        
        # Format overages data
        overage_locations = []
        for _, row in overages.iterrows():
            overage_locations.append({
                'location': row['location'],
                'variance': row['variance'],
                'date': row['cycle_date'],
                'warehouse': row.get('warehouse', 'Unknown')
            })
        
        # Format shortages data
        shortage_locations = []
        for _, row in shortages.iterrows():
            shortage_locations.append({
                'location': row['location'],
                'variance': row['variance'],
                'date': row['cycle_date'],
                'warehouse': row.get('warehouse', 'Unknown')
            })
        
        # Calculate total overage and shortage
        total_overage = overages['variance'].sum()
        total_shortage = shortages['variance'].sum()
        net_variance = total_overage + total_shortage  # This will be closer to 0 if they offset well
        
        # Calculate benefit (how much variance would be resolved)
        potential_benefit = min(total_overage, abs(total_shortage))
        
        # Create opportunity record
        opportunity = {
            'item_id': item_id,
            'description': description,
            'unit': unit,
            'overage_locations': overage_locations,
            'shortage_locations': shortage_locations,
            'total_overage': total_overage,
            'total_shortage': total_shortage,
            'net_variance': net_variance,
            'potential_benefit': potential_benefit
        }
        
        opportunities.append(opportunity)
    
    # Convert to DataFrame and sort by potential benefit
    if opportunities:
        opportunities_df = pd.DataFrame(opportunities)
        return opportunities_df.sort_values('potential_benefit', ascending=False)
    else:
        return pd.DataFrame()

# Add this new function to create Excel report for reconciliation
def create_reconciliation_excel(opportunity):
    """
    Create an Excel file for a reconciliation opportunity
    
    Args:
        opportunity: Dictionary containing reconciliation opportunity data
    
    Returns:
        BytesIO object containing Excel file
    """
    buffer = io.BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Create consolidated worksheet
        worksheet = workbook.add_worksheet('Reconciliation Plan')
        
        # Add title and header
        bold_format = workbook.add_format({'bold': True, 'font_size': 14})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        subheader_format = workbook.add_format({'bold': True, 'bg_color': '#E8E8E8', 'border': 1})
        cell_format = workbook.add_format({'border': 1})
        number_format = workbook.add_format({'border': 1, 'num_format': '0.00'})
        positive_format = workbook.add_format({'border': 1, 'num_format': '0.00', 'font_color': 'green'})
        negative_format = workbook.add_format({'border': 1, 'num_format': '0.00', 'font_color': 'red'})
        
        # Title and item details
        worksheet.write(0, 0, f"Inventory Reconciliation Plan", bold_format)
        worksheet.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Item information
        worksheet.write(3, 0, "Item ID:", header_format)
        worksheet.write(3, 1, opportunity['item_id'], cell_format)
        worksheet.write(3, 2, "Description:", header_format)
        worksheet.write(3, 3, opportunity['description'], cell_format)
        worksheet.write(4, 0, "Unit:", header_format)
        worksheet.write(4, 1, opportunity['unit'], cell_format)
        
        # Summary statistics
        worksheet.write(6, 0, "RECONCILIATION SUMMARY", bold_format)
        worksheet.write(7, 0, "Total Overage:", header_format)
        worksheet.write(7, 1, opportunity['total_overage'], positive_format)
        worksheet.write(7, 2, "Total Shortage:", header_format)
        worksheet.write(7, 3, opportunity['total_shortage'], negative_format)
        worksheet.write(8, 0, "Net Variance After Reconciliation:", header_format)
        worksheet.write(8, 1, opportunity['net_variance'], number_format)
        worksheet.write(8, 2, "Potential Benefit:", header_format)
        worksheet.write(8, 3, opportunity['potential_benefit'], positive_format)
        
        # Instructions
        worksheet.write(10, 0, "ACTION PLAN", bold_format)
        worksheet.write(11, 0, "1. Verify current quantities at all locations listed below")
        worksheet.write(12, 0, "2. Transfer inventory from 'Source' locations to 'Destination' locations as indicated")
        worksheet.write(13, 0, "3. Update system counts after physical transfer is complete")
        
        # Transfer plan header row
        transfer_row = 15
        worksheet.write(transfer_row, 0, "SOURCE LOCATIONS (Overages)", subheader_format)
        worksheet.write(transfer_row, 1, "Qty to Move", subheader_format)
        worksheet.write(transfer_row, 2, "DESTINATION LOCATIONS (Shortages)", subheader_format)
        worksheet.write(transfer_row, 3, "Missing Qty", subheader_format)
        worksheet.write(transfer_row, 4, "Transfer Complete ✓", subheader_format)
        
        # Match overages and shortages
        # Sort both by variance magnitude (descending)
        sorted_overages = sorted(opportunity['overage_locations'], key=lambda x: x['variance'], reverse=True)
        sorted_shortages = sorted(opportunity['shortage_locations'], key=lambda x: abs(x['variance']), reverse=True)
        
        # Determine how many rows we need (max of overages or shortages)
        transfer_count = max(len(sorted_overages), len(sorted_shortages))
        
        # Write transfer plan rows
        for i in range(transfer_count):
            row = transfer_row + i + 1
            
            # Source location (overages)
            if i < len(sorted_overages):
                loc_text = f"{sorted_overages[i]['location']} ({sorted_overages[i]['warehouse']})"
                worksheet.write(row, 0, loc_text, cell_format)
                worksheet.write(row, 1, sorted_overages[i]['variance'], positive_format)
            else:
                worksheet.write(row, 0, "", cell_format)
                worksheet.write(row, 1, "", cell_format)
                
            # Destination location (shortages)
            if i < len(sorted_shortages):
                loc_text = f"{sorted_shortages[i]['location']} ({sorted_shortages[i]['warehouse']})"
                worksheet.write(row, 2, loc_text, cell_format)
                worksheet.write(row, 3, abs(sorted_shortages[i]['variance']), number_format)
            else:
                worksheet.write(row, 2, "", cell_format)
                worksheet.write(row, 3, "", cell_format)
                
            # Checkbox column
            worksheet.write(row, 4, "□", cell_format)
        
        # Set column widths
        worksheet.set_column('A:A', 30)  # Source locations
        worksheet.set_column('B:B', 12)  # Qty to move
        worksheet.set_column('C:C', 30)  # Destination locations
        worksheet.set_column('D:D', 12)  # Missing qty
        worksheet.set_column('E:E', 18)  # Checkbox
        
        # Additional notes section
        notes_row = transfer_row + transfer_count + 3
        worksheet.write(notes_row, 0, "NOTES:", bold_format)
        for i in range(5):
            worksheet.write(notes_row + i + 1, 0, "", cell_format)
            worksheet.merge_range(notes_row + i + 1, 0, notes_row + i + 1, 4, "", cell_format)
    
    # Seek to beginning of file
    buffer.seek(0)
    return buffer

def create_consolidated_excel_report(opportunities):
    """
    Create a consolidated Excel report for all reconciliation opportunities
    
    Args:
        opportunities: DataFrame with all reconciliation opportunities
    
    Returns:
        BytesIO object containing Excel file
    """
    buffer = io.BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Create single consolidated worksheet
        worksheet = workbook.add_worksheet('Reconciliation Report')
        
        # Formats
        title_format = workbook.add_format({'bold': True, 'font_size': 14})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        cell_format = workbook.add_format({'border': 1})
        number_format = workbook.add_format({'border': 1, 'num_format': '0.00'})
        positive_format = workbook.add_format({'border': 1, 'num_format': '0.00', 'font_color': 'green'})
        negative_format = workbook.add_format({'border': 1, 'num_format': '0.00', 'font_color': 'red'})
        item_header_format = workbook.add_format({'bold': True, 'bg_color': '#4F81BD', 'font_color': 'white', 'border': 1})
        transfer_header_format = workbook.add_format({'bold': True, 'bg_color': '#E8E8E8', 'border': 1})
        
        # Title and general information
        worksheet.write(0, 0, "Inventory Reconciliation Opportunities", title_format)
        worksheet.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        worksheet.write(2, 0, f"Total opportunities: {len(opportunities)}")
        
        # Summary table header
        worksheet.write(4, 0, "Item ID", header_format)
        worksheet.write(4, 1, "Description", header_format)
        worksheet.write(4, 2, "Unit", header_format)
        worksheet.write(4, 3, "Total Overage", header_format)
        worksheet.write(4, 4, "Total Shortage", header_format)
        
        # Fill summary table
        total_overage = 0
        total_shortage = 0
        for i, opp in enumerate(opportunities.itertuples()):
            row = 5 + i
            worksheet.write(row, 0, opp.item_id, cell_format)
            worksheet.write(row, 1, opp.description, cell_format)
            worksheet.write(row, 2, opp.unit, cell_format)
            worksheet.write(row, 3, opp.total_overage, positive_format)
            worksheet.write(row, 4, opp.total_shortage, negative_format)
            total_overage += opp.total_overage
            total_shortage += opp.total_shortage
        
        # Summary totals
        worksheet.write(5 + len(opportunities), 0, "TOTAL", header_format)
        worksheet.write(5 + len(opportunities), 3, total_overage, positive_format)
        worksheet.write(5 + len(opportunities), 4, total_shortage, negative_format)
        
        # Set column widths for summary
        worksheet.set_column('A:A', 15)  # Item ID
        worksheet.set_column('B:B', 30)  # Description
        worksheet.set_column('C:C', 10)  # Unit
        worksheet.set_column('D:E', 15)  # Numeric columns
        
        # Start of detailed plans
        detail_row = 8 + len(opportunities)
        worksheet.write(detail_row, 0, "DETAILED TRANSFER PLANS", title_format)
        detail_row += 2
        
        # Process each opportunity
        for opp in opportunities.itertuples():
            # Item header section
            worksheet.write(detail_row, 0, "ITEM:", item_header_format)
            worksheet.write(detail_row, 1, opp.item_id, item_header_format)
            worksheet.write(detail_row, 2, opp.description, item_header_format)
            worksheet.write(detail_row, 3, f"Unit: {opp.unit}", item_header_format)
            worksheet.write(detail_row, 4, f"Benefit: {opp.potential_benefit:.0f}", item_header_format)
            detail_row += 1
            
            # Transfer plan header
            worksheet.write(detail_row, 0, "SOURCE LOCATION (Overage)", transfer_header_format)
            worksheet.write(detail_row, 1, "Warehouse", transfer_header_format)
            worksheet.write(detail_row, 2, "Qty to Move", transfer_header_format)
            worksheet.write(detail_row, 3, "DESTINATION LOCATION (Shortage)", transfer_header_format)
            worksheet.write(detail_row, 4, "Warehouse", transfer_header_format)
            worksheet.write(detail_row, 5, "Missing Qty", transfer_header_format)
            detail_row += 1
            
            # Sort overages and shortages by variance magnitude
            sorted_overages = sorted(opp.overage_locations, key=lambda x: x['variance'], reverse=True)
            sorted_shortages = sorted(opp.shortage_locations, key=lambda x: abs(x['variance']), reverse=True)
            
            # Determine number of rows needed
            transfer_count = max(len(sorted_overages), len(sorted_shortages))
            
            # Write transfer rows
            for j in range(transfer_count):
                # Source location (overage)
                if j < len(sorted_overages):
                    worksheet.write(detail_row, 0, sorted_overages[j]['location'], cell_format)
                    worksheet.write(detail_row, 1, sorted_overages[j]['warehouse'], cell_format)
                    worksheet.write(detail_row, 2, sorted_overages[j]['variance'], positive_format)
                else:
                    worksheet.write(detail_row, 0, "", cell_format)
                    worksheet.write(detail_row, 1, "", cell_format)
                    worksheet.write(detail_row, 2, "", cell_format)
                
                # Destination location (shortage)
                if j < len(sorted_shortages):
                    worksheet.write(detail_row, 3, sorted_shortages[j]['location'], cell_format)
                    worksheet.write(detail_row, 4, sorted_shortages[j]['warehouse'], cell_format)
                    worksheet.write(detail_row, 5, abs(sorted_shortages[j]['variance']), number_format)
                else:
                    worksheet.write(detail_row, 3, "", cell_format)
                    worksheet.write(detail_row, 4, "", cell_format)
                    worksheet.write(detail_row, 5, "", cell_format)
                
                detail_row += 1
            
            # Add space between items
            detail_row += 2
    
    # Seek to beginning of file
    buffer.seek(0)
    return buffer

def render_reconciliation_opportunities(df):
    """
    Render the reconciliation opportunities UI
    
    Args:
        df: DataFrame containing all cycle count data
    """
    # First check if dataframe is empty or very small
    if df is None or df.empty or len(df) < 2:
        st.info("No data available for reconciliation analysis.")
        return
        
    # Ensure we're working with a clean dataset
    working_df = df.copy()
    
    # Drop rows with missing essential data
    required_cols = ['item_id', 'location', 'variance']
    for col in required_cols:
        if col not in working_df.columns:
            st.error(f"Required column '{col}' missing from data.")
            return
    
    working_df = working_df.dropna(subset=required_cols)
    
    if working_df.empty:
        st.info("No valid data available after filtering out incomplete records.")
        return
    
    # Add introduction and instructions
    st.warning("This tool is still in development and may not work as expected.")
    st.write("""
    This tool helps identify opportunities to resolve inventory discrepancies by matching locations with overages (positive variance) 
    to locations with shortages (negative variance) for the same items.
    
    **How it works:**
    1. Select a look-back period (default: 7 days)
    2. Review the suggested matches below - each match shows where items are missing and where extras exist
    3. Use this information to relocate inventory and resolve variances
    4. Export all opportunities to Excel for further planning
    """)
    
    # Filter settings
    max_days = st.slider("Look back period (days)", min_value=1, max_value=30, value=7)
    
    # Find opportunities
    opportunities = find_reconciliation_opportunities(working_df, max_days=max_days)
    
    if opportunities.empty:
        st.info(f"No reconciliation opportunities found in the last {max_days} days.")
        return
    
    if opportunities.empty:
        st.info(f"No reconciliation opportunities found.")
        return
    
    # Show summary
    st.success(f"Found {len(opportunities)} reconciliation opportunities. " 
              f"Total potential variance reduction: {opportunities['potential_benefit'].sum():.0f} units")
    
    # Display opportunities
    for idx, opp in opportunities.iterrows():
        with st.expander(f"{opp['item_id']} - {opp['description']} (Benefit: {opp['potential_benefit']:.0f} {opp['unit']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Locations with Overages")
                if opp['overage_locations']:
                    overage_data = []
                    for loc in opp['overage_locations']:
                        overage_data.append({
                            "Location": loc['location'],
                            "Warehouse": loc['warehouse'],
                            "Overage": f"+{loc['variance']:.0f}",
                            "Date": loc['date'].strftime('%Y-%m-%d') if isinstance(loc['date'], pd.Timestamp) else loc['date']
                        })
                    st.table(pd.DataFrame(overage_data))
            
            with col2:
                st.subheader("Locations with Shortages")
                if opp['shortage_locations']:
                    shortage_data = []
                    for loc in opp['shortage_locations']:
                        shortage_data.append({
                            "Location": loc['location'],
                            "Warehouse": loc['warehouse'],
                            "Shortage": f"{loc['variance']:.0f}",
                            "Date": loc['date'].strftime('%Y-%m-%d') if isinstance(loc['date'], pd.Timestamp) else loc['date']
                        })
                    st.table(pd.DataFrame(shortage_data))
            
            st.write(f"Total Overage: +{opp['total_overage']:.0f} | Total Shortage: {opp['total_shortage']:.0f} | "
                    f"Net After Reconciliation: {opp['net_variance']:.0f}")
    
    # Add consolidated export button at the bottom
    if not opportunities.empty:
        st.markdown("---")
        st.subheader("Print Report")
        
        excel_data = create_consolidated_excel_report(opportunities)
        file_name = f"reconciliation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        st.download_button(
            label="📥 Export All Opportunities to Excel",
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download a consolidated report of all reconciliation opportunities"
        ) 
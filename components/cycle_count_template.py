import io
import pandas as pd


def create_import_template():
    """
    Create a template Excel file for data import
    
    Returns:
        BytesIO object containing Excel file
    """
    buffer = io.BytesIO()

    # Create DataFrame
    df = pd.DataFrame()
    
    # Write to Excel
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Import Template', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Import Template']
        
        # Add column width formatting
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
        worksheet.set_row(0, None, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 15)  # item_id
        worksheet.set_column('B:B', 30)  # description
        worksheet.set_column('C:C', 15)  # lot_number
        worksheet.set_column('D:D', 15)  # expiration_date
        worksheet.set_column('E:E', 10)  # unit
        worksheet.set_column('F:F', 10)  # status
        worksheet.set_column('G:G', 15)  # lp
        worksheet.set_column('H:H', 15)  # location
        worksheet.set_column('I:J', 12)  # system_count, actual_count
        worksheet.set_column('K:K', 15)  # customer
        worksheet.set_column('L:L', 30)  # notes
    
    # Reset buffer position
    buffer.seek(0)
    return buffer
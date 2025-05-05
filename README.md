# Cycle Count Tracker

A Streamlit-based application for warehouse inventory cycle count management. This tool allows warehouse managers to upload cycle count data, which is then stored in Supabase using the Supabase Python client. An admin dashboard allows viewing, filtering, and downloading all uploaded data.

## Features

- **User Authentication**: Secure login with different access levels (admin/manager)
- **CSV Upload**: Easy upload of cycle count data with metadata
- **Data Processing**: Automatic calculation of variance and percentage difference
- **Admin Dashboard**: Comprehensive data visualization and filtering
- **Data Export**: Download filtered data as CSV
- **Inventory Reconciliation**: Identify potential inventory discrepancies and suggest matches

## Project Structure

```
cycle-count-tracker/
├── app.py                      # Main entry point with authentication
├── requirements.txt            # Dependencies
├── .streamlit/
│   └── secrets.toml            # Supabase credentials (gitignored)
├── database/
│   ├── client.py               # Supabase connection
│   ├── schema.py               # Database schema definition
│   └── operations.py           # DB operations (queries, inserts)
├── components/
│   ├── authentication.py       # Auth UI components
│   ├── charts.py               # Visualization components
│   ├── cycle_count_template.py # Cycle count template
│   ├── inventory_reconciliation.py # Reconciliation components
│   ├── registration.py         # Registration functionality
│   ├── tutorial.py             # Tutorial components
│   └── upload.py               # Upload functionality
```

## Setup

1. Create a Supabase project at [Supabase](https://supabase.com/)

2. Run the database script in schema.py to create the necessary tables.

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create the `.streamlit/secrets.toml` file with your Supabase credentials:

   ```toml
   [supabase]
   url = "https://your-supabase-url.supabase.co"
   key = "your-supabase-key"
   [app_settings]
   invitation_code = "invitation-code"
   ```

5. Run the application:
   ```
   streamlit run app.py
   ```

## CSV File Format

Check out cycle_count_template.py for the correct column headers.

## User Roles

- **Admin**: Has access to the dashboard and can view all data from all warehouses and users.
- **Manager**: Can upload cycle count data and view data from their own warehouse.

## Deployment

The application can be deployed on [Streamlit Cloud](https://streamlit.io/cloud) by connecting your GitHub repository.

## Technology Stack

- [Streamlit](https://streamlit.io/) - Frontend and UI
- [Supabase](https://supabase.com/) - Database and storage
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Plotly](https://plotly.com/) - Data visualization

# Cycle Count Tracker

A Streamlit-based application for warehouse inventory cycle count management. This tool allows warehouse managers to upload cycle count data, which is then stored in Supabase using the Supabase Python client. An admin dashboard allows viewing, filtering, and downloading all uploaded data.

## Features

- **User Authentication**: Secure login with different access levels (admin/manager)
- **CSV Upload**: Easy upload of cycle count data with metadata
- **Data Processing**: Automatic calculation of variance and percentage difference
- **Admin Dashboard**: Comprehensive data visualization and filtering
- **Data Export**: Download filtered data as CSV

## Project Structure

```
cycle-count-tracker/
├── app.py                      # Main entry point with authentication
├── requirements.txt            # Dependencies
├── .streamlit/
│   └── secrets.toml            # Supabase credentials (gitignored)
├── config/
│   └── auth_config.py          # Authentication configuration
├── database/
│   ├── client.py               # Supabase connection
│   ├── schema.py               # Database schema definition
│   └── operations.py           # DB operations (queries, inserts)
├── components/
│   ├── authentication.py       # Auth UI components
│   ├── upload.py               # Upload functionality
│   ├── dashboard.py            # Admin dashboard components
│   └── charts.py               # Visualization components
├── utils/
│   ├── csv_processor.py        # CSV processing
│   └── data_transformer.py     # Data calculations
└── pages/
    ├── 1_Upload.py             # Upload page for managers
    └── 2_Dashboard.py          # Admin dashboard (restricted)
```

## Setup

1. Create a Supabase project at [Supabase](https://supabase.com/)

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create the `.streamlit/secrets.toml` file with your Supabase credentials:

   ```toml
   [supabase]
   url = "https://your-supabase-url.supabase.co"
   key = "your-supabase-key"
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## CSV File Format

The CSV file should have the following columns:

- Item ID
- Description
- System Count
- Actual Count

Example:

```
Item ID,Description,System Count,Actual Count
A123,Widget A,10,12
B456,Widget B,15,15
C789,Widget C,20,18
```

## User Roles

- **Admin**: Has access to the dashboard and can view all data
- **Manager**: Can upload cycle count data

## Default Users

- Admin:

  - Username: admin
  - Password: admin123

- Managers:

  - Username: manager1
  - Password: manager1pass

  - Username: manager2
  - Password: manager2pass

## Deployment

The application can be deployed on [Streamlit Cloud](https://streamlit.io/cloud) by connecting your GitHub repository.

## Technology Stack

- [Streamlit](https://streamlit.io/) - Frontend and UI
- [Supabase](https://supabase.com/) - Database and storage
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Plotly](https://plotly.com/) - Data visualization

## Security Notes

- For production use, replace the hardcoded user credentials in `auth_config.py`
- Ensure `.streamlit/secrets.toml` is included in your .gitignore file
- Consider adding more robust input validation for CSV files

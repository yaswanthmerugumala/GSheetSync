# 🔄 GSheetSync – Real-time Two-Way Sync Between Google Sheets & MySQL

GSheetSync is a Python-based tool that enables seamless, automatic synchronization of employee data between a Google Sheets spreadsheet and a MySQL database. It ensures both data sources stay up to date by syncing changes bidirectionally at regular intervals.

---

## Key Features

- Two-way data synchronization between Google Sheets and MySQL  
- Syncs employee records: ID, name, department, salary  
- Automated periodic sync using a background scheduler (every 1 minute)  
- Reliable error handling and detailed logging  
- Easy configuration with Google Sheets API and MySQL via SQLAlchemy  

---

## Technologies Used

- Python  
- Google Sheets API (via `gspread` and OAuth2)  
- SQLAlchemy ORM for MySQL integration  
- APScheduler for task scheduling  
- PyMySQL MySQL client  

---

## Quick Setup

1. Clone the repository and install dependencies.  
2. Provide Google service account credentials JSON and set environment variable `GOOGLE_APPLICATION_CREDENTIALS`.  
3. Update MySQL connection details and Google Sheets ID in the script.  
4. Run the sync service:  
   ```bash
   python sync_service.py


## Contact

    Email: yaswanthmerugumala@gmail.com

    LinkedIn: linkedin.com/in/yaswanthmerugumala

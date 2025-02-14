import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import time
import pymysql
import logging
from urllib.parse import quote_plus

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Google Sheets Credentials
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"  # Ensure this file exists!
SPREADSHEET_ID = "15FQxo2ZpIRdHcxuRvvNq6kUrWbjyFewE3vFxhSgCnk4"  # Replace with actual Sheet ID

# MySQL Configuration
DB_USER = 'root'
DB_PASSWORD = 'Yashu4593*?'
DB_HOST = '127.0.0.1'
DB_PORT = '3305'
DB_NAME = 'google_sheet_sync'

# URL Encode Password
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

# SQLAlchemy Setup
Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    salary = Column(DECIMAL(10, 2))

# Connect to MySQL
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Google Sheets Client
def get_google_sheets_client():
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        return gspread.authorize(credentials)
    except Exception as e:
        logging.error(f"Error authorizing Google Sheets client: {e}")
        return None

# Sync Google Sheets to MySQL
def sync_gsheet_to_db():
    session = Session()
    try:
        gc = get_google_sheets_client()
        if not gc:
            return

        sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
        records = sheet.get_all_records()

        if not records:
            logging.warning("No records found in Google Sheets.")
            return

        for record in records:
            employee_id = record.get('employee_id')
            if not str(employee_id).isdigit():
                continue
            
            employee_id = int(employee_id)
            db_record = session.query(Employee).filter_by(employee_id=employee_id).first()

            if db_record:
                db_record.name = record.get('name', db_record.name)
                db_record.department = record.get('department', db_record.department)
                db_record.salary = record.get('salary', db_record.salary)
            else:
                new_record = Employee(
                    employee_id=employee_id,
                    name=record.get('name'),
                    department=record.get('department'),
                    salary=record.get('salary')
                )
                session.add(new_record)
        
        session.commit()
        logging.info("Synced Google Sheets to MySQL.")
    except Exception as e:
        logging.error(f"Error syncing Google Sheets to MySQL: {e}")
        session.rollback()
    finally:
        session.close()

# Sync MySQL to Google Sheets
def sync_db_to_gsheet():
    session = Session()
    try:
        gc = get_google_sheets_client()
        if not gc:
            return

        sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
        records = session.query(Employee).all()
        
        sheet_data = sheet.get_all_values()
        existing_ids = {int(row[0]) for row in sheet_data[1:] if row[0].isdigit()}
        
        for record in records:
            row_data = [record.employee_id, record.name, record.department, float(record.salary)]
            if record.employee_id in existing_ids:
                row_index = next(i for i, row in enumerate(sheet_data) if row and int(row[0]) == record.employee_id)
                sheet.update(f"A{row_index+1}:D{row_index+1}", [row_data])
            else:
                sheet.append_row(row_data)
        
        logging.info("Synced MySQL to Google Sheets.")
    except Exception as e:
        logging.error(f"Error syncing MySQL to Google Sheets: {e}")
    finally:
        session.close()

# Scheduler for periodic syncing
scheduler = BackgroundScheduler()
scheduler.add_job(sync_gsheet_to_db, 'interval', minutes=1)
scheduler.add_job(sync_db_to_gsheet, 'interval', minutes=1)
scheduler.start()

try:
    logging.info("Sync service is running. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    logging.info("Sync service stopped.")
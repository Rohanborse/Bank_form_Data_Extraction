import psycopg2
import pandas as pd

# Database configuration
DB_CONFIG = {
    "host": "157.20.51.93",          # Change this to your database host
    "database": "adm_db",  # Replace with your database name
    "user": "postgres",          # Replace with your username
    "password": "Vikas$7!5&v^ate@",  # Replace with your password
    "port": 9871                  # Default PostgreSQL port
}


EXCEL_FILE = "bank_application_details.xlsx"  # Name of the Excel file
def fetch_bank_application_details():
    """
    Fetch table content using the stored procedure `f_get_bank_application_details`.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Execute the stored procedure
        cursor.execute("SELECT * FROM f_get_bank_application_details();")

        # Fetch all results
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Convert results to a DataFrame
        data_frame = pd.DataFrame(results, columns=column_names)

        return data_frame

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def append_to_excel(data_frame, excel_file):
    """
    Append data to an existing Excel file or create a new one if it doesn't exist.
    :param data_frame: DataFrame to write to Excel.
    :param excel_file: Path to the Excel file.
    """
    try:
        # Check if the file exists
        try:
            existing_data = pd.read_excel(excel_file)
            data_frame = pd.concat([existing_data, data_frame], ignore_index=True)
        except FileNotFoundError:
            print("Excel file not found. A new file will be created.")

        # Write to Excel
        data_frame.to_excel(excel_file, index=False)
        print(f"Data successfully appended to {excel_file}.")

    except Exception as e:
        print(f"Error while writing to Excel: {e}")

def overwrite_excel(data_frame, excel_file):
    """
    Overwrite existing Excel file or create a new one with the latest data.
    :param data_frame: DataFrame to write to Excel.
    :param excel_file: Path to the Excel file.
    """
    try:
        # Overwrite the Excel file
        data_frame.to_excel(excel_file, index=False)
        print(f"Data successfully written to {excel_file} (existing data cleared).")

    except Exception as e:
        print(f"Error while writing to Excel: {e}")


if __name__ == "__main__":
    print("Fetching bank application details...")

    # Fetch data from the database
    data = fetch_bank_application_details()

    if not data.empty:
        print("Data fetched successfully. Overwriting Excel file...")
        overwrite_excel(data, EXCEL_FILE)
    else:
        print("No data fetched. Excel file not updated.")
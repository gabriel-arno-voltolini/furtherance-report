import pandas as pd
from datetime import datetime

def calculate_total_hours_from_total_time(file_path, start_date, end_date):
    """Calculates total hours from the 'Total Time' column for a given date range."""
    try:
        data = pd.read_csv(file_path)

        # Convert start and end dates to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Convert 'Start Time' to datetime objects and extract the date
        data['Start Date'] = pd.to_datetime(data['Start Time'], errors='coerce', format='ISO8601').dt.date

        # Filter the data by date range
        filtered_data = data[(data['Start Date'] >= start_date) & (data['Start Date'] <= end_date)].copy()

        # Convert 'Total Time' to seconds using .loc
        filtered_data.loc[:, 'Total Time (seconds)'] = pd.to_timedelta(filtered_data['Total Time']).dt.total_seconds()

        # Calculate total hours
        total_hours = filtered_data['Total Time (seconds)'].sum() / 3600
        return total_hours
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    input_file = input("Enter the path to the exported CSV file from furtherance: ").strip()
    start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter the end date (YYYY-MM-DD): ").strip()

    total_hours = calculate_total_hours_from_total_time(input_file, start_date, end_date)
    if total_hours is not None:
        print(f"Total hours: {total_hours}")
    else:
        print("Error calculating total hours.")

if __name__ == "__main__":
    main()
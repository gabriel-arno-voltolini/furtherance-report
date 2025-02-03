from datetime import datetime
import pandas as pd
import pytz


def generate_report_by_task(data):
    """Generates a report of total time spent per task with a total sum."""
    data['Total Time (seconds)'] = (data['Stop Time'] - data['Start Time']).dt.total_seconds()
    task_summary = data.groupby('Name', as_index=False)['Total Time (seconds)'].sum()

    total_seconds = task_summary['Total Time (seconds)'].sum()
    total_row = pd.DataFrame({'Name': ['Total'], 'Total Time (seconds)': [total_seconds]})
    task_summary = pd.concat([task_summary, total_row], ignore_index=True)
    return task_summary

def generate_report_by_time_range(data, start_date, end_date):
    """Generates a report filtered by a given time range with a total sum.
    
    For tasks that start within the time range, the full duration is counted.
    The end_date is adjusted to include the entire day.
    """
    timezone = pytz.timezone("America/Sao_Paulo")
    data['Start Time'] = pd.to_datetime(data['Start Time'], utc=True).dt.tz_convert(timezone)
    data['Stop Time']  = pd.to_datetime(data['Stop Time'], utc=True).dt.tz_convert(timezone)
    start_date = timezone.localize(start_date)
    end_date = timezone.localize(end_date) + pd.Timedelta(days=1)
    filtered = data[(data['Start Time'] >= start_date) & (data['Start Time'] < end_date)].copy()
    filtered['Total Time (hours)'] = (filtered['Stop Time'] - filtered['Start Time']).dt.total_seconds() / 3600
    task_summary = filtered.groupby('Name', as_index=False)['Total Time (hours)'].sum()
    total_hours = task_summary['Total Time (hours)'].sum()
    total_row = pd.DataFrame({'Name': ['Total'], 'Total Time (hours)': [total_hours]})
    task_summary = pd.concat([task_summary, total_row], ignore_index=True)
    return task_summary

def generate_monthly_report(data):
    """Generates a report of total time spent per month with a total sum."""
    timezone = pytz.timezone("America/Sao_Paulo")
    data['Start Time'] = pd.to_datetime(data['Start Time'], utc=True).dt.tz_convert(timezone)
    data['Stop Time'] = pd.to_datetime(data['Stop Time'], utc=True).dt.tz_convert(timezone)
    data['Total Time (hours)'] = (data['Stop Time'] - data['Start Time']).dt.total_seconds() / 3600
    data['Month'] = data['Start Time'].dt.to_period('M')
    monthly_summary = data.groupby('Month', as_index=False)['Total Time (hours)'].sum()
    total_hours = monthly_summary['Total Time (hours)'].sum()
    total_row = pd.DataFrame({'Month': ['Total'], 'Total Time (hours)': [total_hours]})
    monthly_summary = pd.concat([monthly_summary, total_row], ignore_index=True)
    return monthly_summary

def main():
    input_file = input("Enter the path to the exported CSV file from furtherance: ").strip()
    output_file = input("Enter the output CSV file name: ").strip()
    try:
        data = pd.read_csv(input_file)
        data['Start Time'] = pd.to_datetime(data['Start Time'], errors='coerce')
        data['Stop Time'] = pd.to_datetime(data['Stop Time'], errors='coerce')
        data = data.dropna(subset=['Start Time', 'Stop Time'])
        print("Choose a report type:")
        print("1. Report by task")
        print("2. Report by time range")
        print("3. Monthly report")
        choice = int(input("Enter your choice (1/2/3): ").strip())
        if choice == 1:
            report = generate_report_by_task(data)
        elif choice == 2:
            start_date = datetime.strptime(input("Enter the start date (YYYY-MM-DD): ").strip(), "%Y-%m-%d")
            end_date = datetime.strptime(input("Enter the end date (YYYY-MM-DD): ").strip(), "%Y-%m-%d")
            report = generate_report_by_time_range(data, start_date, end_date)
        elif choice == 3:
            report = generate_monthly_report(data)
        else:
            print("Invalid choice.")
            return
        report.to_csv(output_file, index=False)
        print(f"Report generated and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

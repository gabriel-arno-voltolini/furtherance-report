from datetime import datetime
import pandas as pd
import pytz

def generate_report_by_task(data):
    data['Total Time (seconds)'] = data['Total Time'].apply(lambda x: pd.to_timedelta(x).total_seconds())
    task_summary = data.groupby('Name', as_index=False)['Total Time (seconds)'].sum()
    return task_summary

def generate_report_by_time_range(data, start_date, end_date):
    data['Start Time'] = pd.to_datetime(data['Start Time'], format='mixed', errors='coerce')
    data['Stop Time'] = pd.to_datetime(data['Stop Time'], format='mixed', errors='coerce')
    data = data.dropna(subset=['Start Time', 'Stop Time'])
    timezone = pytz.timezone("America/Sao_Paulo")
    start_date = timezone.localize(start_date)
    end_date = timezone.localize(end_date)
    filtered_data = data[(data['Start Time'] >= start_date) & (data['Stop Time'] <= end_date)].copy()
    filtered_data['Total Time (seconds)'] = filtered_data['Total Time'].apply(
        lambda x: pd.to_timedelta(x).total_seconds()
    )
    task_summary = filtered_data.groupby('Name', as_index=False)['Total Time (seconds)'].sum()
    return task_summary

def generate_monthly_report(data):
    data['Start Time'] = pd.to_datetime(data['Start Time'], format='ISO8601')
    data['Month'] = data['Start Time'].dt.tz_localize(None).dt.to_period('M')
    data['Total Time (hours)'] = data['Total Time'].apply(lambda x: pd.to_timedelta(x).total_seconds() / 3600)
    monthly_summary = data.groupby('Month', as_index=False)['Total Time (hours)'].sum()
    return monthly_summary

def main():
    input_file = input("Enter the path to the exported CSV file from furtherance: ").strip()
    output_file = input("Enter the output CSV file name: ").strip()

    try:
        data = pd.read_csv(input_file)

        print("Choose a report type:")
        print("1. Report by task")
        print("2. Report by time range")
        print("3. Monthly report")
        choice = int(input("Enter your choice (1/2/3): ").strip())

        if choice == 1:
            report = generate_report_by_task(data)
        elif choice == 2:
            start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter the end date (YYYY-MM-DD): ").strip()
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
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

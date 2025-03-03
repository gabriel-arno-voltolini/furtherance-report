import pandas as pd
from datetime import datetime
import os

def generate_task_report_by_time_range(file_path, start_date, end_date):
    """Generates a task report grouped by time range."""
    try:
        data = pd.read_csv(file_path)
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        data['Start Date'] = pd.to_datetime(data['Start Time'], errors='coerce', format='ISO8601').dt.date
        filtered_data = data[(data['Start Date'] >= start_date) & (data['Start Date'] <= end_date)].copy()
        filtered_data.loc[:, 'Total Time (seconds)'] = pd.to_timedelta(filtered_data['Total Time']).dt.total_seconds()
        task_summary = filtered_data.groupby('Name')['Total Time (seconds)'].sum().reset_index()
        task_summary['Total Time (hours)'] = task_summary['Total Time (seconds)'] / 3600
        total_seconds = task_summary['Total Time (seconds)'].sum()
        total_row = pd.DataFrame({'Name': ['Total'], 'Total Time (seconds)': [total_seconds], 'Total Time (hours)': [total_seconds / 3600]})
        task_summary = pd.concat([task_summary, total_row], ignore_index=True)
        task_summary = task_summary.drop(columns=['Total Time (seconds)'])
        return task_summary
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_monthly_report(file_path):
    """Generates a report of total time spent per month."""
    try:
        data = pd.read_csv(file_path)
        data['Start Time'] = pd.to_datetime(data['Start Time'], errors='coerce', format='ISO8601')
        data['YearMonth'] = data['Start Time'].dt.strftime('%Y-%m')
        data['Total Time (seconds)'] = pd.to_timedelta(data['Total Time']).dt.total_seconds()
        monthly_totals = data.groupby('YearMonth')['Total Time (seconds)'].sum().reset_index()
        monthly_totals['Total Time (hours)'] = monthly_totals['Total Time (seconds)'] / 3600
        monthly_totals = monthly_totals.drop(columns=['Total Time (seconds)'])
        return monthly_totals
    except FileNotFoundError:
        print(f"Error: File not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    input_file = input("Enter the path to the exported CSV file from furtherance: ").strip()
    start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter the end date (YYYY-MM-DD): ").strip()
    base_name, extension = os.path.splitext(input_file)
    task_output_file = f"{base_name}-by-task{extension}"
    task_report = generate_task_report_by_time_range(input_file, start_date, end_date)
    if task_report is not None:
        print("Task Report:")
        print(task_report)
        task_report.to_csv(task_output_file, index=False)
        print(f"Task report saved to {task_output_file}")
    else:
        print("Error generating task report.")
    monthly_output_file = f"{base_name}-monthly{extension}"
    monthly_report = generate_monthly_report(input_file)
    if monthly_report is not None:
        print("\nMonthly Report:")
        print(monthly_report)
        monthly_report.to_csv(monthly_output_file, index=False)
        print(f"Monthly report saved to {monthly_output_file}")
    else:
        print("Error generating monthly report.")

if __name__ == "__main__":
    main()
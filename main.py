import pandas as pd
from datetime import datetime
import os

def generate_task_report_by_time_range(file_path, start_date, end_date):
    """Generates a task report grouped by time range."""
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

        # Group by 'Name' and sum the 'Total Time (seconds)'
        task_summary = filtered_data.groupby('Name')['Total Time (seconds)'].sum().reset_index()

        # Calculate total hours for each task
        task_summary['Total Time (hours)'] = task_summary['Total Time (seconds)'] / 3600

        # Create a total row
        total_seconds = task_summary['Total Time (seconds)'].sum()
        total_row = pd.DataFrame({'Name': ['Total'], 'Total Time (seconds)': [total_seconds], 'Total Time (hours)': [total_seconds / 3600]})
        task_summary = pd.concat([task_summary, total_row], ignore_index=True)

        # Drop the seconds column
        task_summary = task_summary.drop(columns=['Total Time (seconds)'])

        return task_summary

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    input_file = input("Enter the path to the exported CSV file from furtherance: ").strip()
    start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter the end date (YYYY-MM-DD): ").strip()

    # Generate output file name
    base_name, extension = os.path.splitext(input_file)
    output_file = f"{base_name}-by-task{extension}"

    report = generate_task_report_by_time_range(input_file, start_date, end_date)
    if report is not None:
        print(report)
        report.to_csv(output_file, index=False)
        print(f"Report saved to {output_file}")
    else:
        print("Error generating task report.")

if __name__ == "__main__":
    main()
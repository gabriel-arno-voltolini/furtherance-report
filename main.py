import pandas as pd
from datetime import datetime
import os
import re

def generate_task_report_by_time_range(file_path, start_date, end_date):
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
    try:
        data = pd.read_csv(file_path)
        data['Start Time'] = pd.to_datetime(data['Start Time'], errors='coerce', format='ISO8601')
        data['YearMonth'] = data['Start Time'].dt.strftime('%Y-%m')
        data['Total Time (seconds)'] = pd.to_timedelta(data['Total Time']).dt.total_seconds()
        monthly_totals = data.groupby('YearMonth')['Total Time (seconds)'].sum().reset_index()
        monthly_totals['Total Time (hours)'] = monthly_totals['Total Time (seconds)'] / 3600
        monthly_totals['Expected'] = 126
        monthly_totals['Difference'] = monthly_totals['Total Time (hours)'] - monthly_totals['Expected']
        monthly_totals = monthly_totals.drop(columns=['Total Time (seconds)'])

        total_row = pd.DataFrame({
            'YearMonth': ['Total'],
            'Total Time (hours)': [monthly_totals['Total Time (hours)'].sum()],
            'Expected': [monthly_totals['Expected'].sum()],
            'Difference': [monthly_totals['Difference'].sum()]
        })

        monthly_totals = pd.concat([monthly_totals, total_row], ignore_index=True)

        return monthly_totals
    except FileNotFoundError:
        print(f"Error: File not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    input_file = None
    while True:
        input_file = input("Enter the path to the exported CSV file from furtherance: ").strip()
        if os.path.exists(input_file):
            break
        else:
            print("File not found. Please enter a valid file path.")

    date_pattern = r'^\d{4}-\d{2}-\d{2}$'

    while True:
        start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
        if re.match(date_pattern, start_date):
            break
        else:
            print("Invalid date format. Please use YYYY-MM-DD.")

    while True:
        end_date = input("Enter the end date (YYYY-MM-DD): ").strip()
        if re.match(date_pattern, end_date):
            try:
                if datetime.strptime(start_date, "%Y-%m-%d").date() <= datetime.strptime(end_date, "%Y-%m-%d").date():
                    break
                else:
                    print("End date must be after or equal to the start date.")
            except:
                print("invalid date")
        else:
            print("Invalid date format. Please use YYYY-MM-DD.")

    task_report = generate_task_report_by_time_range(input_file, start_date, end_date)
    monthly_report = generate_monthly_report(input_file)

    if task_report is not None and monthly_report is not None:
        try:
            with pd.ExcelWriter(f"{start_date}-report.xlsx") as writer:
                month_name = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m - %B")
                task_report.to_excel(writer, sheet_name=month_name, index=False)
                monthly_report.to_excel(writer, sheet_name="General report", index=False)
            print(f"Reports saved to {start_date}-report.xlsx")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
    else:
        print("Error generating reports.")

if __name__ == "__main__":
    main()
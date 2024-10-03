import csv
import re
from datetime import datetime

def get_announcement_priority(announcement):
    priorities = {
        'Annual Results': 1,
        'Interim Results': 1,
        'CD': 2,
    }
    return priorities.get(announcement, 9)  # Default priority for any unspecified announcement

def process_sort_txt(input_file, output_file):
    with open(input_file, 'r') as file:
        content = file.read()

    # Split the content into rows
    rows = re.split(r'(?=Release Time: )', content)

    # Prepare data for CSV
    csv_data = []

    for row in rows:
        if row.strip():
            # Extract release date and time
            match = re.search(r'Release Time: (\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})', row)
            if match:
                release_date = match.group(1)
                release_time = match.group(2)
                release_datetime = f"{release_date} {release_time}"
            else:
                continue  # Skip this row if no valid release time found

            # Determine announcement type
            if 'Annual Report' in row:
                announcement = 'Annual Report'
            elif 'Interim/Half-Year Report' in row:
                announcement = 'Interim/Half-Year Report'
            elif 'Results of AGM' in row:
                announcement = 'Results of AGM'
            elif 'SALES PERFORMANCE' in row or 'Sales Performance' in row:
                announcement = 'Sales Performance'
            elif 'ANNUAL RESULTS ANNOUNCEMENT' in row or 'Annual Results Announcement' in row:
                announcement = 'Annual Results'
            elif 'Interim Results Announcement' in row:
                announcement = 'Interim Results'
            elif 'Dividend or Distribution' in row:
                announcement = 'CD'
            elif 'Profit Warning / Inside Information' in row:
                announcement = 'Profit Warning'
            else:
                continue  # Skip this row if no valid announcement type

            csv_data.append([release_datetime, announcement, release_date])

    # First, sort by announcement priority
    csv_data.sort(key=lambda x: get_announcement_priority(x[1]))

    # Then, sort by date only in descending order
    csv_data.sort(key=lambda x: datetime.strptime(x[2], '%d/%m/%Y'), reverse=True)

    # Remove the extra date column used for sorting
    csv_data = [[row[0], row[1]] for row in csv_data]

    # Add header row
    csv_data.insert(0, ['Release Date & Time', 'Announcements'])

    # Write to CSV file
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

# Usage
process_sort_txt('sort.txt', 'hksort.csv')
print("Processing complete. Output written to hksort.csv")